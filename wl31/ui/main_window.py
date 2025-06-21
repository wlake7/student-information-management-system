# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        
        # 欢迎页面
        self.welcome_tab = QtWidgets.QWidget()
        self.welcome_tab.setObjectName("welcome_tab")
        self.welcome_layout = QtWidgets.QVBoxLayout(self.welcome_tab)
        self.welcome_label = QtWidgets.QLabel("<h1>欢迎使用学生信息管理系统</h1>")
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        self.welcome_layout.addWidget(self.welcome_label)
        self.tabWidget.addTab(self.welcome_tab, "首页")

        # 学生管理 Tab
        self.student_management_tab = QtWidgets.QWidget()
        self.student_management_tab.setObjectName("student_management_tab")
        self.student_tab_layout = QtWidgets.QVBoxLayout(self.student_management_tab)
        
        # 搜索和按钮布局
        self.student_tools_layout = QtWidgets.QHBoxLayout()
        self.student_search_input = QtWidgets.QLineEdit()
        self.student_search_input.setPlaceholderText("按姓名或学号搜索...")
        self.student_search_button = QtWidgets.QPushButton("查询")
        self.student_add_button = QtWidgets.QPushButton("新增")
        self.student_edit_button = QtWidgets.QPushButton("编辑")
        self.student_delete_button = QtWidgets.QPushButton("删除")
        self.student_import_button = QtWidgets.QPushButton("批量导入")
        
        self.student_tools_layout.addWidget(self.student_search_input)
        self.student_tools_layout.addWidget(self.student_search_button)
        self.student_tools_layout.addStretch()
        self.student_tools_layout.addWidget(self.student_add_button)
        self.student_tools_layout.addWidget(self.student_edit_button)
        self.student_tools_layout.addWidget(self.student_delete_button)
        self.student_tools_layout.addWidget(self.student_import_button)
        
        self.student_tab_layout.addLayout(self.student_tools_layout)
        
        # 学生信息表格
        self.student_table = QtWidgets.QTableWidget()
        self.student_table.setObjectName("student_table")
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels(["ID", "姓名", "性别", "班级", "联系方式"])
        self.student_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.student_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.student_table.horizontalHeader().setStretchLastSection(True)
        self.student_tab_layout.addWidget(self.student_table)
        
        self.tabWidget.addTab(self.student_management_tab, "学生信息管理")

        
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 26))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_manage = QtWidgets.QMenu(self.menubar)
        self.menu_manage.setObjectName("menu_manage")
        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setObjectName("menu_help")
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.action_exit = QtWidgets.QAction(MainWindow)
        self.action_exit.setObjectName("action_exit")
        self.action_student_manage = QtWidgets.QAction(MainWindow)
        self.action_student_manage.setObjectName("action_student_manage")
        self.action_course_manage = QtWidgets.QAction(MainWindow)
        self.action_course_manage.setObjectName("action_course_manage")
        self.action_grade_manage = QtWidgets.QAction(MainWindow)
        self.action_grade_manage.setObjectName("action_grade_manage")
        self.action_about = QtWidgets.QAction(MainWindow)
        self.action_about.setObjectName("action_about")
        
        self.menu_file.addAction(self.action_exit)
        self.menu_manage.addAction(self.action_student_manage)
        self.menu_manage.addAction(self.action_course_manage)
        self.menu_manage.addAction(self.action_grade_manage)
        self.menu_help.addAction(self.action_about)
        
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_manage.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "学生信息管理系统"))
        self.menu_file.setTitle(_translate("MainWindow", "文件"))
        self.menu_manage.setTitle(_translate("MainWindow", "管理"))
        self.menu_help.setTitle(_translate("MainWindow", "帮助"))
        self.action_exit.setText(_translate("MainWindow", "退出"))
        self.action_student_manage.setText(_translate("MainWindow", "学生管理"))
        self.action_course_manage.setText(_translate("MainWindow", "课程管理"))
        self.action_grade_manage.setText(_translate("MainWindow", "成绩管理"))
        self.action_about.setText(_translate("MainWindow", "关于"))