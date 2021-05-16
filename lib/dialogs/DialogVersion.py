import re

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QAbstractItemView)
import os
from PyQt5 import QtCore, QtWidgets, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from ...lib.obj.utils import THIS_FOLDER, BaseInfo
from aqt import mw

VERSION_FOLDER = BaseInfo().baseinfo["versionsDir"]
INTRO_FOLDER = BaseInfo().baseinfo["introDocDir"]
page_empty = '''
<!DOCTYPE html><html><head>
</head>
<body></body>
</html>
'''
class addon_version:
    def __init__(self,v_str):
        self.v = [int(i) for i in v_str.split(".")]

    def __lt__(self, other):
        if self.v[0]!=other.v[0]:
            return self.v[0]< other.v[0]
        elif self.v[1]!=other.v[1]:
            return self.v[1]< other.v[1]
        else:
            return self.v[2]< other.v[2]
def cmpkey(path):
    filename = os.path.basename(path)
    v_str = re.search(r"\d+\.\d+\.\d",filename).group()
    return addon_version(v_str)

class Ui_version(object):
    def setupUi(self, version):
        version.setObjectName("version")
        version.resize(600, 500)
        self.horizontalLayout = QtWidgets.QHBoxLayout(version)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.viewList_HTMLFilename = QtWidgets.QTreeView(version)
        self.viewList_HTMLFilename.setObjectName("versionlist")
        self.horizontalLayout.addWidget(self.viewList_HTMLFilename)
        self.retranslateUi(version)
        QtCore.QMetaObject.connectSlotsByName(version)

    def retranslateUi(self, version):
        _translate = QtCore.QCoreApplication.translate
        version.setWindowTitle(_translate("version", "Form"))


class VersionDialog(QtWidgets.QDialog, Ui_version):
    """版本信息对话框"""

    def __init__(self):
        super().__init__()
        self.parent_versions = None
        self.parent_introDoc = None
        self.webView1 = None
        self.filelist = []
        self.init_UI()
        self.init_model()
        self.init_events()
        self.init_webview()
        self.show()

    def init_UI(self):
        """UI初始化"""
        self.setupUi(self)
        self.setWindowTitle("HJP-bilink Version intro")
        self.setFixedWidth(1000)
        self.webView1 = QWebEngineView(self)
        self.webView1.setFixedWidth(800)
        self.viewList_HTMLFilename.setFixedWidth(160)
        self.viewList_HTMLFilename.header().setMinimumSectionSize(1)
        self.viewList_HTMLFilename.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.viewList_HTMLFilename.setHeaderHidden(True)
        self.viewList_HTMLFilename.setIndentation(8)
        self.horizontalLayout.addWidget(self.webView1)
        self.horizontalLayout.setStretch(0, 0)
        self.horizontalLayout.setStretch(1, 3)

    def init_model(self):
        """初始化模型"""
        self.list_model = QStandardItemModel()
        self.list_model_root = self.list_model.invisibleRootItem()
        self.list_model.takeHorizontalHeaderItem(0)
        # self.list_model.setHorizontalHeaderItem(0, QStandardItem("../resource/versions"))
        self.parent_versions = QStandardItem("versions")
        self.parent_introDoc = QStandardItem("introDoc")
        self.basic_concept = QStandardItem("basic_concept")
        self.parent_introDoc.appendRow(self.basic_concept)
        self.list_model_root.appendRow(self.parent_introDoc)
        self.list_model_root.appendRow(self.parent_versions)
        self.viewList_HTMLFilename.setModel(self.list_model)
        versions_fileLi = self.versionfileLi_get()
        for name, direction in versions_fileLi:
            item = QStandardItem(name[0:-5])
            item.dir = direction
            self.parent_versions.appendRow(item)
        introDoc_fileLi = self.versionfileLi_get(relative_path=INTRO_FOLDER, sort=False)
        for name, direction in introDoc_fileLi:
            item = QStandardItem(name[0:-5])
            item.dir = direction
            if "text link" in name:
                self.basic_concept.appendRow(item)
            else:
                self.parent_introDoc.appendRow(item)
        self.viewList_HTMLFilename.expandAll()

    def init_webview(self):
        html = open(self.parent_versions.child(0).dir, "r", encoding="utf8").read()
        self.webView1.setHtml(html)

    def init_events(self):
        self.closeEvent = self.onClose
        self.viewList_HTMLFilename.clicked.connect(self.onClick)

    def onClick(self, index):
        item = self.list_model.itemFromIndex(index)
        if hasattr(item, "dir"):
            self.webengine_render(item.dir)

    def onClose(self, QCloseEvent):
        addonName = BaseInfo().dialogName
        dialog = self.__class__.__name__
        mw.__dict__[addonName][dialog] = None

    def webengine_render(self, path):
        """可能需要这个"""
        html = open(path, "r", encoding="utf8").read()
        self.webView1.setHtml(html)
        pass

    def versionfileLi_get(self, relative_path=None, sort=True):
        if relative_path is None: relative_path = VERSION_FOLDER
        path1 = os.path.join(THIS_FOLDER, relative_path)
        liname = os.listdir(path1)
        if sort: liname.sort(reverse=True,key = cmpkey)
        li_dirfilename = [[filename, os.path.join(path1, filename)] for filename in liname]
        return li_dirfilename

