from __future__ import annotations

import pathlib
from pathlib import Path

import yaml


class OrchestratorConfig:
    _active: OrchestratorConfig | None = None

    def __init__(self, path: Path | None = None):
        if path is None:
            self.host = "localhost"
            self.port = 8080
            self.ping_interval_seconds = 30
            self.data_dir = pathlib.Path("./data").absolute()
            self.db_url = "sqlite:///data/optuna.db"
        else:
            with path.open("r") as file:
                config = yaml.safe_load(file)
                self.host = config["host"]
                self.port = config["port"]
                self.ping_interval_seconds = config["ping_interval_seconds"]
                self.data_dir = pathlib.Path(
                    config.get("data_dir", "./data")
                ).absolute()

                self.db_url = config["db_url"]

        self.data_dir.mkdir(parents=True, exist_ok=True)
        OrchestratorConfig._active = self

    def __str__(self):
        return (
            f"OrchestratorConfig(host={self.host}, port={self.port}, "
            f"ping_interval_seconds={self.ping_interval_seconds}, "
            f"db_url={self.db_url})"
        )

    def __repr__(self):
        return (
            f"OrchestratorConfig(host={self.host!r}, port={self.port!r}, "
            f"db_host={self.db_host!r}, db_port={self.db_port!r}, "
            f"db_user={self.db_user!r}, db_password=****, "
            f"ping_interval_seconds={self.ping_interval_seconds!r}, "
            f"db_url={self.db_url!r})"
        )

    @staticmethod
    def get() -> OrchestratorConfig:
        if OrchestratorConfig._active is None:
            raise Exception("Tried to access the config while it was not set")
        return OrchestratorConfig._active
