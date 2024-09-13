"""Assorted utilities for dealing with anything related to local file system.

If it is a generic method for dealing with something locally on disk, about a file,
or about something related to a file, it is a good bet that it is a function that
belongs in this module.

.. code-block:: python

    from plox.tools import files
"""

from __future__ import annotations

from argparse import ArgumentTypeError
from collections.abc import Generator
from functools import reduce
from glob import iglob
from logging import getLogger
from os import PathLike, environ, listdir, makedirs
from os.path import exists, expandvars, isdir, isfile
from os.path import join as path_join
from os.path import split as path_split
from pathlib import Path
from re import Pattern
from re import compile as re_compile
from re import match as re_match
from typing import Optional, Union

FilePath = Union[PathLike[str], bytes, Path, str]
"""Represent one of many formats for a local file on disk."""

logger = getLogger(__name__)


def format_bytes(number_bytes: Union[int, float], metric: bool = False, precision: int = 1) -> str:
    """Format bytes to human readable, using binary (1024) or metric (1000) representation.

    Inspired by: https://stackoverflow.com/a/63839503

    Example:

        >>> format_bytes(1024)
        '1.0 KiB'
        >>> format_bytes(1000)
        '1000.0 B'
        >>> format_bytes(1000, metric=True)
        '1.0 kB'
        >>> format_bytes(1024, metric=True, precision=3)
        '1.024 kB'
        >>> format_bytes(1_234_567_898_765_432, metric=True, precision=3)
        '1.235 PB'

    Args:
        number_bytes: The number of bytes to convert to a human
            readable labeled quantity.
        metric: Whether or not the metric system is used; Default is ``False`` -
            results in using binary.
        precision: Number of digits/precision. Must be between 1-3.

    Returns:
        str: The human friendly sized representation of the bytes.
    """
    metric_labels = ("B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    binary_labels = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    precision_offset = 5.0 / (10**precision)

    unit_labels = metric_labels if metric else binary_labels
    last_label = unit_labels[-1]
    unit_step = 1000 if metric else 1024
    unit_step_thresh = unit_step - precision_offset

    maybe_neg = ""
    if number_bytes < 0:
        number_bytes = abs(number_bytes)
        maybe_neg = "-"

    unit = "B"
    for unit in unit_labels:
        if number_bytes < unit_step_thresh:
            # Only accepts the CURRENT unit if we're BELOW the threshold where
            # float rounding behavior would place us into the NEXT unit: F.ex.
            # when rounding a float to 1 decimal, any number ">= 1023.95" will
            # be rounded to "1024.0". Obviously we don't want ugly output such
            # as "1024.0 KiB", since the proper term for that is "1.0 MiB".
            break
        if unit != last_label:
            # We only shrink the number if we HAVEN'T reached the last unit.
            # NOTE: These looped divisions accumulate floating point rounding
            # errors, but each new division pushes the rounding errors further
            # and further down in the decimals, so it doesn't matter at all.
            number_bytes /= unit_step

    return f"{maybe_neg}{number_bytes:.{precision}f} {unit}"


def file_contents(path: FilePath) -> str:
    """Read and return a local file path's contents as a string.

    Args:
        path (FilePath): Path on local disk to file.

    Returns:
        str: Contents of file
    """
    with open(path) as infile:
        return infile.read().rstrip()


def bin_file_contents(path: FilePath) -> bytearray:
    """Read and return a local binary file path's contents as a byte array.

    Args:
        path (FilePath): Path on local disk to file.

    Returns:
        bytearray: Contents of binary file.
    """
    bb = bytearray()

    with open(path, "rb") as inf:
        while (by := inf.read()) != b"":
            bb += by

        return bb


def file_contents_from_envar(key: str) -> str:
    """Fetch and envars's local file path's contents as a string.

    Args:
        key: Name of environment variable whose value represents the file
            path to read.

    Returns:
        str: Contents of the value of the environment's key at local disk path.
    """
    return file_contents(Path(expandvars(environ[key])))


def file_lines(
    filename: FilePath,
    skip_filtration: bool = True,
    patterns: Optional[list[Pattern[str]]] = None,
) -> list[str]:
    """Return the contents of a given filepath as its individual lines.

    By default, will not include any filtration of the file's contents. If desired,
    can set ``skip_filtration`` to ``True`` and specify the list of patterns to exclude
    (on a per-line ``re.match`` basis) via the ``patterns`` argument.

    Args:
        filename (FilePath): The path on disk of the file whose lines of content
            will be parsed and returned.
        skip_filtration: Whether the results should ignore any filtration.
            Default **true**.
        patterns: A list of regex patterns which
            if skip_filtration is false will be ignored if matching a given
            line.

    Returns:
        list[str]: The set of lines that the file consists of after potentially
        filtering.
    """
    content = file_contents(filename).splitlines()
    if skip_filtration:
        return content

    if not patterns:
        patterns = [re_compile(p) for p in [r"^#", r"^\s*$"]]

    acc: list[str] = []
    for li in content:
        li = li.strip()
        if not reduce(lambda a, m: a or m, (bool(re_match(p, li)) for p in patterns), False):  # pyright: ignore
            acc.append(li)
    return acc


def delete_folder_and_contents(pth: Path) -> None:
    """Recursively deletes a given folder path.

    Args:
        pth: The path to local disk to entirely remove.
    """
    if pth.resolve() in [Path("/"), Path("~").expanduser()]:
        logger.warning("Hm, this looks pretty dangerous.")
        return

    for sub in pth.iterdir():
        if sub.is_dir():
            delete_folder_and_contents(sub)
        else:
            sub.unlink()
    pth.rmdir()


def walkdir(
    dirpattern: str, recursive: bool = True, ignore_pattern: Optional[list[str]] = None
) -> Generator[str, None, None]:
    """Walk a local directory, and yield a set of found files.

    Args:
        dirpattern: The pattern to walk through. Example, ``**`` or
            ``/some/path/**``.
        recursive: Whether or not to recursively list sub-items.
        ignore_pattern: A list of wildcard like patterns
            that, if provided, any file matching will _not_ be returned.
    """
    for filename in iglob(dirpattern, recursive=recursive):
        if Path(filename).is_file():
            if ignore_pattern is None:
                yield filename
            else:
                any_skipped = False
                for p in ignore_pattern:
                    if re_match(p, filename):
                        any_skipped = True

                if not any_skipped:
                    yield filename


def ensure_dir(path: str) -> None:
    """Ensure the local directory structure exists for a given path.

    If the path does not exist as a directory, it is made.

    Args:
        path: The path at to check is a valid directory path.
    """
    dirpath, _ = path_split(path)
    if len(dirpath) != 0 and not isdir(dirpath):
        makedirs(dirpath)


def list_files(directory_path: str, sort: bool = False) -> list[str]:
    """Return a list of files (str) in a directory.

    Args:
        directory_path: The path to the local directory on disk.
        sort: Whether or not the results should be alphabetically sorted. Default
            ``False``.
    """
    files = [f for f in listdir(directory_path) if isfile(path_join(directory_path, f))]
    if sort:
        return sorted(files)
    return files


def existing_filepath(file_path: str) -> str:
    """Check whether a given path is an existent file.

    If not, raises and ArgumentTypeError, as the intended purpose of
    this helper utility is a type for an argparse argument.

    Args:
        file_path: The path to the file to check exists.

    Raises:
        argparse.ArgumentTypeError: If the given ``file_path`` does not exist.

    Returns:
        str: Passed in ``file_path``
    """
    if not exists(file_path):
        raise ArgumentTypeError(f"{file_path} does not exist")
    return file_path
