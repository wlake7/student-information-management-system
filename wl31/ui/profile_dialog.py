# wl31/ui/profile_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
                             QPushButton, QMessageBox, QDialogButtonBox)

class ProfileDialog(QDialog):
    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user = current_user
        self.setWindowTitle("修改个人信息")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("当前密码:", self.old_password_input)
        form_layout.addRow("新密码:", self.new_password_input)
        form_layout.addRow("确认新密码:", self.confirm_password_input)
        
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not all([old_password, new_password, confirm_password]):
            QMessageBox.warning(self, "输入错误", "所有字段都必须填写。")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的新密码不匹配。")
            return
            
        if self.db_manager.update_user_profile(self.current_user['id'], old_password, new_password):
            QMessageBox.information(self, "成功", "密码修改成功！")
            super().accept()
        else:
            QMessageBox.warning(self, "失败", "当前密码不正确或发生未知错误。")