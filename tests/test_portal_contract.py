"""HTTP fixtures exercise the real portal adapter; they are not target evidence."""
import asyncio
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from portal import app as portal


def run(payload, *, expect_list=False, status=200):
    async def request():
        transport = httpx.MockTransport(lambda req: httpx.Response(status, json=payload))
        async with httpx.AsyncClient(transport=transport) as client:
            return await portal.fetch_json(client, "http://fixture/state", expect_list=expect_list)
    return asyncio.run(request())


def test_alarm_records_and_empty_lists_are_valid():
    for name in portal.LIST_SOURCES:
        rows = [{"id": "PMS_BLACKOUT", "active": 1, "source": name}]
        assert run(rows, expect_list=True) == rows
    assert run([], expect_list=True) == []


def test_wrong_shape_and_http_error_do_not_become_empty_lists():
    for payload, is_list, status in [
        ({}, True, 200), ([None], True, 200), ([[]], True, 200),
        ([], False, 200), (None, False, 200), ({}, False, 503),
    ]:
        assert run(payload, expect_list=is_list, status=status) == {
            "ready": False, "error": "upstream unavailable"
        }


def test_snapshot_response_keeps_real_endpoint_shapes():
    payloads = {
        name: [{"id": name, "active": 1}] if name in portal.LIST_SOURCES else {"ready": True}
        for name in portal.SNAPSHOT_SOURCES
    }
    by_url = {url: payloads[name] for name, url in portal.SNAPSHOT_SOURCES.items()}
    client_type = httpx.AsyncClient
    def upstream(request):
        return httpx.Response(200, json=by_url[str(request.url)])
    def fixture_client(**kwargs):
        return client_type(transport=httpx.MockTransport(upstream), **kwargs)
    with patch.object(httpx, "AsyncClient", fixture_client), TestClient(portal.app) as client:
        response = client.get("/api/snapshot")
    assert response.status_code == 200
    assert response.json() == payloads


def test_snapshot_partial_failure_preserves_other_sources():
    client_type = httpx.AsyncClient
    def upstream(request):
        url = str(request.url)
        if url.endswith("/alarms"):
            raise httpx.ConnectError("private-token-do-not-expose")
        body = [] if "/history" in url or url.endswith("/catalog") else {"ready": True}
        return httpx.Response(200, json=body)
    def fixture_client(**kwargs):
        return client_type(transport=httpx.MockTransport(upstream), **kwargs)
    with patch.object(httpx, "AsyncClient", fixture_client), TestClient(portal.app) as client:
        response = client.get("/api/snapshot")
    data = response.json()
    assert data["cargo"] == {"ready": True}
    assert data["history"] == []
    assert data["alarms"] == {"ready": False, "error": "upstream unavailable"}
    assert "private-token" not in response.text


def test_portal_serves_guide_dashboard_and_scoped_health():
    with TestClient(portal.app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/static/dashboard.js").status_code == 200
        assert len(client.get("/static/first-session.json").json()["steps"]) == 7
        assert client.get("/health").json()["scope"] == "portal-content-only"
