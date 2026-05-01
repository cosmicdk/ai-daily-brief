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
            updated_at=item.get("updated_at"),
        ))
    return repos


def summarize_repos(repos: list[RepoItem]) -> str:
    """生成摘要文本（不用 LLM，规则化摘要）"""
    lines = [f"共收录 {len(repos)} 个 AI 热门项目\n"]
    lang_count: dict[str, int] = {}
    for r in repos:
        if r.language:
            lang_count[r.language] = lang_count.get(r.language, 0) + 1

    if lang_count:
        top_langs = sorted(lang_count.items(), key=lambda x: -x[1])[:3]
        lines.append(f"语言分布: {', '.join(f'{k}({v})' for k, v in top_langs)}")

    lines.append("")
    for i, r in enumerate(repos[:5], 1):
        desc = (r.description or "暂无描述")[:80]
        lines.append(f"{i}. [{r.name}]({r.url}) ⭐{r.stars} 🍴{r.forks}")
        if r.language:
            lines.append(f"   语言: {r.language} | {desc}")
        else:
            lines.append(f"   {desc}")
        lines.append("")

    lines.append(f"完整列表: {settings.github_per_page} 个项目已收录")
    return "\n".join(lines)
