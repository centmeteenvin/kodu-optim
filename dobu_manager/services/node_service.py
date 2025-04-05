import time

from dobu_manager.repositories.node_repository import (
    delete_node,
    find_node_by_id,
    insert_node,
    update_node,
)
from shared.models.node import Node, NodePing, NodeRegistration


def register_node(registration: NodeRegistration) -> Node:
    node = Node(
        id=registration.node_id,
        capabilities=registration.capabilities,
        last_ping=time.time(),
    )
    return insert_node(node)


def update_node_ping(ping: NodePing) -> Node:
    node = find_node_by_id(ping.node_id)
    node.last_ping = time.time()
    node.current_trial = ping.current_trial_id
    node.status = ping.status
    return update_node(node)


def remove_node(id: str) -> None:
    delete_node(id)


def node_exists(id: str) -> bool:
    return find_node_by_id(id) is not None
