import json
import logging

logging.basicConfig(level=logging.DEBUG)

with open("conf.json") as f:
    proxy_config = json.load(f)

idempotency_cache = {}


async def get_idempotency_cache():
    return idempotency_cache


async def get_proxy_config():
    return proxy_config


async def get_async_client():
    return client
