# WR_Unet_SupplyManage

杭州 XG 项目 —— 集中供料系统（UNET 管理系统）资料库。

## 仓库简介

本仓库用于沉淀集中供料系统的设计、实现与运维资料。目前已整理的文档如下：

| 类型     | 文件                                     | 说明                                 |
|----------|------------------------------------------|--------------------------------------|
| 设计蓝图 | [`docs/system_design.md`](docs/system_design.md) | 系统总体架构、功能模块、接口与验收标准 |

| 原型设计 | [`docs/frontend_prototype.md`](docs/frontend_prototype.md) | 前端界面原型、视觉规范与交互细节       |

目前仓库已经包含一个可运行的 FastAPI + 原生前端 MVP 演示，支持登录、仪表盘监控、任务队列、报警与审计日志的实时展示。后续将继续补充详细需求、接口规范以及正式实现。


## 开发技术栈规划

* **后端**：Python（Flask/FastAPI）
* **前端**：现代 Web 框架（Vue/React 等）
* **数据库**：MySQL 或 SQL Server
* **设备通讯**：Modbus TCP、OPC UA
* **接口协议**：RESTful API（JSON）、OPC UA

## MVP Demo 快速体验

1. 准备 Python 3.10+ 环境并安装依赖：

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. 启动接口服务（默认端口 8000）：

   ```bash
   uvicorn app.main:app --reload
   ```

3. 在浏览器访问 [http://127.0.0.1:8000/](http://127.0.0.1:8000/) 体验集中供料驾驶舱界面。

4. 演示账号口令：

   | 用户名    | 密码      | 角色         |
   |-----------|-----------|--------------|
   | `admin`   | `admin123`| 系统管理员   |
   | `operator`| `op2024`  | 现场操作员   |
   | `viewer`  | `guest`   | 只读观察者   |

> 演示数据由内置的模拟器实时更新，包含设备状态、任务进度、报警信息与审计日志，刷新周期为 3~5 秒。

### 接口4 产出归档演示

* 侧边栏新增 “接口4 产出记录” 页面，展示基于 OPC UA / Modbus 触发的产出留痕，支持关键字、状态与时间范围查询。
* 后端使用内嵌 SQLite（`backend/app/db.py`）自动建表并持久化事件，文件位于运行时生成的 `backend/data/interface4_events.sqlite3`。
* “导出 CSV” 将按照筛选条件导出当前数据，方便上传至报表或共享给第三方系统。


### 使用 PyCharm 启动与调试

为方便在 PyCharm 中验证环境与接口，请按以下步骤配置：

1. **导入项目**：在 PyCharm 选择 *Open*，指向仓库根目录 `WR_Unet_SupplyManage`，等待 IDE 建立虚拟环境索引。
2. **配置 Python 解释器**：在 *Settings → Project → Python Interpreter* 中选择 Python 3.10+，若需要可创建新的虚拟环境，并在终端执行 `pip install -r backend/requirements.txt` 安装依赖。
3. **创建运行配置**：
   - 打开 *Run → Edit Configurations…*，新建 **FastAPI/uvicorn** 类型（PyCharm 专业版）或 **Python** 类型运行配置。
   - 运行模块/脚本：`uvicorn`
   - 参数：`app.main:app --reload`
   - 工作目录：`${PROJECT_ROOT}/backend`
   - 环境变量：可按需补充，如 `UVICORN_RELOAD_DIRS=${PROJECT_ROOT}/backend/app`
4. **启动调试**：点击 *Run* 或 *Debug*，PyCharm 会自动在控制台启动 uvicorn 服务，默认监听 `http://127.0.0.1:8000`。
5. **前端联调**：在 PyCharm 内置浏览器或外部浏览器访问 `http://127.0.0.1:8000/`，即可验证仪表盘、任务流、报警等交互效果。

> 若需模拟正式部署，可在 PyCharm 的 *Terminal* 中执行 `uvicorn app.main:app --host 0.0.0.0 --port 8080`，并通过 Nginx 或容器化方式对外暴露。


## 贡献指引

1. Fork 仓库或新建分支进行开发。
2. 提交前请确保文档或代码通过相应检查并附带说明。
3. 所有文档放置于 `docs/` 目录，源代码按照模块化结构组织。

欢迎根据项目进展持续完善文档与实现。
