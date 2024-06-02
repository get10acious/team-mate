import os
import asyncio
from .weaviate_interface import WeaviateInterface
from dotenv import load_dotenv

load_dotenv()


async def setup_weaviate_interface_async() -> WeaviateInterface:
    openai_key = os.getenv("OPENAI_API_KEY")
    weaviate_url = os.getenv("WEAVIATE_URL", "http://0.0.0.0:8080")
    schema_file = "./weaviate/schema.json"

    if not openai_key or not weaviate_url:
        raise Exception("Missing OPENAI_API_KEY or WEAVIATE_URL")

    weaviate_interface = WeaviateInterface(weaviate_url, openai_key, schema_file)
    await weaviate_interface.async_init()
    return weaviate_interface


def setup_weaviate_interface():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        task = asyncio.create_task(setup_weaviate_interface_async())
        return task
    else:
        return loop.run_until_complete(setup_weaviate_interface_async())
