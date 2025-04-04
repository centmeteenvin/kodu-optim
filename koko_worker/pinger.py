from threading import Thread
import time
from typing import override

from loguru import logger

from koko_worker.requests import request
from shared.models.node import NodePing, NodeStatus, PingResult

class Pinger(Thread):
    def __init__(self, ping_interval: int, node_id: str):
        super().__init__(name="pinger", daemon=False)
        self.ping_interval = ping_interval
        self.node_id = node_id
        self.status : NodeStatus = "idle"
        self.current_trial_id = None
        self.is_running = False
        
    @override
    def run(self):
        self.is_running = True
        self.time = 0
        while self.is_running:
            time.sleep(2.5)
            self.time += 2.5
            if self.time > self.ping_interval:
                self.time = 0
                try:
                    logger.info("Pinging")
                    request("/ping", "POST", data=NodePing(
                        node_id=self.node_id,
                        status=self.status,
                        current_trial_id=self.current_trial_id,
                    ), result_type=PingResult)
                except Exception as e:
                    logger.warning(f"An error occurred when pinging {e}")
        logger.info("Stopping pinger")
