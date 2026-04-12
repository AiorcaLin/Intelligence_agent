# 本地 Linux 无 Docker 可运行性评估（第 10 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：在 **本地 Linux 机器**上，**不使用 Docker**，本项目是否可以运行？  
**结论（摘要）**：**可以**，但运维复杂度 **明显高于** `docker-compose` 一键起栈；你需要自行安装并维护 **PostgreSQL、Redis、Chroma 服务端** 及与版本、端口、系统服务（systemd）相关的配置。当前代码通过 **`chromadb.HttpClient` 连接 Chroma**，因此 **必须** 有可达的 **Chroma HTTP 服务**（与是否用 Docker 无关）。

---

## 1. 无 Docker 时各组件如何满足

| 组件 | 无 Docker 时的常见做法 | 说明 |
|:---|:---|:---|
| **PostgreSQL** | 发行版包管理器或官方仓库安装 **PostgreSQL 16**（或与迁移兼容的主版本） | **参考**：[PostgreSQL Linux downloads](https://www.postgresql.org/download/linux/) **解释**：需自建库、用户、监听地址，并与 `DATABASE_URL` 一致。 |
| **Redis** | 包管理器或源码安装 **Redis 7.x**（或与客户端兼容版本） | **参考**：[Redis 安装文档](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) |
| **Chroma** | 使用 **`chroma run`**（随 `chromadb` 包提供）在指定 `--host` / `--port` 上启动服务端，数据目录用 `--path` 持久化 | **参考**：[Chroma CLI — run](https://docs.trychroma.com/docs/cli/run) **解释**：本项目使用 `HttpClient(host, port)`，对应官方 **Client-Server** 模式；与 [Chroma 部署相关说明](https://docs.trychroma.com/guides/deploy/client-server-mode) 一致（若链接变更以官网为准）。 |
| **FastAPI / Celery / Next** | 与 `07-本地Linux可运行性评估.md` 相同：虚拟环境 + `uvicorn` + `celery` + `npm` | 无 Docker 时不改变 Python/Node 需求。 |

---

## 2. 与「使用 Docker」相比的利弊

| 维度 | 无 Docker | 使用 Docker Compose |
|:---|:---|:---|
| **可重复性** | 依赖你记录的安装步骤与版本，**环境漂移**风险更大 | 镜像版本钉死，**更接近「换机可复现」** |
| **端口与冲突** | 需自己保证 **5432 / 6379 / 8000**（Chroma）等不与其它服务冲突 | `compose` 中已映射，冲突相对直观 |
| **资源隔离** | 进程直接跑在宿主机，**少一层** cgroup 隔离 | 容器有边界，便于限额与迁移 |
| **学习成本** | 需熟悉 **Linux 服务管理、PG 调优入门、Chroma 持久化路径** | 主要学 Docker 与 compose |

---

## 3. 特别注意事项（针对本仓库）

1. **Chroma 端口**：默认文档中 Chroma 常用 **8000**；后端 README 中 API 常用 **8001**，需避免与系统上其它占用 8000 的进程冲突。  
2. **数据库名**：`alembic.ini` / `.env` / 实际创建的 PostgreSQL 库名需一致（见 `03` / `05` 篇）。  
3. **不修改代码**的前提下：**不能**把 `HttpClient` 换成嵌入式 Chroma 而不改 `embedding.py`；无 Docker 时仍应 **启动 Chroma 服务端**。

---

## 4. 总表

| 维度 | 判断 |
|:---|:---|
| **能否在无 Docker 的本地 Linux 上跑通** | **能**，需手动安装 PG + Redis + Chroma Server + 应用进程。 |
| **是否推荐作为首选** | **更推荐 Docker**（或至少用 **docker-compose 只跑依赖**，应用在宿主机）以降低环境差异。 |
| **与 `07` 对比** | 操作系统仍是 Linux；**差异在依赖交付方式**（包管理 vs 容器）。 |

---

## 5. 文件变更

- 新增：`docs/phased_documents/test_run/10-本地Linux无Docker可运行性评估.md`
