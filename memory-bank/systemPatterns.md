# System Patterns *Optional*

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-06-21 10:25:54 - Log of updates made.

*

## Coding Patterns

*   **模块化:** 代码将按照功能划分为 `main.py`, `database.py`, `utils.py`, 和 `ui/` 子目录，遵循高内聚、低耦合的原则。
*   **类封装:** 数据库操作将封装在 `DatabaseManager` 类中，UI 逻辑将封装在各自的 Controller 类中（如 `LoginController`, `MainWindowController`）。
*   **信号与槽:** UI 事件处理将使用 PyQt/PySide 的信号与槽机制。

## Architectural Patterns

*   **Model-View-Controller (MVC) 的变体:**
    *   **Model:** 由 `database.py` 和部分 `utils.py` 的业务逻辑组成，负责数据持久化和业务规则。
    *   **View:** 由 `ui/` 目录下的 UI 定义文件组成，负责界面的展示。
    *   **Controller:** 由 `main.py` 中的 `LoginController` 和 `MainWindowController` 等类组成，负责响应用户输入，协调 View 和 Model。

## Testing Patterns

*   暂未定义。