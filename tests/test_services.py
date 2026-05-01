import pytest
from app.services.github import summarize_repos
from app.models.schemas import RepoItem


def test_summarize_empty():
    result = summarize_repos([])
    assert "共收录 0 个" in result


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
            updated_at="2026-01-01T00:00:00Z",
        )
    ]
    result = summarize_repos(repos)
    assert "test/repo" in result
    assert "⭐1000" in result
    assert "Python" in result
