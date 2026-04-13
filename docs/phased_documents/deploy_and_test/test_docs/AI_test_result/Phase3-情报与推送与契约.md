# Phase 3 测试报告：情报生成与报告 + 推送系统 + 前后端契约验证

> **测试时间**：2026-04-13  
> **测试环境**：FastAPI 后端 http://localhost:8001，前端 http://localhost:3000  
> **测试账号**：phase3_tester@test.com / TestPass123  
> **User ID**：f587f4ad-97be-45c2-a5d2-a390cbaef4c3  
> **测试报告 ID**：70ec7dab-986b-40ff-8386-5eff2ac8e6ad  
> **订阅 ID**：077fadeb-ceb5-4c0a-b4c4-1852c4fd780a  

---

## 前置步骤执行记录

| 步骤 | 操作 | 结果 |
|------|------|------|
| 1 | 注册 phase3_tester@test.com | 用户已存在，改用 login 获取 token ✅ |
| 2 | 创建订阅（AI域，standard密度） | 201 创建成功，SUB_ID=077fadeb... ✅ |
| 3 | 获取模板列表，取 AI每日精选 ID | TPL_ID=3adf0f8e... ✅ |
| 4 | 手动插入测试报告到 intel_reports | INSERT 0 1 成功 ✅（需修正 formats_generated 为 `ARRAY['text']::varchar[]`） |

---

## Part 1：情报系统测试 (06)

### 1.1 情报查询接口

| # | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|---|------|-----------|------|----------|------|
| 01 | GET /api/intel/today | `curl GET /api/intel/today` | 200，返回今日报告列表 | **HTTP 500** — `Internal Server Error`。后端日志：`pydantic_core ValidationError: ReportResponse.created_at Input should be a valid string, input_type=datetime` | **Fail** ⚠️ |
| 02 | GET /api/intel/list | `curl GET /api/intel/list` | 200，返回分页列表 | **HTTP 500** — 同上 `created_at` datetime→string 验证失败 | **Fail** ⚠️ |
| 03 | GET /api/intel/list?domain=AI | `curl GET /api/intel/list?domain=AI` | 200，按域筛选 | **HTTP 500** — 同上序列化错误 | **Fail** ⚠️ |
| 04 | GET /api/intel/{report_id} | `curl GET /api/intel/70ec7dab-...` | 200，返回报告详情 | **HTTP 500** — 同上序列化错误 | **Fail** ⚠️ |
| 05 | GET /api/intel/{report_id}/history | `curl GET /api/intel/70ec7dab-.../history` | 200，历史列表（可能为空） | **HTTP 200** — `[]`（空数组，因 embedding_id 为 null） | **Pass** ✅ |
| 06 | GET /api/intel/{nonexistent_id} | `curl GET /api/intel/00000000-...` | 404 | **HTTP 404** — `{"detail":"报告不存在"}` | **Pass** ✅ |

#### 根因分析（NEW-BUG-001）

`ReportResponse` Pydantic 模型定义 `created_at: str | None`，但 SQLAlchemy ORM 返回的 `IntelReport.created_at` 是 `datetime` 对象。`model_validate(r)` 时 Pydantic 严格校验 string 类型，导致 500。

**影响范围**：所有返回 `ReportResponse` 的端点（/today、/list、/{id}、/regenerate）

**修复建议**：将 `created_at` 类型改为 `datetime | None` 或添加 `@field_serializer` 将 datetime 转为 ISO 字符串。

---

### 1.2 报告再生成与反馈

| # | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|---|------|-----------|------|----------|------|
| 07 | POST regenerate（BUG-010 验证） | `curl POST /api/intel/{id}/regenerate -d '{"feedback_text":"请增加更多技术细节"}'` | 200 并返回新报告 | **HTTP 500** — 同 NEW-BUG-001 序列化错误。但源码审查确认 BUG-010：`regenerate_report` 方法直接复制 `original.items` 和 `original.action_items`，未调用任何 AI 服务 | **Fail** ⚠️ |
| 08 | 再生成后余额变化 | 查看 /api/credits/balance | 应扣 10 积分 | 余额不变（1000.0→1000.0），因 500 导致事务回滚，未执行扣费。源码确认扣费金额为 `estimated_cost = 10.0` | **Fail**（无法验证） |
| 09 | POST feedback 标记重要 | `curl POST /api/intel/{id}/items/0/feedback -d '{"is_important":true}'` | 200 | **HTTP 200** — `{"ok":true}` | **Pass** ✅ |
| 10 | POST feedback 取消标记 | `curl POST /api/intel/{id}/items/0/feedback -d '{"is_important":false}'` | 200 | **HTTP 200** — `{"ok":true}` | **Pass** ✅ |
| 11 | 连续再生成 4 次，第 4 次应 429 | 循环调 regenerate 4 次 | 前 3 次 200，第 4 次 429 | 全部 **HTTP 500** — 因序列化 Bug，无法验证速率限制。源码审查确认限制逻辑存在：`if regen_count >= 3: raise 429` | **Fail**（无法验证） |

#### BUG-010 验证结论

通过源码审查确认：`IntelService.regenerate_report()` 方法（`intel_service.py:128-141`）仅执行：
```python
new_report = IntelReport(
    items=original.items,           # 直接复制
    action_items=original.action_items,  # 直接复制
    title=f"{original.title} (重新生成)",
    is_regenerated=True,
    ...
)
```
**未调用任何 AI 模型**，`feedback_text` 参数被完全忽略。BUG-010 确认存在。

---

## Part 2：推送系统测试 (07)

| # | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|---|------|-----------|------|----------|------|
| 12 | GET /api/push/status（无推送） | `curl GET /api/push/status` | 200，空数组 | **HTTP 500** — `PushStatusResponse.sent_at` datetime→string 序列化失败（同类 Bug） | **Fail** ⚠️ |
| 13 | POST /api/push/test web 渠道 | `curl POST /api/push/test -d '{"report_id":"...","channels":["web"]}'` | 200 推送成功 | **HTTP 200** — `{"ok":true,"message":"推送已发起"}`。DB 记录 channel=web, status=sent | **Pass** ✅ |
| 14 | POST /api/push/test email 渠道 | `curl POST /api/push/test -d '{"report_id":"...","channels":["email"]}'` | 200 推送成功 | **HTTP 200** — `{"ok":true,"message":"推送已发起"}`。DB 记录 channel=email, status=sent | **Pass** ✅ |
| 15 | POST /api/push/test sms 未知渠道 | `curl POST /api/push/test -d '{"report_id":"...","channels":["sms"]}'` | 应返回 400 或明确告知渠道不支持 | **HTTP 200** — `{"ok":true,"message":"推送已发起"}`，但 DB 记录 status=failed, error_msg="未知推送渠道: sms" | **Fail** ⚠️ |
| 16 | POST /api/push/test 多渠道 | `curl POST /api/push/test -d '{"report_id":"...","channels":["web","email"]}'` | 200 推送成功 | **HTTP 200** — `{"ok":true,"message":"推送已发起"}`。DB 两条记录均为 sent | **Pass** ✅ |
| 17 | GET /api/push/status（推送后） | `curl GET /api/push/status` | 200，显示推送日志 | **HTTP 500** — 同 #12 序列化错误。**另外**：源码审查发现查询条件 `PushLog.sent_at >= today_start` 排除了所有 `sent_at IS NULL` 的记录（即 pending/failed），确认 **BUG-019** | **Fail** ⚠️ |
| 18 | 推送不存在的 report_id | `curl POST /api/push/test -d '{"report_id":"00000000-...","channels":["web"]}'` | 应返回 404 | **HTTP 500** — FK 约束违反导致 DB 错误，未被捕获为友好的 404 | **Fail** ⚠️ |

#### BUG-019 验证结论

通过源码审查确认：`PushService.get_push_status()` 查询条件为 `PushLog.sent_at >= today_start`，这会排除所有 `sent_at IS NULL` 的记录（pending 和 failed 记录均无 sent_at 值）。**BUG-019 确认存在**。

#### NEW-BUG-002：推送失败静默吞没

`push_report` 方法中 `_send` 异常被 catch 后仅写入 DB 日志，但 API 层面始终返回 `{"ok":true}`，不告知客户端推送失败。

#### NEW-BUG-003：推送不验证 report_id 存在性

`push_report` 不检查 report_id 是否存在就直接创建 push_log 记录，不存在的 report_id 触发 FK 约束导致 500 而非 404。

#### NEW-BUG-004：推送状态查询序列化错误

`PushStatusResponse.sent_at` 定义为 `str | None`，但 DB 返回 `datetime`。同 NEW-BUG-001 同类问题。

---

## Part 3：前后端契约关键验证 (09)

| # | 描述 | 测试方式 | 预期 | 实际 | 对应契约ID | 结果 |
|---|------|----------|------|------|-----------|------|
| 19 | 前端路径 /api/intel/reports/today vs 后端 /api/intel/today | 分别 curl 两个路径 | 前端路径 404 | 前端路径 **404** `{"detail":"Not Found"}`；后端路径 **500**（序列化 Bug，但路由存在） | **C-003** 确认 | **Fail** |
| 20 | 模板列表响应结构 | `GET /api/templates/` | 前端期望直接数组 | 返回 `{items:[...], total:9, page:1, size:20}` 包装对象 | **C-011** 确认 | **Fail** |
| 21 | 余额字段名检查 | `GET /api/credits/balance` | 前端读 `balance` / `freeRemaining` | 返回 `total_balance` / `free_credits_remaining` | **C-020, C-021** 确认 | **Fail** |
| 22 | 充值 tier 字符串 | `POST /api/credits/recharge -d '{"tier":"basic"}'` | 前端传字符串 | **HTTP 422** — `"Input should be a valid integer, unable to parse string as an integer"` | **C-022** 确认 | **Fail** |
| 23 | 记录查询 limit vs size | `GET /api/credits/records?limit=20` 和 `?size=20` | 前端用 limit | 两者均 **HTTP 500**（created_at 序列化 Bug）。源码确认后端参数名为 `size`，`limit` 被忽略 | **C-025** 确认 | **Fail** |
| 24 | 前端字段名创建订阅 | `POST /api/subscriptions/ -d '{"density":"brief","pushTime":"09:00"}'` | 后端应拒绝或识别 | **HTTP 201** — 前端字段 `density`/`pushTime` 被静默忽略，使用默认值 `density_level=standard`, `push_time_bucket=09` | **C-014, C-017** 确认 | **Fail** |

### 契约不一致验证汇总

| 契约 ID | 状态 | 验证结果 |
|---------|------|----------|
| C-003 | 🔴 路径不匹配 | **确认**：`/intel/reports/today` → 404，后端为 `/intel/today` |
| C-011 | 🟡 结构不匹配 | **确认**：模板返回 `{items, total, page, size}` 而非直接数组 |
| C-014 | 🟠 字段名 | **确认**：前端 `density` 被忽略，后端期望 `density_level` |
| C-017 | 🟠 字段名+格式 | **确认**：前端 `pushTime:"09:00"` 被忽略，后端期望 `push_time_bucket:"09"` |
| C-020 | 🟠 字段名 | **确认**：后端返回 `total_balance`，前端读 `balance` |
| C-021 | 🟠 字段名 | **确认**：后端返回 `free_credits_remaining`，前端读 `freeRemaining` |
| C-022 | 🔵 类型不匹配 | **确认**：后端期望 `tier: int`，前端传 `tier: string` → 422 |
| C-025 | 🟠 参数名 | **确认**：后端使用 `size` 参数，前端传 `limit` 被忽略 |

---

## Part 4：补充发现

### 4.1 安全测试

| # | 描述 | 测试数据 | 预期 | 实际响应 | 结果 |
|---|------|----------|------|----------|------|
| 25 | SQL 注入 | name: `'; DROP TABLE users; --` | 注入无效 | **HTTP 201** — 字符串作为普通值存入。验证 users 表仍存在（12 条记录） | **Pass** ✅ |
| 26 | XSS 注入 | name: `<script>alert(1)</script>` | 应拒绝或转义 | **HTTP 201** — `<script>alert(1)</script>` 原样存入数据库，未做任何 HTML 转义或过滤 | **Warn** ⚠️ |
| 27 | 超长字段 | name: 1000 个 'A' 字符 | 应返回 400/422 长度校验 | **HTTP 500** — DB varchar(200) 约束溢出，后端无 Schema 层面的长度校验 | **Fail** ⚠️ |

#### NEW-BUG-005：存储型 XSS 风险

后端不对用户输入做 HTML 转义，`<script>alert(1)</script>` 原样存入。如果前端使用 `dangerouslySetInnerHTML` 或类似方式渲染，将触发 XSS。

**风险等级**：中（取决于前端是否转义渲染）  
**修复建议**：后端对所有用户文本输入进行 HTML 实体转义，或前端确保不使用 innerHTML 类渲染。

#### NEW-BUG-006：缺少输入长度校验

订阅 name 字段 DB 限制为 varchar(200)，但 Pydantic Schema `SubscriptionCreate` 无 `max_length` 校验。超长输入直接到达 DB 层导致 500。

**修复建议**：在 `SubscriptionCreate.name` 添加 `Field(max_length=200)`。

---

### 4.2 并发测试

| # | 描述 | 测试方式 | 预期 | 实际 | 结果 |
|---|------|----------|------|------|------|
| 28 | 同时 5 个充值请求 | 并行 curl 5 次 `{"tier":10}` | 余额增加 5×1000=5000 | 余额仅增加 1000（1000→2000），但 token_records 表有 5 条新记录共 5000 积分。DB 中 10 条总计 10000 积分，token_balance 仅 2000 | **Fail** 🔴 |

#### NEW-BUG-007：充值并发竞态导致积分丢失（严重）

**根因**：`CreditsService.add_credits()` 使用非原子的读-改-写模式：

```python
user = user_result.scalar_one()
user.token_balance = float(user.token_balance) + amount  # 经典竞态
```

5 个并发请求同时读取 `token_balance=1000`，各自计算 `1000+1000=2000`，最终写入 2000。实际丢失 4000 积分。

**数据证据**：
- `token_records` 表 recharge 记录：10 条，SUM(amount) = 10000
- `users.token_balance` = 2000
- 丢失积分：10000 - 2000 = **8000**

**风险等级**：🔴 严重（涉及资金安全）  
**修复建议**：使用 SQL 原子更新替代 ORM 读写：
```sql
UPDATE users SET token_balance = token_balance + :amount WHERE id = :user_id
```
或使用数据库行锁 `SELECT ... FOR UPDATE`。

---

## 已知 BUG 验证总结

| BUG ID | 描述 | 验证结果 |
|--------|------|----------|
| BUG-010 | regenerate 不调 AI，仅复制原报告 | **确认** ✅ — 源码 `intel_service.py:128-141` 直接复制 items/action_items，feedback_text 被忽略 |
| BUG-019 | push/status 不显示 pending/failed 记录 | **确认** ✅ — 查询条件 `sent_at >= today_start` 排除 sent_at=NULL 的记录 |

---

## 新发现问题清单

| ID | 严重等级 | 模块 | 描述 | 影响 |
|----|---------|------|------|------|
| **NEW-BUG-001** | 🔴 阻断 | Intel | `ReportResponse.created_at` 类型定义为 `str | None`，但 ORM 返回 `datetime`，Pydantic 校验失败导致所有情报查询接口 500 | /today、/list、/{id}、/regenerate 四个核心端点全部不可用 |
| **NEW-BUG-002** | 🟠 严重 | Push | 推送失败时 API 仍返回 `{"ok":true}`，不告知客户端失败 | 用户以为推送成功，实际已失败 |
| **NEW-BUG-003** | 🟠 严重 | Push | push_report 不验证 report_id 存在性，FK 约束报 500 而非 404 | 推送不存在的报告时用户看到不友好的错误 |
| **NEW-BUG-004** | 🔴 阻断 | Push | `PushStatusResponse.sent_at` 同类 datetime→string 序列化错误导致 /push/status 500 | 推送状态查询不可用 |
| **NEW-BUG-005** | 🟡 中等 | 通用 | 用户输入未做 HTML 转义，`<script>` 标签原样存入 DB | 潜在存储型 XSS 风险 |
| **NEW-BUG-006** | 🟡 中等 | Subscription | Pydantic Schema 缺少 name 字段长度校验，超 varchar(200) 限制后 500 | 用户输入超长文本时崩溃 |
| **NEW-BUG-007** | 🔴 严重 | Credits | `add_credits()` 非原子读写导致并发充值积分丢失 | 并发 5 次充值只有 1 次生效，资金安全问题 |

---

## 统计总结

### 测试用例统计

| 类别 | 总计 | Pass | Fail | Warn | 无法验证 |
|------|------|------|------|------|---------|
| Part 1: 情报系统 | 11 | 3 | 6 | 0 | 2 |
| Part 2: 推送系统 | 7 | 3 | 4 | 0 | 0 |
| Part 3: 契约验证 | 6 | 0 | 6 | 0 | 0 |
| Part 4: 补充发现 | 4 | 1 | 2 | 1 | 0 |
| **合计** | **28** | **7** | **18** | **1** | **2** |

**通过率**：7/28 = **25.0%**

### 问题严重度分布

| 等级 | 数量 | 说明 |
|------|------|------|
| 🔴 阻断/严重 | 3 | NEW-BUG-001（情报序列化）、NEW-BUG-004（推送序列化）、NEW-BUG-007（并发积分丢失） |
| 🟠 严重 | 2 | NEW-BUG-002（推送失败静默）、NEW-BUG-003（推送不验证报告） |
| 🟡 中等 | 2 | NEW-BUG-005（XSS 风险）、NEW-BUG-006（长度校验缺失） |
| 已知确认 | 2 | BUG-010（再生成不调 AI）、BUG-019（状态不显示 failed） |
| 契约不一致 | 8 | C-003、C-011、C-014、C-017、C-020、C-021、C-022、C-025 已验证确认 |

---

## 修复建议（按优先级排序）

### P0 — 立即修复

1. **NEW-BUG-001 + NEW-BUG-004**：将所有 Pydantic Response 模型中的 `created_at: str | None` 改为 `datetime | None`。涉及文件：
   - `backend/routers/intel.py` → `ReportResponse`
   - `backend/routers/push.py` → `PushStatusResponse`
   - `backend/routers/credits.py` → `TokenRecordResponse`（Phase 2 已发现同类问题）

2. **NEW-BUG-007**：`CreditsService.add_credits()` 和 `consume_credits()` 使用 SQL 原子更新：
   ```python
   from sqlalchemy import update
   await self.db.execute(
       update(User).where(User.id == user_id).values(
           token_balance=User.token_balance + amount
       )
   )
   ```

### P1 — 优先修复

3. **BUG-010**：`regenerate_report` 接入 AI 服务，或至少根据 feedback_text 做差异化处理。
4. **BUG-019**：`get_push_status` 查询改为 `PushLog.user_id == user_id`（去掉 sent_at 过滤），或改为过滤 `created_at >= today_start`。
5. **NEW-BUG-003**：`push_report` 先验证 report_id 存在，不存在时抛 404。
6. **NEW-BUG-002**：`test_push` 端点检查 push_log 状态，如有 failed 则在响应中告知。

### P2 — 正常修复

7. **NEW-BUG-006**：Pydantic Schema 加 `name: str = Field(max_length=200)`。
8. **NEW-BUG-005**：后端对用户文本输入进行 sanitize，或确认前端不使用 innerHTML。
9. **契约不一致 C-003~C-025**：按照 `09-前后端契约不一致汇总.md` 方案 A（修前端适配后端）执行统一修复。

---

## 附录：关键测试命令记录

### 前置数据插入 SQL（修正版）

```sql
INSERT INTO intel_reports (
    id, user_id, subscription_id, template_id,
    domain, title, items, density_level,
    formats_generated, is_regenerated, sources, action_items
) SELECT
    gen_random_uuid(), u.id, s.id, t.id,
    'AI', '测试报告 - AI每日精选 2026-04-13',
    '[{"title":"GPT-5正式发布","summary":"OpenAI发布GPT-5","importance_score":9.5},
      {"title":"DeepSeek开源V3","summary":"DeepSeek开源最新模型","importance_score":8.7}]'::json,
    'standard',
    ARRAY['text']::varchar[],   -- 注意：不能用 json 类型，必须用 varchar[]
    false,
    '[{"name":"TechCrunch","url":"https://tc.com"},{"name":"arXiv","url":"https://arxiv.org"}]'::json,
    '[{"action":"关注GPT-5 API","priority":"high"},{"action":"评估DeepSeek V3","priority":"medium"}]'::json
FROM users u, subscriptions s, templates t
WHERE u.email='phase3_tester@test.com'
AND s.user_id = u.id AND t.name='AI每日精选'
LIMIT 1;
```

### 并发测试证据

```
token_records 表：10 条 recharge 记录，SUM(amount) = 10000.00
users.token_balance = 2000.00
差额（丢失积分）= 8000.00
```
