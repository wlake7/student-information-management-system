# wl31/ui/login_window.py
# 描述: 定义登录界面的 UI 控件和布局。

from PyQt5.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QVBoxLayout, QFormLayout, 
    QLabel, QComboBox, QHBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class Ui_LoginWindow(object):
    """
    登录窗口的UI类。
    """
    def setupUi(self, LoginWindow: QDialog):
        LoginWindow.setWindowTitle("学生信息管理系统 - 登录")
        LoginWindow.setFixedSize(350, 400)

        # Main layout
        main_layout = QVBoxLayout(LoginWindow)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("用户登录")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Username
        self.wl_username_input = QLineEdit()
        self.wl_username_input.setPlaceholderText("请输入用户名")
        form_layout.addRow("用户名:", self.wl_username_input)

        # Password
        self.wl_password_input = QLineEdit()
        self.wl_password_input.setEchoMode(QLineEdit.Password)
        self.wl_password_input.setPlaceholderText("请输入密码")
        form_layout.addRow("密  码:", self.wl_password_input)

        # Captcha
        captcha_layout = QHBoxLayout()
        self.wl_captcha_input = QLineEdit()
        self.wl_captcha_input.setPlaceholderText("请输入验证码")
        self.wl_captcha_image = QLabel("点击刷新")
        self.wl_captcha_image.setFixedSize(150, 60)
        self.wl_captcha_image.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.wl_captcha_image.setAlignment(Qt.AlignCenter)
        self.wl_captcha_image.setCursor(Qt.PointingHandCursor) # Add hand cursor
        captcha_layout.addWidget(self.wl_captcha_input)
        captcha_layout.addWidget(self.wl_captcha_image)
        form_layout.addRow("验证码:", captcha_layout)

        # Role
        self.wl_role_combobox = QComboBox()
        self.wl_role_combobox.addItems(["学生", "教师", "管理员"])
        form_layout.addRow("角  色:", self.wl_role_combobox)

        main_layout.addLayout(form_layout)

        # Buttons
        self.wl_login_button = QPushButton("登录")
        main_layout.addWidget(self.wl_login_button)

        # Status label
        self.wl_status_label = QLabel("")
        self.wl_status_label.setAlignment(Qt.AlignCenter)
        self.wl_status_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.wl_status_label)

        main_layout.addStretch() # Add some space at the bottom