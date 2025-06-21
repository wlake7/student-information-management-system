# wl31/ui/course_management_tab.py
# 描述: 课程管理选项卡的UI和逻辑。

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                             QPushButton, QLineEdit, QDialog, QFormLayout,
                             QMessageBox, QHeaderView, QComboBox, QLabel, QDoubleSpinBox)
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtCore import Qt

class CourseManagementTab(QWidget):
    """
    课程管理选项卡，提供课程的CRUD功能。
    """
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user_id = user_id
        self.init_ui()
        self.load_courses()

    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("按课程名称搜索...")
        self.search_input.textChanged.connect(self.search_courses)
        self.add_button = QPushButton("添加课程")
        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button = QPushButton("修改课程")
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button = QPushButton("删除课程")
        self.delete_button.clicked.connect(self.delete_course)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.edit_button)
        toolbar_layout.addWidget(self.delete_button)
        layout.addLayout(toolbar_layout)

        # 课程表格
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setEditTriggers(QTableView.NoEditTriggers)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_view)

    def load_courses(self):
        """从数据库加载课程数据到表格"""
        self.courses_data = self.db_manager.get_all_courses()
        
        # 使用 QSqlTableModel 来展示数据
        # 注意：这里我们手动获取数据，然后填充模型，而不是直接连接数据库
        # 这样可以更好地控制数据展示和与我们现有的db_manager集成
        # 为了简单起见，我们这里直接用 QStandardItemModel
        from PyQt5.QtGui import QStandardItemModel, QStandardItem

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['ID', '课程名称', '学分', '授课教师', '开课学期', '描述'])
        
        for row_data in self.courses_data:
            row = [QStandardItem(str(item)) for item in row_data[:6]] # teacher_id不显示
            self.model.appendRow(row)

        self.table_view.setModel(self.model)
        self.table_view.hideColumn(0) # 隐藏ID列
        self.table_view.hideColumn(6) # 隐藏teacher_id列

    def search_courses(self, text):
        """根据搜索文本过滤课程"""
        for i in range(self.model.rowCount()):
            match = text.lower() in self.model.item(i, 1).text().lower()
            self.table_view.setRowHidden(i, not match)

    def open_add_dialog(self):
        """打开添加课程的对话框"""
        dialog = CourseDialog(self.db_manager, self)
        if dialog.exec_():
            self.load_courses() # 刷新列表

    def open_edit_dialog(self):
        """打开编辑课程的对话框"""
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要修改的课程。")
            return

        row_index = selected_rows[0].row()
        course_id = self.model.item(row_index, 0).text()
        
        # 从原始数据中找到完整信息
        course_data = next((c for c in self.courses_data if str(c[0]) == course_id), None)
        if not course_data:
            QMessageBox.critical(self, "错误", "找不到所选课程的数据。")
            return

        dialog = CourseDialog(self.db_manager, self, course_data=course_data)
        if dialog.exec_():
            self.load_courses()

    def delete_course(self):
        """删除选定的课程"""
        selected_rows = self.table_view.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的课程。")
            return

        row_index = selected_rows[0].row()
        course_id = self.model.item(row_index, 0).text()
        course_name = self.model.item(row_index, 1).text()

        reply = QMessageBox.question(self, "确认删除", f"确定要删除课程 '{course_name}' 吗？\n这将同时删除所有与该课程相关的学生成绩。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_course(self.current_user_id, int(course_id)):
                QMessageBox.information(self, "成功", f"课程 '{course_name}' 已被删除。")
                self.load_courses()
            else:
                QMessageBox.critical(self, "失败", "删除课程时发生错误。")


class CourseDialog(QDialog):
    """
    用于添加或编辑课程的对话框。
    """
    def __init__(self, db_manager, parent=None, course_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.course_data = course_data
        self.is_edit_mode = course_data is not None
        self.init_ui()
        self.load_teachers()
        if self.is_edit_mode:
            self.populate_data()

    def init_ui(self):
        self.setWindowTitle("编辑课程" if self.is_edit_mode else "添加课程")
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.credits_input = QDoubleSpinBox()
        self.credits_input.setRange(0, 20)
        self.credits_input.setDecimals(1)
        self.credits_input.setSingleStep(0.5)
        self.teacher_combo = QComboBox()
        self.semester_input = QLineEdit()
        self.semester_input.setPlaceholderText("例如: 2024-2025秋季")
        self.description_input = QLineEdit()

        layout.addRow("课程名称:", self.name_input)
        layout.addRow("学分:", self.credits_input)
        layout.addRow("授课教师:", self.teacher_combo)
        layout.addRow("开课学期:", self.semester_input)
        layout.addRow("描述:", self.description_input)

        # 按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_course)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)

    def load_teachers(self):
        """加载教师列表到下拉框"""
        self.teacher_combo.addItem("无", None) # 允许不指定教师
        teachers = self.db_manager.get_all_teachers()
        for teacher_id, username in teachers:
            self.teacher_combo.addItem(username, teacher_id)

    def populate_data(self):
        """如果是编辑模式，则填充现有数据"""
        course_id, name, credits, teacher_name, semester, description, teacher_id = self.course_data
        self.name_input.setText(name)
        self.credits_input.setValue(float(credits))
        self.semester_input.setText(semester)
        self.description_input.setText(description or "")
        
        # 设置教师下拉框的选中项
        if teacher_id:
            index = self.teacher_combo.findData(teacher_id)
            if index != -1:
                self.teacher_combo.setCurrentIndex(index)
        else:
            self.teacher_combo.setCurrentIndex(0) # "无"

    def save_course(self):
        """保存课程信息到数据库"""
        course_info = {
            'name': self.name_input.text().strip(),
            'credits': self.credits_input.value(),
            'teacher_id': self.teacher_combo.currentData(),
            'semester': self.semester_input.text().strip(),
            'description': self.description_input.text().strip()
        }

        if not course_info['name'] or not course_info['semester']:
            QMessageBox.warning(self, "输入错误", "课程名称和开课学期不能为空。")
            return

        admin_id = self.parent().current_user_id

        if self.is_edit_mode:
            # 更新课程
            success = self.db_manager.update_course(admin_id, self.course_data[0], course_info)
            message = "课程信息更新成功！" if success else "更新失败。"
        else:
            # 添加新课程
            success = self.db_manager.add_course(admin_id, course_info)
            message = "课程添加成功！" if success else "添加失败，可能是课程名称已存在。"

        if success:
            QMessageBox.information(self, "成功", message)
            self.accept()
        else:
            QMessageBox.critical(self, "失败", message)