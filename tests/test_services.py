from datetime import date, datetime
from app.models.schemas import RepoItem, DailyReportCreate, DailyReportOut
from app.services.summarizer import _rule_summary


def test_summarize_empty():
    result = _rule_summary([])
    assert "今日收录 0 个" in result


def test_summarize_one_repo():
    repos = [
        RepoItem(
            name="test/repo",
            url="https://github.com/test/repo",
            description="A test repo",
            stars=1000,
            language="Python",
            source="github",
        )
    ]
    result = _rule_summary(repos)
    assert "test/repo" in result
    assert "⭐1000" in result
    assert "Python" in result


def test_summarize_multi_source():
    repos = [
        RepoItem(
            name="p1",
            url="https://a.com",
            stars=100,
            source="github",
            language="Python",
        ),
        RepoItem(
            name="p2",
            url="https://b.com",
            stars=200,
            source="huggingface",
            language=None,
        ),
    ]
    result = _rule_summary(repos)
    assert "GitHub" in result
    assert "Hugging Face" in result


def test_repo_item_defaults():
    """验证 RepoItem 字段默认值"""
    item = RepoItem(name="test/repo", url="https://example.com", stars=500, source="github")
    assert item.description == ""
    assert item.language is None
    assert item.extra_tags == []


def test_daily_report_create():
    """验证 DailyReportCreate 构建"""
    items = [
        RepoItem(name="a/b", url="https://x.com", stars=100, source="github"),
    ]
    report = DailyReportCreate(
        date=date.today().isoformat(),
        title="Test Report",
        summary="A summary",
        items=items,
        sources=["github"],
    )
    assert report.date == date.today().isoformat()
    assert len(report.items) == 1
    assert "github" in report.sources


def test_daily_report_out_serde():
    """验证 DailyReportOut JSON 序列化"""
    report = DailyReportOut(
        id=1,
        date=date.today().isoformat(),
        title="Test",
        summary="Sum",
        sources=["github"],
        created_at=datetime.now(),
    )
    d = report.model_dump()
    assert d["id"] == 1
    assert d["date"] == date.today().isoformat()
    assert d["title"] == "Test"
    assert d["sources"] == ["github"]


def test_daily_report_out_from_orm():
    """验证 DailyReportOut 从 ORM 数据构建"""
    from datetime import datetime, timezone
    report = DailyReportOut(
        id=2,
        date="2026-05-01",
        title="ORM Test",
        summary="Built from DB",
        sources=["github", "arxiv"],
        created_at=datetime.now(timezone.utc),
    )
    assert report.repo_count == 0


def test_repo_item_full_fields():
    """验证 RepoItem 所有字段"""
    item = RepoItem(
        name="full/repo",
        url="https://github.com/full/repo",
        description="Full featured repo",
        stars=9999,
        language="Rust",
        source="github",
        extra_tags=["llm", "rag"],
    )
    assert item.language == "Rust"
    assert "llm" in item.extra_tags
    assert item.stars == 9999
