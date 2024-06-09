import httpx
from typing import Any, Dict, Optional


class HttpClient:
    def __init__(self, base_url: str, headers: Dict[str, str]) -> None:
        self.base_url = base_url
        self.headers = headers
        self.client = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        response = await self.client.request(
            method, url, headers=self.headers, json=data
        )
        response.raise_for_status()
        return response


class HttpHandler:
    def __init__(self, http_client: HttpClient) -> None:
        self.http_client = http_client

    async def get_json_response(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Any:
        try:
            response = await self.http_client.make_request(
                method, endpoint, data
            )
            if response.text:
                json_response = response.json()
            else:
                json_response = {}
            return json_response
        except httpx.HTTPError as e:
            raise e
        except ValueError as e:
            raise e
