import asyncio
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


STATIC_DIR = Path(__file__).with_name("static")

app = FastAPI(title="OT Learning Portal")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

SNAPSHOT_SOURCES = {
    "cargo": "http://cargo-plant:8100/state",
    "pms": "http://pms-plant:8200/state",
    "propulsion": "http://propulsion-plant:8300/state",
    "vessel": "http://vessel-coordinator:8600/state",
    "alarms": "http://alarm-engine:8400/alarms",
    "catalog": "http://alarm-engine:8400/catalog",
    "history": "http://alarm-engine:8400/history?limit=30",
    "alarm_metrics": "http://alarm-engine:8400/metrics",
}

CONTRACT_SOURCES = {
    "cargo": "http://cargo-plant:8100/contract",
    "pms": "http://pms-plant:8200/contract",
    "propulsion": "http://propulsion-plant:8300/contract",
}


@app.get("/")
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, Any]:
    # This proves only that the read-only portal can serve lessons. Upstream
    # model readiness remains visible in /api/snapshot.
    return {
        "ready": True,
        "service": "learning-portal",
        "scope": "portal-content-only",
    }


async def fetch_json(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    try:
        response = await client.get(url)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("upstream response is not an object")
        return payload
    except (httpx.HTTPError, ValueError):
        # Do not expose infrastructure names or exception details to learners.
        return {"ready": False, "error": "upstream unavailable"}


async def fetch_all(
    client: httpx.AsyncClient, sources: dict[str, str]
) -> dict[str, dict[str, Any]]:
    results = await asyncio.gather(
        *(fetch_json(client, url) for url in sources.values())
    )
    return dict(zip(sources, results, strict=True))


@app.get("/api/snapshot")
async def snapshot() -> dict[str, dict[str, Any]]:
    async with httpx.AsyncClient(timeout=1) as client:
        return await fetch_all(client, SNAPSHOT_SOURCES)


@app.get("/api/contracts")
async def contracts() -> dict[str, dict[str, Any]]:
    async with httpx.AsyncClient(timeout=1) as client:
        return await fetch_all(client, CONTRACT_SOURCES)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8500)
