from pathlib import Path

import pytest

TEMPFILE_ENV = """FOO=BAR
BAZ=QUX
# comment"""

TEMPFILE_CONTENTS = """foo
bar
baz qux
# comment

end
FOOBAR=foobar
KEY=VALUE"""
TEMPFILE_CONTENTS_IGNORED = ["foo", "bar", "baz qux", "end", "FOOBAR=foobar", "KEY=VALUE"]


@pytest.fixture(scope="function")
def temp_file_creation(tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp_path_factory._retention_policy = "none"
    tmpdir: Path = tmp_path_factory.mktemp("slurptest")
    tempfile: Path = tmpdir / "file.txt"
    with open(tempfile, "a") as outfile:
        outfile.write(TEMPFILE_CONTENTS)
    return tempfile


@pytest.fixture(scope="function")
def temp_env_file_creation(tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp_path_factory._retention_policy = "none"
    tmpdir: Path = tmp_path_factory.mktemp("slurptest")
    tempfile: Path = tmpdir / "file.env"
    with open(tempfile, "a") as outfile:
        outfile.write(TEMPFILE_ENV)
    return tempfile


def pytest_configure(config):
    pytest.TEMPFILE_CONTENTS = TEMPFILE_CONTENTS
    pytest.TEMPFILE_CONTENTS_IGNORED = TEMPFILE_CONTENTS_IGNORED
    pytest.TEMPFILE_ENV = TEMPFILE_ENV
