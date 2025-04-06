from typing import Literal, Type, TypeVar

import aiohttp
from pydantic import BaseModel

type HTTPMethod = Literal["GET"] | Literal["PUT"] | Literal["POST"] | Literal["DELETE"]

T = TypeVar("T", bound=BaseModel)


async def request(
    url: str, method: HTTPMethod, data: BaseModel | None, result_type: Type[T]
) -> T:
    raw = data.model_dump(mode="json") if data is not None else {}
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            result = await session.get(url)
        elif method == "PUT":
            result = await session.put(
                url,
                json=raw,
                headers={"content-type": "application/json"},
            )

        elif method == "POST":
            result = await session.post(
                url,
                json=raw,
                headers={"content-type": "application/json"},
            )
        elif method == "DELETE":
            result = await session.get(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        result.raise_for_status()
        if result_type is None:
            return None
    return result_type.model_validate(await result.json())
