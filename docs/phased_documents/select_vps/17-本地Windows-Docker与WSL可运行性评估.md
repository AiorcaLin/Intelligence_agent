# 本地 Windows + Docker + WSL 可运行性评估（第 17 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：在 **本地 Windows** 上，**使用 Docker** 且环境涉及 **WSL**，本项目是否可以运行？  
**结论（摘要）**：**可以**。在当代 Windows 上，**Docker Desktop 的推荐后端就是 WSL 2**——二者通常是 **同一条技术路径**（Docker 在 WSL2 提供的 Linux 内核上跑容器），而不是「Docker 与 WSL 两套互相冲突的虚拟化」。另有一条进阶路径是在 **WSL 发行版内直接安装 Docker Engine**（可不装 Docker Desktop），同样能跑 `docker compose`，但运维责任更大。

---

## 1. 关系说明（避免概念混淆）

| 模式 | 说明 |
|:---|:---|
| **Docker Desktop + WSL 2 后端（常见）** | Docker Desktop 使用 WSL2 运行 Linux 容器引擎；可在设置中启用 **WSL 集成**，在 Ubuntu 等发行版终端里直接使用 `docker`。**参考**：[Docker Desktop WSL 2 backend](https://docs.docker.com/desktop/features/wsl/) **解释**：这是微软与 Docker 文档共同描述的主流方案。 |
| **在 WSL 内安装 Docker Engine（无 Desktop）** | 适合想减少 Desktop 组件的用户；需自行维护 `docker` 服务与更新。**参考**：[Microsoft Learn — WSL 上的容器入门](https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers) |

**与 `14-本地Windows含Docker可运行性评估.md` 的关系**：`14` 已说明「Windows + Docker」可行；本篇明确 **WSL2 往往是 Docker 的承载层**，不是额外再叠一层冲突栈。

---

## 2. 与本项目相关的注意点

| 点 | 说明 |
|:---|:---|
| **容器内依赖** | `docker-compose` 起的 **Postgres / Redis / Chroma** 行为与 Linux 一致（见 `14`）。 |
| **仓库放哪** | 若项目在 **`C:\`** 等 NTFS 路径，经 WSL 访问有时 **IO 偏慢**；将仓库放在 **WSL 文件系统**（如 `\\wsl$\Ubuntu\home\...`）常更利于 `npm install` / `git`。**解释**：属 Windows/WSL 通用实践，非本项目独有。 |
| **内存** | **WSL2 + Docker + 多容器** 会占用 **可观 RAM**；可在用户目录配置 **`.wslconfig`** 限制 `memory`，避免拖垮 Windows（具体键名以微软文档为准）。**参考**：[WSL 配置](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) |
| **Celery** | Worker 若在 **Linux 容器**内运行，按 Linux 规则（见 `14`）。 |

---

## 3. 总表

| 维度 | 判断 |
|:---|:---|
| **能否跑通** | **能**；与「仅 Docker Desktop」本质一致，只是明确了 **WSL2 的角色**。 |
| **主要风险** | **整机内存** 与 **跨文件系统 IO**（仓库位置）。 |
| **是否必须同时装「Docker + 独立 WSL 里再装一套数据库」** | **不必**；除非你有意 **在 WSL 里原生跑** Postgres 而不用容器——那是另一条路径（与 `11` 混合）。 |

---

## 4. 文件变更

- 新增：`docs/phased_documents/test_run/17-本地Windows-Docker与WSL可运行性评估.md`
