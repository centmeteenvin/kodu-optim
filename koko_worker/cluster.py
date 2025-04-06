from __future__ import annotations

import asyncio

import aiohttp
import aiohttp.client_exceptions
import aiohttp.http_exceptions
from loguru import logger

from koko_worker.config import WorkerConfig
from koko_worker.download import DownloadService
from koko_worker.environment import run_python_file, sync
from koko_worker.pinger import Pinger
from koko_worker.requests import request
from shared.models.node import (
    NodeCapabilities,
    NodeRegistration,
    NodeRegistrationSuccess,
    PingResult,
)
from shared.models.study import CodeBaseStudy


class ClusterService:
    _instance: ClusterService | None = None

    @staticmethod
    def get() -> ClusterService:
        if ClusterService._instance is None:
            raise Exception("Not yet instantiated")
        return ClusterService._instance

    def __init__(
        self,
        id: str,
        capabilities: NodeCapabilities,
        download_service: DownloadService,
        uv_executable: str,
    ):
        self.id = id
        self.capabilities = capabilities
        self._pinger: Pinger | None = None
        self.current_study: CodeBaseStudy | None = None
        self.download_service = download_service
        self.uv_executable = uv_executable
        ClusterService._instance = self

    async def register(self):
        logger.info("registering with orchestrator")
        try:
            result = await request(
                "register",
                "POST",
                NodeRegistration(node_id=self.id, capabilities=self.capabilities),
                NodeRegistrationSuccess,
            )
        except aiohttp.client_exceptions.ClientConnectionError:
            logger.error("Failed to connect to orchestrator, are the settings correct?")
            exit(-1)
        logger.info(f"registration successful {result}")
        self.db_url = WorkerConfig.get().orchestrator_url
        self.ping_interval = result.ping_interval
        logger.info("Creating pinger")
        self._pinger = Pinger(self.ping_interval, self.id)
        asyncio.create_task(self._pinger.run())

    async def request_study(self) -> CodeBaseStudy | None:
        try:
            return await request("study/request", "GET", None, CodeBaseStudy)
        except aiohttp.client_exceptions.ClientResponseError:
            return None

    async def main(self):
        try:
            while True:
                if self.current_study is None:
                    logger.info("Checking if a study is available")
                    study = await self.request_study()
                    if study is None:
                        logger.info("No study available, checking again in 15 seconds")
                        await asyncio.sleep(15)
                    else:
                        self.current_study = study
                # A study is found
                else:
                    await self.run_study()

        except Exception as e:
            logger.error(f"Error occurred {e}")
            raise e
        except KeyboardInterrupt:
            pass
        except asyncio.exceptions.CancelledError:
            pass
        logger.info("Gracefully shutting down server")
        await self.teardown()

    async def run_study(self) -> None:
        logger.info(f"Starting study: {self.current_study}")
        study = self.current_study
        if not self.download_service.is_study_cached(study.name):
            logger.info("The study was not yet cached, downloading it now")
            await self.download_service.download_study(study.name)
        else:
            logger.info(f"Found the study cached {self.download_service.studies_dir}")
        study_dir = self.download_service.studies_dir.joinpath(study.name).absolute()
        logger.info(f"Synchronizing virtual environment at: {study_dir.as_posix()}")
        await sync(project_dir=study_dir, uv_executable=self.uv_executable)
        await run_python_file(
            project_dir=study_dir,
            uv_executable=self.uv_executable,
            python_file="execute",
            args=f"--objective-file {study.objective_file} --objective-function {study.objective_function} --study-name {study.name} --storage {self.db_url}",
        )
        self.current_study = None

    async def teardown(self):
        try:
            self._pinger.is_running = False
            await request(f"node/{self.id}", "DELETE", None, PingResult)
        except:  # noqa: E722
            pass
