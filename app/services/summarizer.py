import json
import httpx
from app.core.config import settings
from app.models.schemas import RepoItem


LLM_SUMMARY_PROMPT = """你是一位资深 AI 技术研究员兼科技编辑。根据以下来自 GitHub、Hugging Face、ArXiv、Hacker News 的今日热门 AI 项目数据，生成一份**深度技术简报**。

## 简报结构要求

### 一、今日焦点 🔥
从所有项目中精选 **1-2 个最具影响力或最有创新性**的项目，深度解读：
- 这个项目解决了什么核心问题？
- 它的技术/架构创新点是什么？（如用了什么新算法、新框架、新范式）
- 与同类项目相比有什么差异化优势？（如果数据中有竞品，进行对比）
- 为什么今天值得关注？（里程碑、突破、社区热度激增等）

### 二、项目深度速览 📋
按类别分组（如模型与嵌入、开发者工具、图像生成等）。**每个项目写成可折叠的格式**，初始只显示标题和一句话总结：

<details>
<summary><strong>项目名</strong> — 一句话总结（20字内）</summary>

🔥 **技术亮点**：一句话说明技术/架构创新点
💡 **为什么重要**：一句话说明对开发者的价值
📊 **数据**：Star/Fork/下载量
</details>

每个 <details> 块之间空一行。
<strong>项目名</strong> 中的项目名会被前端自动添加马克笔高亮颜色，非常醒目。

### 三、趋势洞察 📈
- 今日整体的技术方向趋势
- 值得关注的新兴细分方向

### 四、编辑点评 ✏️
- 对开发者的 actionable 建议
- 哪些项目值得立即试用？哪些值得深入研究？

## 输出要求
- 使用中文
- Markdown 格式
- 注意**必须使用上方指定的 <details> 格式**来表示每个项目
- 语言风格：专业、简洁、有见解
- 篇幅：600-1000 字

## 数据
{data}
"""


async def generate_llm_summary(repos: list[RepoItem]) -> str:
    """调用 LLM 生成摘要"""
    if not settings.llm_api_key:
        return _rule_summary(repos)

    # 精简传给 LLM 的数据以控制 prompt 长度
    # 保留 top-15 GitHub + top-10 其他来源，LLM 做分析概括即可
    sorted_repos = sorted(repos, key=lambda r: -r.stars)
    top_hits = sorted_repos[:25]
    data = json.dumps(
        [
            {
                "name": r.name,
                "url": r.url,
                "description": (r.description or "")[:200],
                "stars": r.stars,
                "forks": r.forks,
                "language": r.language,
                "source": r.source,
                "owner": r.owner,
            }
            for r in top_hits
        ],
        ensure_ascii=False,
        indent=2,
    )
    payload = {
        "model": settings.llm_model or "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一位资深 AI 技术研究员，输出有深度见解的中文技术简报。分析要具体、有数据支撑、有对比、有判断。",
            },
            {"role": "user", "content": LLM_SUMMARY_PROMPT.format(data=data)},
        ],
        "temperature": 0.3,
        "max_tokens": 3072,
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
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
