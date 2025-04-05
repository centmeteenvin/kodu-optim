import argparse
import pathlib

import uvicorn
from loguru import logger

from dobu_manager.app import app
from dobu_manager.config import OrchestratorConfig


def main(config_path: str | None):
    print("[DOBU] Lets get to work")
    config = OrchestratorConfig(
        pathlib.Path(config_path) if config_path is not None else None
    )
    logger.info(f"Starting server with the following settings: {config}")
    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default=None, help="The path to the configuration file"
    )
    args = parser.parse_args()
    main(config_path=args.config)
