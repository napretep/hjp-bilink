# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UIdialog_storage_switcher.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 104)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_from = QtWidgets.QLabel(Dialog)
        self.label_from.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_from)
        self.comboBox_from = QtWidgets.QComboBox(Dialog)
        self.comboBox_from.setObjectName("comboBox")
        self.horizontalLayout_2.addWidget(self.comboBox_from)
        self.label_to = QtWidgets.QLabel(Dialog)
        self.label_to.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_to)
        self.comboBox_to = QtWidgets.QComboBox(Dialog)
        self.comboBox_to.setObjectName("comboBox_2")
        self.horizontalLayout_2.addWidget(self.comboBox_to)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(3, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_switchMode = QtWidgets.QLabel(Dialog)
        self.label_switchMode.setObjectName("label_4")
        self.horizontalLayout_3.addWidget(self.label_switchMode)
        self.comboBox_switchMode = QtWidgets.QComboBox(Dialog)
        self.comboBox_switchMode.setObjectName("comboBox_3")
        self.horizontalLayout_3.addWidget(self.comboBox_switchMode)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout.addLayout(self.horizontalLayout_3)
        self.button_correct = QtWidgets.QPushButton(Dialog)
        self.button_correct.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.button_correct)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_from.setText(_translate("Dialog", "从"))
        self.label_to.setText(_translate("Dialog", "转移到"))
        self.label_switchMode.setText(_translate("Dialog", "转移模式"))
        self.button_correct.setText(_translate("Dialog", "确定"))
        self.label.setText(_translate("Dialog", "注意：当数据从A转移到B，会删除A中的数据记录"))
