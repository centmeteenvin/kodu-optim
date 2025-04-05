from shared.models.node import Node

active_nodes: dict[str, Node] = {}


def insert_node(node: Node) -> Node:
    active_nodes[node.id] = node


def update_node(node: Node) -> Node:
    active_nodes[node.id] = node


def delete_node(id: str) -> bool:
    if id in active_nodes:
        active_nodes.pop(id)
        return True
    return False


def find_node_by_id(id: str) -> Node | None:
    return active_nodes.get(id).model_copy()
