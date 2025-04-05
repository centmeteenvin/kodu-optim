from fastapi import Depends, HTTPException
from loguru import logger

from dobu_manager.app import app
from dobu_manager.config import OrchestratorConfig
from dobu_manager.services.node_service import (
    node_exists,
    register_node,
    remove_node,
    update_node_ping,
)
from shared.models.node import (
    NodePing,
    NodeRegistration,
    NodeRegistrationSuccess,
    PingResult,
)


@app.post("/register")
async def handle_register_node(
    node: NodeRegistration, config: OrchestratorConfig = Depends(OrchestratorConfig.get)
) -> NodeRegistrationSuccess:
    """Register a new worker node"""
    if node_exists(node.node_id):
        raise HTTPException(400, detail=f"Node with id {node.node_id} already exists")

    logger.info(f"Node {node.node_id} registered:\n{node.capabilities}")
    register_node(node)

    return NodeRegistrationSuccess(
        ping_interval=config.ping_interval_seconds,
    )


@app.post("/ping")
async def handle_node_ping(ping: NodePing) -> PingResult:
    node_id = ping.node_id
    if not node_exists(node_id):
        raise HTTPException(status_code=404, detail="Node not registered")
    update_node_ping(ping)
    return PingResult(status="ok")


@app.delete("/node/{node_id}")
async def handle_delete_node(node_id: str) -> PingResult:
    if not node_exists(node_id):
        raise HTTPException(status_code=404, detail="Node not registered")
    remove_node(node_id)
    return PingResult(status="ok")
