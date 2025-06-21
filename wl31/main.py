# wl31/main.py
# 描述: 应用程序的主入口和逻辑控制中心。

import sys
import os

# 将项目根目录添加到 sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QMainWindow, QTableWidgetItem, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap
import io

# --- 项目模块导入 ---
from wl31.ui.login_window import Ui_LoginWindow
from wl31.ui.main_window import Ui_MainWindow
from wl31.ui.student_dialog import Ui_StudentDialog
from wl31.ui.course_management_tab import CourseManagementTab
from wl31.ui.grade_management_tab import GradeManagementTab
from wl31.ui.my_grades_tab import MyGradesTab
from wl31.ui.data_analysis_tab import DataAnalysisTab
from wl31.ui.teacher_management_tab import TeacherManagementTab
from wl31.ui.action_log_tab import ActionLogTab
from wl31.ui.profile_dialog import ProfileDialog
from wl31.database.database_manager import DatabaseManager
from wl31.utils.captcha import Captcha
from wl31.utils.hash_utils import hash_password, verify_password
from wl31.utils import excel_utils
from wl31 import config

# --- 全局变量 ---
db_manager = DatabaseManager(config.DATABASE_PATH)
captcha_generator = Captcha()
current_user = None

# --- 登录窗口逻辑 ---
class LoginController(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        
        self.captcha_text = ""

        # 连接信号和槽
        self.ui.wl_login_button.clicked.connect(self.handle_login)
        self.ui.wl_captcha_image.mousePressEvent = self.refresh_captcha # 点击图片刷新

        self.refresh_captcha()

    def refresh_captcha(self, event=None):
        self.captcha_text, captcha_image_pil = captcha_generator.generate()
        
        # Convert PIL image to QPixmap using a buffer to avoid version conflicts
        buffer = io.BytesIO()
        captcha_image_pil.save(buffer, "PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue(), "PNG")

        self.ui.wl_captcha_image.setPixmap(pixmap)
        self.ui.wl_status_label.setText("") # 清除状态信息

    def handle_login(self):
        # 1. 获取输入
        username = self.ui.wl_username_input.text().strip()
        password = self.ui.wl_password_input.text()
        role_text = self.ui.wl_role_combobox.currentText()
        role_map = {"学生": "student", "教师": "teacher", "管理员": "admin"}
        role = role_map.get(role_text)
        captcha_input = self.ui.wl_captcha_input.text().strip()

        # 2. 验证输入
        if not all([username, password, captcha_input]):
            self.ui.wl_status_label.setText("错误：所有字段均为必填项！")
            self.refresh_captcha()
            return
        
        if captcha_input.lower() != self.captcha_text.lower():
            QMessageBox.warning(self, "登录失败", "验证码错误。")
            self.refresh_captcha()
            return

        # 3. 验证用户
        user_data = db_manager.get_user(username)

        if user_data and user_data['role'] == role and verify_password(password, user_data['password_hash']):
            if user_data['is_frozen']:
                QMessageBox.warning(self, "登录失败", "该账户已被冻结！")
                self.refresh_captcha()
                return
            
            global current_user
            current_user = user_data
            db_manager.update_last_login_time(current_user['id'])
            self.accept() # 验证成功，关闭登录窗口
        else:
            QMessageBox.warning(self, "登录失败", "用户名、密码或角色错误。")
            self.refresh_captcha()



# --- 学生信息对话框逻辑 ---
class StudentDialogController(QDialog):
    def __init__(self, student_id=None):
        super().__init__()
        self.ui = Ui_StudentDialog()
        self.ui.setupUi(self)
        self.student_id = student_id
        self.archive_path = None # 初始化档案路径

        # 连接信号
        self.ui.select_archive_button.clicked.connect(self.select_archive_file)

        if self.student_id:
            self.setWindowTitle("编辑学生信息")
            self.load_student_data()
        else:
            self.setWindowTitle("新增学生")

    def load_student_data(self):
        student_data = db_manager.get_student_by_id(self.student_id)
        if not student_data:
            QMessageBox.critical(self, "错误", "无法加载学生数据。")
            self.reject()
            return
        
        self.ui.name_input.setText(student_data['name'] or '')
        self.ui.gender_combobox.setCurrentText(student_data['gender'] or '男')
        self.ui.enrollment_year_combobox.setCurrentText(str(student_data['enrollment_year'] or ''))
        self.ui.department_combobox.setCurrentText(student_data['department'] or '')
        # 触发一次专业更新，以防学院加载后专业列表不匹配
        self.ui.update_majors()
        self.ui.major_combobox.setCurrentText(student_data['major'] or '')
        self.ui.class_input.setText(student_data['class_name'] or '')
        self.ui.contact_input.setText(student_data['contact_info'] or '')
        
        self.archive_path = student_data['archive_path']
        if self.archive_path:
            self.ui.archive_path_label.setText(os.path.basename(self.archive_path))
        else:
            self.ui.archive_path_label.setText("未选择文件")


    def select_archive_file(self):
        """打开文件对话框以选择档案文件"""
        path, _ = QFileDialog.getOpenFileName(self, "选择档案文件", "", "文件 (*.pdf *.png *.jpg *.jpeg)")
        if path:
            self.archive_path = path
            self.ui.archive_path_label.setText(os.path.basename(path)) # 显示文件名

    def get_student_data(self):
        return {
            "name": self.ui.name_input.text().strip(),
            "gender": self.ui.gender_combobox.currentText(),
            "enrollment_year": self.ui.enrollment_year_combobox.currentText(),
            "department": self.ui.department_combobox.currentText(),
            "major": self.ui.major_combobox.currentText(),
            "class_name": self.ui.class_input.text().strip(),
            "contact_info": self.ui.contact_input.text().strip(),
            "archive_path": self.archive_path,
            "password": self.ui.password_input.text() # Can be empty
        }


# --- 主窗口逻辑 ---
class MainWindowController(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.user_info = user_info

        self.setup_menu()
        self.update_status_bar()
        self.setup_tabs_for_role()
        self.connect_signals()

    def setup_menu(self):
        """设置菜单栏"""
        # 新增动作
        self.ui.action_data_analysis = QtWidgets.QAction(self)
        self.ui.action_data_analysis.setObjectName("action_data_analysis")
        self.ui.action_log_view = QtWidgets.QAction(self)
        self.ui.action_log_view.setObjectName("action_log_view")
        self.ui.action_change_password = QtWidgets.QAction(self)
        self.ui.action_change_password.setObjectName("action_change_password")

        # 添加到菜单
        self.ui.menu_manage.addAction(self.ui.action_data_analysis)
        self.ui.menu_manage.addAction(self.ui.action_log_view)
        self.ui.menu_file.addAction(self.ui.action_change_password)
        
        # 设置文本
        self.ui.action_data_analysis.setText("数据分析")
        self.ui.action_log_view.setText("操作日志")
        self.ui.action_change_password.setText("修改密码")

    def connect_signals(self):
        """连接所有信号到槽"""
        # 菜单项
        self.ui.action_change_password.triggered.connect(self.open_profile_dialog)
        self.ui.action_exit.triggered.connect(self.close)

        # 学生管理
        if hasattr(self, 'student_management_tab'):
            self.ui.student_add_button.clicked.connect(self.add_student)
            self.ui.student_edit_button.clicked.connect(self.edit_student)
            self.ui.student_delete_button.clicked.connect(self.delete_student)

            self.ui.student_import_button.clicked.connect(self.handle_student_batch_import)

        # 数据分析
        if hasattr(self, 'data_analysis_tab'):
            self.data_analysis_tab.search_grades_button.clicked.connect(self.query_grades)
            self.data_analysis_tab.search_pinyin_button.clicked.connect(self.search_student_by_pinyin)
            self.data_analysis_tab.calculate_stats_button.clicked.connect(self.calculate_stats)
            self.data_analysis_tab.export_button.clicked.connect(self.export_data_analysis_results)

        # 教师管理
        if hasattr(self, 'teacher_management_tab'):
            self.teacher_management_tab.import_button.clicked.connect(self.handle_teacher_batch_import)

    def setup_tabs_for_role(self):
        """根据用户角色动态创建和设置选项卡"""
        role = self.user_info['role']
        
        # 清除除欢迎页外的所有标签页
        while self.ui.tabWidget.count() > 1:
            self.ui.tabWidget.removeTab(1)

        if role == 'admin':
            self.setup_student_management_tab()
            self.setup_teacher_management_tab()
            self.setup_course_management_tab()
            self.setup_grade_management_tab()
            self.setup_data_analysis_tab()
            self.setup_action_log_tab()
        elif role == 'teacher':
            self.setup_grade_management_tab()
            self.setup_data_analysis_tab()
        elif role == 'student':
            self.setup_my_grades_tab()
        
        self.configure_menu_by_role(role)

    def configure_menu_by_role(self, role):
        """根据角色配置菜单可见性"""
        is_admin = (role == 'admin')
        is_teacher = (role == 'teacher')
        
        self.ui.action_student_manage.setVisible(is_admin)
        self.ui.action_course_manage.setVisible(is_admin)
        self.ui.action_grade_manage.setVisible(is_admin or is_teacher)
        self.ui.action_data_analysis.setVisible(is_admin or is_teacher)
        self.ui.action_log_view.setVisible(is_admin)

    def setup_student_management_tab(self):
        """设置学生管理选项卡"""
        self.student_management_tab = self.ui.student_management_tab
        self.ui.tabWidget.addTab(self.student_management_tab, "学生信息管理")
        self.load_students()

    def setup_teacher_management_tab(self):
        """设置教师管理选项卡"""
        self.teacher_management_tab = TeacherManagementTab(db_manager, self.user_info)
        self.ui.tabWidget.addTab(self.teacher_management_tab, "教师信息管理")

    def setup_course_management_tab(self):
        """设置课程管理选项卡"""
        self.course_management_tab = CourseManagementTab(db_manager, self.user_info['id'])
        self.ui.tabWidget.addTab(self.course_management_tab, "课程管理")

    def setup_grade_management_tab(self):
        """设置成绩管理选项卡"""
        self.grade_management_tab = GradeManagementTab(db_manager, self.user_info)
        self.ui.tabWidget.addTab(self.grade_management_tab, "成绩管理")

    def setup_my_grades_tab(self):
        """设置我的成绩选项卡"""
        self.my_grades_tab = MyGradesTab(db_manager, self.user_info)
        self.ui.tabWidget.addTab(self.my_grades_tab, "我的成绩")

    def setup_data_analysis_tab(self):
        """设置数据分析选项卡"""
        self.data_analysis_tab = DataAnalysisTab(db_manager, self.user_info)
        self.ui.tabWidget.addTab(self.data_analysis_tab, "数据分析")
        self.load_data_for_analysis_tab()


    def setup_action_log_tab(self):
        """设置操作日志选项卡"""
        self.action_log_tab = ActionLogTab(db_manager, self.user_info)
        self.ui.tabWidget.addTab(self.action_log_tab, "操作日志")

    def load_students(self):
        """从数据库加载学生信息并填充到表格中"""
        # 修正：严格按照 学号, 姓名, 性别, 入学年份, 院系, 专业, 班级, 联系方式 的顺序
        headers = ["学号", "姓名", "性别", "入学年份", "院系", "专业", "班级", "联系方式"]
        self.ui.student_table.setColumnCount(len(headers))
        self.ui.student_table.setHorizontalHeaderLabels(headers)
        
        students = db_manager.get_all_students()
        self.ui.student_table.setRowCount(0)
        for row, student in enumerate(students):
            self.ui.student_table.insertRow(row)
            # 数据库字段: id, name, gender, enrollment_year, department, major, class_name, contact_info
            self.ui.student_table.setItem(row, 0, QTableWidgetItem(str(student['id'])))
            self.ui.student_table.setItem(row, 1, QTableWidgetItem(student['name']))
            self.ui.student_table.setItem(row, 2, QTableWidgetItem(student['gender']))
            self.ui.student_table.setItem(row, 3, QTableWidgetItem(str(student['enrollment_year'])))
            self.ui.student_table.setItem(row, 4, QTableWidgetItem(student['department']))
            self.ui.student_table.setItem(row, 5, QTableWidgetItem(student['major']))
            self.ui.student_table.setItem(row, 6, QTableWidgetItem(student['class_name']))
            self.ui.student_table.setItem(row, 7, QTableWidgetItem(student['contact_info']))
        self.ui.student_table.resizeColumnsToContents()

    def add_student(self):
        """打开新增学生对话框"""
        dialog = StudentDialogController()
        if dialog.exec_() == QDialog.Accepted:
            student_data = dialog.get_student_data()
            # 验证必填项
            required_fields = ['name', 'enrollment_year', 'class_name', 'password']
            if not all(student_data.get(field) for field in required_fields):
                 QMessageBox.warning(self, "警告", "姓名、入学年份、班级和初始密码为必填项。")
                 return

            student_id = db_manager.add_student_record(self.user_info['id'], student_data)
            if student_id:
                self.load_students() # 重新加载列表
                QMessageBox.information(self, "成功", f"学生 {student_data['name']} 已成功添加，学号/用户名为 {student_id}。")
            else:
                QMessageBox.critical(self, "错误", "添加学生失败，可能是学号/用户名已存在。")

    def edit_student(self):
        """打开编辑学生对话框"""
        selected_rows = self.ui.student_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要编辑的学生。")
            return
        
        student_id_str = self.ui.student_table.item(selected_rows[0].row(), 0).text()
        student_id = int(student_id_str)

        dialog = StudentDialogController(student_id=student_id)
        if dialog.exec_() == QDialog.Accepted:
            student_data = dialog.get_student_data()
            # 验证必填项 (密码可选)
            required_fields = ['name', 'enrollment_year', 'class_name']
            if not all(student_data.get(field) for field in required_fields):
                 QMessageBox.warning(self, "警告", "姓名、入学年份和班级为必填项。")
                 return

            if db_manager.update_student_record(self.user_info['id'], student_id, student_data):
                self.load_students()
                QMessageBox.information(self, "成功", "学生信息已成功更新。")
            else:
                QMessageBox.critical(self, "错误", "更新学生信息失败。")


    def delete_student(self):
        """删除选定的学生"""
        selected_rows = self.ui.student_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的学生。")
            return

        reply = QMessageBox.question(self, '确认删除', '您确定要删除选定的学生记录吗？此操作将同时删除关联的用户账号和成绩记录，且不可恢复。',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 从UI和数据库中删除
            # 从后往前删，避免索引错乱
            for row in sorted([r.row() for r in selected_rows], reverse=True):
                student_id = self.ui.student_table.item(row, 0).text()
                if db_manager.delete_student_record(self.user_info['id'], int(student_id)):
                    self.ui.student_table.removeRow(row)
                else:
                    QMessageBox.critical(self, "错误", f"删除学生ID {student_id} 时失败。")
            QMessageBox.information(self, "成功", "所选学生记录已删除。")

    def handle_student_batch_import(self):
        """处理批量导入学生数据"""
        path, _ = QFileDialog.getOpenFileName(self, "选择学生信息Excel文件", "", "Excel 文件 (*.xlsx *.xls)")
        if not path:
            return

        try:
            students_data = excel_utils.import_students_from_excel(path)
            if students_data is None: # 函数出错返回None
                QMessageBox.critical(self, "错误", "读取Excel文件失败，请检查文件格式或内容。")
                return
            if not students_data: # 文件为空或只有标题行
                QMessageBox.warning(self, "警告", "Excel文件中没有找到有效数据（已跳过首行）。")
                return

            success_count, failure_count, errors = db_manager.batch_import_students(self.user_info['id'], students_data)

            summary_message = f"学生导入完成。\n成功导入 {success_count} 条记录。\n失败 {failure_count} 条记录。"
            if errors:
                error_details = "\n\n失败详情:\n" + "\n".join(errors[:10]) # 最多显示10条错误
                summary_message += error_details
            
            QMessageBox.information(self, "导入结果", summary_message)
            self.load_students() # 刷新学生列表

        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理文件时发生未知错误: {e}")

    def handle_teacher_batch_import(self):
        """处理批量导入教师数据"""
        path, _ = QFileDialog.getOpenFileName(self, "选择教师信息Excel文件", "", "Excel 文件 (*.xlsx *.xls)")
        if not path:
            return

        try:
            teachers_data = excel_utils.import_teachers_from_excel(path)
            if teachers_data is None:
                QMessageBox.critical(self, "错误", "读取Excel文件失败，请检查文件格式或内容。")
                return
            if not teachers_data:
                QMessageBox.warning(self, "警告", "Excel文件中没有找到有效数据（已跳过首行）。")
                return

            # 假设 db_manager 中有 batch_import_teachers 方法
            success_count, failure_count, errors = db_manager.batch_import_teachers(self.user_info['id'], teachers_data)

            summary_message = f"教师导入完成。\n成功导入 {success_count} 条记录。\n失败 {failure_count} 条记录。"
            if errors:
                error_details = "\n\n失败详情:\n" + "\n".join(errors[:10])
                summary_message += error_details
            
            QMessageBox.information(self, "导入结果", summary_message)
            self.teacher_management_tab.load_teachers() # 刷新教师列表

        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理文件时发生未知错误: {e}")

    def open_profile_dialog(self):
        """打开修改个人信息对话框"""
        dialog = ProfileDialog(db_manager, self.user_info, self)
        dialog.exec_()

    def load_data_for_analysis_tab(self):
        """为数据分析选项卡加载课程和班级列表"""
        # 加载课程
        courses = db_manager.get_all_courses()
        self.data_analysis_tab.course_name_combo.clear()
        self.data_analysis_tab.course_combo_stats.clear()
        self.data_analysis_tab.course_name_combo.addItem("所有课程", None)
        self.data_analysis_tab.course_combo_stats.addItem("请选择课程", None)
        for course in courses:
            self.data_analysis_tab.course_name_combo.addItem(course['name'], course['id'])
            self.data_analysis_tab.course_combo_stats.addItem(course['name'], course['id'])
        
        # 加载班级
        # A bit inefficient, but works for now.
        students = db_manager.get_all_students()
        classes = sorted(list(set(s['class_name'] for s in students if s['class_name'])))
        self.data_analysis_tab.class_combo.clear()
        self.data_analysis_tab.class_combo.addItem("请选择班级", None)
        for class_name in classes:
            self.data_analysis_tab.class_combo.addItem(class_name)

    def query_grades(self):
        """处理成绩组合查询"""
        student_id = self.data_analysis_tab.student_id_input.text().strip()
        course_id = self.data_analysis_tab.course_name_combo.currentData()
        
        if not student_id and not course_id:
            QMessageBox.warning(self, "提示", "请输入学号或选择一门课程进行查询。")
            return
            
        results = db_manager.query_grades(student_id if student_id else None, course_id)
        table = self.data_analysis_tab.result_table
        table.setRowCount(0)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["学号", "姓名", "课程", "成绩"])
        for row, data in enumerate(results):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(data['student_id'])))
            table.setItem(row, 1, QTableWidgetItem(data['student_name']))
            table.setItem(row, 2, QTableWidgetItem(data['course_name']))
            table.setItem(row, 3, QTableWidgetItem(str(data['score'])))

    def search_student_by_pinyin(self):
        """处理姓名拼音模糊搜索"""
        pinyin = self.data_analysis_tab.pinyin_input.text().strip()
        if not pinyin:
            QMessageBox.warning(self, "提示", "请输入拼音首字母进行搜索。")
            return
        
        results = db_manager.search_students_by_pinyin(pinyin)
        table = self.data_analysis_tab.result_table
        table.setRowCount(0)
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["学号", "姓名", "班级"])
        for row, data in enumerate(results):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(data['id'])))
            table.setItem(row, 1, QTableWidgetItem(data['name']))
            table.setItem(row, 2, QTableWidgetItem(data['class_name']))

    def calculate_stats(self):
        """处理班级课程统计"""
        class_name = self.data_analysis_tab.class_combo.currentText()
        course_id = self.data_analysis_tab.course_combo_stats.currentData()

        if not class_name or class_name == "请选择班级" or not course_id:
            QMessageBox.warning(self, "提示", "请选择一个班级和一门课程。")
            return
            
        stats = db_manager.calculate_class_grade_stats(class_name, course_id)
        result_text = (f"统计结果: \n"
                       f"  - 人数: {stats['count']}\n"
                       f"  - 平均分: {stats['average']}\n"
                       f"  - 标准差: {stats['std_dev']}\n"
                       f"  - 及格率: {stats['pass_rate']}%")
        self.data_analysis_tab.stats_result_label.setText(result_text)

    def export_data_analysis_results(self):
        """导出数据分析表格中的数据到Excel"""
        table = self.data_analysis_tab.result_table
        if table.rowCount() == 0:
            QMessageBox.warning(self, "提示", "表格中没有数据可以导出。")
            return

        path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "Excel 文件 (*.xlsx)")
        if not path:
            return

        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        data = []
        for row in range(table.rowCount()):
            row_data = [table.item(row, col).text() for col in range(table.columnCount())]
            data.append(row_data)

        if excel_utils.export_to_excel(data, headers, path):
            QMessageBox.information(self, "成功", f"数据已成功导出到 {path}")
        else:
            QMessageBox.critical(self, "错误", "导出数据时发生错误。")

    def update_status_bar(self):
        """更新状态栏信息"""
        role_map = {"admin": "管理员", "teacher": "教师", "student": "学生"}
        role = self.user_info['role']
        role_text = role_map.get(role, '未知')
        
        # 根据角色获取姓名
        user_id = self.user_info['id']
        name = "N/A"
        if role == 'student':
            student_info = db_manager.get_student_by_user_id(user_id)
            if student_info:
                name = student_info['name'] or self.user_info['username']
        elif role == 'teacher':
            teacher_info = db_manager.get_teacher_by_user_id(user_id)
            if teacher_info:
                 name = teacher_info['name'] or self.user_info['username']
        else: # Admin
            name = self.user_info['username']


        # 重新从数据库获取最新的登录时间
        fresh_user_data = db_manager.get_user_by_id(user_id)
        last_login = fresh_user_data['last_login_at'] if fresh_user_data and fresh_user_data['last_login_at'] else '首次登录'

        status_text = f"欢迎您，{role_text} {name}！ | 上次登录时间：{last_login}"
        self.ui.statusbar.showMessage(status_text)


# --- 程序入口 ---
def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True) # 主窗口关闭时退出程序

    login_window = LoginController()
    
    # 显示登录窗口，如果登录成功 (dialog accepted)
    if login_window.exec_() == QDialog.Accepted:
        main_window = MainWindowController(current_user)
        main_window.show()
        sys.exit(app.exec_())
    # 如果登录被取消，程序将在这里自然结束

if __name__ == "__main__":
    try:
        main()
    finally:
        db_manager.close() # 确保程序退出时关闭数据库连接
        print("数据库连接已关闭。")