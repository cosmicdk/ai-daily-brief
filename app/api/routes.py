from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.schemas import DailyReportOut, DailyReportList
from app.services import report_service

router = APIRouter(prefix="/daily-reports", tags=["日报"])


@router.get("", response_model=DailyReportList)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    items = await report_service.get_reports(session, skip=skip, limit=limit)
    return DailyReportList(total=len(items), items=items)


@router.get("/today", response_model=DailyReportOut)
async def get_today_report(session: AsyncSession = Depends(get_session)):
    from datetime import date
    report = await report_service.get_report_by_date(session, date.today().isoformat())
    if not report:
        raise HTTPException(status_code=404, detail="今日日报尚未生成")
    return report


@router.post("/generate", response_model=DailyReportOut)
async def generate_report(session: AsyncSession = Depends(get_session)):
    from datetime import date
    existing = await report_service.get_report_by_date(session, date.today().isoformat())
    if existing:
        raise HTTPException(status_code=409, detail="今日日报已存在")
    return await report_service.generate_today_report(session)


@router.get("/{date}", response_model=DailyReportOut)
async def get_report(date: str, session: AsyncSession = Depends(get_session)):
    report = await report_service.get_report_by_date(session, date)
    if not report:
        raise HTTPException(status_code=404, detail=f"{date} 没有日报")
    return report
