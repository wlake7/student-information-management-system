# wl31 学生信息管理系统 - 伪代码规范

## 1. 项目结构

```
wl31/
├── main.py                 # 主程序入口
├── database.py             # 数据库交互模块
├── utils.py                # 工具函数模块 (密码处理, 拼音, 验证码等)
├── config.py               # 配置文件 (数据库路径, 常量等)
├── ui/
│   ├── __init__.py
│   ├── wl_login_window.py      # 登录窗口 UI
│   ├── wl_main_window.py       # 主窗口 UI
│   ├── wl_student_admin.py     # 学生管理界面 UI
│   ├── wl_course_admin.py      # 课程管理界面 UI
│   ├── wl_grade_admin.py       # 成绩管理界面 UI
│   └── wl_user_profile.py      # 个人信息修改界面 UI
└── assets/
    └── captcha_fonts/        # 验证码字体
```

## 2. 数据库模块 (`database.py`)

```python
# 模块: database.py
# 描述: 负责所有与 SQLite 数据库的交互。

CLASS DatabaseManager:
    FUNCTION __init__(db_path):
        # 初始化数据库连接
        # 如果表不存在，则创建所有表 (Users, Students, Courses, Grades, ActionLogs)
        pass

    # --- 用户管理 ---
    FUNCTION get_user(username):
        # 根据用户名查询用户信息
        # 返回: 用户对象或 None
        pass

    FUNCTION check_student_id_exists(student_id):
        # 检查学号是否已在 Users 表中注册
        # 返回: True 或 False
        pass

    FUNCTION create_user(username, hashed_password, role, student_id=None):
        # 创建新用户 (用于注册)
        pass

    FUNCTION update_user_info(user_id, new_info):
        # 更新用户信息 (用于教师/学生修改个人信息)
        pass

    FUNCTION update_last_login_time(user_id):
        # 更新用户最后登录时间
        pass

    FUNCTION reset_user_password(admin_id, target_user_id, new_password):
        # 管理员重置用户密码
        # 记录操作到 ActionLogs
        pass

    FUNCTION set_user_account_status(admin_id, target_user_id, is_frozen):
        # 管理员冻结/解冻账户
        # 记录操作到 ActionLogs
        pass

    FUNCTION batch_import_students(admin_id, student_data_list):
        # 批量导入学生用户
        # 为每个学生在 Users 表创建账户，并在 Students 表创建信息记录
        # 记录操作到 ActionLogs
        pass

    # --- 学生信息管理 ---
    FUNCTION get_student_details(student_id):
        # 获取单个学生详细信息
        pass

    FUNCTION get_all_students(filters=None, sort_by=None):
        # 获取学生列表，支持过滤和排序
        pass

    FUNCTION add_student_record(admin_id, student_info):
        # 添加单个学生记录 (通常由批量导入调用)
        pass

    FUNCTION update_student_record(editor_id, student_id, new_info):
        # 更新学生信息
        # 记录操作到 ActionLogs
        pass

    FUNCTION delete_student_record(admin_id, student_id):
        # 删除学生记录
        # 记录操作到 ActionLogs
        pass

    FUNCTION update_student_archive(student_id, file_path):
        # 更新学生的电子档案路径
        pass

    # --- 课程与成绩管理 ---
    FUNCTION get_courses_by_teacher(teacher_id):
        # 获取某位教师教授的所有课程
        pass

    FUNCTION get_all_courses():
        # 获取所有课程列表
        pass

    FUNCTION add_course(admin_id, course_info):
        # 添加新课程
        pass

    FUNCTION update_course(admin_id, course_id, new_info):
        # 更新课程信息
        pass

    FUNCTION assign_grade(teacher_id, student_id, course_id, score):
        # 教师为学生录入/修改成绩
        # 验证该教师是否是该课程的授课教师
        # 记录操作到 ActionLogs
        pass

    # --- 数据查询与统计 ---
    FUNCTION query_grades(student_id=None, course_name=None):
        # 组合查询: 根据学号和课程名称查询成绩
        pass

    FUNCTION search_students_by_pinyin(pinyin_initials):
        # 模糊搜索: 根据姓名拼音首字母缩写查询学生
        # 需要一个额外的字段或在查询时动态转换
        pass

    FUNCTION calculate_class_grade_stats(class_name, course_id):
        # 计算班级某门课程的成绩统计数据
        # 返回: {average, std_dev, pass_rate}
        pass

    # --- 操作记录 ---
    FUNCTION log_action(user_id, action_type, description):
        # 记录用户操作
        pass

    FUNCTION get_action_logs(user_id, role):
        # 获取操作日志
        # 如果是管理员，可以查看所有教师和自己的日志
        # 如果是教师，只能查看自己的日志
        pass

END CLASS
```

## 3. 工具模块 (`utils.py`)

```python
# 模块: utils.py
# 描述: 提供各种辅助功能。

MODULE Utils:
    FUNCTION hash_password(password):
        # 使用安全的哈希算法 (如 bcrypt) 加密密码
        # 返回: 哈希后的密码字符串
        pass

    FUNCTION verify_password(hashed_password, plain_password):
        # 验证输入的密码是否与哈希匹配
        # 返回: True 或 False
        pass

    FUNCTION generate_captcha():
        # 生成图形验证码
        # 返回: (验证码图片对象, 验证码字符串)
        pass

    FUNCTION convert_to_pinyin_initials(text):
        # 将中文字符串转换为拼音首字母缩写
        # 例如: "张三" -> "zs"
        # 返回: 转换后的字符串
        pass

    FUNCTION export_to_excel(data, filename):
        # 将数据 (如查询结果) 导出到 Excel 文件
        # data 是一个二维列表或类似结构
        pass

    FUNCTION read_from_excel(filepath):
        # 从 Excel 文件读取数据 (用于批量导入)
        # 返回: 数据列表
        pass

END MODULE
```

## 4. UI 模块 (`ui/`)

### 4.1 登录窗口 (`wl_login_window.py`)

```python
# 模块: wl_login_window.py
# 描述: 定义登录界面的 UI 控件和布局。

CLASS Ui_LoginWindow:
    FUNCTION setupUi(self, LoginWindow):
        # 设置窗口大小、标题
        # 创建控件:
        self.wl_username_input = QLineEdit()
        self.wl_password_input = QLineEdit()
        self.wl_password_input.setEchoMode(Password)

        self.wl_captcha_image = QLabel() # 用于显示验证码图片
        self.wl_captcha_input = QLineEdit()

        self.wl_role_combobox = QComboBox() # 角色选择: 管理员, 教师, 学生
        self.wl_login_button = QPushButton("登录")
        self.wl_register_button = QPushButton("注册")

        # ... 添加布局 ...
    END FUNCTION
END CLASS
```

### 4.2 主窗口 (`wl_main_window.py`)

```python
# 模块: wl_main_window.py
# 描述: 系统主窗口，包含菜单、工具栏、状态栏和主工作区。

CLASS Ui_MainWindow:
    FUNCTION setupUi(self, MainWindow):
        # 创建菜单栏:
        # - 文件 (导出, 退出)
        # - 管理 (学生管理, 课程管理, 成绩管理, 用户管理[管理员可见])
        # - 查询 (成绩查询, 学生查询)
        # - 帮助 (关于)

        # 创建工具栏 (常用功能的快捷方式)

        # 创建状态栏:
        self.wl_status_label = QLabel() # 显示 "角色 + 姓名 + 最后登录时间"
        self.wl_db_status_label = QLabel() # 显示 "数据库连接状态"

        # 创建主工作区 (使用 QTabWidget 或 QStackedWidget)
        # 每个 Tab/Page 对应一个功能模块 (如学生管理界面)

        # ... 添加布局 ...
    END FUNCTION
END CLASS
```

## 5. 主逻辑模块 (`main.py`)

```python
# 模块: main.py
# 描述: 应用程序的主入口和逻辑控制中心。

# --- 全局变量 ---
db_manager = DatabaseManager(config.DATABASE_PATH)
current_user = None # 存储当前登录用户信息的对象

# --- 登录窗口逻辑 ---
CLASS LoginController(QDialog):
    FUNCTION __init__(self):
        # 初始化 UI (来自 Ui_LoginWindow)
        # 连接信号和槽
        self.ui.wl_login_button.clicked.connect(self.handle_login)
        self.ui.wl_register_button.clicked.connect(self.open_register_dialog)
        self.refresh_captcha()

    FUNCTION refresh_captcha(self):
        # 调用 utils.generate_captcha() 并更新界面
        pass

    FUNCTION handle_login(self):
        # 1. 获取用户名、密码、角色、输入的验证码
        # 2. 验证验证码是否正确
        # 3. 调用 db_manager.get_user() 查询用户
        # 4. 调用 utils.verify_password() 验证密码
        # 5. 如果验证成功:
        #    - 设置全局变量 current_user
        #    - 调用 db_manager.update_last_login_time()
        #    - 实例化并显示主窗口 MainWindowController
        #    - 关闭登录窗口
        # 6. 如果失败，显示错误提示

    FUNCTION open_register_dialog(self):
        # 打开注册对话框
        pass

# --- 主窗口逻辑 ---
CLASS MainWindowController(QMainWindow):
    FUNCTION __init__(self):
        # 初始化 UI (来自 Ui_MainWindow)
        # 根据 current_user.role 设置界面元素的可见性 (例如管理员菜单)
        # 更新状态栏信息
        self.update_status_bar()
        # 连接菜单项的信号到对应的槽函数
        # (e.g., self.ui.action_student_manage.triggered.connect(self.show_student_management_tab))

    FUNCTION update_status_bar(self):
        # 设置 self.ui.wl_status_label 的文本
        # 检查数据库连接并设置 self.ui.wl_db_status_label
        pass

    FUNCTION show_student_management_tab(self):
        # 在主工作区加载学生管理界面
        # 需要二次确认的关键操作 (如删除)
        # e.g., show_confirmation_dialog("确定要删除吗?")
        pass

    # ... 其他功能模块的加载和控制函数 ...

    FUNCTION handle_export(self):
        # 获取当前活动表格的数据
        # 调用 utils.export_to_excel()
        pass

# --- 程序入口 ---
FUNCTION main():
    app = QApplication(sys.argv)
    login_window = LoginController()
    IF login_window.exec_() == QDialog.Accepted:
        main_window = MainWindowController()
        main_window.show()
        sys.exit(app.exec_())

IF __name__ == "__main__":
    main()
```

## 6. 功能流程伪代码

### 6.1 用户注册

```
PROCEDURE UserRegistration:
    INPUT: username, password, role, student_id (if role is 'student')
    
    1. UI: 用户在注册界面填写信息。
    2. LOGIC (实时验证):
       IF role is 'student':
           WHEN student_id input field loses focus:
               is_exist = db_manager.check_student_id_exists(student_id)
               IF is_exist:
                   SHOW_ERROR("学号已存在")
               ELSE:
                   CLEAR_ERROR()
    3. LOGIC (点击注册按钮):
       - 验证所有字段不为空。
       - 验证两次输入的密码是否一致。
       - hashed_password = utils.hash_password(password)
       - db_manager.create_user(username, hashed_password, role, student_id)
       - SHOW_INFO("注册成功")
       - CLOSE_REGISTRATION_DIALOG()
END PROCEDURE
```

### 6.2 模糊搜索学生

```
PROCEDURE FuzzySearchStudent:
    INPUT: search_term (e.g., "zs")
    
    1. UI: 用户在搜索框输入 "zs" 并点击搜索。
    2. LOGIC:
       - pinyin_initials = utils.convert_to_pinyin_initials(search_term) if it contains Chinese characters, otherwise use search_term directly.
       - search_results = db_manager.search_students_by_pinyin(pinyin_initials)
    3. UI:
       - 清空现有的学生信息表格。
       - 将 search_results 中的每一条记录填充到表格中。
END PROCEDURE
```

### 6.3 教师录入成绩

```
PROCEDURE TeacherEntersGrade:
    INPUT: student_id, course_id, score
    
    1. PRE-CONDITION: 教师 (current_user) 已登录。
    2. UI: 教师在成绩管理界面选择一个他/她教授的课程。
       - 课程下拉列表只应包含 db_manager.get_courses_by_teacher(current_user.id) 的结果。
    3. UI: 教师选择学生，并输入分数。
    4. LOGIC (点击保存/更新按钮):
       - 调用 db_manager.assign_grade(current_user.id, student_id, course_id, score)
       - assign_grade 内部会进行权限验证。
       - IF success:
           - SHOW_INFO("成绩录入成功")
           - REFRESH_GRADE_TABLE()
       - ELSE:
           - SHOW_ERROR("操作失败，您可能没有权限")
END PROCEDURE
```

### 6.4 管理员批量导入

```
PROCEDURE AdminBatchImport:
    1. UI: 管理员点击 "批量导入" 按钮，打开文件选择对话框。
    2. LOGIC:
       - admin_id = current_user.id
       - selected_file = GET_FILE_PATH_FROM_DIALOG()
       - IF selected_file is not None:
           - student_data_list = utils.read_from_excel(selected_file)
           - db_manager.batch_import_students(admin_id, student_data_list)
           - SHOW_INFO("导入完成")
           - REFRESH_STUDENT_LIST()
END PROCEDURE