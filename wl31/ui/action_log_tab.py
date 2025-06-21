# wl31/ui/action_log_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QTableWidget, 
                             QHeaderView, QTableWidgetItem, QPushButton)
from PyQt5.QtCore import Qt

class ActionLogTab(QWidget):
    def __init__(self, db_manager, current_user):
        super().__init__()
        self.db_manager = db_manager
        self.current_user = current_user
        self.init_ui()
        self.load_logs()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        logs_group = QGroupBox("操作历史记录")
        logs_layout = QVBoxLayout()

        self.refresh_button = QPushButton("刷新记录")
        self.refresh_button.clicked.connect(self.load_logs)
        
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels(["ID", "操作用户", "操作类型", "详细描述", "时间"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        logs_layout.addWidget(self.refresh_button)
        logs_layout.addWidget(self.logs_table)
        logs_group.setLayout(logs_layout)
        
        main_layout.addWidget(logs_group)
        self.setLayout(main_layout)

    def load_logs(self):
        self.logs_table.setRowCount(0)
        logs = self.db_manager.get_action_logs(self.current_user['role'])
        for row, log_data in enumerate(logs):
            self.logs_table.insertRow(row)
            self.logs_table.setItem(row, 0, QTableWidgetItem(str(log_data['id'])))
            self.logs_table.setItem(row, 1, QTableWidgetItem(log_data['username']))
            self.logs_table.setItem(row, 2, QTableWidgetItem(log_data['action_type']))
            self.logs_table.setItem(row, 3, QTableWidgetItem(log_data['description']))
            self.logs_table.setItem(row, 4, QTableWidgetItem(log_data['timestamp']))