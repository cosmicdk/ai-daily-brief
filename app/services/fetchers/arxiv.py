import httpx
from app.models.schemas import RepoItem


ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.MA", "cs.RO", "stat.ML"]


async def fetch_arxiv_papers() -> list[RepoItem]:
    """从 ArXiv 获取热门 AI 论文"""
    query = "+OR+".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
    url = f"http://export.arxiv.org/api/query?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results=20"

    headers = {"Accept": "application/atom+xml"}

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        text = resp.text

    repos = []
    for entry in _parse_arxiv_entries(text)[:15]:
        repos.append(
            RepoItem(
                name=entry["title"],
                owner=",".join(a["name"] for a in entry.get("authors", [])),
                url=entry["id"],
                description=entry.get("summary", "")[:300],
                stars=0,
                forks=0,
                language=None,
                source="arxiv",
                extra_tags=[c["term"] for c in entry.get("categories", [])],
            )
        )
    return repos


def _parse_arxiv_entries(xml_text: str) -> list[dict]:
    """简单 XML 解析，不依赖外部库"""
    entries = []
    for raw in xml_text.split("<entry>")[1:]:
        entry = raw.split("</entry>")[0]

        def extract(tag):
            import re

            m = re.search(f"<{tag}[^>]*>(.*?)</{tag}>", entry, re.DOTALL)
            return m.group(1).strip() if m else ""

        entry_data = {
            "id": extract("id"),
            "title": extract("title").replace("\n", " ").strip(),
            "summary": extract("summary").replace("\n", " ").strip(),
        }
        # authors
        authors = []
        for a in entry.split("<author>")[1:]:
            aname = a.split("</author>")[0]
            import re

            m = re.search(r"<name>(.*?)</name>", aname)
            if m:
                authors.append({"name": m.group(1).strip()})
        entry_data["authors"] = authors
        # categories
        cats = []
        for c in entry.split("<category")[1:]:
            c = c.split(">")[0]
            import re

            m = re.search(r'term="([^"]+)"', c)
            if m:
                cats.append({"term": m.group(1)})
        entry_data["categories"] = cats
        entries.append(entry_data)
    return entries
