import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    await init_db()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_reports_empty(client: AsyncClient):
    resp = await client.get("/api/v1/daily-reports")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_today_report_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/daily-reports/today")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_report_by_date_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/daily-reports/2099-01-01")
    assert resp.status_code == 404
