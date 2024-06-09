import os
from .weaviate_interface import WeaviateInterface
from dotenv import load_dotenv

load_dotenv()


async def setup_weaviate_interface_async() -> WeaviateInterface:
    openai_key = os.getenv("OPENAI_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL")
    schema_file = "./weaviate/schema.json"

    if not openai_key or not weaviate_url:
        raise Exception("Missing OPENAI_API_KEY or WEAVIATE_URL")

    weaviate_interface = WeaviateInterface(
        weaviate_url, openai_key, schema_file
    )
    return weaviate_interface


async def setup_weaviate_interface():
    return await setup_weaviate_interface_async()
