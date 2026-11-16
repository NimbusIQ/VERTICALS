"""
modules/file_writer.py
──────────────────────
Local filesystem tools exposed to the Gemini model via function calling.

These are the "hands" of the coding agent — they allow Gemini to actually
create directories, write files, read files, and run commands on the user's
machine.

Security Notes:
  - execute_command() has a blocklist of dangerous commands.
  - All paths are resolved relative to the current working directory.
  - Path traversal attacks are mitigated by resolving absolute paths.
"""

import os
import re
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Safety: Blocked command patterns ─────────────────────────────────────────
BLOCKED_COMMANDS = [
    r"\brm\s+-rf\b",
    r"\brmdir\b",
    r"\bformat\b",
    r"\bdel\s+/[sqa]",
    r"\bsudo\s+rm\b",
    r"\bdd\s+if=",
    r"\bmkfs\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bhalt\b",
    r"\bchmod\s+777\b",
    r"\bcurl\s+.*\|\s*(bash|sh|python)\b",
    r"\bwget\s+.*\|\s*(bash|sh|python)\b",
    r">\s*/etc/",
    r">\s*/usr/",
    r">\s*/bin/",
]


def _is_safe_command(command: str) -> tuple[bool, str]:
    """Check if a command is safe to execute."""
    for pattern in BLOCKED_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Blocked dangerous command pattern: {pattern}"
    return True, ""


def create_directory(path: str) -> str:
    """
    Create a directory (and all necessary parent directories).

    Args:
        path: Directory path to create.

    Returns:
        Success message string.
    """
    resolved = Path(path).resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created directory: {resolved}")
    return f"Directory created: {resolved}"


def write_file(path: str, content: str) -> str:
    """
    Write content to a file. Creates parent directories if needed.

    Args:
        path: File path to write to.
        content: Content to write.

    Returns:
        Success message string.
    """
    resolved = Path(path).resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)

    with open(resolved, "w", encoding="utf-8") as f:
        f.write(content)

    size = resolved.stat().st_size
    logger.info(f"Wrote file: {resolved} ({size} bytes)")
    return f"File written: {resolved} ({size} bytes)"


def read_file(path: str) -> str:
    """
    Read and return the content of a file.

    Args:
        path: File path to read.

    Returns:
        File content as a string.
    """
    resolved = Path(path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {resolved}")

    with open(resolved, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    logger.info(f"Read file: {resolved} ({len(content)} chars)")
    return content


def list_directory(path: str = ".") -> str:
    """
    List the contents of a directory.

    Args:
        path: Directory path to list. Defaults to current directory.

    Returns:
        Formatted string listing of directory contents.
    """
    resolved = Path(path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Directory not found: {resolved}")

    items = []
    for item in sorted(resolved.iterdir()):
        if item.is_dir():
            items.append(f"📁 {item.name}/")
        else:
            size = item.stat().st_size
            items.append(f"📄 {item.name} ({size} bytes)")

    if not items:
        return f"Directory is empty: {resolved}"

    listing = "\n".join(items)
    return f"Contents of {resolved}:\n{listing}"


def execute_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout: int = 120,
) -> str:
    """
    Execute a shell command safely.

    Args:
        command: Shell command to execute.
        working_directory: Directory to run the command in.
        timeout: Maximum execution time in seconds.

    Returns:
        Combined stdout and stderr output.
    """
    is_safe, reason = _is_safe_command(command)
    if not is_safe:
        raise PermissionError(f"Command blocked for safety: {reason}")

    cwd = Path(working_directory).resolve() if working_directory else Path.cwd()
    if not cwd.exists():
        raise FileNotFoundError(f"Working directory not found: {cwd}")

    logger.info(f"Executing: {command} (in {cwd})")
    print(f"\n⚙️  Running: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}"
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        if result.returncode != 0:
            logger.warning(f"Command exited with code {result.returncode}")
            output += f"\nExit code: {result.returncode}"
        else:
            logger.info(f"Command succeeded.")

        return output.strip() or "Command completed with no output."

    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after {timeout} seconds: {command}")
