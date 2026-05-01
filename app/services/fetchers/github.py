import json
import httpx
from app.core.config import settings
from app.models.schemas import RepoItem


async def fetch_trending_repos() -> list[RepoItem]:
    """从 GitHub API 获取热门 AI 项目"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    params = {
        "q": settings.github_search_query,
        "sort": "stars",
        "order": "desc",
        "per_page": settings.github_per_page,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://api.github.com/search/repositories",
            headers=headers,
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    repos = []
    for item in data.get("items", []):
        repos.append(RepoItem(
            name=item["full_name"],
            owner=item["owner"]["login"],
            url=item["html_url"],
            description=item.get("description"),
            stars=item["stargazers_count"],
            forks=item["forks_count"],
            language=item.get("language"),
            source="github",
            updated_at=item.get("updated_at"),
        ))
    return repos
