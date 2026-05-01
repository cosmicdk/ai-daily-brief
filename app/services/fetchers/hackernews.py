import httpx
from app.models.schemas import RepoItem


HN_BEST = "https://hacker-news.firebaseio.com/v0/beststories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"


async def fetch_hackernews() -> list[RepoItem]:
    """从 Hacker News 获取 AI 相关热门讨论"""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(HN_BEST)
        resp.raise_for_status()
        ids = resp.json()[:30]

        items = []
        for item_id in ids:
            item_resp = await client.get(HN_ITEM.format(item_id))
            if item_resp.status_code == 200:
                items.append(item_resp.json())

    repos = []
    for item in items:
        title = item.get("title", "")
        # 只保留 AI 相关
        ai_keywords = [
            "ai",
            "llm",
            "gpt",
            "neural",
            "deep learning",
            "machine learning",
            "transformer",
            "openai",
            "anthropic",
            "claude",
            "gemini",
        ]
        if not any(kw in title.lower() for kw in ai_keywords):
            continue

        url = item.get("url") or f"https://news.ycombinator.com/item?id={item['id']}"
        repos.append(
            RepoItem(
                name=title[:120],
                owner=item.get("by", "unknown"),
                url=url,
                description=f"HN points: {item.get('score', 0)} | comments: {item.get('descendants', 0)}",
                stars=item.get("score", 0),
                forks=item.get("descendants", 0),
                language=None,
                source="hackernews",
            )
        )
        if len(repos) >= 10:
            break

    return repos
