from os import environ, getuid
from pathlib import Path
from pwd import getpwuid

import pytest

from plox.tools.environment import (
    MissingEnvironmentVariableError,
    ensure_envars_set,
    envvar_or_bail,
    parse_environment_file_to_values,
)


def test_envvar_or_bail():
    envar = "FOO_BAR_TESTING_BAZ_QUZ_BAIL"
    if envar in environ:
        del environ[envar]

    with pytest.raises(MissingEnvironmentVariableError):
        envvar_or_bail(envar)

    environ[envar] = "foo"
    val = envvar_or_bail(envar)
    assert val == "foo"


def test_ensure_envars_set(temp_file_creation: Path):
    from os import environ

    if "FOO_BAR_TESTING_BAZ_QUZ" in environ:
        del environ["FOO_BAR_TESTING_BAZ_QUZ"]
    try:
        environ["FOO_BAR_TESTING_BAZ_QUZ"] = "foobar"
        assert ensure_envars_set(["FOO_BAR_TESTING_BAZ_QUZ"]) is None

        del environ["FOO_BAR_TESTING_BAZ_QUZ"]

        with pytest.raises(MissingEnvironmentVariableError) as pytest_wrapped_e:
            ensure_envars_set(["FOO_BAR_TESTING_BAZ_QUZ"])
        assert pytest_wrapped_e.type is MissingEnvironmentVariableError
        assert pytest_wrapped_e.value.args == ("FOO_BAR_TESTING_BAZ_QUZ is not set.",)
        ### paths
        # valid
        environ["FOO_BAR_TESTING_BAZ_QUZ"] = str(temp_file_creation)
        assert ensure_envars_set(["FOO_BAR_TESTING_BAZ_QUZ"], True) is None

        # not valid
        p: Path = temp_file_creation.parents[0] / "doesnotexit.txt"
        environ["FOO_BAR_TESTING_BAZ_QUZ"] = str(p)
        with pytest.raises(MissingEnvironmentVariableError) as pytest_wrapped_e:
            ensure_envars_set(["FOO_BAR_TESTING_BAZ_QUZ"], True, False)
        assert pytest_wrapped_e.type is MissingEnvironmentVariableError
        assert pytest_wrapped_e.value.args == (
            "FOO_BAR_TESTING_BAZ_QUZ does not exist on local disk.",
        )

        assert ensure_envars_set(["FOO_BAR_TESTING_BAZ_QUZ"], True, True) is None
        assert ensure_envars_set(["FOO_BAR_TESTING_BAZ_QUZ"], True, False) is None

        # does not exist, unable to create
        if getpwuid(getuid())[0] == "root":
            return

        p: Path = Path("/thisdirdoesnotexist/doesnotexist.txt")
        environ["FOO_BAR_TESTING_BAZ_QUZ"] = str(p)
        with pytest.raises(OSError) as e:
            ensure_envars_set(["FOO_BAR_TESTING_BAZ_QUZ"], True, True)
        assert e.exconly() == "OSError: [Errno 30] Read-only file system: '/thisdirdoesnotexist'"

    finally:
        if "FOO_BAR_TESTING_BAZ_QUZ" in environ:
            del environ["FOO_BAR_TESTING_BAZ_QUZ"]


def test_parse_environment_file_to_values(temp_file_creation: Path, temp_env_file_creation: Path):
    def test_non_compliant():
        with pytest.raises(RuntimeError) as e:
            parse_environment_file_to_values(str(temp_file_creation))
            assert e.exconly == "Failed to prepare environment line foo"

    def test_compliant():
        d = parse_environment_file_to_values(str(temp_env_file_creation))
        assert d == {"FOO": "BAR", "BAZ": "QUX"}

    test_non_compliant()
    test_compliant()
