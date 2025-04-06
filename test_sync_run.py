import asyncio
from pathlib import Path

from koko_worker.environment import run_python_file, sync
from shared.models.node import NodeCapabilities


async def main():
    project_dir = Path(".").joinpath("data_worker", "studies", "test-study")
    _, uv_executable = await NodeCapabilities.from_system()
    print(project_dir, uv_executable)
    await sync(project_dir.as_posix(), uv_executable)
    await run_python_file(
        project_dir,
        uv_executable,
        "execute",
        "--objective-file hello.py --objective-function object_function_1 --storage http://localhost:8080 --study-name test-study",
    )


if __name__ == "__main__":
    asyncio.run(main())
