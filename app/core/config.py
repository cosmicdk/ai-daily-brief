from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./data/daily_brief.db"
    github_token: str = ""
    github_search_query: str = "topic:ai stars:>1000"
    github_per_page: int = 15
    timezone: str = "Asia/Shanghai"
    api_prefix: str = "/api/v1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
