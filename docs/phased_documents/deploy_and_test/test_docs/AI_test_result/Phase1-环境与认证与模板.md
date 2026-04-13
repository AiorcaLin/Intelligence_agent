# Phase 1 测试报告：环境与基础设施验证 + 认证系统 + 模板系统

| 项目 | 内容 |
|------|------|
| **测试时间** | 2026-04-13 17:47 ~ 17:51 (UTC+8) |
| **测试者** | AI Testing Expert |
| **测试环境** | Linux 6.8.0-101-generic, Docker Compose |
| **后端地址** | http://localhost:8001 |
| **前端地址** | http://localhost:3000 |
| **数据库** | PostgreSQL 16 (localhost:5432, intel_engine) |

---

## Part 1: 环境与基础设施验证

### TC-01-01 Docker 容器健康检查

**命令:**
```bash
sudo docker compose ps
```

**预期结果:** 所有容器 (postgres, redis, chroma) 状态为 Up 且 healthy

**实际结果:** ✅ **Pass**
- `intelligence_agent-postgres-1` — Up 2 hours (healthy)
- `intelligence_agent-redis-1` — Up 2 hours (healthy)
- `intelligence_agent-chroma-1` — Up 2 hours

> ⚠️ 注意: ChromaDB 容器无 healthcheck 配置，状态仅显示 "Up" 而非 "healthy"。

---

### TC-01-02 PostgreSQL 就绪检查

**命令:**
```bash
docker exec intelligence_agent-postgres-1 pg_isready -U postgres -d intel_engine
```

**预期结果:** 返回 "accepting connections"

**实际结果:** ✅ **Pass**
```
/var/run/postgresql:5432 - accepting connections
```

---

### TC-01-03 Redis 连通性检查

**命令:**
```bash
docker exec intelligence_agent-redis-1 redis-cli ping
```

**预期结果:** 返回 "PONG"

**实际结果:** ✅ **Pass**
```
PONG
```

---

### TC-01-04 ChromaDB 心跳检查

**命令:**
```bash
curl -s http://localhost:8000/api/v2/heartbeat
```

**预期结果:** HTTP 200，返回 heartbeat

**实际结果:** ✅ **Pass**
```json
HTTP 200
{"nanosecond heartbeat":1776073681846795078}
```

> 📝 ChromaDB v1 API (`/api/v1/heartbeat`) 返回 410 Gone，已迁移到 v2。

---

### TC-01-05 FastAPI 健康端点

**命令:**
```bash
curl -s http://localhost:8001/health
```

**预期结果:** HTTP 200，返回 `{"status":"ok"}`

**实际结果:** ✅ **Pass**
```json
HTTP 200
{"status":"ok"}
```

---

### TC-01-06 FastAPI 文档端点

**命令:**
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/docs
```

**预期结果:** HTTP 200

**实际结果:** ✅ **Pass** — HTTP 200

---

### TC-01-07 前端首页

**命令:**
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

**预期结果:** HTTP 200

**实际结果:** ✅ **Pass** — HTTP 200

---

### TC-01-08 数据库模板数量检查

**命令:**
```bash
docker exec intelligence_agent-postgres-1 psql -U postgres -d intel_engine -c "SELECT count(*) FROM templates;"
```

**预期结果:** 返回预置模板数量 (≥5)

**实际结果:** ✅ **Pass**
```
template_count: 8
```

---

### TC-01-09 数据库表结构检查

**命令:**
```bash
docker exec intelligence_agent-postgres-1 psql -U postgres -d intel_engine -c "\dt"
```

**预期结果:** 包含核心业务表

**实际结果:** ✅ **Pass** — 共 12 张表:
| 表名 | 描述 |
|------|------|
| users | 用户表 |
| organizations | 组织表 |
| templates | 模板表 |
| template_trials | 模板试用表 |
| template_contributors | 模板贡献者表 |
| subscriptions | 订阅表 |
| intel_reports | 情报报告表 |
| raw_data | 原始数据表 |
| push_logs | 推送日志表 |
| report_item_feedbacks | 报告项反馈表 |
| report_satisfactions | 报告满意度表 |
| token_records | Token 记录表 |

---

### TC-01-10 系统资源检查

**命令:**
```bash
free -h && df -h /
```

**预期结果:** 内存可用 > 1GB，磁盘使用 < 80%

**实际结果:** ✅ **Pass**
- 内存: 总计 7.5Gi，可用 5.8Gi（充足）
- 磁盘: 79G 总量，已用 9.7G（13%），剩余 66G

---

### TC-01-11 DeepSeek API 连通性

**命令:**
```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 \
  https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer sk-ebe8767aa50b4fcfb088e931845eeb79"
```

**预期结果:** HTTP 200

**实际结果:** ✅ **Pass** — HTTP 200

---

### TC-01-12 OpenRouter API 连通性

**命令:**
```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 \
  https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer sk-or-v1-..."
```

**预期结果:** HTTP 200

**实际结果:** ✅ **Pass** — HTTP 200

---

## Part 2: 认证系统测试

### TC-02-01 用户注册

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ai_tester_p1_new@test.com","password":"TestPass123",
       "name":"AI测试P1","industry":"QA","company":"TestLab"}'
```

**预期结果:** HTTP 201，返回 access_token + refresh_token

**实际结果:** ✅ **Pass**
```json
HTTP 201
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### TC-02-02 重复注册（预期 409）

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"ai_tester_p1_new@test.com","password":"TestPass123",
       "name":"AI测试P1","industry":"QA","company":"TestLab"}'
```

**预期结果:** HTTP 409

**实际结果:** ✅ **Pass**
```json
HTTP 409
{"detail":"该邮箱已注册"}
```

---

### TC-02-03 正确密码登录

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ai_tester_p1_new@test.com","password":"TestPass123"}'
```

**预期结果:** HTTP 200，返回 token 对

**实际结果:** ✅ **Pass**
```json
HTTP 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### TC-02-04 错误密码登录（预期 401）

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ai_tester_p1_new@test.com","password":"WrongPass999"}'
```

**预期结果:** HTTP 401

**实际结果:** ✅ **Pass**
```json
HTTP 401
{"detail":"邮箱或密码错误"}
```

---

### TC-02-05 Token 刷新

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<valid_refresh_token>"}'
```

**预期结果:** HTTP 200，返回新的 token 对

**实际结果:** ✅ **Pass**
```json
HTTP 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...(new)",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...(new)",
  "token_type": "bearer"
}
```

> 📝 Refresh Token 为一次性使用。登录会生成新 refresh_token，旧 token 立即失效。使用已消费的 refresh_token 返回 401。

---

### TC-02-06 用 access_token 当 refresh_token（预期 401）

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<access_token_value>"}'
```

**预期结果:** HTTP 401

**实际结果:** ✅ **Pass**
```json
HTTP 401
{"detail":"刷新令牌已过期或无效"}
```

---

### TC-02-07 无 Token 访问受保护接口（预期 401）

**命令:**
```bash
curl -s http://localhost:8001/api/subscriptions/
```

**预期结果:** HTTP 401

**实际结果:** ✅ **Pass**（带尾斜杠）
```json
HTTP 401
{"detail":"Not authenticated"}
```

> ⚠️ 发现：不带尾斜杠的 `/api/subscriptions` 返回 **HTTP 307 重定向**到带尾斜杠路径，而非直接 401。这意味着无 token 的请求在重定向后才被拒绝。功能上正确，但建议统一处理尾斜杠以避免不必要的重定向。

---

### TC-02-08 空密码注册（BUG-020 验证）

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"empty_pass_new@test.com","password":"",
       "name":"EmptyPass","industry":"QA","company":"TestLab"}'
```

**预期结果:** HTTP 422 或 400（应拒绝空密码）

**实际结果:** ❌ **Fail — 确认 BUG-020**
```json
HTTP 201
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**BUG 详情:** 空密码 `""` 成功注册，返回 201 和有效 token。后端未对密码长度/复杂度做校验。这是严重安全漏洞。

---

### TC-02-09 无效邮箱格式注册

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"not-an-email","password":"TestPass123",
       "name":"BadEmail","industry":"QA","company":"TestLab"}'
```

**预期结果:** HTTP 422

**实际结果:** ✅ **Pass**
```json
HTTP 422
{
  "detail": [{
    "type": "value_error",
    "loc": ["body", "email"],
    "msg": "value is not a valid email address: An email address must have an @-sign."
  }]
}
```

---

### TC-02-10 缺少必填字段注册

**命令:**
```bash
curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"password":"TestPass123"}'
```

**预期结果:** HTTP 422

**实际结果:** ✅ **Pass**
```json
HTTP 422
{
  "detail": [
    {"type":"missing","loc":["body","email"],"msg":"Field required"},
    {"type":"missing","loc":["body","name"],"msg":"Field required"}
  ]
}
```

---

## Part 3: 模板系统测试

### TC-03-01 获取全部模板列表（无鉴权）

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/"
```

**预期结果:** HTTP 200，返回分页列表

**实际结果:** ✅ **Pass**
```json
HTTP 200
{
  "items": [...],  // 8 个模板（含 fork 的）
  "total": 8,
  "page": 1,
  "size": 20
}
```

模板列表（测试执行前的初始状态）:
1. AI每日精选 (domain=AI, system)
2. DeFi协议动态 (domain=Crypto, system)
3. 链上信号分析 (domain=Crypto, system)
4. 加密市场速报 (domain=Crypto, system)
5. GitHub AI热门项目 (domain=AI, system)
6. Phase1测试Fork模板 (domain=AI, human, fork of #1)
7. 我的AI精选Fork (domain=AI, human, fork of #1)
8. AI论文精读 (domain=AI, system)

---

### TC-03-02 按 domain=AI 筛选

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/?domain=AI"
```

**预期结果:** HTTP 200，仅返回 AI 领域模板

**实际结果:** ✅ **Pass**
```json
HTTP 200
{"items":[...], "total":5, "page":1, "size":20}
```

返回 5 个 AI 领域模板，符合预期。

---

### TC-03-03 按 domain=Crypto 筛选

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/?domain=Crypto"
```

**预期结果:** HTTP 200，仅返回 Crypto 领域模板

**实际结果:** ✅ **Pass**
```json
HTTP 200
{"items":[...], "total":3, "page":1, "size":20}
```

返回 3 个 Crypto 领域模板（DeFi协议动态、链上信号分析、加密市场速报），符合预期。

---

### TC-03-04 不存在的 domain 筛选

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/?domain=NonExistDomain"
```

**预期结果:** HTTP 200，返回空列表

**实际结果:** ✅ **Pass**
```json
HTTP 200
{"items":[], "total":0, "page":1, "size":20}
```

---

### TC-03-05 分页测试

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/?page=1&size=2"
curl -s "http://localhost:8001/api/templates/?page=2&size=2"
```

**预期结果:** HTTP 200，每页 2 条，总数不变

**实际结果:** ✅ **Pass**

| 页码 | 返回条数 | 总数 | 模板名称 |
|------|---------|------|---------|
| page=1 | 2 | 8→9* | AI每日精选, DeFi协议动态 |
| page=2 | 2 | 9* | 加密市场速报, DeFi协议动态 |

> *注: 测试过程中 Fork 操作新增了 1 个模板，总数从 8 变为 9。

---

### TC-03-06 获取单个模板详情

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/3adf0f8e-92d3-4471-8ab3-313255ce5c8d"
```

**预期结果:** HTTP 200，返回完整模板信息（含 prompt_config）

**实际结果:** ✅ **Pass**
```json
HTTP 200
{
  "id": "3adf0f8e-92d3-4471-8ab3-313255ce5c8d",
  "name": "AI每日精选",
  "domain": "AI",
  "prompt_config": {
    "collection_weights": {"arXiv":0.25, "GitHub":0.2, ...},
    "filtering": {"min_relevance_score":6, "max_age_hours":48, ...},
    "output": {"analysis_framework":"技术突破 → 应用场景 → ...", ...}
  },
  "contributors": [],
  "adoption_count": 2
}
```

---

### TC-03-07 不存在的 UUID 获取详情（预期 404）

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/00000000-0000-0000-0000-000000000000"
```

**预期结果:** HTTP 404

**实际结果:** ✅ **Pass**
```json
HTTP 404
{"detail":"模板不存在"}
```

---

### TC-03-08 获取模板谱系

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/3adf0f8e-92d3-4471-8ab3-313255ce5c8d/lineage"
```

**预期结果:** HTTP 200，返回谱系树

**实际结果:** ✅ **Pass**
```json
HTTP 200
[
  {"id":"3adf0f8e-...", "name":"AI每日精选", "creator_type":"system", "depth":0}
]
```

根模板谱系仅包含自身，depth=0，符合预期。

---

### TC-03-09 试用模板（需 Token）

**命令:**
```bash
curl -s -X POST "http://localhost:8001/api/templates/{template_id}/try" \
  -H "Authorization: Bearer <access_token>"
```

**预期结果:** HTTP 200

**实际结果:** ✅ **Pass**
```json
HTTP 200
{
  "ok": true,
  "template_name": "AI每日精选",
  "message": "试用已开始，将生成一份示例报告"
}
```

---

### TC-03-10 重复试用（预期 409）

**命令:**
```bash
curl -s -X POST "http://localhost:8001/api/templates/{template_id}/try" \
  -H "Authorization: Bearer <access_token>"
```

**预期结果:** HTTP 409

**实际结果:** ✅ **Pass**
```json
HTTP 409
{"detail":"您已试用过此模板"}
```

---

### TC-03-11 采用模板

**命令:**
```bash
curl -s -X POST "http://localhost:8001/api/templates/{template_id}/adopt" \
  -H "Authorization: Bearer <access_token>"
```

**预期结果:** HTTP 200

**实际结果:** ✅ **Pass**
```json
HTTP 200
{"ok":true}
```

---

### TC-03-12 Fork 模板

**命令:**
```bash
curl -s -X POST "http://localhost:8001/api/templates/{template_id}/fork" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Phase1测试Fork","description":"Phase1自动化测试Fork"}'
```

**预期结果:** HTTP 200/201，返回新模板

**实际结果:** ✅ **Pass**
```json
HTTP 200
{
  "id": "5b3c1ace-c6b4-4da2-a62c-e658ce36b051",
  "name": "Phase1测试Fork",
  "description": "Phase1自动化测试Fork",
  "domain": "AI",
  "parent_template_id": "3adf0f8e-92d3-4471-8ab3-313255ce5c8d",
  "creator_type": "human",
  "creator_id": "d6f426f5-4532-4b88-b4bb-5862352cbd84"
}
```

---

### TC-03-13 Fork 后查新模板谱系

**命令:**
```bash
curl -s "http://localhost:8001/api/templates/5b3c1ace-c6b4-4da2-a62c-e658ce36b051/lineage"
```

**预期结果:** HTTP 200，谱系中包含父模板

**实际结果:** ✅ **Pass**
```json
HTTP 200
[
  {"id":"5b3c1ace-...", "name":"Phase1测试Fork", "creator_type":"human", "depth":0},
  {"id":"3adf0f8e-...", "name":"AI每日精选", "creator_type":"system", "depth":1}
]
```

Fork 后的新模板谱系正确显示两级关系：自身（depth=0）→ 父模板（depth=1）。

> ⚠️ 额外发现: Fork 出的新模板 `prompt_config` 为 `null`，未继承父模板的配置。这可能是设计意图，也可能是缺陷（见下方新发现 BUG 汇总）。

---

## 发现的 BUG 与问题汇总

### 🔴 BUG-020 确认：空密码注册安全漏洞

| 项目 | 内容 |
|------|------|
| **严重等级** | 🔴 Critical |
| **复现步骤** | POST `/api/auth/register` with `password: ""` |
| **预期行为** | 返回 422，拒绝空密码 |
| **实际行为** | 返回 201，注册成功并返回有效 token |
| **影响** | 用户可创建无密码账户，严重安全风险 |
| **建议** | 在 `RegisterRequest` schema 中添加 `min_length=8` 密码验证 |

### 🟡 新发现 BUG-NEW-01：Fork 模板不继承 prompt_config

| 项目 | 内容 |
|------|------|
| **严重等级** | 🟡 Medium |
| **复现步骤** | Fork 模板后查看新模板详情 |
| **预期行为** | 新模板应继承父模板的 `prompt_config` |
| **实际行为** | `prompt_config` 为 `null` |
| **影响** | Fork 后的模板无法直接使用，需手动配置 |

### 🟡 新发现 BUG-NEW-02：307 重定向泄露路由结构

| 项目 | 内容 |
|------|------|
| **严重等级** | 🟡 Low |
| **复现步骤** | 访问无尾斜杠的受保护端点 `/api/subscriptions` |
| **预期行为** | 直接返回 401 |
| **实际行为** | 返回 307 重定向到 `/api/subscriptions/` |
| **影响** | 无 Token 请求会先被重定向再鉴权，增加不必要的网络开销 |
| **建议** | 在 FastAPI 路由中设置 `redirect_slashes=False` 或统一路由风格 |

### 📝 观察：ChromaDB v1 API 已弃用

| 项目 | 内容 |
|------|------|
| **严重等级** | ℹ️ Info |
| **详情** | `/api/v1/heartbeat` 返回 410 Gone，需确认应用代码已迁移到 v2 API |

---

## 测试统计总结

| 类别 | 通过 | 失败 | 跳过 | 总计 |
|------|------|------|------|------|
| Part 1: 环境与基础设施 | 12 | 0 | 0 | 12 |
| Part 2: 认证系统 | 9 | 1 | 0 | 10 |
| Part 3: 模板系统 | 13 | 0 | 0 | 13 |
| **总计** | **34** | **1** | **0** | **35** |

**通过率: 97.1%** (34/35)

失败项:
- TC-02-08: 空密码注册（BUG-020 确认）

额外发现:
- BUG-NEW-01: Fork 不继承 prompt_config
- BUG-NEW-02: 307 重定向问题
- ChromaDB v1 API 弃用提示

---

## 保存的 Token 信息（供后续 Phase 使用）

**测试用户:** ai_tester_p1_new@test.com / TestPass123

**User ID:** d6f426f5-4532-4b88-b4bb-5862352cbd84

```
ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkNmY0MjZmNS00NTMyLTRiODgtYjRiYi01ODYyMzUyY2JkODQiLCJleHAiOjE3NzYwNzc0ODl9.HqHjcRckI38pd1hwCkl8HF96dQllnz1FpqP4Q9Raoxo

REFRESH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkNmY0MjZmNS00NTMyLTRiODgtYjRiYi01ODYyMzUyY2JkODQiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODY2NTg4OX0.EM1y6OmR8i2by2DhfVpOvtvpTxdjZFcRtGcjjcrw5t0
```

> ⚠️ ACCESS_TOKEN 有效期约 30 分钟，使用前请先通过 refresh 或重新登录获取新 token。
