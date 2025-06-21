# wl31/database/database_manager.py
# 描述: 负责所有与 SQLite 数据库的交互。

import sqlite3
import os
import numpy as np
from wl31 import config # 使用绝对导入
from wl31.utils.hash_utils import hash_password, verify_password
from wl31.utils.pinyin_utils import convert_to_pinyin_initials


class DatabaseManager:
    """
    数据库管理类，负责所有数据库操作。
    """
    def __init__(self, db_path=config.DATABASE_PATH):
        """
        初始化数据库连接，并确保所有表都已创建。
        :param db_path: 数据库文件的路径。
        """
        self.db_path = db_path
        # 确保数据库所在的目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row # 将元组结果转换为类似字典的对象
        self.cursor = self.conn.cursor()
        self._run_migrations() # 运行数据库迁移
        self._create_tables()
        self._create_default_admin_if_not_exists()

    def _create_tables(self):
        """
        创建所有必要的数据库表（如果它们不存在）。
        """
        # 用户表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student')),
            student_id INTEGER UNIQUE,
            is_frozen INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login_at TEXT,
            FOREIGN KEY(student_id) REFERENCES Students(id)
        );
        ''')

        # 学生信息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_pinyin TEXT,
            gender TEXT CHECK(gender IN ('男', '女')),
            enrollment_year INTEGER,
            department TEXT,
            major TEXT,
            class_name TEXT,
            contact_info TEXT,
            id_card TEXT,
            archive_path TEXT
        );
        ''')

        # 教师信息表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            title TEXT,
            department TEXT,
            contact_info TEXT,
            id_card TEXT,
            FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE
        );
        ''')

        # 课程表
        # 设计决策：根据功能要求，将授课教师和学期直接作为课程属性。
        # 这简化了UI和逻辑，因此移除了多对多的TeacherCourses表。
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            credits REAL NOT NULL,
            teacher_id INTEGER,
            semester TEXT,
            description TEXT,
            FOREIGN KEY(teacher_id) REFERENCES Teachers(id) ON DELETE SET NULL
        );
        ''')

        # 成绩表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            score REAL NOT NULL,
            recorded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            recorder_id INTEGER NOT NULL,
            UNIQUE (student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES Students(id),
            FOREIGN KEY(course_id) REFERENCES Courses(id),
            FOREIGN KEY(recorder_id) REFERENCES Users(id)
        );
        ''')

        # 操作日志表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ActionLogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES Users(id)
        );
        ''')

        self.conn.commit()

    def _create_default_admin_if_not_exists(self):
        """如果不存在任何管理员，则创建一个默认管理员账户。"""
        self.cursor.execute("SELECT id FROM Users WHERE role = 'admin'")
        if self.cursor.fetchone() is None:
            print("No admin user found. Creating default admin...")
            default_username = "admin"
            default_password = "admin123"
            hashed_pass = hash_password(default_password)
            try:
                self.cursor.execute(
                    "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                    (default_username, hashed_pass, 'admin')
                )
                self.conn.commit()
                print(f"Default admin created. Username: {default_username}, Password: {default_password}")
            except sqlite3.IntegrityError:
                # In case of a race condition where another process creates it
                self.conn.rollback()

    def _run_migrations(self):
        """
        执行数据库迁移，确保表结构是最新的。
        这对于向后兼容旧的数据库文件至关重要。
        """
        try:
            # 1. 检查 Students 表的列
            self.cursor.execute("PRAGMA table_info(Students);")
            columns_info = self.cursor.fetchall()
            column_names = {info['name'] for info in columns_info}

            # 2. 如果缺少 enrollment_year 列，则添加它
            if 'enrollment_year' not in column_names:
                print("Migrating database: Adding 'enrollment_year' to Students table...")
                self.cursor.execute("ALTER TABLE Students ADD COLUMN enrollment_year INTEGER;")

            # 3. 如果缺少 department 列，则添加它
            if 'department' not in column_names:
                print("Migrating database: Adding 'department' to Students table...")
                self.cursor.execute("ALTER TABLE Students ADD COLUMN department TEXT;")

            # 4. 如果缺少 major 列，则添加它
            if 'major' not in column_names:
                print("Migrating database: Adding 'major' to Students table...")
                self.cursor.execute("ALTER TABLE Students ADD COLUMN major TEXT;")

            # 5. 为 Students 表添加 id_card
            if 'id_card' not in column_names:
                print("Migrating database: Adding 'id_card' to Students table...")
                self.cursor.execute("ALTER TABLE Students ADD COLUMN id_card TEXT;")

            # 6. 为 Teachers 表添加 id_card
            self.cursor.execute("PRAGMA table_info(Teachers);")
            teacher_columns_info = self.cursor.fetchall()
            teacher_column_names = {info['name'] for info in teacher_columns_info}
            if 'id_card' not in teacher_column_names:
                print("Migrating database: Adding 'id_card' to Teachers table...")
                self.cursor.execute("ALTER TABLE Teachers ADD COLUMN id_card TEXT;")

            self.conn.commit()
            print("Database migration check completed.")
        except sqlite3.Error as e:
            print(f"An error occurred during database migration: {e}")
            self.conn.rollback()


    def get_user(self, username: str):
        """
        根据用户名查询用户信息。
        :param username: 登录用户名。
        :return: 包含用户信息的字典，或在未找到时返回 None。
        """
        self.cursor.execute("SELECT id, username, password_hash, role, student_id, is_frozen, last_login_at FROM Users WHERE username = ?", (username,))
        user_data = self.cursor.fetchone()
        if user_data:
            return dict(user_data)
        return None

    def get_user_by_id(self, user_id: int):
        """根据用户ID查询用户信息"""
        self.cursor.execute("SELECT id, username, password_hash, role, student_id, is_frozen, last_login_at FROM Users WHERE id = ?", (user_id,))
        user_data = self.cursor.fetchone()
        if user_data:
            return dict(user_data)
        return None

    def check_username_exists(self, username: str) -> bool:
        """
        检查用户名是否已存在。
        :param username: 要检查的用户名。
        :return: 如果存在返回 True，否则返回 False。
        """
        self.cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
        return self.cursor.fetchone() is not None

    def check_student_id_exists(self, student_id: str) -> bool:
        """
        检查学号是否已在 Users 表中注册。
        :param student_id: 要检查的学号。
        :return: 如果存在返回 True，否则返回 False。
        """
        self.cursor.execute("SELECT id FROM Users WHERE student_id = ?", (student_id,))
        return self.cursor.fetchone() is not None

    def create_user(self, username: str, hashed_password: str, role: str, student_id: str = None):
        """
        创建新用户 (用于注册)。
        :param username: 用户名。
        :param hashed_password: 哈希后的密码。
        :param role: 角色 ('student', 'teacher')。
        :param student_id: 学号 (仅当角色为学生时需要)。
        :return: 新创建用户的ID。
        """
        try:
            self.cursor.execute(
                "INSERT INTO Users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
                (username, hashed_password, role, student_id)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            # 如果发生唯一性约束冲突 (例如，用户名或学号已存在)
            self.conn.rollback()
            print(f"Error creating user: {e}")
            return None

    def update_last_login_time(self, user_id: int):
        """
        更新用户的最后登录时间。
        :param user_id: 用户ID。
        """
        try:
            self.cursor.execute(
                "UPDATE Users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating last login time: {e}")

    # --- 学生信息管理 ---

    def update_student_pinyin(self, student_id, name):
        """根据姓名更新学生的拼音首字母"""
        pinyin_initials = convert_to_pinyin_initials(name)
        try:
            self.cursor.execute("UPDATE Students SET name_pinyin = ? WHERE id = ?", (pinyin_initials, student_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating pinyin for student {student_id}: {e}")

    def get_all_students(self, filters=None, sort_by=None):
        """获取学生列表，支持过滤和排序"""
        query = "SELECT id, name, gender, enrollment_year, department, major, class_name, contact_info FROM Students ORDER BY id"
        # TODO: Add filtering and sorting logic
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_student_record(self, user_id, student_info):
        """添加单个学生记录，并创建关联的用户账号"""
        try:
            # 1. 创建学生记录
            self.cursor.execute(
                """INSERT INTO Students (name, gender, enrollment_year, department, major, class_name, contact_info, archive_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    student_info['name'], student_info['gender'], student_info['enrollment_year'],
                    student_info['department'], student_info['major'], student_info['class_name'],
                    student_info['contact_info'], student_info.get('archive_path')
                )
            )
            student_id = self.cursor.lastrowid
            self.update_student_pinyin(student_id, student_info['name'])

            # 2. 创建关联的用户账号 (使用学号作为默认用户名)
            username = str(student_id) # 使用自增ID作为学号和用户名
            hashed_password = hash_password(student_info['password'])
            self.cursor.execute(
                "INSERT INTO Users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
                (username, hashed_password, 'student', student_id)
            )
            
            self.conn.commit()
            self.log_action(user_id, 'ADD_STUDENT', f'Added student {student_info["name"]} with ID {student_id} and user account {username}')
            return student_id
        except sqlite3.IntegrityError as e:
            print(f"Error adding student (likely duplicate username): {e}")
            self.conn.rollback()
            return None
        except sqlite3.Error as e:
            print(f"Error adding student: {e}")
            self.conn.rollback()
            return None

    def get_student_by_id(self, student_id):
        """根据ID获取单个学生信息"""
        self.cursor.execute("SELECT * FROM Students WHERE id = ?", (student_id,))
        student_data = self.cursor.fetchone()
        if student_data:
            return dict(student_data)
        return None

    def update_student_record(self, user_id, student_id, new_info):
        """更新学生信息，并可选择重置密码"""
        try:
            self.cursor.execute(
                """UPDATE Students SET name=?, gender=?, enrollment_year=?, department=?, major=?, class_name=?, contact_info=?, archive_path=?
                   WHERE id=?""",
                (
                    new_info['name'], new_info['gender'], new_info['enrollment_year'],
                    new_info['department'], new_info['major'], new_info['class_name'],
                    new_info['contact_info'], new_info.get('archive_path'), student_id
                )
            )
            self.update_student_pinyin(student_id, new_info['name'])

            # 如果提供了新密码，则更新用户密码
            if new_info.get('password'):
                hashed_password = hash_password(new_info['password'])
                self.cursor.execute(
                    "UPDATE Users SET password_hash = ? WHERE student_id = ?",
                    (hashed_password, student_id)
                )
                self.log_action(user_id, 'RESET_PASSWORD', f'Reset password for student ID {student_id}')

            self.conn.commit()
            self.log_action(user_id, 'UPDATE_STUDENT', f'Updated student with ID {student_id}')
            return True
        except sqlite3.Error as e:
            print(f"Error updating student: {e}")
            self.conn.rollback()
            return False

    def delete_student_record(self, admin_id, student_id):
        """删除学生记录，并级联删除关联的用户账户和成绩"""
        try:
            # First, delete the associated user account
            self.cursor.execute("DELETE FROM Users WHERE student_id = ?", (student_id,))
            # Then, delete grades associated with the student
            self.cursor.execute("DELETE FROM Grades WHERE student_id = ?", (student_id,))
            # Finally, delete the student record
            self.cursor.execute("DELETE FROM Students WHERE id = ?", (student_id,))
            self.conn.commit()
            self.log_action(admin_id, 'DELETE_STUDENT', f'Deleted student with ID {student_id} and associated user account and grades.')
            return True
        except sqlite3.Error as e:
            print(f"Error deleting student: {e}")
            self.conn.rollback()
            return False

    def batch_import_students(self, admin_id, students_data):
        """
        从Excel批量导入学生数据，并自动创建用户账户。
        列顺序: 学院, 班级, 姓名, 性别, 入学年份, 身份证号, 联系方式
        """
        success_count = 0
        failure_count = 0
        errors = []
        for student_info in students_data:
            try:
                # 验证数据完整性
                required_fields = ['department', 'class', 'name', 'gender', 'enrollment_year', 'id_card']
                if not all(student_info.get(field) for field in required_fields):
                    failure_count += 1
                    errors.append(f"记录 {student_info} 缺少必要字段。")
                    continue

                # 1. 插入学生记录
                self.cursor.execute(
                    """INSERT INTO Students (department, class_name, name, gender, enrollment_year, id_card, contact_info)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        student_info['department'], student_info['class'], student_info['name'],
                        student_info['gender'], student_info['enrollment_year'], student_info['id_card'],
                        student_info.get('contact')
                    )
                )
                student_id = self.cursor.lastrowid
                self.update_student_pinyin(student_id, student_info['name'])

                # 2. 创建关联的用户账号
                # 使用学号作为用户名，身份证后六位作为默认密码
                username = str(student_id)
                default_password = str(student_info['id_card'])[-6:]
                hashed_password = hash_password(default_password)
                
                self.cursor.execute(
                    "INSERT INTO Users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
                    (username, hashed_password, 'student', student_id)
                )
                
                success_count += 1
            except sqlite3.IntegrityError as e:
                failure_count += 1
                errors.append(f"导入学生 {student_info.get('name', 'N/A')} 失败 (可能学号或用户名已存在): {e}")
                self.conn.rollback()
            except Exception as e:
                failure_count += 1
                errors.append(f"处理学生 {student_info.get('name', 'N/A')} 时发生未知错误: {e}")
                self.conn.rollback()

        self.conn.commit()
        if success_count > 0:
            self.log_action(admin_id, 'BATCH_IMPORT_STUDENTS', f'Batch imported {success_count} students.')
        return success_count, failure_count, errors

    def get_student_by_user_id(self, user_id):
        """根据用户ID获取学生信息"""
        self.cursor.execute("SELECT s.* FROM Students s JOIN Users u ON s.id = u.student_id WHERE u.id = ?", (user_id,))
        student_data = self.cursor.fetchone()
        if student_data:
            return dict(student_data)
        return None

    # --- 教师管理 ---

    def get_all_teachers_info(self):
        """获取所有教师的详细信息列表"""
        query = """
            SELECT t.id, u.username, t.name, t.title, t.department, t.contact_info, u.is_frozen
            FROM Teachers t
            JOIN Users u ON t.user_id = u.id
            ORDER BY t.id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_teacher(self, admin_id, teacher_info):
        """添加新教师及其用户账户"""
        try:
            # 1. 创建用户账户
            hashed_password = hash_password(teacher_info['password'])
            self.cursor.execute(
                "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                (teacher_info['username'], hashed_password, 'teacher')
            )
            user_id = self.cursor.lastrowid

            # 2. 创建教师记录
            self.cursor.execute(
                "INSERT INTO Teachers (user_id, name, title, department, contact_info) VALUES (?, ?, ?, ?, ?)",
                (user_id, teacher_info['name'], teacher_info.get('title'), teacher_info.get('department'), teacher_info.get('contact_info'))
            )
            self.conn.commit()
            self.log_action(admin_id, 'ADD_TEACHER', f"Added teacher {teacher_info['name']} with username {teacher_info['username']}")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return "username_exists" # 特殊返回值表示用户名已存在
        except sqlite3.Error as e:
            print(f"Error adding teacher: {e}")
            self.conn.rollback()
            return None

    def update_teacher(self, admin_id, teacher_id, new_info):
        """更新教师信息，并可选择重置密码"""
        try:
            # 获取关联的 user_id
            self.cursor.execute("SELECT user_id FROM Teachers WHERE id = ?", (teacher_id,))
            result = self.cursor.fetchone()
            if not result:
                return False
            user_id = result['user_id']

            # 更新 Teachers 表
            self.cursor.execute(
                "UPDATE Teachers SET name=?, title=?, department=?, contact_info=? WHERE id=?",
                (new_info['name'], new_info.get('title'), new_info.get('department'), new_info.get('contact_info'), teacher_id)
            )

            # 如果提供了新密码，则更新 Users 表
            if new_info.get('password'):
                hashed_password = hash_password(new_info['password'])
                self.cursor.execute("UPDATE Users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
                self.log_action(admin_id, 'RESET_PASSWORD', f'Reset password for teacher {new_info["name"]}')

            self.conn.commit()
            self.log_action(admin_id, 'UPDATE_TEACHER', f"Updated teacher {new_info['name']}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating teacher: {e}")
            self.conn.rollback()
            return False

    def delete_teacher(self, admin_id, teacher_id):
        """删除教师记录（关联的User记录会通过外键级联删除）"""
        try:
            self.cursor.execute("DELETE FROM Teachers WHERE id = ?", (teacher_id,))
            self.conn.commit()
            self.log_action(admin_id, 'DELETE_TEACHER', f'Deleted teacher with ID {teacher_id}')
            return True
        except sqlite3.Error as e:
            print(f"Error deleting teacher: {e}")
            self.conn.rollback()
            return False

    def batch_import_teachers(self, admin_id, teachers_data):
        """
        从Excel批量导入教师数据，并自动创建用户账户。
        列顺序: 学院, 姓名, 性别, 职称, 身份证号, 联系方式
        """
        success_count = 0
        failure_count = 0
        errors = []
        for teacher_info in teachers_data:
            try:
                # 验证数据
                required_fields = ['department', 'name', 'gender', 'title', 'id_card']
                if not all(teacher_info.get(field) for field in required_fields):
                    failure_count += 1
                    errors.append(f"记录 {teacher_info} 缺少必要字段。")
                    continue

                # 1. 创建用户账户
                # 使用姓名拼音作为建议用户名，身份证后六位作为默认密码
                username = convert_to_pinyin_initials(teacher_info['name'])
                # 检查用户名是否重复，如果重复则添加后缀
                temp_username = username
                counter = 1
                while self.check_username_exists(temp_username):
                    temp_username = f"{username}{counter}"
                    counter += 1
                username = temp_username
                
                default_password = str(teacher_info['id_card'])[-6:]
                hashed_password = hash_password(default_password)

                self.cursor.execute(
                    "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, hashed_password, 'teacher')
                )
                user_id = self.cursor.lastrowid

                # 2. 创建教师记录
                self.cursor.execute(
                    """INSERT INTO Teachers (user_id, name, gender, title, department, id_card, contact_info)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        user_id, teacher_info['name'], teacher_info['gender'], teacher_info['title'],
                        teacher_info['department'], teacher_info['id_card'], teacher_info.get('contact')
                    )
                )
                success_count += 1
            except sqlite3.IntegrityError as e:
                failure_count += 1
                errors.append(f"导入教师 {teacher_info.get('name', 'N/A')} 失败: {e}")
                self.conn.rollback()
            except Exception as e:
                failure_count += 1
                errors.append(f"处理教师 {teacher_info.get('name', 'N/A')} 时发生未知错误: {e}")
                self.conn.rollback()

        self.conn.commit()
        if success_count > 0:
            self.log_action(admin_id, 'BATCH_IMPORT_TEACHERS', f'Batch imported {success_count} teachers.')
        return success_count, failure_count, errors
             
    def get_teacher_by_user_id(self, user_id):
        """根据用户ID获取教师信息"""
        self.cursor.execute("SELECT * FROM Teachers WHERE user_id = ?", (user_id,))
        teacher_data = self.cursor.fetchone()
        if teacher_data:
            return dict(teacher_data)
        return None

    # --- 课程与成绩管理 ---

    def get_all_courses(self):
        """获取所有课程列表，并带上教师姓名"""
        query = """
            SELECT c.id, c.name, c.credits, u.username, c.semester, c.description, c.teacher_id
            FROM Courses c
            LEFT JOIN Users u ON c.teacher_id = u.id
            ORDER BY c.id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_all_teachers(self):
        """获取所有教师角色的用户（用于课程分配下拉框）"""
        query = """
            SELECT t.id, t.name
            FROM Teachers t
            JOIN Users u ON t.user_id = u.id
            WHERE u.role = 'teacher'
            ORDER BY t.name
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_course(self, admin_id, course_info):
        """添加新课程"""
        try:
            self.cursor.execute(
                "INSERT INTO Courses (name, credits, teacher_id, semester, description) VALUES (?, ?, ?, ?, ?)",
                (course_info['name'], course_info['credits'], course_info['teacher_id'], course_info['semester'], course_info.get('description', ''))
            )
            self.conn.commit()
            course_id = self.cursor.lastrowid
            self.log_action(admin_id, 'ADD_COURSE', f'Added course {course_info["name"]} with ID {course_id}')
            return course_id
        except sqlite3.Error as e:
            print(f"Error adding course: {e}")
            self.conn.rollback()
            return None

    def update_course(self, admin_id, course_id, new_info):
        """更新课程信息"""
        try:
            self.cursor.execute(
                "UPDATE Courses SET name=?, credits=?, teacher_id=?, semester=?, description=? WHERE id=?",
                (new_info['name'], new_info['credits'], new_info['teacher_id'], new_info['semester'], new_info.get('description', ''), course_id)
            )
            self.conn.commit()
            self.log_action(admin_id, 'UPDATE_COURSE', f'Updated course with ID {course_id}')
            return True
        except sqlite3.Error as e:
            print(f"Error updating course: {e}")
            self.conn.rollback()
            return False

    def delete_course(self, admin_id, course_id):
        """删除课程"""
        try:
            # Also delete associated grades
            self.cursor.execute("DELETE FROM Grades WHERE course_id = ?", (course_id,))
            self.cursor.execute("DELETE FROM Courses WHERE id = ?", (course_id,))
            self.conn.commit()
            self.log_action(admin_id, 'DELETE_COURSE', f'Deleted course with ID {course_id} and its grades.')
            return True
        except sqlite3.Error as e:
            print(f"Error deleting course: {e}")
            self.conn.rollback()
            return False

    def get_courses_by_teacher(self, teacher_id):
        """获取某位教师教授的所有课程"""
        self.cursor.execute("SELECT id, name, semester FROM Courses WHERE teacher_id = ?", (teacher_id,))
        return self.cursor.fetchall()

    def get_student_grades_by_course(self, course_id):
        """
        获取指定课程的所有学生及其成绩。
        这将返回所有学生，以及他们在这门课上的成绩（如果有的话）。
        """
        query = """
            SELECT s.id, s.name, s.class_name, g.score
            FROM Students s
            LEFT JOIN Grades g ON s.id = g.student_id AND g.course_id = ?
            ORDER BY s.id
        """
        self.cursor.execute(query, (course_id,))
        return self.cursor.fetchall()

    def assign_grade(self, recorder_id, student_id, course_id, score):
        """为学生录入/修改成绩. 如果成绩已存在则更新，否则插入."""
        try:
            # 检查成绩是否已存在
            self.cursor.execute(
                "SELECT id FROM Grades WHERE student_id = ? AND course_id = ?",
                (student_id, course_id)
            )
            grade_exists = self.cursor.fetchone()

            if score is None or score == '':
                # 如果分数是空的，认为是删除成绩
                if grade_exists:
                    self.cursor.execute("DELETE FROM Grades WHERE id = ?", (grade_exists[0],))
                    action = 'DELETE_GRADE'
                    self.log_action(recorder_id, action, f'Deleted grade for student {student_id} for course {course_id}')
            elif grade_exists:
                # 更新现有成绩
                self.cursor.execute(
                    "UPDATE Grades SET score = ?, recorded_at = CURRENT_TIMESTAMP, recorder_id = ? WHERE id = ?",
                    (score, recorder_id, grade_exists[0])
                )
                action = 'UPDATE_GRADE'
                self.log_action(recorder_id, action, f'Updated score to {score} for student {student_id} for course {course_id}')
            else:
                # 插入新成绩
                self.cursor.execute(
                    "INSERT INTO Grades (student_id, course_id, score, recorder_id) VALUES (?, ?, ?, ?)",
                    (student_id, course_id, score, recorder_id)
                )
                action = 'ADD_GRADE'
                self.log_action(recorder_id, action, f'Added score {score} for student {student_id} for course {course_id}')

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error assigning grade: {e}")
            self.conn.rollback()
            return False

    def get_grades_by_student(self, student_id):
        """获取某个学生的所有成绩"""
        query = """
            SELECT c.name, c.credits, c.semester, u.username, g.score
            FROM Grades g
            JOIN Courses c ON g.course_id = c.id
            LEFT JOIN Users u ON c.teacher_id = u.id
            WHERE g.student_id = ?
        """
        self.cursor.execute(query, (student_id,))
        return self.cursor.fetchall()

    def get_action_logs(self, role):
        query = """
        SELECT al.id, u.username, al.action_type, al.description, al.timestamp
        FROM ActionLogs al
        JOIN Users u ON al.user_id = u.id
        ORDER BY al.timestamp DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def log_action(self, user_id, action_type, description):
        query = "INSERT INTO ActionLogs (user_id, action_type, description) VALUES (?, ?, ?)"
        self.cursor.execute(query, (user_id, action_type, description))
        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            print("数据库连接已关闭。")