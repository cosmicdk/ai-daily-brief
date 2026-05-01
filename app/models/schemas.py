from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class RepoItem(BaseModel):
    name: str
    url: str
    description: str = ""
    stars: int = 0
    forks: int = 0
    owner: str = ""
    language: Optional[str] = None
    source: str = "github"
    extra_tags: list[str] = []
    trend_badge: str = ""
    updated_at: Optional[str] = None


class DailyReportCreate(BaseModel):
    date: str
    title: str
    summary: str
    items: list[RepoItem]
    sources: list[str]


class DailyReportOut(BaseModel):
    id: int
    date: str
    title: str = ""
    summary: str
    items: list[RepoItem] = []
    repo_count: int = 0
    sources: list[str] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class DailyReportList(BaseModel):
    total: int
    items: list[DailyReportOut]
