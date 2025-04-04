from __future__ import annotations
import time

from loguru import logger
import requests

from koko_worker.download import DownloadService
from koko_worker.pinger import Pinger
from koko_worker.requests import request
from shared.models.node import NodeCapabilities, NodeRegistration, NodeRegistrationSuccess, PingResult
from shared.models.study import Study


class ClusterService:
    _instance : ClusterService | None = None
    
    @staticmethod
    def get() -> ClusterService:
        if ClusterService._instance is None:
            raise Exception("Not yet instantiated")
        return ClusterService._instance
        
    def __init__(self, id: str, capabilities: NodeCapabilities, download_service = DownloadService):
        self.id = id
        self.capabilities = capabilities
        self._pinger : Pinger | None = None
        self.current_study: Study | None = None
        self.download_service = download_service
        ClusterService._instance = self
        
        
    def register(self):
        logger.info("registering with orchestrator")
        try:
            result = request("register", "POST", NodeRegistration(node_id=self.id, capabilities=self.capabilities), NodeRegistrationSuccess,)
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to orchestrator, are the settings correct?")
            exit(-1)
        logger.info(f"registration successful {result}")
        self.db_url = result.db_url
        self.ping_interval = result.ping_interval
        logger.info("Creating pinger")
        self._pinger = Pinger(self.ping_interval, self.id)
        self._pinger.start()
        
    def request_study(self) -> Study | None:
        try:
            return request("study/request", "GET", None, Study)
        except requests.exceptions.HTTPError:
            return None
        
    def main(self):
        try:
            while True:
                if self.current_study is None:
                    logger.info("Checking if a study is available")
                    study = self.request_study()
                    if study is None:
                        logger.info("No study available, checking again in 15 seconds")
                        time.sleep(15)
                    else:
                        self.current_study = study
                # A study is found
                else:
                    self.run_study()

        except KeyboardInterrupt:
            pass
        logger.info("Gracefully shutting down server")
        self.teardown()
        
    def run_study(self) -> None:
        logger.info(f"Starting study: {self.current_study}")
        study = self.current_study
        if not self.download_service.is_study_cached(study.name):
            logger.info("The study was not yet cached, downloading it now")
            self.download_service.download_study(study.name)
        else:
            logger.info(f"Found the study cached {self.download_service.studies_dir}")    
        time.sleep(10)
        self.current_study = None
        

    def teardown(self):
        try: 
            self._pinger.is_running = False
            request(f"node/{self.id}", "DELETE", None, PingResult)
            self._pinger.join()
        except:
            pass
    
