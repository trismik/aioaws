from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from httpx import AsyncClient

from .core import AWSV4AuthFlow, RequestError

__all__ = ('BedrockClient', 'BedrockConfig')


@dataclass
class BedrockConfig:
    aws_access_key: str
    aws_secret_key: str
    aws_region: str
    aws_session_token: str | None = None


class BedrockClient:
    def __init__(self, http_client: AsyncClient, config: BedrockConfig) -> None:
        self._client = http_client
        self._base_url = f'https://bedrock-runtime.{config.aws_region}.amazonaws.com'
        self._auth = AWSV4AuthFlow(
            aws_access_key=config.aws_access_key,
            aws_secret_key=config.aws_secret_key,
            region=config.aws_region,
            service='bedrock',
            session_token=config.aws_session_token,
        )

    async def invoke(self, model: str, body: dict[str, Any]) -> dict[str, Any]:
        return await self._request(model, 'invoke', body)

    async def converse(self, model: str, body: dict[str, Any]) -> dict[str, Any]:
        return await self._request(model, 'converse', body)

    async def _request(self, model: str, action: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f'{self._base_url}/model/{quote(model, safe=":")}/{action}'
        r = await self._client.post(url, json=body, auth=self._auth)
        if r.status_code != 200:
            raise RequestError(r)
        return r.json()
