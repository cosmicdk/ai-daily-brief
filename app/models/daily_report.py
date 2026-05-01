from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, func, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, comment="报告日期 YYYY-MM-DD")
    summary: Mapped[str] = mapped_column(Text, nullable=False, comment="AI 生成的摘要总结")
    raw_data: Mapped[str] = mapped_column(Text, nullable=False, comment="各数据源原始数据 JSON")
    repo_count: Mapped[int] = mapped_column(Integer, default=0, comment="收录项目数")
    sources: Mapped[str] = mapped_column(String(255), default="github", comment="数据源列表,逗号分隔")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
