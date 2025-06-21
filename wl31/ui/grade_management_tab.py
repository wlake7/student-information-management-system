# wl31/ui/grade_management_tab.py
# 描述: 成绩管理选项卡的UI和逻辑。

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                             QPushButton, QComboBox, QLabel, QMessageBox, QHeaderView)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class GradeManagementTab(QWidget):
    """
    成绩管理选项卡，允许教师和管理员录入、修改和查看成绩。
    """
    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user = current_user
        self.init_ui()
        self.load_courses_for_user()

    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)

        # 顶部选择区域
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("选择课程:"))
        self.course_combo = QComboBox()
        self.course_combo.currentIndexChanged.connect(self.on_course_selected)
        selection_layout.addWidget(self.course_combo)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)

        # 成绩表格
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 允许编辑成绩列
        self.table_view.doubleClicked.connect(self.on_table_double_clicked)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['学号', '姓名', '班级', '成绩'])
        self.table_view.setModel(self.model)
        self.model.itemChanged.connect(self.on_grade_changed)

        layout.addWidget(self.table_view)

    def load_courses_for_user(self):
        """根据用户角色加载课程列表"""
        self.course_combo.clear()
        self.course_combo.addItem("请选择课程...", None)

        if self.current_user['role'] == 'admin':
            # 管理员可以查看所有课程
            courses = self.db_manager.get_all_courses()
            for course in courses:
                # course format: (id, name, credits, teacher_name, semester, description, teacher_id)
                display_name = f"{course[1]} ({course[4]})"
                self.course_combo.addItem(display_name, course[0])
        elif self.current_user['role'] == 'teacher':
            # 教师只能查看自己教的课程
            courses = self.db_manager.get_courses_by_teacher(self.current_user['id'])
            for course_id, course_name, semester in courses:
                display_name = f"{course_name} ({semester})"
                self.course_combo.addItem(display_name, course_id)

    def on_course_selected(self, index):
        """当选择的课程变化时，加载该课程的学生和成绩"""
        course_id = self.course_combo.itemData(index)
        if course_id is None:
            self.model.removeRows(0, self.model.rowCount())
            return

        self.current_course_id = course_id
        student_grades = self.db_manager.get_student_grades_by_course(course_id)
        
        self.model.itemChanged.disconnect(self.on_grade_changed) # 临时断开信号
        self.model.removeRows(0, self.model.rowCount())

        for student_id, name, class_name, score in student_grades:
            id_item = QStandardItem(str(student_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable) # 学号不可编辑
            
            name_item = QStandardItem(name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable) # 姓名不可编辑

            class_item = QStandardItem(class_name or "")
            class_item.setFlags(class_item.flags() & ~Qt.ItemIsEditable) # 班级不可编辑

            score_text = str(score) if score is not None else ""
            score_item = QStandardItem(score_text)
            # 成绩列可编辑
            
            self.model.appendRow([id_item, name_item, class_item, score_item])
        
        self.model.itemChanged.connect(self.on_grade_changed) # 重新连接信号

    def on_table_double_clicked(self, index):
        """双击时，确保该列是成绩列才进入编辑模式"""
        if index.column() != 3: # 只有成绩列 (第4列)
            return
        self.table_view.edit(index)

    def on_grade_changed(self, item):
        """当成绩单元格内容改变时，保存到数据库"""
        if item.column() != 3:
            return

        row = item.row()
        student_id = int(self.model.item(row, 0).text())
        score_text = item.text().strip()

        try:
            # 允许输入空字符串来删除成绩
            score = float(score_text) if score_text else None
            if score is not None and (score < 0 or score > 150): # 简单验证
                 raise ValueError("Score out of range")
        except ValueError:
            QMessageBox.warning(self, "输入无效", "请输入有效的数字分数，或留空以删除成绩。")
            # 恢复原值
            self.on_course_selected(self.course_combo.currentIndex())
            return

        recorder_id = self.current_user['id']
        
        success = self.db_manager.assign_grade(recorder_id, student_id, self.current_course_id, score)

        if not success:
            QMessageBox.critical(self, "保存失败", "更新成绩时发生错误。")
            # 失败时也刷新以显示数据库中的真实状态
            self.on_course_selected(self.course_combo.currentIndex())