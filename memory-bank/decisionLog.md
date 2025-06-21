# Decision Log

This file records architectural and implementation decisions using a list format.
2025-06-21 10:25:43 - Log of updates made.

*

## Decision

*   [2025-06-21 10:25:43] - 采用 SQLite 作为项目的数据库。

## Rationale

*   **轻量级与便携性:** SQLite 是一个无服务器、零配置的数据库引擎，数据库本身只是一个单一的文件，非常便于项目的分发和部署，无需用户安装和配置独立的数据库服务。
*   **满足需求:** 对于桌面应用场景的学生信息管理系统，SQLite 提供的功能和性能完全足够。它支持标准的 SQL 语法、事务、视图和触发器。
*   **Python 内置支持:** Python 标准库 `sqlite3` 提供了对 SQLite 的原生支持，无需安装额外的第三方库即可进行数据库操作，简化了开发环境。
*   **伪代码指引:** 项目的伪代码规范 (`wl31_pseudocode.md`) 明确指出了使用 SQLite。

## Implementation Details

*   数据库交互逻辑将封装在 `database.py` 模块的 `DatabaseManager` 类中。
*   数据库文件的路径将在 `config.py` 中定义，方便统一管理。
---
### Decision (Debug)
[2025-06-21 12:15:35] - 实施数据库自动迁移以修复因缺少列而导致的启动崩溃。

**Rationale:**
应用程序在使用旧版数据库文件时启动失败，抛出 `sqlite3.OperationalError: no such column: enrollment_year` 错误。这是因为 `Students` 表缺少在后续开发中添加的 `enrollment_year`, `department`, 和 `major` 列。通过在程序启动时执行一个自动迁移脚本，系统可以检查并添加缺失的列。这种方法确保了对旧数据库文件的向后兼容性，防止了因架构不匹配而导致的崩溃，同时保留了现有用户数据。

**Details:**
*   **受影响的文件:** `wl31/database/database_manager.py`
*   **操作:**
    *   在 `DatabaseManager` 中添加了 `_run_migrations()` 方法。
    *   该方法使用 `PRAGMA table_info(Students)` 检查现有列。
    *   如果 `enrollment_year`, `department`, 或 `major` 列不存在，则使用 `ALTER TABLE ... ADD COLUMN ...` 动态添加它们。
*   **附加修复:** 创建了 `wl31/assets/captcha_fonts/` 目录以消除一个无关的字体路径警告。
---
### Decision (Debug)
[2025-06-21 12:53:07] - [Bug Fix Strategy: Removed logging from DB migrations]

**Rationale:**
The application was crashing on startup with `AttributeError: 'DatabaseManager' object has no attribute 'log_action'`. This was caused by calls to `self.log_action` within the `_run_migrations` method of the `DatabaseManager`. Database migrations are a system-level, backward-compatibility operation and should not be logged as a user action. Removing these calls is the cleanest and most correct fix.

**Details:**
*   **Affected file:** `wl31/database/database_manager.py`
*   **Action:** Removed all `self.log_action(...)` calls from the `_run_migrations` method.
---
### Decision (Debug)
[2025-06-21 12:59:29] - [Bug Fix Strategy: Re-implement missing methods in `DatabaseManager`]

**Rationale:**
The application was crashing due to `AttributeError` exceptions caused by missing `get_action_logs`, `log_action`, and `close` methods in the `DatabaseManager` class. Re-implementing these critical methods is the direct solution to restore functionality.

**Details:**
Affected components/files:
* `wl31/database/database_manager.py`