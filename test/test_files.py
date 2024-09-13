from argparse import ArgumentTypeError
from os.path import exists, isdir, join, split
from pathlib import Path
from re import compile
from tempfile import NamedTemporaryFile, TemporaryDirectory

from pytest import TEMPFILE_CONTENTS, TEMPFILE_CONTENTS_IGNORED, raises  # type: ignore

from plox.tools.environment import modified_environ
from plox.tools.files import (
    bin_file_contents,
    ensure_dir,
    existing_filepath,
    file_contents,
    file_contents_from_envar,
    file_lines,
    format_bytes,
    list_files,
    walkdir,
)


def test_format_bytes_metric():
    assert format_bytes(1, metric=True, precision=0) == "1 B"
    for prec in range(1, 10):
        assert format_bytes(1, metric=True, precision=prec) == f"1.{'0'*prec} B"

    pebibytes = 2251799813685247
    assert format_bytes(pebibytes, True, 7) == "2.2517998 PB"
    assert format_bytes(pebibytes, True, 6) == "2.251800 PB"
    assert format_bytes(pebibytes, True, 5) == "2.25180 PB"
    assert format_bytes(pebibytes, True, 4) == "2.2518 PB"
    assert format_bytes(pebibytes, True, 3) == "2.252 PB"
    assert format_bytes(pebibytes, True, 2) == "2.25 PB"
    assert format_bytes(pebibytes, True, 1) == "2.3 PB"
    assert format_bytes(pebibytes, True, 0) == "2 PB"

    petabytes = 2000000000000000
    for precision in range(1, 10):
        assert format_bytes(petabytes, True, precision) == f"2.{"0"*precision} PB"

    assert format_bytes(petabytes, True, 0) == "2 PB"


def test_format_bytes_binary():
    assert format_bytes(1, precision=0) == "1 B"
    for prec in range(1, 4):
        assert format_bytes(1, precision=prec) == "1." + "0" * prec + " B"

    pebibytes = 2251799813685247
    for precision in range(1, 10):
        assert format_bytes(pebibytes, precision=precision) == f"2.{"0"*precision} PiB"
    assert format_bytes(pebibytes, precision=0) == "2 PiB"

    petabytes = 2000000000000000
    assert format_bytes(petabytes, precision=3) == "1.776 PiB"
    assert format_bytes(petabytes, precision=2) == "1.78 PiB"
    assert format_bytes(petabytes, precision=1) == "1.8 PiB"
    assert format_bytes(petabytes, precision=0) == "2 PiB"


def test_file_contents(temp_file_creation: Path):
    assert file_contents(temp_file_creation) == TEMPFILE_CONTENTS


def test_bin_file_contents():
    tempbin = NamedTemporaryFile("wb")
    tempbin.write(b"hello, world!\ntest")
    tempbin.seek(0)
    try:
        assert bin_file_contents(tempbin.name) == b"hello, world!\ntest"
    finally:
        tempbin.close()


def test_file_contents_from_envar(temp_file_creation: Path):
    with modified_environ(ENVAR_TO_READ=str(temp_file_creation)):
        assert file_contents_from_envar("ENVAR_TO_READ") == TEMPFILE_CONTENTS


def test_file_lines(temp_file_creation: Path):
    def ignore():
        assert file_lines(temp_file_creation, skip_filtration=True) == TEMPFILE_CONTENTS.split(  # type: ignore
            "\n"
        )

    def no_ignore():
        assert file_lines(temp_file_creation, skip_filtration=False) == TEMPFILE_CONTENTS_IGNORED

    def ignore_non_standard():
        assert file_lines(temp_file_creation, skip_filtration=False, patterns=[compile(".*")]) == []

        assert file_lines(
            temp_file_creation, skip_filtration=False, patterns=[compile("NOTHING")]
        ) == TEMPFILE_CONTENTS.split("\n")  # type: ignore

    no_ignore()
    ignore()
    ignore_non_standard()


def test_walkdir_delete_folder_and_contents(temp_file_creation: Path):
    tempdir = str(temp_file_creation.parents[0])
    tempdir_up_dir = str(temp_file_creation.parents[1])

    assert list(walkdir(f"{tempdir}/*")) == [f"{tempdir}/file.txt"]
    assert f"{tempdir}/file.txt" in list(walkdir(f"{tempdir_up_dir}/**"))
    assert list(walkdir(f"{tempdir_up_dir}/**", recursive=False)) == []
    assert list(walkdir(f"{tempdir}/*", True, [".*"])) == []
    assert list(walkdir(f"{tempdir}/*", True, [".*DUMMYPATTERN.*"])) == [f"{tempdir}/file.txt"]


def test_ensure_dir():
    with TemporaryDirectory() as tempdir:
        to_make = join(tempdir, "foo", "bar", "baz", "")
        assert not exists(to_make)
        ensure_dir(to_make)
        assert exists(to_make) and isdir(to_make)

        to_make = join(tempdir, "oof", "rab", "zab", "qux.txt")
        ensure_dir(to_make)
        assert exists(split(to_make)[0]) and isdir(split(to_make)[0])


def test_list_files():
    alpha_files = ["abb.txt", "bat.txt", "c.txt", "zar.txt", "zod.txt"]
    with TemporaryDirectory() as tempdir:
        for f in alpha_files:
            fpath = Path(join(tempdir, f))
            fpath.touch()

            assert existing_filepath(str(fpath))

        assert list_files(tempdir, sort=True) == sorted(alpha_files)

    with raises(ArgumentTypeError) as e:
        existing_filepath("/tmp/some/non/existent/file.txt")
        assert e.match(".*does not exist.*")
