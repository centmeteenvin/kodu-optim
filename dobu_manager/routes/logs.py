import asyncio
import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from dobu_manager.app import app
from dobu_manager.registry import active_nodes
from shared.models.node import LogUpdate, PingResult

@app.post("/node/{node_id}/logs")
async def update_node_log(node_id: str, log_update: LogUpdate) -> PingResult:
    if node_id not in active_nodes:
        raise HTTPException(status_code=404, detail="Node not registered")
    
    node = active_nodes[node_id]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    node.logs.append(f"[{timestamp}] {log_update.content}")
    if len(node.logs) > 1000:
        node.logs = node.logs[-1000:]
        
    return PingResult(status="ok")

@app.get("/node/{node_id}/logs")
async def get_node_logs(node_id: str):
    if node_id not in active_nodes:
        raise HTTPException(status_code=404, detail="Node not registered")
    async def generate():
        node = active_nodes[node_id]
        current_index = 0
        while True:
            if current_index < len(node.logs):
                logs = "\n".join(node.logs)
                current_index = len(node.logs)
                logger.info(logs)
                logger.info(node.logs)
                yield logs + "\n"
            await asyncio.sleep(1)
    return StreamingResponse(generate(), media_type="text/plain")