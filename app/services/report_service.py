import json
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_report import DailyReport
from app.models.schemas import RepoItem, DailyReportOut
from app.core.config import settings
from app.services.fetchers import github, huggingface, arxiv, hackernews
from app.services.summarizer import generate_llm_summary

FETCHERS = []

if settings.enable_github:
    FETCHERS.append(("github", github.fetch_trending_repos))
if settings.enable_huggingface:
    FETCHERS.append(("huggingface", huggingface.fetch_huggingface_models))
if settings.enable_arxiv:
    FETCHERS.append(("arxiv", arxiv.fetch_arxiv_papers))
if settings.enable_hackernews:
    FETCHERS.append(("hackernews", hackernews.fetch_hackernews))


async def _fetch_all() -> tuple[list[RepoItem], list[str]]:
    all_repos = []
    sources = []
    for name, fetcher in FETCHERS:
        try:
            repos = await fetcher()
            all_repos.extend(repos)
            sources.append(name)
        except Exception as e:
            print(f"[warn] fetcher '{name}' failed: {e}")
    return all_repos, sources


async def generate_today_report(session: AsyncSession) -> DailyReportOut:
    today = date.today().isoformat()

    repos, sources = await _fetch_all()
    summary = await generate_llm_summary(repos)
    raw_data = json.dumps([r.model_dump() for r in repos], ensure_ascii=False)

    report = DailyReport(
        date=today,
        title=f"AI 日报 - {today}",
        summary=summary,
        raw_data=raw_data,
        repo_count=len(repos),
        sources=",".join(sources),
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return DailyReportOut.model_validate(report)


async def get_reports(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    q: str = "",
) -> list[DailyReportOut]:
    stmt = select(DailyReport).order_by(DailyReport.date.desc())
    if q:
        stmt = stmt.where(DailyReport.summary.ilike(f"%{q}%"))
    stmt = stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    reports = result.scalars().all()
    return [DailyReportOut.model_validate(r) for r in reports]


async def count_reports(session: AsyncSession, q: str = "") -> int:
    stmt = select(func.count()).select_from(DailyReport)
    if q:
        stmt = stmt.where(DailyReport.summary.ilike(f"%{q}%"))
    result = await session.execute(stmt)
    return result.scalar() or 0


async def get_report_by_date(
    session: AsyncSession, date_str: str
) -> DailyReportOut | None:
    stmt = select(DailyReport).where(DailyReport.date == date_str)
    result = await session.execute(stmt)
    report = result.scalar_one_or_none()
    return DailyReportOut.model_validate(report) if report else None


async def get_trends(session: AsyncSession, days: int = 30) -> dict:
    """获取趋势统计数据"""
    from datetime import timedelta

    start = date.today() - timedelta(days=days)
    stmt = (
        select(DailyReport)
        .where(DailyReport.date >= start.isoformat())
        .order_by(DailyReport.date)
    )
    result = await session.execute(stmt)
    reports = result.scalars().all()

    dates = []
    repo_counts = []
    all_sources = set()
    for r in reports:
        dates.append(r.date)
        repo_counts.append(r.repo_count)
        for s in r.sources.split(","):
            if s:
                all_sources.add(s)

    return {
        "dates": dates,
        "repo_counts": repo_counts,
        "sources": list(all_sources),
        "total_reports": len(reports),
    }
