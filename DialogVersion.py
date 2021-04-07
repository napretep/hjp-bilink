from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAbstractItemView)
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from .utils import THIS_FOLDER, BaseInfo
from aqt import mw

VERSION_FOLDER = BaseInfo().baseinfo["versionsDir"]
page_empty = '''
<!DOCTYPE html><html><head>
</head>
<body></body>
</html>
'''


class Ui_version(object):
    def setupUi(self, version):
        version.setObjectName("version")
        version.resize(600, 500)
        self.horizontalLayout = QtWidgets.QHBoxLayout(version)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.versionlist = QtWidgets.QListView(version)
        self.versionlist.setObjectName("versionlist")
        self.horizontalLayout.addWidget(self.versionlist)
        self.retranslateUi(version)
        QtCore.QMetaObject.connectSlotsByName(version)

    def retranslateUi(self, version):
        _translate = QtCore.QCoreApplication.translate
        version.setWindowTitle(_translate("version", "Form"))


class VersionDialog(QtWidgets.QDialog, Ui_version):
    """版本信息对话框"""

    def __init__(self):
        super().__init__()
        self.webView1 = None
        self.filelist = self.fileLi_get()
        self.init_UI()
        self.init_model()
        self.init_events()
        self.webengine_render(self.filelist[0])
        self.show()

    def init_UI(self):
        """UI初始化"""
        self.setupUi(self)
        self.setWindowTitle("HJP-bilink Version intro")
        self.setFixedWidth(1000)
        self.webView1 = QWebEngineView(self)
        self.webView1.setFixedWidth(800)
        self.versionlist.setFixedWidth(150)
        self.versionlist.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalLayout.addWidget(self.webView1)
        self.horizontalLayout.setStretch(0, 0)
        self.horizontalLayout.setStretch(1, 3)

    def init_model(self):
        """初始化模型"""
        fileLi = self.filelist
        self.list_model = QStandardItemModel()
        self.list_model_root = self.list_model.invisibleRootItem()
        self.list_model.setHorizontalHeaderItem(0, QStandardItem("versions"))
        self.versionlist.setModel(self.list_model)
        for filename in fileLi:
            self.list_model.appendRow(QStandardItem(filename[0:-5]))

    def init_events(self):
        self.closeEvent = self.onClose
        self.versionlist.clicked.connect(self.onClick)

    def onClick(self, index):
        item = self.list_model.itemFromIndex(index)
        if item:
            self.webengine_render(item.text() + ".html")

    def onClose(self, QCloseEvent):
        addonName = BaseInfo().dialogName
        dialog = self.__class__.__name__
        mw.__dict__[addonName][dialog] = None

    def webengine_render(self, filename):
        """可能需要这个"""
        html = open(os.path.join(THIS_FOLDER, VERSION_FOLDER, filename), "r", encoding="utf8").read()
        self.webView1.setHtml(html)
        pass

    def fileLi_get(self, path=None):
        if path:
            path = path
        else:
            path = os.path.join(THIS_FOLDER, VERSION_FOLDER)
            liname = os.listdir(path)
            liname.sort(reverse=True)
        return liname
