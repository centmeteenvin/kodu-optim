from __future__ import annotations

import asyncio
import os
import socket
import subprocess
from typing import Literal

import psutil
from pydantic import BaseModel


class NodeCapabilities(BaseModel):
    cpu_count: int
    memory_gb: float
    hostname: str

    @staticmethod
    async def from_system() -> tuple[NodeCapabilities, str | None]:
        async def run_command(command: str) -> str | None:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                return None
            return stdout.decode().strip()

        uv_path = await run_command("where uv" if os.name == "nt" else "which uv")

        return NodeCapabilities(
            cpu_count=os.cpu_count(),
            memory_gb=psutil.virtual_memory().total / (1024**3),
            hostname=socket.gethostname(),
        ), uv_path


class NodeRegistration(BaseModel):
    node_id: str
    capabilities: NodeCapabilities


class NodeRegistrationSuccess(BaseModel):
    # db_url: str
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
