import pytest
from app.models.schemas import RepoItem
from app.services.summarizer import _rule_summary


def test_summarize_empty():
    result = _rule_summary([])
    assert "今日收录 0 个" in result


def test_summarize_one_repo():
    repos = [
        RepoItem(
            name="test/repo",
            owner="test",
            url="https://github.com/test/repo",
            description="A test repo",
            stars=1000,
            forks=500,
            language="Python",
            source="github",
            updated_at="2026-01-01T00:00:00Z",
        )
    ]
    result = _rule_summary(repos)
    assert "test/repo" in result
    assert "⭐1000" in result
    assert "Python" in result


def test_summarize_multi_source():
    repos = [
        RepoItem(name="p1", owner="u1", url="https://a.com", stars=100, source="github", language="Python"),
        RepoItem(name="p2", owner="u2", url="https://b.com", stars=200, source="huggingface"),
    ]
    result = _rule_summary(repos)
    assert "GitHub" in result
    assert "Hugging Face" in result
