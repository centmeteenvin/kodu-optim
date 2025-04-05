import asyncio
from pathlib import Path

from koko_worker.environment import run_python_file, sync
from shared.models.node import NodeCapabilities


async def main():
    project_dir = Path(".").joinpath("data_worker", "studies", "test-study")
    _, uv_executable = await NodeCapabilities.from_system()
    print(project_dir, uv_executable)
    await sync(project_dir, uv_executable)
    await run_python_file(
        project_dir,
        uv_executable,
        Path("koko_worker").absolute().joinpath("executor.py"),
        "--objective-file hello.py --objective-function object_function_1",
    )


if __name__ == "__main__":
    asyncio.run(main())
