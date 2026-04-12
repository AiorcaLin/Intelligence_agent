# 本地 Windows + Docker 可运行性评估（第 14 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：在 **本地 Windows** 上，**使用 Docker**（如 Docker Desktop），本项目是否可以运行？  
**结论（摘要）**：**可以**。这是 Windows 上 **较推荐** 的路径之一：依赖（Postgres、Redis、Chroma）以 **Linux 容器** 运行，与生产环境一致；**Celery Worker 若在 Linux 容器内运行**，则使用 **prefork** 等与 Linux 相同的并发模型（与 `03` 中「宿主机 Windows 需 `--pool=solo`」针对的是 **Windows 原生进程**，二者不要混淆）。主要瓶颈仍是 **整机内存与 WSL2/Docker 开销**（见第 3 节）。

---

## 1. 技术路径说明

| 组件 | Windows + Docker 下的常见形态 |
|:---|:---|
| **Docker Desktop** | 在 Windows 上通过 **WSL2** 或 Hyper-V 运行 Linux 容器；主流为新式 **WSL2 后端**。**参考**：[Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/) **解释**：容器内仍是 Linux，与 `06`/`07` 上的行为一致。 |
| **`docker-compose.yml`** | 与本仓库一致：拉取 **Postgres / Redis / Chroma** 镜像并映射端口。 |
| **后端 / Celery / Next** | 常见两种做法：**(A)** 仍在 Windows 宿主机用 Python/Node 跑；**(B)** 再写 Dockerfile 一并容器化。README 当前示例偏 **(A)**。 |

---

## 2. 与 `03`（Windows 无容器）的关系

| 点 | 说明 |
|:---|:---|
| **Celery** | 若在 **Windows 宿主机**直接 `celery` → 仍建议 `--pool=solo`（`03`）。若在 **Linux 容器**里跑 Celery → **按 Linux 规则**（通常 prefork 可用）。 |
| **Redis/Postgres** | 用 Docker 后，**不必**在 Windows 上原生安装 Redis（`11` 中的痛点被规避）。 |

---

## 3. 资源与体验（与你本机 16 GB 场景）

- **Docker Desktop + WSL2** 自身会占用 **可观内存**；再叠加 **三容器 + IDE + 浏览器**，**8 GB 以下整机** 往往非常紧。  
- **`next build`** 若在 **Windows 宿主机**执行，仍可能出现 **高内存峰值**（与 `05`/`11` 一致）。  
- **建议**：整机 **≥16 GB** 更从容；或 **构建在 CI/其它机器完成**，本机只 `run dev` / `start`。

---

## 4. 实操注意（与平台无关）

- 从**仓库根目录**启动后端时，注意 `uvicorn backend.main:app` 与 `PYTHONPATH`（见 `03`/`05`）。  
- **`.env`** 中 `localhost` 指向本机映射端口，与容器 `ports` 一致。  

---

## 5. 总表

| 维度 | 判断 |
|:---|:---|
| **能否在 Windows + Docker 上跑通** | **能**，且为 **Windows 上较推荐** 的依赖交付方式。 |
| **主要风险** | **内存** 与 **WSL2 配置**；非 Docker 本身不可用。 |
| **与 `11` 对比** | **含 Docker** 显著降低 **Redis/Postgres 安装** 难度。 |

---

## 6. 文件变更

- 新增：`docs/phased_documents/test_run/14-本地Windows含Docker可运行性评估.md`
