import httpx
from app.core.config import settings
from app.models.schemas import RepoItem


async def _search_github(
    client: httpx.AsyncClient,
    query: str,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = 15,
    headers: dict | None = None,
) -> list[dict]:
    """通用 GitHub Search API 调用"""
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
    }
    resp = await client.get(
        "https://api.github.com/search/repositories",
        headers=headers or {},
        params=params,
    )
    resp.raise_for_status()
    return resp.json().get("items", [])


def _item_to_repo(item: dict, badge: str = "") -> RepoItem:
    """API item 转 RepoItem"""
    return RepoItem(
        name=item["full_name"],
        owner=item["owner"]["login"],
        url=item["html_url"],
        description=item.get("description") or "",
        stars=item["stargazers_count"],
        forks=item["forks_count"],
        language=item.get("language"),
        source="github",
        trend_badge=badge,
        updated_at=item.get("updated_at"),
    )


async def fetch_trending_repos() -> list[RepoItem]:
    """从 GitHub API 按多维度获取热门 AI 项目"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    base_query = settings.github_search_query or "topic:ai stars:>1000"
    page_size = 15

    async with httpx.AsyncClient(timeout=30) as client:
        # === 1. Star 最多 (top 15) ===
        star_items = await _search_github(
            client, base_query, sort="stars", order="desc",
            per_page=page_size, headers=headers,
        )

        # === 2. Fork 最多 (top 10) ===
        fork_items = await _search_github(
            client, base_query, sort="forks", order="desc",
            per_page=10, headers=headers,
        )

        # === 3. 近期增长最快（最近 30 天创建的仓库，按 stars 排序 ===
        from datetime import datetime, timedelta, timezone

        one_month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()[:10]
        recent_query = f"{base_query} created:>={one_month_ago}"
        recent_items = await _search_github(
            client, recent_query, sort="stars", order="desc",
            per_page=8, headers=headers,
        )

        # === 4. Fork/Star 比最好（forks:>50 的项目中 star 最多的）===
        # 取 fork 较多的项目，计算 fork_star_ratio
        fork_query = f"{base_query} forks:>50"
        fork_ratio_items = await _search_github(
            client, fork_query, sort="stars", order="desc",
            per_page=50, headers=headers,
        )

    # 处理结果
    seen = {}  # name -> (repo, [badges])
    all_repos = []

    for item in star_items:
        repo = _item_to_repo(item, "⭐ Star 最多")
        seen[repo.name] = (repo, ["⭐ Star 最多"])
        all_repos.append(repo)

    for item in fork_items:
        name = item["full_name"]
        if name in seen:
            repo, badges = seen[name]
            badges.append("🍴 Fork 最多")
            repo.trend_badge = " / ".join(badges)
        else:
            repo = _item_to_repo(item, "🍴 Fork 最多")
            seen[name] = (repo, ["🍴 Fork 最多"])
            all_repos.append(repo)

    for item in recent_items:
        name = item["full_name"]
        if name in seen:
            repo, badges = seen[name]
            badges.append("🔥 快速上升")
            repo.trend_badge = " / ".join(badges)
        else:
            repo = _item_to_repo(item, "🔥 快速上升")
            seen[name] = (repo, ["🔥 快速上升"])
            all_repos.append(repo)

    # Fork/Star 比：取 forks/star > 0.3 且 top-5
    ratio_candidates = []
    for item in fork_ratio_items:
        s = item["stargazers_count"]
        f = item["forks_count"]
        if s > 0:
            ratio = f / s
            ratio_candidates.append((item, ratio))

    ratio_candidates.sort(key=lambda x: -x[1])
    for item, ratio in ratio_candidates[:8]:
        name = item["full_name"]
        if name in seen:
            # 已经有 badge 了就附加
            pass  # 不覆盖已有 badge，Fork/Star 比作为 extra_tag
        else:
            repo = RepoItem(
                name=item["full_name"],
                owner=item["owner"]["login"],
                url=item["html_url"],
                description=item.get("description") or "",
                stars=item["stargazers_count"],
                forks=item["forks_count"],
                language=item.get("language"),
                source="github",
                trend_badge="📊 Fork/Star 比高",
                extra_tags=[f"fork_star_ratio={ratio:.2f}"],
                updated_at=item.get("updated_at"),
            )
            seen[name] = (repo, ["📊 Fork/Star 比高"])
            all_repos.append(repo)

    # 去重：按 name 去重，保留后出现的 badge 信息
    # 实际上 all_repos 已经保证了每个 name 只出现一次且 badge 合并
    # 但排序一下：有 badge 的优先靠前
    badge_order = {"🔥 快速上升": 0, "⭐ Star 最多": 1, "🍴 Fork 最多": 2, "📊 Fork/Star 比高": 3}
    all_repos.sort(key=lambda r: (badge_order.get(r.trend_badge.split(" / ")[0], 9), -r.stars))

    return all_repos
