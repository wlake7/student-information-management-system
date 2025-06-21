# wl31/ui/data_analysis_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QFormLayout, 
                             QLineEdit, QPushButton, QTableWidget, QHeaderView,
                             QMessageBox, QFileDialog, QLabel, QComboBox,
                             QTableWidgetItem, QHBoxLayout)
from PyQt5.QtCore import Qt

class DataAnalysisTab(QWidget):
    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 组合查询
        query_group = QGroupBox("成绩组合查询")
        query_layout = QFormLayout()
        self.student_id_input = QLineEdit()
        self.course_name_combo = QComboBox()
        self.search_grades_button = QPushButton("查询成绩")
        query_layout.addRow("学号:", self.student_id_input)
        query_layout.addRow("课程名称:", self.course_name_combo)
        query_layout.addRow(self.search_grades_button)
        query_group.setLayout(query_layout)
        main_layout.addWidget(query_group)

        # 模糊搜索
        fuzzy_search_group = QGroupBox("学生模糊搜索 (姓名拼音首字母)")
        fuzzy_layout = QFormLayout()
        self.pinyin_input = QLineEdit()
        self.search_pinyin_button = QPushButton("搜索学生")
        fuzzy_layout.addRow("姓名拼音首字母:", self.pinyin_input)
        fuzzy_layout.addRow(self.search_pinyin_button)
        fuzzy_search_group.setLayout(fuzzy_layout)
        main_layout.addWidget(fuzzy_search_group)

        # 统计功能
        stats_group = QGroupBox("班级课程成绩统计")
        stats_layout = QFormLayout()
        self.class_combo = QComboBox()
        self.course_combo_stats = QComboBox()
        self.calculate_stats_button = QPushButton("计算统计数据")
        self.stats_result_label = QLabel("统计结果将显示在这里")
        stats_layout.addRow("选择班级:", self.class_combo)
        stats_layout.addRow("选择课程:", self.course_combo_stats)
        stats_layout.addRow(self.calculate_stats_button)
        stats_layout.addRow(self.stats_result_label)
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        # 结果显示与导出
        result_group = QGroupBox("查询与统计结果")
        result_layout = QVBoxLayout()
        self.export_button = QPushButton("导出为Excel")
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["学号", "姓名", "课程", "成绩"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.export_button)
        
        result_layout.addLayout(hbox)
        result_layout.addWidget(self.result_table)
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)

        self.setLayout(main_layout)