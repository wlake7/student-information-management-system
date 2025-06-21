# wl31/ui/teacher_management_tab.py
# 描述: 教师信息管理选项卡，提供对教师用户的增删改查功能。

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QHeaderView, QInputDialog
)
from PyQt5.QtCore import Qt
from wl31.utils.hash_utils import hash_password

class TeacherDialog(QDialog):
    """用于新增或编辑教师信息的对话框。"""
    def __init__(self, teacher_data=None, parent=None):
        super().__init__(parent)
        self.is_edit_mode = teacher_data is not None
        self.setWindowTitle("编辑教师信息" if self.is_edit_mode else "新增教师")
        self.setMinimumWidth(400)

        self.layout = QFormLayout(self)

        self.username_input = QLineEdit()
        self.name_input = QLineEdit()
        self.title_input = QLineEdit()
        self.department_input = QLineEdit()
        self.contact_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.layout.addRow("登录名:", self.username_input)
        self.layout.addRow("姓名:", self.name_input)
        self.layout.addRow("职称:", self.title_input)
        self.layout.addRow("院系:", self.department_input)
        self.layout.addRow("联系方式:", self.contact_input)
        self.layout.addRow("密码:", self.password_input)

        if self.is_edit_mode:
            self.username_input.setText(teacher_data.get('username', ''))
            self.username_input.setReadOnly(True) # 用户名不可编辑
            self.name_input.setText(teacher_data.get('name', ''))
            self.title_input.setText(teacher_data.get('title', ''))
            self.department_input.setText(teacher_data.get('department', ''))
            self.contact_input.setText(teacher_data.get('contact_info', ''))
            self.password_input.setPlaceholderText("留空则不修改密码")
        else:
            self.password_input.setPlaceholderText("必填")

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

    def get_data(self):
        """获取对话框中输入的数据。"""
        data = {
            "username": self.username_input.text().strip(),
            "name": self.name_input.text().strip(),
            "title": self.title_input.text().strip(),
            "department": self.department_input.text().strip(),
            "contact_info": self.contact_input.text().strip(),
            "password": self.password_input.text()
        }
        return data

class TeacherManagementTab(QWidget):
    """教师管理选项卡UI和逻辑。"""
    def __init__(self, db_manager, user_info, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_info = user_info
        self.setup_ui()
        self.connect_signals()
        self.load_teachers()

    def setup_ui(self):
        """初始化UI组件。"""
        main_layout = QVBoxLayout(self)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("新增教师")
        self.edit_button = QPushButton("编辑教师")
        self.delete_button = QPushButton("删除教师")
        self.freeze_button = QPushButton("冻结/解冻账户")
        self.reset_password_button = QPushButton("重置密码")
        self.import_button = QPushButton("批量导入教师") # 新增按钮
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.import_button) # 添加到布局
        button_layout.addStretch()
        button_layout.addWidget(self.freeze_button)
        button_layout.addWidget(self.reset_password_button)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "登录名", "姓名", "职称", "院系", "联系方式", "状态"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

    def connect_signals(self):
        """连接信号和槽。"""
        self.add_button.clicked.connect(self.add_teacher)
        self.edit_button.clicked.connect(self.edit_teacher)
        self.delete_button.clicked.connect(self.delete_teacher)
        self.freeze_button.clicked.connect(self.toggle_freeze_account)
        self.reset_password_button.clicked.connect(self.reset_password)

    def load_teachers(self):
        """从数据库加载教师数据并填充到表格中。"""
        self.table.setRowCount(0)
        teachers = self.db_manager.get_all_teachers_info()
        for row, teacher in enumerate(teachers):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(teacher['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(teacher['username']))
            self.table.setItem(row, 2, QTableWidgetItem(teacher['name']))
            self.table.setItem(row, 3, QTableWidgetItem(teacher['title']))
            self.table.setItem(row, 4, QTableWidgetItem(teacher['department']))
            self.table.setItem(row, 5, QTableWidgetItem(teacher['contact_info']))
            status = "冻结" if teacher['is_frozen'] else "正常"
            self.table.setItem(row, 6, QTableWidgetItem(status))

    def get_selected_teacher_info(self):
        """获取当前选中行教师的信息。"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择一位教师。")
            return None, None
        
        row = selected_rows[0].row()
        teacher_id = int(self.table.item(row, 0).text())
        
        # 从数据库获取完整信息，因为表格中可能不全
        all_teachers = self.db_manager.get_all_teachers_info()
        teacher_data = next((t for t in all_teachers if t['id'] == teacher_id), None)
        
        return teacher_id, teacher_data

    def add_teacher(self):
        """处理新增教师。"""
        dialog = TeacherDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['username'] or not data['name'] or not data['password']:
                QMessageBox.warning(self, "警告", "登录名、姓名和密码为必填项。")
                return

            result = self.db_manager.add_teacher(self.user_info['id'], data)
            if result == "username_exists":
                QMessageBox.critical(self, "错误", "新增教师失败：登录名已存在。")
            elif result:
                QMessageBox.information(self, "成功", "教师已成功添加。")
                self.load_teachers()
            else:
                QMessageBox.critical(self, "错误", "新增教师失败，请检查数据库连接或日志。")

    def edit_teacher(self):
        """处理编辑教师。"""
        teacher_id, teacher_data = self.get_selected_teacher_info()
        if not teacher_id:
            return

        dialog = TeacherDialog(teacher_data=teacher_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data['name']:
                QMessageBox.warning(self, "警告", "姓名不能为空。")
                return

            if self.db_manager.update_teacher(self.user_info['id'], teacher_id, data):
                QMessageBox.information(self, "成功", "教师信息已成功更新。")
                self.load_teachers()
            else:
                QMessageBox.critical(self, "错误", "更新教师信息失败。")

    def delete_teacher(self):
        """处理删除教师。"""
        teacher_id, teacher_data = self.get_selected_teacher_info()
        if not teacher_id:
            return

        reply = QMessageBox.question(
            self, '确认删除', 
            f"您确定要删除教师 '{teacher_data['name']}' 吗？\n此操作将同时删除其用户账号，且不可恢复。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.delete_teacher(self.user_info['id'], teacher_id):
                QMessageBox.information(self, "成功", "教师已成功删除。")
                self.load_teachers()
            else:
                QMessageBox.critical(self, "错误", "删除教师失败。")

    def toggle_freeze_account(self):
        """冻结或解冻教师账户。"""
        teacher_id, teacher_data = self.get_selected_teacher_info()
        if not teacher_id:
            return
        
        # 需要从Users表获取user_id
        user = self.db_manager.get_user(teacher_data['username'])
        if not user:
             QMessageBox.critical(self, "错误", "找不到关联的用户账户。")
             return

        current_status = user['is_frozen']
        new_status = 1 - current_status
        action_text = "冻结" if new_status == 1 else "解冻"

        reply = QMessageBox.question(
            self, f'确认{action_text}',
            f"您确定要{action_text}教师 '{teacher_data['name']}' 的账户吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.db_manager.set_user_account_status(self.user_info['id'], user['id'], new_status):
                QMessageBox.information(self, "成功", f"账户已成功{action_text}。")
                self.load_teachers()
            else:
                QMessageBox.critical(self, "错误", f"{action_text}账户失败。")

    def reset_password(self):
        """重置教师密码。"""
        teacher_id, teacher_data = self.get_selected_teacher_info()
        if not teacher_id:
            return

        user = self.db_manager.get_user(teacher_data['username'])
        if not user:
             QMessageBox.critical(self, "错误", "找不到关联的用户账户。")
             return

        new_password, ok = QInputDialog.getText(
            self, '重置密码', f"请输入教师 '{teacher_data['name']}' 的新密码:", QLineEdit.Password
        )

        if ok and new_password:
            if self.db_manager.reset_user_password(self.user_info['id'], user['id'], new_password):
                QMessageBox.information(self, "成功", "密码已成功重置。")
            else:
                QMessageBox.critical(self, "错误", "重置密码失败。")
        elif ok:
            QMessageBox.warning(self, "警告", "密码不能为空。")