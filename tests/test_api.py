"""API 集成测试 — 使用独立的测试数据库"""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import get_session, init_db
from app.models.daily_report import Base

# 用 SQLite 做测试（避免 asyncpg loop 问题）
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_db():
    """每个测试模块重建表"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "database" in data
    assert "sources" in data


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


@pytest.mark.asyncio
async def test_trends_endpoint(client: AsyncClient):
    resp = await client.get("/api/v1/daily-reports/trends?days=7")
    assert resp.status_code == 200
    data = resp.json()
    # 空数据返回格式
    assert isinstance(data, dict)
    assert "dates" in data


@pytest.mark.asyncio
async def test_list_with_pagination(client: AsyncClient):
    resp = await client.get("/api/v1/daily-reports?skip=0&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 5


@pytest.mark.asyncio
async def test_list_with_search(client: AsyncClient):
    resp = await client.get("/api/v1/daily-reports?q=AI")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_spa_fallback(client: AsyncClient):
    """SPA 路由应该返回 index.html"""
    # SPA fallback 只在前端 dist 存在时生效
    from pathlib import Path
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if not frontend_dist.exists():
        pytest.skip("前端 dist 目录不存在，跳过 SPA 测试")
    resp = await client.get("/trends")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_api_404(client: AsyncClient):
    """API 未找到路由应返回 JSON 404"""
    resp = await client.get("/api/v1/nonexistent")
    assert resp.status_code == 404
    assert resp.headers.get("content-type", "").startswith("application/json")


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """API 响应应包含 CORS 头"""
    resp = await client.options(
        "/api/v1/daily-reports",
        headers={"Origin": "http://example.com", "Access-Control-Request-Method": "GET"},
    )
    assert resp.status_code == 200
    assert "access-control-allow-origin" in resp.headers
