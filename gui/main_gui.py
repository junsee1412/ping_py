# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(724, 532)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.btn_remove = QtWidgets.QPushButton(self.centralwidget)
        self.btn_remove.setMinimumSize(QtCore.QSize(0, 0))
        self.btn_remove.setObjectName("btn_remove")
        self.gridLayout.addWidget(self.btn_remove, 2, 6, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.spin_count = QtWidgets.QSpinBox(self.centralwidget)
        self.spin_count.setMaximum(500)
        self.spin_count.setProperty("value", 5)
        self.spin_count.setObjectName("spin_count")
        self.gridLayout.addWidget(self.spin_count, 2, 0, 1, 1)
        self.spin_ttl = QtWidgets.QSpinBox(self.centralwidget)
        self.spin_ttl.setMaximum(512)
        self.spin_ttl.setProperty("value", 64)
        self.spin_ttl.setObjectName("spin_ttl")
        self.gridLayout.addWidget(self.spin_ttl, 2, 1, 1, 1)
        self.btn_clear_list = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear_list.setObjectName("btn_clear_list")
        self.gridLayout.addWidget(self.btn_clear_list, 2, 5, 1, 1)
        self.btn_clear_log = QtWidgets.QPushButton(self.centralwidget)
        self.btn_clear_log.setObjectName("btn_clear_log")
        self.gridLayout.addWidget(self.btn_clear_log, 2, 4, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 1)
        self.spin_timeout = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.spin_timeout.setProperty("value", 4.0)
        self.spin_timeout.setObjectName("spin_timeout")
        self.gridLayout.addWidget(self.spin_timeout, 2, 2, 1, 1)
        self.btn_new = QtWidgets.QPushButton(self.centralwidget)
        self.btn_new.setObjectName("btn_new")
        self.gridLayout.addWidget(self.btn_new, 0, 6, 1, 1)
        self.btn_start = QtWidgets.QPushButton(self.centralwidget)
        self.btn_start.setObjectName("btn_start")
        self.gridLayout.addWidget(self.btn_start, 1, 5, 1, 1)
        self.line_ip = QtWidgets.QLineEdit(self.centralwidget)
        self.line_ip.setObjectName("line_ip")
        self.gridLayout.addWidget(self.line_ip, 0, 1, 1, 5)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 3, 1, 1)
        self.btn_stop = QtWidgets.QPushButton(self.centralwidget)
        self.btn_stop.setObjectName("btn_stop")
        self.gridLayout.addWidget(self.btn_stop, 1, 6, 1, 1)
        self.spin_size = QtWidgets.QSpinBox(self.centralwidget)
        self.spin_size.setMaximum(512)
        self.spin_size.setProperty("value", 56)
        self.spin_size.setObjectName("spin_size")
        self.gridLayout.addWidget(self.spin_size, 2, 3, 1, 1)
        self.proc_list = QtWidgets.QListWidget(self.centralwidget)
        self.proc_list.setMinimumSize(QtCore.QSize(0, 0))
        self.proc_list.setMaximumSize(QtCore.QSize(125, 16777215))
        self.proc_list.setObjectName("proc_list")
        self.gridLayout.addWidget(self.proc_list, 3, 6, 1, 1)
        self.proc_log = QtWidgets.QTextBrowser(self.centralwidget)
        self.proc_log.setObjectName("proc_log")
        self.gridLayout.addWidget(self.proc_log, 3, 0, 1, 6)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 724, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PING"))
        self.btn_remove.setText(_translate("MainWindow", "Remove"))
        self.label_3.setText(_translate("MainWindow", "ttl:"))
        self.label.setText(_translate("MainWindow", "IP:"))
        self.btn_clear_list.setText(_translate("MainWindow", "Clear List"))
        self.btn_clear_log.setText(_translate("MainWindow", "Clear Log"))
        self.label_4.setText(_translate("MainWindow", "timeout:"))
        self.btn_new.setText(_translate("MainWindow", "New"))
        self.btn_start.setText(_translate("MainWindow", "Start"))
        self.line_ip.setText(_translate("MainWindow", "8.8.8.8"))
        self.label_2.setText(_translate("MainWindow", "count:"))
        self.label_5.setText(_translate("MainWindow", "size:"))
        self.btn_stop.setText(_translate("MainWindow", "Stop"))