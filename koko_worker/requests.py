from typing import IO, Literal, Type, TypeVar

from pydantic import BaseModel
import requests
from koko_worker.config import WorkerConfig

type HTTPMethod = Literal["GET"] | Literal["PUT"] | Literal["POST"] | Literal["DELETE"]

T = TypeVar("T", bound=BaseModel)

def request(uri: str, method: HTTPMethod, data: BaseModel | None, result_type: Type[T]) -> T:
    config = WorkerConfig.get()
    url = f"{config.orchestrator_host}:{config.orchestrator_port}/{uri}"
    
    if method == "GET":
        response = requests.get(url, headers={'content-type': 'application/json'})
    elif method == "PUT":
        response = requests.put(url, json=data.model_dump(mode="json"), headers={'content-type': 'application/json'})
    elif method == "POST":
        response = requests.post(url, json=data.model_dump(mode="json"), headers={'content-type': 'application/json'})
    elif method == "DELETE":
        response = requests.delete(url, headers={'content-type': 'application/json'})
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response.raise_for_status()
    return result_type.model_validate(response.json())

def request_file(uri: str, method: HTTPMethod, data: BaseModel | None, output_file: IO) -> None:
    config = WorkerConfig.get()
    url = f"{config.orchestrator_host}:{config.orchestrator_port}/{uri}"
    
    if method == "GET":
        response = requests.get(url, headers={'content-type': 'application/json'}, stream=True)
    elif method == "PUT":
        response = requests.put(url, json=data.model_dump(mode="json"), headers={'content-type': 'application/json'}, stream=True)
    elif method == "POST":
        response = requests.post(url, json=data.model_dump(mode="json"), headers={'content-type': 'application/json'}, stream=True)
    elif method == "DELETE":
        response = requests.delete(url, headers={'content-type': 'application/json'}, stream=True)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response.raise_for_status()
    
    # Write the response content to the output file
    for chunk in response.iter_content(chunk_size=8192):
        output_file.write(chunk)


