"""Prepare the environment for uv execution"""

import asyncio
import subprocess
import sys
from pathlib import Path


# Process both stdout and stderr
async def read_stream(stream: asyncio.StreamReader):
    while True:
        chunk = await stream.read(n=1024)

        if not chunk:
            break
        text = chunk.decode("utf-8").rstrip()
        print(text)
        sys.stdout.flush()


async def sync(project_dir: Path, uv_executable: Path):
    process = await asyncio.create_subprocess_shell(
        f"rm -rf .venv && {uv_executable} sync --no-install-workspace",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={"VIRTUAL_ENV": ".venv", "PYTHONUNBUFFERED": "1"},
        cwd=project_dir.as_posix(),
    )

    stdout_task = asyncio.create_task(read_stream(process.stdout))
    stderr_task = asyncio.create_task(read_stream(process.stderr))

    await asyncio.wait([stdout_task, stderr_task])
    returncode = await process.wait()

    if returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=returncode,
            cmd=f"{uv_executable} sync --frozen",
        )


async def run_python_file(
    project_dir: Path, uv_executable: Path, python_file: Path, args: str = ""
):
    process = await asyncio.create_subprocess_shell(
        f"{uv_executable} run --no-sync {python_file} {args}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={"VIRTUAL_ENV": ".venv", "PYTHONUNBUFFERED": "1"},
        cwd=project_dir,
    )

    # Create tasks for reading both stdout and stderr
    await asyncio.gather(read_stream(process.stdout), read_stream(process.stderr))

    returncode = await process.wait()
    if returncode != 0:
        raise subprocess.CalledProcessError(
            returncode=returncode,
            cmd=f"{uv_executable} run --no-sync {python_file} {args}",
        )
