# Linux 云服务器可运行性评估（第 6 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：当前项目是否可以在 **Linux 云服务器**上运行？  
**结论（摘要）**：**可以**，且 **Linux 是本项目最「对味」的运行环境**：Docker 官方引擎、PostgreSQL、Redis、Celery **prefork** Worker、常见部署文档均以 Linux 为一类事实标准；与 `03-本地Windows可运行性评估.md` 相比，**无需**为 Celery 单独处理 `--pool=solo` 一类平台特例（除非你愿意）。

---

## 1. 为何 Linux 云主机特别适合本仓库

| 组件 | Linux 上情况 |
|:---|:---|
| **Docker / containerd** | 云主机普遍预装或一键安装 **Docker Engine**；无 Desktop 虚拟化层，资源路径清晰。**参考**：[Docker Engine 概览](https://docs.docker.com/engine/) **解释**：服务端交付常用 Linux + Engine，与 `docker-compose.yml` 中镜像（Postgres、Redis、Chroma）一致。 |
| **Celery** | 默认 **prefork** 池在类 Unix 上可用，与生产常见配置一致。**参考**：[Celery Workers Guide](https://docs.celeryq.dev/en/stable/userguide/workers.html) |
| **Python / Node** | 发行版包管理器或官方二进制安装均可；无 Windows 路径与编码历史包袱。 |
| **systemd** | 可用 **systemd unit** 或 **supervisor** 托管 `uvicorn`、`celery`、`next start`，进程守护成熟。 |

---

## 2. 与「能否跑通」相关的实操注意（与平台无关，但 Linux 上同样要做）

1. **启动路径**：后端使用 `from backend.xxx`，建议在**项目根目录**执行 `uvicorn backend.main:app ...`（与 `03` / `04` 中说明一致）。  
2. **环境变量**：`.env` 或 systemd `EnvironmentFile=` 注入 `DATABASE_URL`、`CELERY_*`、各 API Key。  
3. **出站网络**：云安全组放行 **出站 HTTPS**，以访问 DeepSeek、（若使用）OpenRouter/嵌入服务等；与 `02-资源评估-云服务器建议.md` 一致。  
4. **防火墙**：除业务需要外，**勿把 Postgres/Redis/Chroma 端口公网暴露**；仅 SSH 与反向代理（80/443）按需开放。

---

## 3. 资源（单人、验证跑通）

结论与 `02` 篇对齐，此处仅强调 **Linux 不会 magically 省内存**：

- **约 4 GB**：偏紧，适合极简或分拆服务。  
- **约 8 GB**：单人全栈（Docker 三服务 + 后端 + Celery + 前端）较稳妥。  

磁盘建议 **≥ 40–60 GB** SSD，留日志与数据库增长余量。

---

## 4. 发行版与内核

- **Ubuntu LTS**、**Debian**、**Alma/Rocky** 等均可；优先选 **长期支持版本** 与云厂商维护良好的镜像。  
- 内核需满足 Docker 与 **overlay 存储驱动** 要求（主流云镜像已满足）。

---

## 5. 总表

| 维度 | 判断 |
|:---|:---|
| **能否在云服务器 Linux 上跑通** | **能**，且为推荐路径。 |
| **相对 Windows / Mac 本机** | **更少 Celery/路径层面的摩擦**；主要剩资源与网络配置。 |
| **相对 Mac Apple Silicon** | **无 ARM 镜像兼容性顾虑**（常见云机为 **x86_64**）。 |

---

## 6. 文件变更

- 新增：`docs/phased_documents/test_run/06-Linux云服务器可运行性评估.md`
