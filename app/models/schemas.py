from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class RepoItem(BaseModel):
    name: str
    owner: str
    url: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    language: Optional[str] = None
    source: str = "github"
    extra_tags: list[str] = []
    updated_at: Optional[str] = None


class DailyReportOut(BaseModel):
    id: int
    date: str
    summary: str
    repo_count: int
    created_at: datetime
    sources: list[str] = []

    model_config = {"from_attributes": True}


class DailyReportList(BaseModel):
    total: int
    items: list[DailyReportOut]
