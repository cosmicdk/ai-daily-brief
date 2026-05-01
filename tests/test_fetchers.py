"""测试各数据源 fetcher 的辅助函数和异常处理"""

import pytest
from app.models.schemas import RepoItem


def _make_item(**kwargs) -> RepoItem:
    """创建测试用 RepoItem 的辅助函数"""
    defaults = dict(
        name="test/repo",
        url="https://github.com/test/repo",
        stars=100,
        source="test",
    )
    defaults.update(kwargs)
    return RepoItem(**defaults)


class TestRepoItemFactory:
    def test_basic_item(self):
        item = _make_item()
        assert item.name == "test/repo"
        assert item.stars == 100

    def test_with_all_fields(self):
        item = _make_item(
            name="full/test",
            stars=5000,
            language="Go",
            description="A Go project",
            extra_tags=["ai", "ml"],
        )
        assert item.language == "Go"
        assert len(item.extra_tags) == 2

    def test_item_to_dict_keys(self):
        item = _make_item(name="dict/test", stars=42)
        d = item.model_dump()
        assert "name" in d
        assert "url" in d
        assert "stars" in d
        assert "source" in d
        assert "extra_tags" in d
