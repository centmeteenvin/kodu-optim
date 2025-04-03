import time

from loguru import logger
from dobu_manager.app import app

from dobu_manager.config import OrchestratorConfig
from shared.models.node import Node, NodeRegistration, NodeRegistrationSuccess
from dobu_manager.registry import active_nodes


@app.post("/register")
async def register_node(node: NodeRegistration) -> NodeRegistrationSuccess:
    """Register a new worker node"""
    active_nodes[node.node_id] = Node(
        id=node.node_id,
        last_ping=time.time(),
        capabilities=node.capabilities,
    )
    
    logger.info(f"Noe {node.node_id} registered:\n{node.capabilities}")
    
    return NodeRegistrationSuccess(
        db_url=OrchestratorConfig.get().db_url,
        ping_interval=OrchestratorConfig.get().ping_interval_seconds
    )