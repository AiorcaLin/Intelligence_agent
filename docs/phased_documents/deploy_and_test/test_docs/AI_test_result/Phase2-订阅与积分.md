# Phase 2 测试报告：订阅管理 + 积分系统

> **测试时间**：2026-04-13  
> **测试环境**：FastAPI 后端 http://localhost:8001  
> **测试用户**：phase2_v2@test.com（新注册干净用户）  
> **测试执行方式**：curl 命令行自动化

---

## Part 1: 订阅管理测试

### 1.1 创建订阅

| 编号 | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|------|------|-----------|------|----------|------|
| 01 | 空 body `{}` 创建订阅 — 验证默认值 | `curl -X POST /api/subscriptions/ -d '{}'` | 200/201，使用默认值创建 | **HTTP 422** — `{"detail":[{"type":"missing","loc":["body","domain"],"msg":"Field required","input":{}}]}` | **Fail** |
| 02 | 完整字段创建 | `curl -X POST /api/subscriptions/ -d '{"name":"我的AI订阅","domain":"AI","density_level":"standard","frequency":"daily","push_time_bucket":"09","formats":["text"]}'` | 201 创建成功 | **HTTP 201** — `{"id":"1dc19722-...","name":"我的AI订阅","domain":"AI","density_level":"standard","formats":["text"],"frequency":"daily","push_time_bucket":"09","is_active":true}` | **Pass** |
| 03 | Crypto 域创建 | `curl -X POST /api/subscriptions/ -d '{"domain":"Crypto","name":"加密货币追踪"}'` | 201 创建成功 | **HTTP 201** — `{"id":"6fc85d70-...","name":"加密货币追踪","domain":"Crypto","density_level":"standard","is_active":true}` | **Pass** |
| 04 | custom 域创建 | `curl -X POST /api/subscriptions/ -d '{"domain":"custom","name":"自定义领域"}'` | 201 创建成功 | **HTTP 201** — `{"id":"76b9b24f-...","name":"自定义领域","domain":"custom","density_level":"standard","is_active":true}` | **Pass** |
| 05 | 非法 domain: Finance | `curl -X POST /api/subscriptions/ -d '{"domain":"Finance"}'` | 400 拒绝 | **HTTP 400** — `{"detail":"无效的领域: Finance"}` | **Pass** |
| 06 | 非法 density_level: ultra | `curl -X POST /api/subscriptions/ -d '{"domain":"AI","density_level":"ultra"}'` | 400 拒绝 | **HTTP 400** — `{"detail":"无效的密度级别: ultra"}` | **Pass** |
| 07 | 非法 frequency: hourly | `curl -X POST /api/subscriptions/ -d '{"domain":"AI","frequency":"hourly"}'` | 400 拒绝 | **HTTP 400** — `{"detail":"无效的频率: hourly"}` | **Pass** |
| 08 | 非法 push_time_bucket: 07 | `curl -X POST /api/subscriptions/ -d '{"domain":"AI","push_time_bucket":"07"}'` | 400 拒绝 | **HTTP 400** — `{"detail":"无效的推送时段: 07"}` | **Pass** |

### 1.2 查询订阅

| 编号 | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|------|------|-----------|------|----------|------|
| 09 | GET 列出所有订阅 | `curl -X GET /api/subscriptions/` | 200，返回数组（含3条） | **HTTP 200** — 返回3条订阅记录的 JSON 数组 | **Pass** |
| 10 | GET 单条详情 | `curl -X GET /api/subscriptions/{id}` | 200，返回完整订阅对象 | **HTTP 200** — `{"id":"1dc19722-...","name":"我的AI订阅","domain":"AI",...}` | **Pass** |
| 11 | GET 不存在的 ID | `curl -X GET /api/subscriptions/00000000-0000-0000-0000-000000000000` | 404 | **HTTP 404** — `{"detail":"订阅不存在"}` | **Pass** |

### 1.3 更新订阅

| 编号 | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|------|------|-----------|------|----------|------|
| 12 | PUT 更新 name | `curl -X PUT /api/subscriptions/{id} -d '{"name":"更新后的AI订阅"}'` | 200，name 已更新 | **HTTP 200** — `{"name":"更新后的AI订阅",...}` | **Pass** |
| 13 | PUT 更新 density_level 为非法值 ultra（验证 BUG-012） | `curl -X PUT /api/subscriptions/{id} -d '{"density_level":"ultra"}'` | 应 400 拒绝 | **HTTP 200** — `{"density_level":"ultra",...}` ⚠️ 非法值被接受！ | **Fail** |
| 14 | PUT 更新 domain 为非法值 Finance（验证 BUG-012） | `curl -X PUT /api/subscriptions/{id} -d '{"domain":"Finance"}'` | 应 400 拒绝 | **HTTP 200** — `{"domain":"Finance",...}` ⚠️ 非法值被接受！ | **Fail** |

### 1.4 切换与删除

| 编号 | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|------|------|-----------|------|----------|------|
| 15 | PATCH toggle 停用 | `curl -X PATCH /api/subscriptions/{id}/toggle` | 200，is_active=false | **HTTP 200** — `{"is_active":false,...}` | **Pass** |
| 16 | PATCH toggle 恢复激活 | `curl -X PATCH /api/subscriptions/{id}/toggle` | 200，is_active=true | **HTTP 200** — `{"is_active":true,...}` | **Pass** |
| 17 | DELETE 删除订阅 | `curl -X DELETE /api/subscriptions/{id}` | 204 No Content | **HTTP 204** — 空响应体 | **Pass** |
| 18 | GET 确认已删除 | `curl -X GET /api/subscriptions/{id}` | 404 | **HTTP 404** — `{"detail":"订阅不存在"}` | **Pass** |

---

## Part 2: 积分系统测试

### 2.1 查询余额

| 编号 | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|------|------|-----------|------|----------|------|
| 19 | GET 新用户初始余额 | `curl -X GET /api/credits/balance` | 200，total_balance=0 | **HTTP 200** — `{"total_balance":0.0,"free_credits_remaining":50}` | **Pass** |
| 20 | 验证 free_credits_remaining=50 | （同上） | free_credits_remaining=50 | `"free_credits_remaining":50` ✅ | **Pass** |

### 2.2 充值（Mock）

| 编号 | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|------|------|-----------|------|----------|------|
| 21 | POST recharge tier=10 | `curl -X POST /api/credits/recharge -d '{"tier":10}'` | 200 + payment_url 含 mock:// | **HTTP 200** — `{"payment_url":"mock://payment/success?order=706073c3-...","order_id":"706073c3-..."}` | **Pass** |
| 22 | 查余额验证 +1000 | `curl -X GET /api/credits/balance` | total_balance=1000 | **HTTP 200** — `{"total_balance":1000.0,"free_credits_remaining":50}` | **Pass** |
| 23 | POST recharge tier=30 | `curl -X POST /api/credits/recharge -d '{"tier":30}'` | 200 + payment_url | **HTTP 200** — `{"payment_url":"mock://payment/success?order=6d943493-...","order_id":"6d943493-..."}` | **Pass** |
| 24 | 查余额验证累计 4500 | `curl -X GET /api/credits/balance` | total_balance=4500 | **HTTP 200** — `{"total_balance":4500.0,"free_credits_remaining":50}` | **Pass** |
| 25 | POST recharge tier=100 | `curl -X POST /api/credits/recharge -d '{"tier":100}'` | 200 + payment_url | **HTTP 200** — `{"payment_url":"mock://payment/success?order=d89c2233-...","order_id":"d89c2233-..."}` | **Pass** |
| 26 | 查余额验证累计 17500 | `curl -X GET /api/credits/balance` | total_balance=17500 | **HTTP 200** — `{"total_balance":17500.0,"free_credits_remaining":50}` | **Pass** |
| 27 | 非法 tier=50 | `curl -X POST /api/credits/recharge -d '{"tier":50}'` | 400 或 422 拒绝 | **HTTP 400** — `{"detail":"无效的充值档位: 50，可选: [10, 30, 100]"}` | **Pass** |

### 2.3 积分记录

| 编号 | 描述 | curl 命令 | 预期 | 实际响应 | 结果 |
|------|------|-----------|------|----------|------|
| 28 | GET /api/credits/records | `curl -X GET /api/credits/records` | 200，有充值记录 | **HTTP 500** — `Internal Server Error` | **Fail** |
| 29 | GET records?record_type=recharge 按类型过滤 | `curl -X GET /api/credits/records?record_type=recharge` | 200，过滤后的记录 | **HTTP 500** — `Internal Server Error` | **Fail** |
| 30 | GET records?page=1&size=1 分页测试 | `curl -X GET /api/credits/records?page=1&size=1` | 200，仅1条记录 | **HTTP 500** — `Internal Server Error` | **Fail** |
| 31 | GET /api/credits/earnings | `curl -X GET /api/credits/earnings` | 200，空列表 | **HTTP 200** — `{"items":[],"total":0,"page":1,"size":20}` | **Pass** |

---

## BUG 验证与新发现

### 已知 BUG 验证

#### BUG-012：更新订阅时不校验枚举值 — ✅ 已确认复现

| 验证项 | 创建接口行为 | 更新接口行为 | 结论 |
|--------|-------------|-------------|------|
| 非法 domain "Finance" | HTTP 400 正确拒绝 | HTTP 200 ⚠️ 接受了非法值 | **BUG 确认** |
| 非法 density_level "ultra" | HTTP 400 正确拒绝 | HTTP 200 ⚠️ 接受了非法值 | **BUG 确认** |

**分析**：创建接口（POST）对 domain、density_level、frequency、push_time_bucket 均有严格的枚举校验，但更新接口（PUT）完全缺失校验逻辑，允许任意非法值写入数据库。这会导致数据一致性问题，后续使用这些脏数据的下游服务可能异常。

### 新发现 BUG

#### NEW-BUG-P2-001：创建订阅的 domain 字段应有默认值但实际为必填

- **严重程度**：低
- **描述**：用例 01 使用空 body `{}` 创建订阅，期望系统提供默认值（类似其他字段如 density_level、frequency 等有默认值），但 domain 字段是 required，返回 422。
- **影响**：这可能是设计意图（domain 确实应该是必填），但与"最简创建"的预期不完全一致。如果是设计意图则为 Pass，否则需要补充默认值。
- **建议**：确认产品需求 — domain 是否应有默认值（如 "AI"）。

#### NEW-BUG-P2-002：积分记录接口 /api/credits/records 返回 500 内部服务器错误

- **严重程度**：🔴 严重（Critical）
- **描述**：`GET /api/credits/records` 接口在所有调用场景下均返回 HTTP 500 Internal Server Error，包括：
  - 无参数调用
  - 带 record_type=recharge 过滤
  - 带 page/size 分页参数
- **影响**：用户完全无法查看自己的积分变动记录（充值、消费等），影响核心功能可用性。
- **可能原因**：后端代码在查询积分记录时可能存在序列化错误、数据库查询异常、或模型字段映射问题。
- **注意**：`/api/credits/earnings` 接口正常返回 200，说明类似的分页查询框架本身可用，问题可能出在 records 特有的逻辑或数据模型上。

---

## 测试统计汇总

| 类别 | 总用例 | Pass | Fail | 通过率 |
|------|--------|------|------|--------|
| 订阅管理 — 创建 | 8 | 7 | 1 | 87.5% |
| 订阅管理 — 查询 | 3 | 3 | 0 | 100% |
| 订阅管理 — 更新 | 3 | 1 | 2 | 33.3% |
| 订阅管理 — 切换与删除 | 4 | 4 | 0 | 100% |
| 积分系统 — 余额 | 2 | 2 | 0 | 100% |
| 积分系统 — 充值 | 7 | 7 | 0 | 100% |
| 积分系统 — 记录 | 4 | 1 | 3 | 25% |
| **合计** | **31** | **25** | **6** | **80.6%** |

### 失败用例归因

| 失败用例 | 归因 |
|----------|------|
| 01 | domain 字段为必填（可能为设计意图，待确认） |
| 13, 14 | **BUG-012** — 更新接口缺失枚举校验 |
| 28, 29, 30 | **NEW-BUG-P2-002** — /api/credits/records 接口 500 错误 |

### 风险评估

1. **BUG-012（更新不校验枚举）**：中风险。允许脏数据写入可能导致下游服务崩溃或逻辑异常。修复建议：在 PUT 更新逻辑中复用创建时的枚举校验函数。
2. **NEW-BUG-P2-002（积分记录500）**：高风险。核心功能完全不可用，用户无法审计积分流水。需紧急排查后端日志定位根因。
