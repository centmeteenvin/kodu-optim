import argparse
import pathlib

import optuna
import optuna_dashboard
import uvicorn
from fastapi.middleware.wsgi import WSGIMiddleware
from loguru import logger

from dobu_manager.app import app
from dobu_manager.config import OrchestratorConfig


class PrefixMiddleware:
    def __init__(self, app, prefix: str):
        self.app = app
        self.prefix = prefix.rstrip("/")

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        if path.startswith(self.prefix):
            # Strip prefix before passing to Bottle app
            environ["SCRIPT_NAME"] = self.prefix
            environ["PATH_INFO"] = path[len(self.prefix) :] or "/"
            return self.app(environ, start_response)
        else:
            # 404 for non-prefixed paths
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"This route does not exist in the dashboard."]


def main(config_path: str | None):
    print("[DOBU] Lets get to work")
    config = OrchestratorConfig(
        pathlib.Path(config_path) if config_path is not None else None
    )
    logger.info(f"Starting server with the following settings: {config}")
    storage = optuna.storages.RDBStorage(config.db_url)
    dashboard = optuna_dashboard.wsgi(storage=storage)
    # app.mount(
    #     "/dashboard/", (WSGIMiddleware(PrefixMiddleware(dashboard, "/dashboard")))
    # )
    app.mount("/", (WSGIMiddleware(dashboard)))
    uvicorn.run(app, host=config.host, port=config.port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", default=None, help="The path to the configuration file"
    )
    args = parser.parse_args()
    main(config_path=args.config)
