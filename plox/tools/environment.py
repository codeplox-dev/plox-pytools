"""Assorted utilities for dealing with anything related the current process' environment.

.. code-block:: python

    from plox.tools import environment
"""

from __future__ import annotations

from contextlib import contextmanager
from logging import getLogger
from os import environ
from os.path import expandvars
from pathlib import Path
from re import compile as re_compile
from typing import Any, Generator

from plox.tools.files import FilePath, file_lines

logger = getLogger(__name__)


class MissingEnvironmentVariableError(Exception):
    """Custom exception to represent a missing environment variable."""

    pass


def parse_environment_file_to_values(envfile: FilePath, expand_vars: bool = True) -> dict[Any, Any]:
    """Parse local file containing key=value environment pairs into their values and return as dict.

    The environment file should consistent of a set of <keys>=<values> where the
    keys represent environment variable names, and <values> are their value.

    An example envfile:

    .. code-block:: text

        FOOBAR=/tmp/some_key
        FOOBAZ=${HOME}/some_other_key

    ``parse_environment_file_to_values`` would return the following dict:

    .. code-block:: python

        {"FOOBAR": "/tmp/some_key", "FOOBAZ": "<expanded HOME variable>/some_other_key"}

    Args:
        envfile: Path to local file on disk containing vars to parse into the environment.
        expand_vars: Whether or not to expand variables in the values. Default ``true``.

    Returns:
        dict[typing.Any, typing.Any]: The dictionary representing the key:value pairs of
        the env file.
    """
    pattern = re_compile(r"(?P<key>[^=]+)=(?P<value>.*)")

    def process_line(line: str) -> tuple[Any, Any]:
        m = pattern.search(line)
        if not m:
            raise RuntimeError(f"Failed to prepare environment line {line}")

        val = m.group("value")
        if expand_vars:
            val = expandvars(val)

        return m.group("key"), val

    prepped = dict(map(process_line, file_lines(envfile)))
    return prepped


def add_to_env_from_file(environment_file: FilePath) -> None:
    """Add a set of ``key=value`` pairs from an env file to the current environment.

    The environment file should consistent of a set of <keys>=<values> where the
    keys represent environment variable names, and <values> are their value.

    For example, if the following envfile resided at ``/tmp/foo.env``:

    .. code-block:: text

        FOOBAR=/tmp/some_key
        FOOBAZ=${HOME}/some_other_key

    ``add_to_env_from_file("/tmp/foo.env")`` would result in the following items
    being added to the process' environ:

    .. code-block:: python

        {"FOOBAR": "/tmp/some_key", "FOOBAZ": "<expanded HOME variable>/some_other_key"}

    Args:
        environment_file: Path to local file on disk containing vars
            to parse into environment.
    """
    for k, v in parse_environment_file_to_values(environment_file, expand_vars=True).items():
        logger.debug(f"Setting envvar {k} from file {environment_file}")  # type: ignore
        environ[k] = v


def ensure_envars_set(
    to_validate: list[str], are_paths: bool = False, create_ok: bool = False
) -> None:
    """Validate that a list of variables exists in current environment.

    Args:
        to_validate: A list of envar names to check existence of.
        are_paths: Whether or not the envars are representing local file system paths
            that should exist; if set to ``True``, each envar's value will be checked to
            ensure is an existing path.
        create_ok: Whether or not the path should be created if not existent.

    Raises:
        MissingEnvironmentVariableError: If any specified items in ``to_validate`` are
            not in present env.
        OSError: If error encountered when trying to make directory to path when
            ``are_paths`` is also ``True``.
    """
    for var in to_validate:
        try:
            if var not in environ:
                raise MissingEnvironmentVariableError(f"{var} is not set.")

            if are_paths:
                p = Path(environ[var])

                if p.exists():
                    continue

                if not p.exists() and not create_ok:
                    logger.error(f"ERR - {var}'s path {p.name} is not an existing path")
                    raise MissingEnvironmentVariableError(f"{var} does not exist on local disk.")

                try:
                    p.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    logger.error(f"ERR - couldn't make {var}'s path {p.name}")
                    logger.error(str(e))
                    raise e

        except AssertionError:
            logger.error(f"ERR - must set envar {var} to required value")
            exit(-1)


def envvar_or_bail(k: str) -> str:
    """Read and return an environment variable or raise an Exception.

    Args:
        k: Key name for environment variable to read.

    Raises:
        MissingEnvironmentVariableError: If specified ``k`` not in present env.

    Returns:
        str: Value of environment variable
    """
    if (v := environ.get(k, None)) is None:
        raise MissingEnvironmentVariableError(f"{k} is not set.")
    return v


@contextmanager
def modified_environ(*remove: str, **update: str) -> Generator[None, None, None]:
    """Temporarily modify process environment within a contextmanger wrapping.

    Will remove and/or update process' environment values based on based
    arguments. Useful for running a command/sub-process with a temporarily modified
    env. If ``"ALL"`` is passed as an argument to remove, then the entirety of the
    existing environment will be removed.

    Example:

        >>> # removing all vars
        >>> from plox.tools.environment import modified_environ
        >>> from os import environ
        >>> len(environ)
        72
        >>> with modified_environ("ALL"):
        >>>     print(len(env))
        0
        >>> len(environ)
        72
        >>> # Adding a temporary var
        >>> environ.get("FOOBAR", "not set")
        'not set'
        >>> with modified_environ(FOOBAR="set"):
        >>>     print(environ.get("FOOBAR", "not set"))
        set
        >>> environ.get("FOOBAR", "not set")
        'not set'
        >>> # both
        >>> with modified_environ("ALL", FOOBAR="set"):
        >>>     print(len(env))
        1

    Args:
        remove: Name of environment variables to _remove_ from the environment.
        update: Dictionary pairing of key:value items to _add_ to the environment.

    Returns:
        typing.Generator[None, None, None]: Modified envrionment
        that will be reverted upon context manager exiting scope.
    """
    env = environ
    update = update or {}
    remove = remove or []  # type: ignore
    if "ALL" in remove:
        remove = environ.keys()  # type: ignore

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        [env.pop(k, None) for k in remove]
        env.update(update)
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]
