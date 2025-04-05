import argparse
import asyncio
import atexit
from pathlib import Path
from uuid import uuid4

from loguru import logger

from koko_worker.cluster import ClusterService
from koko_worker.config import WorkerConfig
from koko_worker.download import DownloadService
from shared.models.node import NodeCapabilities


async def main(config_path=str | None):
    config = WorkerConfig.from_file(None if config_path is None else Path(config_path))
    logger.info(f"Loaded config: {config}")
    capabilities, uv_path = await NodeCapabilities.from_system()
    if uv_path is None:
        logger.error("uv executable could not be found")
    logger.info(f"Analyzed system: {capabilities}\nuv path: {uv_path}")

    download_service = DownloadService(config.data_dir)

    cluster_service = ClusterService(
        f"{capabilities.hostname}-{uuid4().hex[:4]}",
        capabilities,
        download_service,
        uv_executable=uv_path,
    )
    await cluster_service.register()

    def sync_teardown():
        asyncio.run(cluster_service.teardown())

    atexit.register(sync_teardown)
    await cluster_service.main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default=None, help="The path to the configuration file"
    )
    args = parser.parse_args()
    asyncio.run(main(config_path=args.config))
