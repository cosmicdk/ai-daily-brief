from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    db_url: str = (
        "postgresql+asyncpg://dailybrief:dailybrief123@localhost:5432/dailybrief"
    )
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_search_query: str = "topic:ai stars:>1000"
    github_per_page: int = 15
    timezone: str = "Asia/Shanghai"
    api_prefix: str = "/api/v1"

    # LLM summarizer (optional)
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(default="https://api.deepseek.com", alias="LLM_BASE_URL")
    llm_model: str = "deepseek-chat"

    # 数据源开关
    enable_github: bool = True
    enable_huggingface: bool = True
    enable_arxiv: bool = True
    enable_hackernews: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
