from typing import Literal
from pydantic import BaseModel
import os
import psutil
import socket


class NodeCapabilities(BaseModel):
    cpu_count: int
    memory_gb: float
    hostname: str

    @staticmethod
    def from_system() -> "NodeCapabilities":
        return NodeCapabilities(
            cpu_count=os.cpu_count(),
            memory_gb=psutil.virtual_memory().total / (1024 ** 3),
            hostname=socket.gethostname()
        )

class NodeRegistration(BaseModel):
    node_id:str
    capabilities: NodeCapabilities

class NodeRegistrationSuccess(BaseModel):
    db_url: str
    ping_interval: int
    
type NodeStatus = Literal["idle"]
    
class Node(BaseModel):
    id: str
    last_ping: float
    capabilities: NodeCapabilities
    status: NodeStatus = "idle"
    current_study: None = None
    current_trial: None = None
    logs: list[str] = []
    
class NodePing(BaseModel):
    node_id: str
    current_trial_id: int | None 
    status: NodeStatus
    
type PingResultStatus = Literal["ok"] | Literal["invalid"]
class PingResult(BaseModel):
    status: PingResultStatus
    
class LogUpdate(BaseModel):
    content: str
    