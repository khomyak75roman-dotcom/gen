"""
Subprocess utility functions.
"""

import asyncio
import shlex
import subprocess
from pathlib import Path
from typing import Optional, Union, List, Tuple

from .logging import get_logger

logger = get_logger(__name__)

def run_command(
    command: Union[str, List[str]],
    cwd: Optional[Union[str, Path]] = None,
    timeout: Optional[float] = None,
    check: bool = True,
    capture_output: bool = True,
    text: bool = True,
    encoding: str = "utf-8",
) -> subprocess.CompletedProcess:
    """
    Run a command and return the result.

    Args:
        command: Command to run (string or list)
        cwd: Working directory
        timeout: Timeout in seconds
        check: Raise exception on non-zero exit
        capture_output: Capture stdout/stderr
        text: Decode output as text
        encoding: Text encoding

    Returns:
        CompletedProcess
    """
    if isinstance(command, str):
        command = shlex.split(command)

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=text,
            encoding=encoding,
            errors="replace",
        )

        if check and result.returncode != 0:
            error_msg = result.stderr or result.stdout or ""
            logger.error(f"Command failed: {' '.join(command)}\nError: {error_msg[-500:]}")
            raise subprocess.CalledProcessError(
                result.returncode, command, result.stdout, result.stderr
            )

        return result
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {' '.join(command)}")
        raise

async def run_async(
    command: Union[str, List[str]],
    cwd: Optional[Union[str, Path]] = None,
    timeout: Optional[float] = None,
) -> Tuple[int, str, str]:
    """
    Run a command asynchronously.

    Args:
        command: Command to run
        cwd: Working directory
        timeout: Timeout in seconds

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    if isinstance(command, str):
        command = shlex.split(command)

    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )
        return (
            process.returncode,
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise

def check_output(
    command: Union[str, List[str]],
    cwd: Optional[Union[str, Path]] = None,
    timeout: Optional[float] = None,
) -> str:
    """
    Run a command and return stdout.

    Args:
        command: Command to run
        cwd: Working directory
        timeout: Timeout in seconds

    Returns:
        stdout as string
    """
    result = run_command(
        command,
        cwd=cwd,
        timeout=timeout,
        check=True,
        capture_output=True,
    )
    return result.stdout or ""
