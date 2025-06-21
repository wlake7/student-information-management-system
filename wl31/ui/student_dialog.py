# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator
import datetime
from wl31.data import department_data

class Ui_StudentDialog(object):
    def setupUi(self, StudentDialog):
        StudentDialog.setObjectName("StudentDialog")
        StudentDialog.resize(450, 450) # 调整窗口大小以容纳新字段
        self.formLayout = QtWidgets.QFormLayout(StudentDialog)
        self.formLayout.setObjectName("formLayout")
        
        # 姓名
        self.label_name = QtWidgets.QLabel("姓名:", StudentDialog)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_name)
        self.name_input = QtWidgets.QLineEdit(StudentDialog)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.name_input)
        
        # 性别
        self.label_gender = QtWidgets.QLabel("性别:", StudentDialog)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_gender)
        self.gender_combobox = QtWidgets.QComboBox(StudentDialog)
        self.gender_combobox.addItems(["男", "女"])
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.gender_combobox)

        # 入学年份
        self.label_enrollment_year = QtWidgets.QLabel("入学年份:", StudentDialog)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_enrollment_year)
        self.enrollment_year_combobox = QtWidgets.QComboBox(StudentDialog)
        current_year = datetime.date.today().year
        years = [str(y) for y in range(current_year - 5, current_year + 2)]
        self.enrollment_year_combobox.addItems(years)
        self.enrollment_year_combobox.setCurrentText(str(current_year))
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.enrollment_year_combobox)

        # 所属院系
        self.label_department = QtWidgets.QLabel("所属院系:", StudentDialog)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_department)
        self.department_combobox = QtWidgets.QComboBox(StudentDialog)
        self.department_combobox.addItems(department_data.get_departments())
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.department_combobox)

        # 专业名称
        self.label_major = QtWidgets.QLabel("专业名称:", StudentDialog)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_major)
        self.major_combobox = QtWidgets.QComboBox(StudentDialog)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.major_combobox)
        
        # 班级
        self.label_class = QtWidgets.QLabel("班级:", StudentDialog)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_class)
        self.class_input = QtWidgets.QLineEdit(StudentDialog)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.class_input)
        
        # 联系方式
        self.label_contact = QtWidgets.QLabel("联系方式:", StudentDialog)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_contact)
        self.contact_input = QtWidgets.QLineEdit(StudentDialog)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.contact_input)
        
        # 电子档案
        self.label_archive = QtWidgets.QLabel("电子档案:", StudentDialog)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_archive)
        self.archive_layout = QtWidgets.QHBoxLayout()
        self.archive_path_label = QtWidgets.QLabel("未选择文件", StudentDialog)
        self.archive_path_label.setWordWrap(True)
        self.select_archive_button = QtWidgets.QPushButton("选择文件", StudentDialog)
        self.archive_layout.addWidget(self.archive_path_label)
        self.archive_layout.addWidget(self.select_archive_button)
        self.formLayout.setLayout(7, QtWidgets.QFormLayout.FieldRole, self.archive_layout)

        # 密码
        self.label_password = QtWidgets.QLabel("初始密码:", StudentDialog)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label_password)
        self.password_input = QtWidgets.QLineEdit(StudentDialog)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input.setPlaceholderText("新增时必填，编辑时留空则不修改")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.password_input)

        # 按钮
        self.buttonBox = QtWidgets.QDialogButtonBox(StudentDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(StudentDialog)
        self.buttonBox.accepted.connect(StudentDialog.accept)
        self.buttonBox.rejected.connect(StudentDialog.reject)

        # 信号连接
        self.department_combobox.currentIndexChanged.connect(self.update_majors)
        
        self.update_majors() # 初始化专业列表
        QtCore.QMetaObject.connectSlotsByName(StudentDialog)

    def update_majors(self):
        """根据所选学院动态更新专业列表"""
        department = self.department_combobox.currentText()
        majors = department_data.get_majors_by_department(department)
        self.major_combobox.clear()
        self.major_combobox.addItems(majors)

    def retranslateUi(self, StudentDialog):
        _translate = QtCore.QCoreApplication.translate
        StudentDialog.setWindowTitle(_translate("StudentDialog", "学生信息"))