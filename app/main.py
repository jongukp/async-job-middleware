import asyncio
import logging
from typing import Dict
from uuid import uuid4

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

logging.basicConfig(level=logging.INFO)

CALLBACK_URL_DEFAULT = "http://localhost:8000/callback/{job_id}"
job_results: Dict[str, dict] = {}


async def proxy(request: Request) -> JSONResponse:
    data = await request.json()
    account = data.get("account")
    callback_url_template = data.get("callback_url", CALLBACK_URL_DEFAULT)
    if not account:
        return JSONResponse({"error": "Account is required"}, status_code=400)

    job_id = str(uuid4())

    if "callback_url" not in data:
        logging.info("No callback_url provided, using default: %s",
                     CALLBACK_URL_DEFAULT)

    callback_url = callback_url_template.format(job_id=job_id)
    asyncio.create_task(start_async_job(account, callback_url))
    return JSONResponse({"state": "running", "id": job_id})


async def callback(request: Request) -> JSONResponse:
    job_id = request.path_params["job_id"]
    result = await request.json()
    job_results[job_id] = result
    return JSONResponse({"status": "success"})


async def status(request: Request) -> JSONResponse:
    job_id = request.path_params["job_id"]
    result = job_results.get(job_id)
    if not result:
        return JSONResponse({"state": "pending"})
    return JSONResponse(result)


async def start_async_job(account: str, callback_url: str) -> None:
    process = await asyncio.create_subprocess_exec(
        "./jobclient",
        "--account",
        account,
        "--wait",
        "false",
        "--callback",
        callback_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if stdout:
        print(stdout.decode())
    if stderr:
        print(stderr.decode())


routes = [
    Route("/proxy", endpoint=proxy, methods=["POST"]),
    Route("/callback/{job_id}", endpoint=callback, methods=["POST"]),
    Route("/status/{job_id}", endpoint=status, methods=["GET"]),
]

app = Starlette(routes=routes)
