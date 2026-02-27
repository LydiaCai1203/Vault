# Vault Backend (FastAPI)

## 1) 为什么建议 PostgreSQL（PG）
- **并发与可靠性**：C 端用户量起来后，PG 更适合多连接并发。
- **查询与分析**：复盘统计/筛选会越来越复杂，PG 的索引/查询优化更强。
- **演进能力**：后续做多 Portfolio、用户系统、权限、审计日志、异步任务等，PG 更稳。

本后端 **仅支持 PostgreSQL**。

## 2) 配置 DATABASE_URL
后端通过环境变量 `DATABASE_URL` 连接数据库。

- PostgreSQL（推荐）：
```bash
export DATABASE_URL='postgresql+psycopg://vault:vault@localhost:5432/vault'
```


## 3) 运行（本地）

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 4) Docker Compose（一键启动 PG + API）

我们这里把 **api 也放进 compose**，这样就不需要本机 Python 环境：

```bash
cd backend
docker compose up -d --build
```

- PostgreSQL：localhost:5432
- API：localhost:8000

如果你想在本机跑 uvicorn（开发调试），也可以：
```bash
cd backend
export DATABASE_URL='postgresql+psycopg://vault:vault@localhost:5432/vault'
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

> 目前脚手架用 `Base.metadata.create_all()` 自动建表（适合快速起步）。
> 真正上线建议加 Alembic 做迁移（我也可以下一步补）。

## 5) 多租户迁移（已有数据库）

若从旧版升级，需执行迁移添加 `user_id`：

```bash
psql $DATABASE_URL -f migrations/001_add_user_id.sql
```

## 6) Agent 沙箱与异步任务

- **多租户**：所有 API 通过 `X-User-Id` 区分用户（无则用 `default`）。
- **Agent 沙箱**：每次调用起独立容器，`--read-only` + `--network=none`。
- **异步**：`POST /api/agent/recorder/run?async=1` 入队，`GET /api/agent/tasks/{task_id}` 轮询结果。
- **Executor Worker**：需 Docker 访问，拉 Redis 任务并 `docker run` 启动 Agent 镜像。

```bash
# 构建 Agent 镜像（需先 cd backend）
docker build -f agent_runtime/docker/Dockerfile.recorder -t vault-agent-recorder .

# 本地跑 Worker
REDIS_URL=redis://localhost:6379/0 python -m agent_runtime.worker
```
