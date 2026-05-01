import httpx
from app.models.schemas import RepoItem


async def fetch_huggingface_models() -> list[RepoItem]:
    """从 Hugging Face 获取热门 AI 模型"""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://huggingface.co/api/models",
            params={"sort": "downloads", "direction": -1, "limit": 8},
        )
        resp.raise_for_status()
        data = resp.json()

    repos = []
    for item in data:
        repos.append(
            RepoItem(
                name=item.get("modelId", item["id"]),
                owner=item["id"].split("/")[0] if "/" in item["id"] else "unknown",
                url=f"https://huggingface.co/{item['id']}",
                description=item.get("description") or "",
                stars=item.get("downloads", 0),
                forks=item.get("likes", 0),
                language=None,
                source="huggingface",
                extra_tags=item.get("tags", []),
                updated_at=item.get("lastModified", ""),
            )
        )
    return repos
