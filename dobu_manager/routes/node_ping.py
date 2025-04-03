import time
from fastapi import HTTPException
from dobu_manager.app import app
from shared.models.node import NodePing, PingResult
from dobu_manager.registry import active_nodes

@app.post("/ping")
async def node_ping(ping: NodePing) -> PingResult:
    node_id = ping.node_id
    if node_id not in active_nodes:
        raise HTTPException(status_code=404, detail="Node not registered")
    node = active_nodes[node_id]
    node.last_ping=time.time()
    node.status = ping.status
    node.current_trial = ping.current_trial_id
    return PingResult(status="ok")