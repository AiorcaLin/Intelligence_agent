# 本地 Linux 机器可运行性评估（第 7 轮 · 阶段性总结）

**日期**：2026-04-12  
**问题**：当前项目是否可以在 **本地 Linux 机器**（非云服务器）上运行？  
**结论（摘要）**：**可以**。与 `06-Linux云服务器可运行性评估.md` 在 **内核与软件栈** 上一致：Docker Engine、Celery prefork、Python/Node 与常见发行版工具链均匹配；**差异**主要在于本地桌面环境（显示服务器、资源被本机其它应用占用）与 **网络出口**（与你家宽/校园网是否稳定访问各 API 有关，与「云机房线路」无关）。

---

## 1. 与 Linux 云服务器相比：相同点

| 点 | 说明 |
|:---|:---|
| **Celery** | 类 Unix 上 **prefork** 默认可用，**参考**：[Celery Workers Guide](https://docs.celeryq.dev/en/stable/userguide/workers.html) |
| **Docker** | 本地安装 **Docker Engine** + Compose 即可；**参考**：[Docker Engine](https://docs.docker.com/engine/) |
| **启动方式** | 在**仓库根目录**使用 `uvicorn backend.main:app ...`，与 `03` / `04` / `06` 中说明一致）。 |

---

## 2. 与 Linux 云服务器相比：本地特有注意点

| 点 | 说明 |
|:---|:---|
| **内存** | 与 Windows/Mac 类似：若同时开 **浏览器、IDE、桌面环境**，留给 Docker + `next build` 的 RAM 会缩水；**16 GB 整机**仍建议控制并行重载。 |
| **网络** | 访问 **DeepSeek / OpenRouter / 嵌入服务** 取决于你当前网络（运营商、IPv6、防火墙），**不等同**于云机房国际出口；若本机 API 超时，可改用 `curl` 探活再排错。 |
| **磁盘** | 本地盘与云盘一样会随镜像层、数据库、Chroma 增长；注意 **根分区** 空间。 |
| **权限** | Linux 上常见将用户加入 `docker` 组以便无 `sudo` 运行 `docker`；属常规操作，**参考**各发行版 Docker 安装文档。 |

---

## 3. 发行版与桌面

- **Ubuntu LTS / Fedora / Debian / Arch** 等均可；优先选 **LTS 或稳定版** 以减少内核/驱动与 Docker 的兼容摩擦。  
- **无桌面服务器**（仅 SSH）与 **带桌面** 的本地机：对运行本项目**无本质区别**，仅影响你是否在本机开浏览器访问 `localhost:3000`。

---

## 4. 虚拟机与双系统

- **在 Linux 虚拟机里跑**（如 Windows 上 VMware/VirtualBox/KVM）：总 RAM 被 **宿主机 + 虚拟机** 分摊，若只给虚拟机 **4 GB**，则比 `02` 篇建议的 **8 GB 云机** 更吃紧；**建议给虚拟机 ≥ 8 GB**（若宿主机总内存允许）。  
- **双系统物理机**：资源分配与单机 Linux 相同，无额外虚拟化损耗。

---

## 5. 总表

| 维度 | 判断 |
|:---|:---|
| **能否在本地 Linux 跑通** | **能**，与云上 Linux 技术栈一致。 |
| **相对云服务器** | **多一层「本机桌面与其它进程」** 与 **家宽网络质量** 变量。 |
| **相对 Windows 本机** | **更少 Celery/路径层面的摩擦**（与 `06` 一致）。 |

---

## 6. 文件变更

- 新增：`docs/phased_documents/test_run/07-本地Linux可运行性评估.md`
