# 本地 Windows 可运行性评估（第 3 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：当前项目是否可以在 **本地 Windows** 上运行？  
**结论（摘要）**：**可以**，用于开发与验证「能否跑通」是可行的；但 **Celery 在 Windows 上需改用非 prefork 并发池**，且 **README 中的部分启动命令与包结构不一致**，应从**仓库根目录**按 `backend.*` 模块方式启动（见第 4 节）。完整生产级 Worker 仍更推荐 **Linux 云主机**（与第 `02` 篇一致）。

---

## 1. 技术栈与 Windows 的匹配度

| 组件 | Windows 上情况 |
|:---|:---|
| **Docker Desktop**（Postgres / Redis / Chroma） | 官方支持；现代安装通常依赖 **WSL2** 作为后端。**解释**：容器内服务为 Linux 镜像，与宿主机是否为 Windows 无关，由 Docker 提供 Linux 容器运行时。**参考**：[Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/)（系统要求与 WSL2 说明以该页为准）。 |
| **Python / FastAPI / Uvicorn** | 官方支持 Windows；无平台性阻碍。 |
| **Node.js / Next.js** | 官方支持 Windows；`next dev` / `next build` 在 Windows 上常用。 |
| **Celery Worker** | **关键差异点**：默认 **prefork** 池依赖类 Unix 的 `fork` 语义；在 Windows 上应使用 **`solo`**（或 `threads` 等）而非默认 prefork。**解释**：Celery 文档在 Workers 指南中列出各能力对 **pool** 的支持，其中 **`solo` pool** 为阻塞、单任务串行模型，适合本机调试。**参考**：[Workers Guide — Concurrency](https://docs.celeryq.dev/en/stable/userguide/workers.html)（文中对 `solo` pool 行为有说明）。 |

---

## 2. 资源（与你机器是否「够跑」）

在 **单人、开发、不开视频** 的前提下，本地 Windows 与云服务器结论一致：**内存往往是第一瓶颈**（Docker 三容器 + IDE + 浏览器 + `next build` 峰值）。

- **Next.js**：构建阶段内存峰值可能明显高于运行期；官方对内存行为有专门说明。**参考**：[Next.js — Memory Usage](https://nextjs.org/docs/app/guides/memory-usage)。  
- **PostgreSQL**：轻载下调参随数据量增长再考虑。**参考**：[PostgreSQL — Resource Consumption](https://www.postgresql.org/docs/current/runtime-config-resource.html)。  

**粗建议**：**16 GB 系统内存** 的 Windows 笔记本/台式机更从容；**8 GB** 可尝试，但需接受 Docker/构建阶段更容易触顶、需要关其它重应用。

---

## 3. 网络（你在成都）

与 `02-资源评估-云服务器建议.md` 相同：运行依赖 **对外 HTTPS** 访问 **DeepSeek、OpenRouter、（默认嵌入）OpenAI** 等；与「是否在 Windows」无关，取决于你本机出口能否稳定访问这些端点。

---

## 4. 启动方式注意（仓库现状）

1. **工作目录与模块名**：后端代码普遍使用 `from backend.xxx` 导入，**应在仓库根目录**执行 Uvicorn，例如：  
   `uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload`  
   根目录 README 中 `cd backend` 后 `uvicorn main:app` 易与包布局不一致；项目内其它文档曾出现 `uvicorn backend.main:app` 写法，更一致。  
2. **Celery（Windows）**：在默认 prefork 不适用的环境下，使用例如：  
   `celery -A backend.tasks.celery_app worker --loglevel=info --beat --pool=solo`  
   （具体 `-A` 路径以你在根目录下能 `python -c "import backend.tasks"` 为准。）  
3. **Alembic / 数据库名**：`backend/alembic.ini` 中示例库名与 `.env.example` 可能不一致，迁移前请与 `DATABASE_URL` 对齐，避免「库连上了但迁移打在别的库名上」。

---

## 5. 总表：能否在本地 Windows 跑？

| 维度 | 判断 |
|:---|:---|
| **能否跑通（开发验证）** | **能**，需 Docker Desktop + Python + Node，并按上节处理 Celery 与启动路径。 |
| **是否与 Linux 完全一致** | **Worker 并发模型不同**（solo 偏串行）；极端并发行为以 Linux prefork 为准。 |
| **是否推荐长期生产部署在 Windows Server** | **一般不推荐**作为 Celery 主力 Worker 环境；应用与任务队列更适合 Linux 云主机。 |

---

## 6. 文件变更

- 新增：`docs/phased_documents/test_run/03-本地Windows可运行性评估.md`
