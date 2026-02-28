# Vault Backend

交易日志系统后端 — FastAPI + PostgreSQL + LLM Agent 架构。

## 目录结构

```
backend/
├── app/                        # FastAPI 应用层
│   ├── main.py                 # 应用入口，挂载路由 & CORS
│   ├── config.py               # 环境变量读取 (DATABASE_URL 等)
│   ├── db.py                   # SQLAlchemy ORM 定义 (Trade/Review/Checklist)
│   ├── schemas.py              # Pydantic 请求/响应模型
│   ├── dependencies.py         # FastAPI 依赖 (DB session, 用户鉴权)
│   └── routers/
│       ├── health.py           #   GET /health
│       ├── trades.py           #   CRUD /api/trades
│       ├── dashboard.py        #   GET  /api/dashboard/summary
│       ├── reviews.py          #   复盘生成 /api/reviews
│       ├── checklist.py       #   待办清单 /api/checklist
│       └── agent.py            #   Agent 入口 /api/agent/*
│
├── agents/                     # LLM Agent 层 (有 Agent Loop 的模块)
│   ├── base.py                 # BaseAgent: Perceive → Think → Act → Observe 循环
│   ├── llm.py                  # LLMGateway: litellm 统一调用 + ModelConfig
│   ├── tools.py                # Tool 基类: LocalTool / RemoteTool
│   ├── protocol.py             # JSONL 沙箱通信协议 & 共享类型
│   ├── prompts/                # 各 Agent 的 System Prompt
│   │   ├── orchestrator.py
│   │   ├── recorder.py
│   │   ├── reporter.py
│   │   └── analyzer.py
│   ├── orchestrator/           # 协调者 Agent: 意图识别 + 子任务分发
│   ├── recorder/               # 记录 Agent: 自然语言 → 结构化交易记录
│   ├── reporter/               # 报告 Agent: 分析数据 → 中文复盘报告
│   ├── analyzer/               # 向后兼容重定向 → analysis/ 模块
│   └── acp/                    # ACP 协议适配层 (外部互操作)
│       ├── server.py
│       ├── orchestrator_acp.py
│       ├── recorder_acp.py
│       └── reporter_acp.py
│
├── analysis/                   # 分析引擎 (纯代码计算，无 LLM)
│   ├── engine.py               # 路由: Base + Style 分析 → 合并结果
│   ├── base.py                 # 通用指标: 胜率/盈亏比/3M 评分/最大连亏...
│   └── styles/                 # 可插拔风格分析器
│       └── technical.py        # 技术派: 信号验证/K线分析/出场质量
│
├── data_service/               # 数据服务层 (行情数据 + 交易丰富化)
│   ├── service.py              # 高层 API: enrich_trades / enrich_single_trade
│   ├── enrichment.py           # 交易记录 + K线/大盘数据拼合
│   └── market_data.py          # 行情源: AKShareProvider / NullProvider
│
├── agent_runtime/              # Agent 运行时 (沙箱执行 & 工具代理)
│   ├── executor.py             # SandboxExecutor: Docker/inline 双模式
│   ├── tool_handlers.py        # ToolProxy 处理函数 (DB 操作/子Agent调用)
│   ├── queue.py                # Redis 任务队列
│   └── worker.py               # 后台 Worker: 拉取队列 → 沙箱执行
│
├── migrations/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI (app/)                            │
│  /health  /api/trades  /api/dashboard  /api/reviews  /api/agent  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                     ┌─────────▼──────────┐
                     │  /api/agent/chat    │  ← 主入口
                     │  (agent router)     │
                     └─────────┬──────────┘
                               │
              ┌────────────────▼────────────────┐
              │        Agent Runtime             │
              │  SandboxExecutor + ToolProxy     │
              │  (inline 开发模式 / Docker 生产)  │
              └────────────────┬────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │ Orchestrator  │   │  Recorder    │   │  Reporter    │
   │  (LLM Agent)  │   │  (LLM Agent) │   │  (LLM Agent) │
   │  意图路由     │   │  NLU→结构化  │   │  数据→报告   │
   └──────┬───────┘   └──────────────┘   └──────────────┘
          │
          │ call_analyzer (tool call)
          ▼
   ┌──────────────┐     ┌──────────────┐
   │ Data Service  │────▶│Analysis Engine│
   │  K线/大盘数据  │     │ 纯代码计算    │
   │  交易丰富化   │     │ Base + Style  │
   └──────────────┘     └──────────────┘
```

### 模块职责

| 模块 | 类型 | 职责 |
|------|------|------|
| **Orchestrator** | LLM Agent | 理解用户意图，拆解任务并分发给专业模块，汇总结果 |
| **Recorder** | LLM Agent | 从自然语言描述中提取结构化交易数据，引导补全、校验、存储 |
| **Reporter** | LLM Agent | 将分析结果转化为用户可读的中文复盘报告 (3M 维度) |
| **Analysis Engine** | 纯代码 | 计算交易指标: 胜率、盈亏比、期望值、3M 评分；风格分析 (技术派信号验证) |
| **Data Service** | 纯代码 | 拉取 K 线行情 (AKShare)，丰富交易记录，提供市场上下文 |
| **Agent Runtime** | 基础设施 | Agent 沙箱执行、工具代理、Redis 异步任务队列 |

### 复盘时序图

```
用户                Orchestrator       Data Service      Analysis Engine     Reporter
 │                      │                  │                   │                │
 │  "分析上周比亚迪那笔"  │                  │                   │                │
 │─────────────────────▶│                  │                   │                │
 │                      │  call_analyzer   │                   │                │
 │                      │─────────────────▶│                   │                │
 │                      │                  │  fetch K-lines +   │                │
 │                      │                  │  enrich trades     │                │
 │                      │                  │──────────────────▶│                │
 │                      │                  │  base_metrics +    │                │
 │                      │                  │  signal_verified   │                │
 │                      │◀─────────────────│◀──────────────────│                │
 │                      │  call_reporter(analysis_data)        │                │
 │                      │─────────────────────────────────────────────────────▶│
 │                      │  中文复盘报告     │                   │                │
 │                      │◀─────────────────────────────────────────────────────│
 │  复盘报告             │                  │                   │                │
 │◀─────────────────────│                  │                   │                │
```

### 双模式执行

| 模式 | 环境变量 | 说明 |
|------|---------|------|
| **inline** (默认) | `VAULT_AGENT_MODE=inline` | Agent 在 API 进程内执行，适合开发调试 |
| **sandbox** | `VAULT_AGENT_MODE=sandbox` | Agent 在 Docker 容器内执行，`--read-only --network=none` 隔离 |

## API 一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/trades` | 交易列表 |
| GET | `/api/trades/{id}` | 交易详情 |
| POST | `/api/trades` | 创建交易 |
| PATCH | `/api/trades/{id}` | 更新交易 |
| GET | `/api/dashboard/summary` | 仪表盘统计 |
| GET | `/api/reviews` | 复盘列表 |
| POST | `/api/reviews/generate` | 生成复盘报告 |
| GET | `/api/checklist` | 待办清单 |
| POST | `/api/agent/chat` | **主入口**: 自然语言对话 |
| POST | `/api/agent/recorder/run` | 直接调用 Recorder |
| POST | `/api/agent/analyzer/run` | 直接调用 Analysis Engine |
| POST | `/api/agent/reporter/run` | 直接调用 Reporter |
| GET | `/api/agent/tasks/{id}` | 轮询异步任务结果 |

多租户: 所有接口通过 `X-User-Id` Header 区分用户 (缺省 `default`)。

**接口文档（前端对接）**：启动后访问  
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)（可导入 Postman/代码生成）

## Quick Start

### 方式一: Docker Compose

```bash
cd backend
cp .env.example .env
# 编辑 .env 添加 LLM API Key: ANTHROPIC_API_KEY 或 OPENAI_API_KEY

docker compose up -d --build
# PostgreSQL: localhost:5432
# API:        localhost:8000
```

### 方式二: 本地开发

```bash
cd backend
pip install -r requirements.txt

# 启动 PG + Redis
docker compose up -d postgres redis

export DATABASE_URL='postgresql+psycopg://vault:vault@localhost:5432/vault'
export ANTHROPIC_API_KEY='sk-ant-xxx'
export VAULT_AGENT_MODE=inline

uvicorn app.main:app --reload --port 8000
```

### 验证

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user" \
  -d '{"input": "记一笔，今天买了比亚迪002594，230元，2成仓位"}'
```

## 环境变量

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `DATABASE_URL` | 是 | - | PostgreSQL 连接串 |
| `REDIS_URL` | 否 | - | Redis (异步任务需要) |
| `VAULT_AGENT_MODE` | 否 | `inline` | `inline` / `sandbox` |
| `ANTHROPIC_API_KEY` | 是* | - | Anthropic API Key |
| `OPENAI_API_KEY` | 是* | - | OpenAI API Key |
| `VAULT_MODEL_ORCHESTRATOR` | 否 | claude-3-5-haiku | Orchestrator 模型 |
| `VAULT_MODEL_RECORDER` | 否 | claude-3-5-haiku | Recorder 模型 |
| `VAULT_MODEL_REPORTER` | 否 | claude-sonnet | Reporter 模型 |

\* LLM API Key 至少配一个。

## 数据库迁移

首次启动自动建表。从旧版升级:

```bash
psql $DATABASE_URL -f migrations/001_add_user_id.sql
```
