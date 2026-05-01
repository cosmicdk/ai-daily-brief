import json
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_report import DailyReport
from app.models.schemas import RepoItem, DailyReportOut
from app.services.github import fetch_trending_repos, summarize_repos


async def generate_today_report(session: AsyncSession) -> DailyReportOut:
    """生成今日日报并入库"""
    today = date.today().isoformat()

    repos = await fetch_trending_repos()
    summary = summarize_repos(repos)
    raw_data = json.dumps([r.model_dump() for r in repos], ensure_ascii=False)

    report = DailyReport(
        date=today,
        summary=summary,
        raw_data=raw_data,
        repo_count=len(repos),
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return DailyReportOut.model_validate(report)


async def get_reports(session: AsyncSession, skip: int = 0, limit: int = 20) -> list[DailyReportOut]:
    stmt = select(DailyReport).order_by(DailyReport.date.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    reports = result.scalars().all()
    return [DailyReportOut.model_validate(r) for r in reports]


async def get_report_by_date(session: AsyncSession, date_str: str) -> DailyReportOut | None:
    stmt = select(DailyReport).where(DailyReport.date == date_str)
    result = await session.execute(stmt)
    report = result.scalar_one_or_none()
    return DailyReportOut.model_validate(report) if report else None
