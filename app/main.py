from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
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
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(router, prefix="/api/v1")


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
        "version": "0.2.0",
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
