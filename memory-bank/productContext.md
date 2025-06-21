# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-06-21 10:25:13 - Log of updates made will be appended as footnotes to the end of this file.

*

## Project Goal

*   开发一个功能全面的学生信息管理系统，支持管理员、教师和学生三种角色。系统应提供用户管理、学生信息管理、课程管理、成绩管理、数据查询与统计、数据导入导出等核心功能。

## Key Features

*   **用户管理:** 支持用户注册、登录、信息修改、密码重置、账户冻结/解冻。
*   **角色权限:** 系统分为管理员、教师、学生三种角色，各自拥有不同的操作权限。
*   **学生信息管理:** 管理员可以批量导入、添加、修改、删除和查询学生信息，并管理学生的电子档案。
*   **课程管理:** 管理员可以管理课程信息，教师可以查看其授课列表。
*   **成绩管理:** 教师可以录入和修改其所授课程学生的成绩。学生可以查询自己的成绩。
*   **数据查询:** 支持多条件组合查询（如按学号、课程名查成绩）和模糊查询（如按姓名拼音首字母查学生）。
*   **数据统计:** 能够计算班级课程的平均分、标准差、及格率等统计指标。
*   **数据交互:** 支持从 Excel 批量导入学生数据，以及将查询结果导出为 Excel 文件。
*   **操作日志:** 记录关键操作（如信息修改、删除、成绩录入、密码重置等），便于审计和追溯。
*   **安全特性:** 包括密码哈希存储、图形验证码登录。

## Overall Architecture

*   **前端:** 使用 PyQt/PySide 作为 GUI 框架，构建桌面应用程序界面。
*   **后端:** 使用 Python 作为主要开发语言。
*   **数据库:** 使用 SQLite 作为本地数据库，方便部署和管理。
*   **模块化设计:** 系统将分为主逻辑模块 (`main.py`)、数据库交互模块 (`database.py`)、UI 模块 (`ui/`) 和工具模块 (`utils.py`)，以实现高内聚、低耦合。