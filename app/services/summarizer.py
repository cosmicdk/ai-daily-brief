import json
import httpx
from app.core.config import settings
from app.models.schemas import RepoItem


LLM_SUMMARY_PROMPT = """你是一个 AI 技术简报编辑。根据以下来自 GitHub、Hugging Face、ArXiv、Hacker News 的热门 AI 项目数据，生成一份今日 AI 简报。

要求：
- 用中文
- 按类别归类（LLM/Agent/训练框架/应用/论文/讨论等）
- 每个项目一句话介绍
- 推荐一个今日最值得关注的项目并说明理由
- 总字数 300-500 字
- 格式用 Markdown

数据：
{data}
"""


async def generate_llm_summary(repos: list[RepoItem]) -> str:
    """调用 LLM 生成摘要"""
    if not settings.llm_api_key:
        return _rule_summary(repos)

    data = json.dumps([r.model_dump() for r in repos], ensure_ascii=False, indent=2)
    payload = {
        "model": settings.llm_model or "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个技术简报编辑，输出简洁专业的中文摘要。"},
            {"role": "user", "content": LLM_SUMMARY_PROMPT.format(data=data)},
        ],
        "temperature": 0.3,
        "max_tokens": 1024,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
    except Exception:
        return _rule_summary(repos)


def _rule_summary(repos: list[RepoItem]) -> str:
    """规则摘要（备用）"""
    sources = set(r.source for r in repos)
    lines = [f"📡 数据来源: {', '.join(sorted(sources))}"]
    lines.append(f"📊 今日收录 {len(repos)} 个项目/论文\n")

    lang_count: dict[str, int] = {}
    for r in repos:
        if r.language:
            lang_count[r.language] = lang_count.get(r.language, 0) + 1
    if lang_count:
        top = sorted(lang_count.items(), key=lambda x: -x[1])[:5]
        lines.append(f"🔤 语言分布: {' | '.join(f'{k}({v})' for k, v in top)}")
        lines.append("")

    # 按来源分组
    for source in ["github", "huggingface", "arxiv", "hackernews"]:
        items = [r for r in repos if r.source == source]
        if not items:
            continue
        source_names = {
            "github": "🐙 GitHub",
            "huggingface": "🤗 Hugging Face",
            "arxiv": "📄 ArXiv",
            "hackernews": "🔴 Hacker News",
        }
        lines.append(f"### {source_names.get(source, source)}")
        for i, r in enumerate(items[:10], 1):
            desc = (r.description or "")[:100]
            line = f"{i}. [{r.name}]({r.url})"
            if r.stars:
                line += f" ⭐{r.stars}"
            if r.language:
                line += f" [{r.language}]"
            lines.append(line)
            if desc:
                lines.append(f"   _{desc}_")
        lines.append("")

    return "\n".join(lines)
