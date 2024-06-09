from .http_client import HttpHandler
from typing import Any, Dict, List
import os
import weaviate
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SCHEMA_ENDPOINT = "/v1/schema"
GRAPHQL_ENDPOINT = "/v1/graphql"
OBJECTS_ENDPOINT = "/v1/objects"
BATCH_OBJECTS_ENDPOINT = "/v1/batch/objects"
load_dotenv()


client = weaviate.Client(
    url=os.getenv("WEAVIATE_URL"),
    additional_headers={
        "X-OpenAI-Api-Key": os.environ[
            "OPENAI_API_KEY"
        ]
    },
)


class WeaviateClient:
    def __init__(self, http_handler: HttpHandler) -> None:
        self.http_handler = http_handler

    async def get_schema(self) -> Dict[str, Any]:
        return await self.http_handler.get_json_response(
            "GET",
            SCHEMA_ENDPOINT
        )

    async def create_class(self, class_info: Dict[str, Any]) -> None:
        await self.http_handler.get_json_response("POST", SCHEMA_ENDPOINT, class_info)

    async def delete_class(self, class_name: str) -> None:
        endpoint = f"{SCHEMA_ENDPOINT}/{class_name}"
        await self.http_handler.get_json_response("DELETE", endpoint)

    async def create_object(self, data: Dict[str, Any], class_name: str) -> str:
        payload = {"class": class_name, "properties": data}
        response = await self.http_handler.get_json_response(
            "POST", OBJECTS_ENDPOINT, payload
        )
        return response.get("id")

    async def batch_create_objects(
        self, objects: List[Dict[str, Any]], class_name: str
    ) -> bool:
        transformed_objects = [
            {"class": class_name, "properties": obj} for obj in objects
        ]
        batch_data = {"objects": transformed_objects}
        response = await self.http_handler.get_json_response(
            "POST", BATCH_OBJECTS_ENDPOINT, batch_data
        )
        return response[0].get("result", {}).get("status") == "SUCCESS"

    async def get_object(self, uuid: str, class_name: str) -> Dict[str, Any]:
        endpoint = f"{OBJECTS_ENDPOINT}/{class_name}/{uuid}"
        return await self.http_handler.get_json_response("GET", endpoint)

    async def update_object(
        self, uuid: str, data: Dict[str, Any], class_name: str
    ) -> bool:
        endpoint = f"{OBJECTS_ENDPOINT}/{class_name}/{uuid}"
        await self.http_handler.get_json_response("PATCH", endpoint, data)
        return True

    async def delete_object(self, uuid: str, class_name: str) -> bool:
        endpoint = f"{OBJECTS_ENDPOINT}/{class_name}/{uuid}"
        await self.http_handler.get_json_response("DELETE", endpoint)
        return True

    async def run_query(self, graphql_query: str) -> Dict[str, Any]:
        return await self.http_handler.get_json_response(
            "POST", GRAPHQL_ENDPOINT, {"query": graphql_query}
        )

    async def run_query_schema(self, graphql_query: str) -> Dict[str, Any]:
        return await self.http_handler.get_json_response(
            "POST", SCHEMA_ENDPOINT, {"query": graphql_query}
        )


    async def semantic_search(
            self,
            class_name: str,
            query: str,
            fields: List[str],
            limit: int = 10,
            offset: int = 0
        ) -> List[Dict[str, Any]]:

        res = client.query.get(class_name, fields)
        print(dir(res))
        res = res.near_text(
            query = query
        ).with_limit(limit).with_offset(offset).do()

        return res
    
    async def semantic_search(
        self, class_name: str, query: str, fields: List[str], limit: int = 5
    ) -> List[Dict[str, Any]]:
        res = client.query.get(class_name, fields).with_limit(limit).do()

        return res["data"]["Get"][class_name]

    




