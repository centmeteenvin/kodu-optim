import asyncio

from loguru import logger

from koko_worker.requests import request
from shared.models.node import NodePing, NodeStatus, PingResult


class Pinger:
    def __init__(self, ping_interval: int, node_id: str):
        self.ping_interval = ping_interval
        self.node_id = node_id
        self.status: NodeStatus = "idle"
        self.current_trial_id = None
        self.is_running = False

    async def run(self):
        self.is_running = True
        self.time = 0
        while self.is_running:
            try:
                logger.info("Pinging")
                await request(
                    "ping",
                    "POST",
                    data=NodePing(
                        node_id=self.node_id,
                        status=self.status,
                        current_trial_id=self.current_trial_id,
                    ),
                    result_type=PingResult,
                )
            except Exception as e:
                logger.warning(f"An error occurred when pinging {e}")
            await asyncio.sleep(self.ping_interval)
        logger.info("Stopping pinger")
