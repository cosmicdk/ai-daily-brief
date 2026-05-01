# AI Daily Brief 📰

GitHub AI 热门项目每日简报服务。

## 快速开始

```bash
# 本地运行
pip install -e ".[dev]"
mkdir -p data
uvicorn app.main:app --reload --port 8000

# Docker
docker compose up -d
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/v1/daily-reports` | 日报列表 |
| GET | `/api/v1/daily-reports/today` | 今日日报 |
| GET | `/api/v1/daily-reports/{date}` | 指定日期日报 |
| POST | `/api/v1/daily-reports/generate` | 手动生成日报 |

## 技术栈

- Python 3.12+ / FastAPI / SQLAlchemy async / SQLite
- Docker Compose 部署
- pytest + pytest-asyncio 测试
