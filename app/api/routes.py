from fastapi import APIRouter, Depends, Query, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.models.schemas import DailyReportOut, DailyReportList
from app.services import report_service

router = APIRouter(prefix="/daily-reports", tags=["日报"])

# WebSocket 连接管理
ws_connections: list[WebSocket] = []


@router.get("", response_model=DailyReportList)
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    q: str = Query("", description="搜索关键词"),
    session: AsyncSession = Depends(get_session),
):
    total = await report_service.count_reports(session, q=q)
    items = await report_service.get_reports(session, skip=skip, limit=limit, q=q)
    return DailyReportList(total=total, items=items)


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
    report = await report_service.generate_today_report(session)
    # 广播给 WebSocket 客户端
    import json
    dead = []
    for ws in ws_connections:
        try:
            await ws.send_json({"type": "new_report", "data": report.model_dump()})
        except Exception:
            dead.append(ws)
    for ws in dead:
        ws_connections.remove(ws)
    return report


@router.get("/trends")
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_session),
):
    return await report_service.get_trends(session, days=days)


@router.websocket("/ws")
async def report_websocket(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections.remove(websocket)


@router.get("/{date}", response_model=DailyReportOut)
async def get_report(date: str, session: AsyncSession = Depends(get_session)):
    report = await report_service.get_report_by_date(session, date)
    if not report:
        raise HTTPException(status_code=404, detail=f"{date} 没有日报")
    return report
