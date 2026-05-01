from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import init_db, get_session
from app.models.daily_report import DailyReport
from app.api.routes import router
from app.core.config import settings

app_start_time = datetime.now(timezone.utc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="AI Daily Brief",
    description="GitHub AI 热门项目每日简报",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

# SPA fallback: 静态文件通过自定义路由服务
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
ASSET_PATHS = {
    "/" + str(p.relative_to(frontend_dist)): p
    for p in (frontend_dist / "assets").rglob("*")
    if p.is_file()
}

if (frontend_dist / "favicon.svg").exists():
    ASSET_PATHS["/favicon.svg"] = frontend_dist / "favicon.svg"


@app.exception_handler(404)
async def spa_fallback(request: Request, exc):
    path = request.url.path
    if path.startswith("/api/") or path == "/health":
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    # 尝试返回静态文件
    if path in ASSET_PATHS:
        return FileResponse(str(ASSET_PATHS[path]))
    if frontend_dist.exists() and (frontend_dist / "index.html").exists():
        return FileResponse(str(frontend_dist / "index.html"))
    return JSONResponse({"detail": "Not Found"}, status_code=404)


@app.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    # 数据库状态
    try:
        count_stmt = select(func.count()).select_from(DailyReport)
        total = (await session.execute(count_stmt)).scalar() or 0
        last_stmt = select(DailyReport).order_by(DailyReport.date.desc()).limit(1)
        last = (await session.execute(last_stmt)).scalar_one_or_none()
        db_status = "ok"
    except Exception:
        db_status = "error"
        total = 0
        last = None

    uptime = (datetime.now(timezone.utc) - app_start_time).total_seconds()

    return {
        "status": "ok",
        "version": "0.3.0",
        "uptime_seconds": round(uptime),
        "database": db_status,
        "total_reports": total,
        "latest_report_date": last.date if last else None,
        "sources": {
            "github": settings.enable_github,
            "huggingface": settings.enable_huggingface,
            "arxiv": settings.enable_arxiv,
            "hackernews": settings.enable_hackernews,
        },
        "llm_summary": bool(settings.llm_api_key),
    }
