"""Hook API main entrypoint."""

import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Add moodle client to the FastAPI app at startup."""
    fastapi_app.moodle = httpx.AsyncClient(
        base_url=os.environ.get("HOOK_MOODLE_URL") + "/webservice/rest/server.php",
        params={
            "wstoken": os.environ.get("HOOK_MOODLE_WEBSERVICE_TOKEN"),
            "moodlewsrestformat": "json",
        },
    )
    yield
    await fastapi_app.moodle.aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root(request: Request):
    """Query a Moodle webservice and return it's response."""
    params = {"wsfunction": "core_webservice_get_site_info"}
    response = await request.app.moodle.get("/", params=params)
    return response.json()
