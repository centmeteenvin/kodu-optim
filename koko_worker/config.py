from __future__ import annotations

import json
from pathlib import Path
from venv import logger

from pydantic import BaseModel, field_validator

_config_instance: WorkerConfig | None = None


class WorkerConfig(BaseModel):
    orchestrator_url: str = "http://localhost:8080"
    data_dir: Path = Path("./data_worker")

    @field_validator("data_dir", mode="before")
    @classmethod
    def ensure_data_dir_exists(cls, v: str | Path) -> Path:
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        elif not path.is_dir():
            raise ValueError(f"{v} exists but is not a directory.")
        return path

    @staticmethod
    def from_file(config_path: Path | None) -> WorkerConfig:
        if config_path is None:
            return WorkerConfig()
        if not config_path.exists():
            raise Exception(f"Config file does not exists: {config_path}")

        with open(config_path, "r") as f:
            return WorkerConfig.model_validate(json.loads(f.read()))

    def model_post_init(self, __context):
        global _config_instance
        logger.info(_config_instance)
        _config_instance = self

    @staticmethod
    def get() -> WorkerConfig:
        global _config_instance
        if _config_instance is None:
            raise Exception("Configuration is not yet initialized")
        return _config_instance
