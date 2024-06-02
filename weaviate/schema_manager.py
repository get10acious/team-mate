import json
from typing import Any, Dict
from .weaviate_client import WeaviateClient


class SchemaManager:
    def __init__(self, client: WeaviateClient, schema_file: str):
        self.client = client
        self.schema_file = schema_file

    def read(self, schema_file: str) -> Dict[str, Any]:
        with open(schema_file, "r") as file:
            return json.load(file)

    async def initialize(self, schema: Dict[str, Any]) -> None:
        try:
            for class_info in schema["classes"]:
                await self.client.create_class(class_info)
        except Exception as e:
            raise e

    async def is_valid(self) -> bool:
        try:
            existing_schema = await self.client.get_schema()
            expected_schema = self.read(self.schema_file)

            existing_classes = {cls["class"]: cls for cls in existing_schema.get("classes", [])}
            for class_info in expected_schema.get("classes", []):
                class_name = class_info["class"]
                if class_name not in existing_classes:
                    return False

                existing_class = existing_classes[class_name]
                expected_properties = {prop["name"]: prop for prop in class_info.get("properties", [])}
                existing_properties = {prop["name"]: prop for prop in existing_class.get("properties", [])}

                for prop_name, expected_prop in expected_properties.items():
                    if prop_name not in existing_properties:
                        return False

                    existing_prop = existing_properties[prop_name]
                    for key, expected_value in expected_prop.items():
                        if existing_prop.get(key) != expected_value:
                            return False

            return True
        except Exception as e:
            return False

    async def reset(self) -> None:
        try:
            existing_schema = await self.client.get_schema()
            if "classes" in existing_schema and isinstance(existing_schema["classes"], list):
                for class_info in existing_schema["classes"]:
                    class_name = class_info.get("class", "")
                    if class_name:
                        await self.client.delete_class(class_name)

            await self.initialize(self.read(self.schema_file))
        except Exception as e:
            raise e
