from typing import IO, Literal, Type, TypeVar

import aiohttp
from pydantic import BaseModel

from koko_worker.config import WorkerConfig

type HTTPMethod = Literal["GET"] | Literal["PUT"] | Literal["POST"] | Literal["DELETE"]

T = TypeVar("T", bound=BaseModel)


async def request(
    uri: str, method: HTTPMethod, data: BaseModel | None, result_type: Type[T]
) -> T:
    config = WorkerConfig.get()
    url = f"{config.orchestrator_url}/{uri}"
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            result = await session.get(url)
        elif method == "PUT":
            result = await session.put(
                url,
                json=data.model_dump(),
                headers={"content-type": "application/json"},
            )

        elif method == "POST":
            result = await session.post(
                url,
                json=data.model_dump(),
                headers={"content-type": "application/json"},
            )
        elif method == "DELETE":
            result = await session.get(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        result.raise_for_status()
    return result_type.model_validate(await result.json())


async def request_file(
    uri: str, method: HTTPMethod, data: BaseModel | None, output_file: IO
) -> None:
    config = WorkerConfig.get()
    url = f"{config.orchestrator_url}/{uri}"

    async with aiohttp.ClientSession() as session:
        if method == "GET":
            result = await session.get(url)
        elif method == "PUT":
            result = await session.put(
                url,
                json=data.model_dump(),
                headers={"content-type": "application/json"},
            )

        elif method == "POST":
            result = await session.post(
                url,
                json=data.model_dump(),
                headers={"content-type": "application/json"},
            )
        elif method == "DELETE":
            result = await session.get(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        result.raise_for_status()

        # Write the response content to the output file
        async for chunk in result.content.iter_chunked(8192):
            output_file.write(chunk)
