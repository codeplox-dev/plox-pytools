"""Utilities for interaction with local system binaries, executables, etc.

.. code-block:: python

    from plox.tools import system
"""

from datetime import datetime, timedelta, timezone
from functools import partial
from logging import ERROR, INFO, getLogger
from pathlib import Path
from subprocess import PIPE, CompletedProcess, Popen
from subprocess import run as subproc_run
from threading import Thread
from time import sleep, time
from typing import IO, Any, Callable, Optional

logger = getLogger(__name__)
exec_logger = getLogger("sys_exec")


def _join_logging_thread(log_fn: Callable[..., None], pipe: Optional[IO[str]]) -> None:
    """Join an existing logging function running in a thread to current stream.

    Args:
        log_fn (Callable[..., None]): Function that is responsible for logging
            output that will be collected.
        pipe (IO[str]): Pipe that should be logged to.
    """
    th = Thread(target=log_fn, args=[pipe])
    th.start()
    th.join()


def _process_out(level: int, prefix: str, cap_dest: Optional[Path], pipe: IO[str]) -> None:
    """Read a logging thread input to pipe.

    Args:
        level (int): Log level
        prefix (str): Prefix to included to every logged message's beginning.
        cap_dest (Optional[Path]): Optional path on disk to store captured
            text to. By default, is not captured to file.
        pipe (IO[str]): Pipe that is being logged to.
    """
    cap_f = None

    if cap_dest is not None:
        cap_dest.parent.mkdir(mode=0o0700, parents=True, exist_ok=True)
        cap_f = cap_dest.open("w")
        logger.info(f"Set up output to capture file: {cap_dest}")

    try:
        while True:
            if pipe.closed:
                return

            try:
                if (line := pipe.readline()) != "":
                    exec_logger.log(level, f"{prefix} {line.rstrip()}")
                    if cap_f is not None:
                        cap_f.write(line)
                else:
                    return
            except Exception as ex:
                logger.error("Exception occurred while processing log messages from subprocess")
                logger.error(ex)
    finally:
        if cap_f is not None:
            cap_f.flush()
            cap_f.close()


def sys_exec(
    cwd: Path,
    executable: Path,
    exec_args: list[str],
    environment: dict[Any, Any],
    stdout_file_dest: Optional[Path] = None,
    quiet_stderr: bool = False,
    exec_timeout_mins: int = 24,
) -> int:
    """Execute a system command, threaded logging safe.

    Args:
        cwd (Path): Current directory that command is being invoked from.
        executable (Path): Path to local binary that should be excecuted.
        exec_args (list[str]): List of args to pass to the executable.
        environment (dict[Any, Any]): Dictionary of k:v pairings to pass to
            the executable process' environment.
        stdout_file_dest (Optional[Path]): Optional file to log output text to.
            By default, does not log to file.
        quiet_stderr (bool): Whether or not stderr output should be silenced.
            By default, stderr is **not** silenced.
        exec_timeout_mins (int): Time in minutes before command is timed out.
            By default, is 24 minutes.

    Returns:
        int: Return code of executed process.
    """
    if not executable.exists():
        raise RuntimeError(f"Cannot use given executable: {executable}")

    # all of the command input joined together
    exec_all = [str(executable), *exec_args]

    logger.debug(f"Executing {exec_all} in {cwd}")

    with Popen(  # noqa: S603
        exec_all,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        bufsize=1,
        universal_newlines=True,
        cwd=cwd,
        env=environment,
        close_fds=True,
    ) as p:
        info_proc_out: Callable[..., None] = partial(_process_out, INFO, "o>>", stdout_file_dest)
        _join_logging_thread(info_proc_out, p.stdout)
        if not quiet_stderr:
            _join_logging_thread(partial(_process_out, ERROR, "e>>", None), p.stderr)

        p.wait(timeout=exec_timeout_mins)
        return p.returncode


def sync_command(
    cmd: str, shell: bool = False, exit_on_error: bool = False
) -> CompletedProcess[bytes]:
    """Executed a system command.

    Args:
        cmd (str): Command to execute on host.
        shell (bool): Whether or not to execute the command as passed, or
            if should be tokenized and passed as list of values to subprocess.
            By default, passed command is split for safety.
        exit_on_error (bool): Whether or not hard exit should occur if process
            does not return successfully. By default, false.

    Returns:
        CompletedProcess[bytes]: The completed process.
    """
    proc = None
    if shell:
        proc = subproc_run(cmd, capture_output=True, shell=True)  # noqa: S602
    else:
        proc = subproc_run(cmd.split(), capture_output=True)  # noqa: S603

    if proc.returncode != 0:
        logger.error(proc.stderr)
        if exit_on_error:
            exit(-1)
    return proc


def block_until(
    condition: Callable[[], bool],
    effect: Callable[[], int],
    timeout_s: int = 360,
    condition_fail_wait_s: int = 10,
) -> int:
    """Block execution (up to timeout_s) until (condition) returns True.

    When condition returns true, executes `effect`.

    Args:
        condition (Callable[[], bool]): Condition to wait for.
        effect (Callable[[], int]): Effect to trigger once condition is met.
        timeout_s (int): Max time in seconds to wait for `condition`. By
            default, is 6 minutes (360 seconds).
        condition_fail_wait_s (int): On condition fail, time to wait before
            attempting to check condition again. By default, is 10 seconds.

    Returns:
        int: `effect`'s return code.
    """
    start = datetime.fromtimestamp(int(time()), timezone.utc)
    while True:
        if datetime.fromtimestamp(int(time()), timezone.utc) - start > timedelta(seconds=timeout_s):
            raise TimeoutError(
                f"Timeout waiting for condition {condition} to obtain before executing {effect}"
            )

        if condition():
            logger.debug("Condition obtained, executing effect")
            return effect()
        else:
            logger.info(f"Condition failed, sleeping for {condition_fail_wait_s} seconds")
            sleep(condition_fail_wait_s)


def syscall_to_condition(call: Callable[[], int]) -> Callable[[], bool]:
    """Convert syscall function (returns int) to boolean with exception catch.

    Args:
        call (Callable[[], int]): System call funciton that should be wrapped
            into a condition that is awaited until exit code.

    Returns:
        Callable[[], bool]: Wrapped system call.
    """

    def _c() -> bool:
        try:
            return call() == 0
        except Exception as ex:
            logger.exception(ex)
            return False

    return _c
