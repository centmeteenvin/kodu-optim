import argparse
import atexit
from pathlib import Path
from uuid import uuid4
from loguru import logger
from koko_worker.cluster import ClusterService
from koko_worker.config import WorkerConfig
from koko_worker.download import DownloadService
from shared.models.node import NodeCapabilities


def main(config_path=str | None): 
    config = WorkerConfig.from_file(None if config_path is None else Path(config_path))
    logger.info(f"Loaded config: {config}")
    capabilities = NodeCapabilities.from_system()
    logger.info(f"Analyzed system: {capabilities}")
    
    download_service = DownloadService(config.data_dir)
    
    cluster_service = ClusterService(f"{capabilities.hostname}-{uuid4().hex[:4]}", capabilities, download_service)
    cluster_service.register()
    atexit.register(cluster_service.teardown)
    cluster_service.main()
    
if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default=None, help="The path to the configuration file")
    args = parser.parse_args()
    main(config_path=args.config)