# ruff: noqa

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import call

from plox.tools.system import sync_command, sys_exec
from pytest import LogCaptureFixture, raises


def test_sys_exec(temp_file_creation: Path, caplog: LogCaptureFixture):
    parent_dir = temp_file_creation.parents[0]
    out_file = parent_dir / "output.txt"

    rc = sys_exec(
        parent_dir, Path("/bin/ls"), exec_args=[], environment={}, stdout_file_dest=out_file
    )
    assert "o>> file.txt" in caplog.text.strip()

    assert rc == 0
    with open(str(out_file)) as infile:
        assert "file.txt" in infile.read()


def test_sys_exec_neg_bad_exec(temp_file_creation: Path):
    parent_dir = temp_file_creation.parents[0]
    out_file = parent_dir / "output.txt"

    with raises(RuntimeError) as e:
        sys_exec(
            parent_dir, Path("/bin/lsss"), exec_args=[], environment={}, stdout_file_dest=out_file
        )
    assert e.exconly() == "RuntimeError: Cannot use given executable: /bin/lsss"


def test_sys_exec_neg(temp_file_creation: Path, caplog: LogCaptureFixture):
    parent_dir = temp_file_creation.parents[0]
    out_file = parent_dir / "output.txt"

    rc = sys_exec(
        parent_dir,
        Path("/bin/ls"),
        exec_args=["--garbage"],
        environment={},
        stdout_file_dest=out_file,
    )

    assert rc != 0
    assert "unrecognized option" in caplog.text.strip()


def test_sys_exec_neg_no_errlog(temp_file_creation: Path, caplog: LogCaptureFixture):
    parent_dir = temp_file_creation.parents[0]
    out_file = parent_dir / "output.txt"

    rc = sys_exec(
        parent_dir,
        Path("/bin/ls"),
        exec_args=["garbage"],
        environment={},
        stdout_file_dest=out_file,
        quiet_stderr=True,
    )

    assert rc != 0
    assert "Set up output to capture file" in caplog.text
    assert "Executing" in caplog.text
    assert "e>>" not in caplog.text


def test_sync_command(temp_file_creation: Path):
    def test_valid(out: CompletedProcess[bytes]) -> None:
        assert out.stderr.decode() == ""
        assert out.stdout.decode().strip() == str(temp_file_creation)
        assert out.returncode == 0

    def no_shell():
        test_valid(sync_command(f"ls {str(temp_file_creation)}", shell=False, exit_on_error=False))

    def shell():
        test_valid(sync_command(f"ls {str(temp_file_creation)}", shell=True, exit_on_error=False))

    no_shell()
    shell()


def test_sync_command_negative():
    out = sync_command("ls /doesnotexit", shell=True, exit_on_error=False)
    assert out.stdout.decode() == ""
    assert (
        out.stderr.decode().strip() == "ls: cannot access '/doesnotexit': No such file or directory"
    )

    with raises(SystemExit) as e:
        out = sync_command("ls /doesnotexit", shell=False, exit_on_error=True)
    assert e.exconly() == "SystemExit: -1"
    assert e.type == SystemExit
    assert e.value.code == -1
