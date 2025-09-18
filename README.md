# WR_Unet_SupplyManage

杭州 XG 项目 —— 集中供料系统（UNET 管理系统）资料库。

## 仓库简介

本仓库用于沉淀集中供料系统的设计、实现与运维资料。目前已整理的文档如下：

| 类型     | 文件                                     | 说明                                 |
|----------|------------------------------------------|--------------------------------------|
| 设计蓝图 | [`docs/system_design.md`](docs/system_design.md) | 系统总体架构、功能模块、接口与验收标准 |

| 原型设计 | [`docs/frontend_prototype.md`](docs/frontend_prototype.md) | 前端界面原型、视觉规范与交互细节       |

后续迭代将补充详细需求、接口规范以及代码实现。


## 开发技术栈规划

* **后端**：Python（Flask/FastAPI）
* **前端**：现代 Web 框架（Vue/React 等）
* **数据库**：MySQL 或 SQL Server
* **设备通讯**：Modbus TCP、OPC UA
* **接口协议**：RESTful API（JSON）、OPC UA

## 贡献指引

1. Fork 仓库或新建分支进行开发。
2. 提交前请确保文档或代码通过相应检查并附带说明。
3. 所有文档放置于 `docs/` 目录，源代码按照模块化结构组织。

欢迎根据项目进展持续完善文档与实现。
