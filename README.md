# Intelligence Agent — 个人化AI情报分析师平台

> 用多智能体系统替用户完成 **采集 → 筛选 → 分析 → 历史关联 → 行动建议 → 推送** 的全流程，将每天1-3小时的信息获取压缩为5-10分钟的高密度阅读/收听/观看。

## 技术栈

| 层 | 技术 |
|:---|:-----|
| 前端 | Next.js 14+ / Tailwind CSS / shadcn/ui / Zustand / PWA |
| 后端 | FastAPI / SQLAlchemy 2.0 / Celery / JWT |
| Agent引擎 | LangGraph / LiteLLM / DeepSeek V3 + Claude Sonnet |
| 数据库 | PostgreSQL / Redis / Chroma (向量DB) |
| 多模态 | Edge-TTS / MoneyPrinterTurbo |
| 部署 | Vercel (前端) / Railway (后端) / Supabase (DB) |

## 快速开始

### 1. 克隆并配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

### 2. 启动基础设施

```bash
docker-compose up -d
```

### 3. 后端

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed_templates
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Celery Worker

```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info --beat
```

### 5. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

## 项目结构

```
intel-engine/
├── frontend/          # Next.js Web App (PWA)
├── backend/           # FastAPI Backend
├── agents/            # GTRME Agent 引擎
├── domains/           # 领域配置 (YAML)
├── templates/         # 初始配方定义
├── distribution/      # 多渠道分发
├── media/             # 多模态转换
├── scripts/           # 脚本工具
└── tests/             # 测试
```

## 文档

- [产品愿景与定位](./specs_v2/21-产品愿景与定位.md)
- [P0核心功能PRD](./specs_v2/22-P0核心功能PRD.md)
- [信息架构与数据模型](./specs_v2/23-信息架构与数据模型.md)
- [用户流程图](./specs_v2/24-用户流程图.md)
- [技术架构与选型](./specs_v2/25-技术架构与选型.md)

## License

Private — All rights reserved.
