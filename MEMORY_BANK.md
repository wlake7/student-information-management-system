# 学生信息管理系统 - 记忆库

本文档是项目的“唯一事实来源”，记录了核心的架构设计决策，包括数据库表结构和项目文件结构。

---

## 1. 项目文件结构

根据 `wl31_pseudocode.md` 的规划，项目将采用以下目录和文件结构，以确保代码的模块化和可维护性。

```
wl31/
├── main.py                 # 主程序入口，包含应用启动逻辑和主窗口控制器
├── database.py             # 数据库交互模块，封装所有 SQL 操作
├── utils.py                # 工具函数模块 (密码哈希, 拼音转换, 验证码生成, Excel操作等)
├── config.py               # 配置文件 (如数据库文件路径, 字体路径, 其他常量)
├── MEMORY_BANK.md          # [本文档] 项目核心架构记录
├── memory-bank/            # 记忆库目录
│   ├── productContext.md
│   ├── activeContext.md
│   ├── progress.md
│   ├── decisionLog.md
│   └── systemPatterns.md
├── ui/                       # UI 定义文件目录
│   ├── __init__.py
│   ├── wl_login_window.py      # 登录窗口 UI
│   ├── wl_main_window.py       # 主窗口 UI
│   ├── wl_student_admin.py     # 学生管理界面 UI
│   ├── wl_course_admin.py      # 课程管理界面 UI
│   ├── wl_grade_admin.py       # 成绩管理界面 UI
│   └── wl_user_profile.py      # 个人信息修改界面 UI
└── assets/                   # 静态资源目录
    └── captcha_fonts/        # 用于生成验证码的字体文件
```

---

## 2. SQLite 数据库表结构

数据库将包含以下核心表，用于存储用户信息、学生、课程、成绩及相关数据。

### 2.1 `Users` - 用户表

存储所有可以登录系统的用户信息，包括管理员、教师和学生。

| 字段名 (Field)         | 数据类型 (Type)      | 约束 (Constraints)                       | 描述 (Description)                               |
| ---------------------- | -------------------- | ---------------------------------------- | ------------------------------------------------ |
| `id`                   | `INTEGER`            | `PRIMARY KEY AUTOINCREMENT`              | 唯一用户 ID                                      |
| `username`             | `TEXT`               | `NOT NULL UNIQUE`                        | 登录用户名                                       |
| `password_hash`        | `TEXT`               | `NOT NULL`                               | 加密后的密码哈希值                               |
| `role`                 | `TEXT`               | `NOT NULL CHECK(role IN ('admin', 'teacher', 'student'))` | 用户角色 ('admin', 'teacher', 'student')         |
| `student_id`           | `INTEGER`            | `UNIQUE`                                 | 关联到 `Students` 表的外键，仅学生角色拥有 |
| `is_frozen`            | `INTEGER`            | `NOT NULL DEFAULT 0`                     | 账户是否被冻结 (0: 正常, 1: 冻结)                |
| `created_at`           | `TEXT`               | `NOT NULL DEFAULT CURRENT_TIMESTAMP`     | 账户创建时间                                     |
| `last_login_at`        | `TEXT`               |                                          | 最后登录时间                                     |
| `FOREIGN KEY(student_id)` | `REFERENCES Students(id)` |                                  | 外键约束                                         |

### 2.2 `Students` - 学生信息表

存储学生的详细个人信息。

| 字段名 (Field)         | 数据类型 (Type)      | 约束 (Constraints)        | 描述 (Description)                               |
| ---------------------- | -------------------- | ------------------------- | ------------------------------------------------ |
| `id`                   | `INTEGER`            | `PRIMARY KEY AUTOINCREMENT` | 唯一学生 ID (学号)                               |
| `name`                 | `TEXT`               | `NOT NULL`                | 学生姓名                                         |
| `name_pinyin`          | `TEXT`               |                           | 姓名拼音首字母 (用于模糊搜索，如 "zs")           |
| `gender`               | `TEXT`               | `CHECK(gender IN ('男', '女'))` | 性别                                             |
| `enrollment_year`      | `INTEGER`            |                           | 入学年份                                         |
| `department`           | `TEXT`               |                           | 所属院系                                         |
| `major`                | `TEXT`               |                           | 专业名称                                         |
| `class_name`           | `TEXT`               |                           | 班级名称                                         |
| `contact_info`         | `TEXT`               |                           | 联系方式 (电话或邮箱)                            |
| `archive_path`         | `TEXT`               |                           | 电子档案文件路径                                 |

### 2.3 `Teachers` - 教师信息表

存储教师的详细个人信息。

| 字段名 (Field)         | 数据类型 (Type)      | 约束 (Constraints)        | 描述 (Description)                               |
| ---------------------- | -------------------- | ------------------------- | ------------------------------------------------ |
| `id`                   | `INTEGER`            | `PRIMARY KEY AUTOINCREMENT` | 唯一教师 ID                                      |
| `user_id`              | `INTEGER`            | `NOT NULL UNIQUE`         | 关联到 `Users` 表的用户 ID                       |
| `name`                 | `TEXT`               | `NOT NULL`                | 教师姓名                                         |
| `title`                | `TEXT`               |                           | 职称 (如: 教授, 副教授)                          |
| `department`           | `TEXT`               |                           | 所属院系                                         |
| `contact_info`         | `TEXT`               |                           | 联系方式                                         |
| `FOREIGN KEY(user_id)` | `REFERENCES Users(id)` | `ON DELETE CASCADE`       | 外键约束，级联删除                               |

### 2.4 `Courses` - 课程表

存储所有课程的信息。

| 字段名 (Field)         | 数据类型 (Type)      | 约束 (Constraints)        | 描述 (Description)                               |
| ---------------------- | -------------------- | ------------------------- | ------------------------------------------------ |
| `id`                   | `INTEGER`            | `PRIMARY KEY AUTOINCREMENT` | 唯一课程 ID                                      |
| `name`                 | `TEXT`               | `NOT NULL`                | 课程名称                                         |
| `credits`              | `REAL`               | `NOT NULL`                | 课程学分                                         |
| `teacher_id`           | `INTEGER`            |                           | 授课教师 ID (关联到 `Teachers` 表)               |
| `semester`             | `TEXT`               |                           | 开设学期 (如 '2023-2024 秋季')                   |
| `description`          | `TEXT`               |                           | 课程描述                                         |
| `FOREIGN KEY(teacher_id)` | `REFERENCES Teachers(id)` | `ON DELETE SET NULL`      | 外键约束，教师被删除时设为 NULL                  |

### 2.5 `Grades` - 成绩表

存储学生在各门课程中的成绩。

| 字段名 (Field)         | 数据类型 (Type)      | 约束 (Constraints)        | 描述 (Description)                               |
| ---------------------- | -------------------- | ------------------------- | ------------------------------------------------ |
| `id`                   | `INTEGER`            | `PRIMARY KEY AUTOINCREMENT` | 唯一成绩记录 ID                                  |
| `student_id`           | `INTEGER`            | `NOT NULL`                | 关联到 `Students` 表的学生 ID                    |
| `course_id`            | `INTEGER`            | `NOT NULL`                | 关联到 `Courses` 表的课程 ID                     |
| `score`                | `REAL`               | `NOT NULL`                | 分数                                             |
| `recorded_at`          | `TEXT`               | `NOT NULL DEFAULT CURRENT_TIMESTAMP` | 成绩录入/更新时间                                |
| `recorder_id`          | `INTEGER`            | `NOT NULL`                | 录入成绩的教师 ID (关联到 `Users` 表)            |
| `UNIQUE`               | `(student_id, course_id)` |                         | 确保一个学生一门课只有一个成绩                   |
| `FOREIGN KEY(student_id)` | `REFERENCES Students(id)` |                       | 外键约束                                         |
| `FOREIGN KEY(course_id)` | `REFERENCES Courses(id)` |                        | 外键约束                                         |
| `FOREIGN KEY(recorder_id)`| `REFERENCES Users(id)` |                          | 外键约束                                         |

### 2.6 `ActionLogs` - 操作日志表

记录系统中的关键操作，用于审计和追溯。

| 字段名 (Field)         | 数据类型 (Type)      | 约束 (Constraints)        | 描述 (Description)                               |
| ---------------------- | -------------------- | ------------------------- | ------------------------------------------------ |
| `id`                   | `INTEGER`            | `PRIMARY KEY AUTOINCREMENT` | 唯一日志 ID                                      |
| `user_id`              | `INTEGER`            | `NOT NULL`                | 执行操作的用户 ID (关联到 `Users` 表)            |
| `action_type`          | `TEXT`               | `NOT NULL`                | 操作类型 (如 'UPDATE_STUDENT', 'DELETE_COURSE', 'RESET_PASSWORD') |
| `description`          | `TEXT`               | `NOT NULL`                | 操作的详细描述                                   |
| `timestamp`            | `TEXT`               | `NOT NULL DEFAULT CURRENT_TIMESTAMP` | 操作发生的时间戳                                 |
| `FOREIGN KEY(user_id)` | `REFERENCES Users(id)` |                         | 外键约束                                         |