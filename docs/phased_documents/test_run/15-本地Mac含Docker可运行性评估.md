# 本地 Mac + Docker 可运行性评估（第 15 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：在 **本地 Mac** 上，**使用 Docker**（Docker Desktop 或同类），本项目是否可以运行？  
**结论（摘要）**：**可以**。这是 Mac 上 **推荐** 的依赖交付方式之一：`docker-compose` 中的 **Postgres / Redis / Chroma** 与仓库一致；容器内为 **Linux**，与 `06`/`07` 行为对齐；**Celery 若在 Linux 容器内运行**，并发模型与 Linux 生产环境一致（与 `04` 中「宿主机上 prefork 默认可用」并行不悖——取决于 Worker 跑在 **宿主机** 还是 **容器**）。主要注意 **Apple Silicon 架构** 与 **整机内存**（见第 2 节）。

---

## 1. 技术路径说明

| 组件 | Mac + Docker 下的常见形态 |
|:---|:---|
| **Docker Desktop for Mac** | 支持 **Intel** 与 **Apple Silicon**；安装与要求以官方为准。**参考**：[Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/) **解释**：通过轻量 Linux VM 跑容器，与 Windows 上 Docker Desktop 类似，都是「Mac 上跑 Linux 容器」。 |
| **`docker-compose.yml`** | 与本仓库一致；镜像需支持 **linux/arm64**（Apple Silicon）或 **amd64**（Intel），多数官方镜像为多架构。**参考**：[Docker multi-platform](https://docs.docker.com/build/building/multi-platform/) **解释**：若 `pull` 失败或运行异常，需核对镜像架构与平台。 |
| **后端 / Celery / Next** | README 常见为 **宿主机** 跑 Python/Node + **仅依赖容器化**；亦可进一步全容器化（需额外 Dockerfile）。 |

---

## 2. Apple Silicon（M 系列）与资源

- **镜像**：多数官方镜像提供 **arm64**；若某镜像仅 **amd64**，可能通过模拟运行，**性能与内存** 可能更差。  
- **内存**：Docker Desktop + 三容器 + IDE + 浏览器；**8 GB 统一内存** 机型常偏紧，**16 GB 及以上** 更从容（与 `04`/`05` 一致）。  
- **`next build`**：在 **宿主机**执行时仍可能产生 **高内存峰值**（与平台无关）。

---

## 3. 与 `04`（Mac 无 Docker）的关系

| 点 | 说明 |
|:---|:---|
| **依赖安装** | 用 Docker 后，**不必**在 Mac 上分别用 Homebrew 装 Postgres/Redis 并手动维护版本。 |
| **一致性** | 与团队/云上 `compose` 对齐，**可重复性更好**。 |

---

## 4. 总表

| 维度 | 判断 |
|:---|:---|
| **能否在 Mac + Docker 上跑通** | **能**，且为 **Mac 上推荐** 路径之一。 |
| **主要风险** | **ARM 镜像兼容性**、**整机内存**；非 Docker 不可用。 |
| **与 `14`（Windows + Docker）对比** | 逻辑相同，差异在 **Apple Silicon 架构** 与 **Docker Desktop 资源占用** 习惯。 |

---

## 5. 文件变更

- 新增：`docs/phased_documents/test_run/15-本地Mac含Docker可运行性评估.md`
