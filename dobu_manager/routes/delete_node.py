from fastapi import HTTPException
from dobu_manager.app import app
from shared.models.node import PingResult
from dobu_manager.registry import active_nodes

@app.delete("/node/{node_id}")
async def delete_node(node_id: str) -> PingResult:
    if node_id not in active_nodes:
        raise HTTPException(status_code=404, detail="Node not registered")
    
    del active_nodes[node_id]
    return PingResult(status="ok")