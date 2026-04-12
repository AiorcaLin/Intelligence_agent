# 本地 Windows 无 Docker 可运行性评估（第 11 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：在 **本地 Windows** 上，**不使用 Docker**，本项目是否可以运行？  
**结论（摘要）**：**可以尝试，但比 Linux 无 Docker 更别扭**：**Redis** 在 Windows 上**没有**与 Linux 同等的官方原生支持路径；**PostgreSQL** 有官方 Windows 安装包；**Chroma** 可通过 Python 环境 **`chroma run`** 起服务；**Celery** 在 Windows 上仍建议 **`--pool=solo`**（见 `03`）。整体上 **不推荐** 作为首选，除非你刻意避免 Docker Desktop 的内存与 WSL2 开销。

---

## 1. 各组件在「无 Docker 的 Windows」上的现实情况

| 组件 | 无 Docker 时的常见做法 | 说明 |
|:---|:---|:---|
| **PostgreSQL** | 使用 **EDB 安装包**等官方渠道安装 Windows 版 | **参考**：[PostgreSQL Windows 下载](https://www.postgresql.org/download/windows/) **解释**：需自建库与账号，并与 `DATABASE_URL` 一致。 |
| **Redis** | **官方推荐路径**为在 **WSL2** 中安装 Linux 版 Redis，或使用 **托管 Redis / 兼容实现** | **参考**：[Redis 文档中关于在 Windows 上使用 Redis 的说明](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-windows/) **解释**：文档指向 **WSL2** 等路径，而非「单一官方 Windows 原生 redis-server」。若坚持纯 Windows 进程，需评估 **Memurai** 等兼容产品与 Celery 的协议兼容性（自行验证）。 |
| **Chroma** | 在 Python 虚拟环境中安装 `chromadb`，使用 **`chroma run`** 监听 **HTTP**（与 `HttpClient` 一致） | **参考**：[Chroma CLI — run](https://docs.trychroma.com/docs/cli/run) |
| **FastAPI / Celery / Next** | 与 `03-本地Windows可运行性评估.md` 相同；Celery 用 **`--pool=solo`** | — |

---

## 2. 与「无 Docker 的 Linux」（`10` 篇）相比

| 维度 | Windows 无 Docker | Linux 无 Docker |
|:---|:---|:---|
| **Redis** | 往往绕不开 **WSL2**、云服务或第三方兼容栈 | 发行版包即可，路径清晰 |
| **与「完全不用 WSL」** | 若你同时 **不用 Docker** 且 **不用 WSL**，Redis 会成为 **首要卡点** | 不涉及此矛盾 |

---

## 3. 与「Windows + Docker」相比

| 维度 | 无 Docker | Docker Desktop |
|:---|:---|:---|
| **依赖交付** | 手动安装、升级、端口、服务自启 | `compose` 一键对齐版本 |
| **内存** | 少 Docker 守护进程，但 **WSL2 仍可能被 Redis 路径引入** | Docker + WSL2 通常较重（见用户本机 16GB 占用场景） |

---

## 4. 总表

| 维度 | 判断 |
|:---|:---|
| **能否跑通** | **能**，但 **Redis 与 Chroma 的落地成本** 明显高于 Docker Compose。 |
| **是否推荐** | **不推荐作为默认**；若反感 Docker，优先考虑 **Linux 云机** 或 **WSL2 内全 Linux 栈**（见 `07`/`10`）。 |
| **不改代码** | 仍须满足 **HTTP 版 Chroma** 与 **Redis 可连**；`REDIS_URL` 可指向本机或远程。 |

---

## 5. 文件变更

- 新增：`docs/phased_documents/test_run/11-本地Windows无Docker可运行性评估.md`
