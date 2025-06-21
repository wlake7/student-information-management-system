# wl31/ui/my_grades_tab.py
# 描述: 学生查看个人成绩的UI。

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableView, QHeaderView, QLabel)
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class MyGradesTab(QWidget):
    """
    学生查看个人成绩的选项卡。
    """
    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user = current_user
        self.init_ui()
        self.load_my_grades()

    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h3>我的成绩单</h3>"))

        self.table_view = QTableView()
        self.table_view.setEditTriggers(QTableView.NoEditTriggers) # 只读
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['课程名称', '学分', '开课学期', '授课教师', '我的成绩'])
        self.table_view.setModel(self.model)

        layout.addWidget(self.table_view)

    def load_my_grades(self):
        """加载当前登录学生的成绩"""
        student_id = self.current_user.get('student_id')
        if not student_id:
            # 理论上，学生角色一定有关联的student_id
            # 但作为安全检查
            return

        grades_data = self.db_manager.get_grades_by_student(student_id)
        self.model.removeRows(0, self.model.rowCount())

        for course_name, credits, semester, teacher_name, score in grades_data:
            row = [
                QStandardItem(str(course_name)),
                QStandardItem(str(credits)),
                QStandardItem(str(semester)),
                QStandardItem(str(teacher_name or 'N/A')),
                QStandardItem(str(score))
            ]
            self.model.appendRow(row)