# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'version.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/1 15:35'
"""
import os
import sys





import json

if __name__ == "__main__":
    from lib import common_tools
    from lib.common_tools.language import rosetta as say
    from lib.common_tools.compatible_import import *

else:
    from ..imports import common_tools
    from ..imports import *
    pass


# say = common_tools.language.rosetta

class VersionDialog(QMainWindow):
    """版本信息对话框"""

    def __init__(self):
        super().__init__()
        self.parent_versions = None
        self.parent_introDoc = None
        self.webView1 = None
        self.中心组件 = QWidget()
        self.horizontalLayout = QHBoxLayout(self)
        self.viewList_HTMLFilename = QTreeView(self)
        self.filelist = []
        self.init_UI()
        self.init_model()
        self.init_events()
        self.init_webview()


    def init_UI(self):
        """UI初始化"""
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.setWindowIcon(QIcon(common_tools.G.src.ImgDir.info))
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.viewList_HTMLFilename.setObjectName("versionlist")
        self.horizontalLayout.addWidget(self.viewList_HTMLFilename)
        self.setWindowTitle("HJP-bilink Version intro")
        self.resize(800, 600)
        self.webView1 = QWebEngineView(self)
        # self.webView1.setFixedWidth(800)
        self.viewList_HTMLFilename.setFixedWidth(160)
        self.viewList_HTMLFilename.header().setMinimumSectionSize(1)
        self.viewList_HTMLFilename.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.viewList_HTMLFilename.setHeaderHidden(True)
        self.viewList_HTMLFilename.setIndentation(8)
        self.horizontalLayout.addWidget(self.webView1)
        self.horizontalLayout.setStretch(0, 0)
        self.horizontalLayout.setStretch(1, 3)
        self.中心组件.setLayout(self.horizontalLayout)
        self.setCentralWidget(self.中心组件)

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
        versions_fileLi = self.fieli_get(path=common_tools.G.src.path.version_dir)
        for name, direction in versions_fileLi:
            item = QStandardItem(name[0:-5])
            item.dir = direction
            self.parent_versions.appendRow(item)
        introDoc_fileLi = self.fieli_get(path=common_tools.G.src.path.introdoc_dir, sort=False)
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
        # addonName = BaseInfo().dialogName
        # dialog = self.__class__.__name__
        common_tools.G.mw_VersionDialog = None
        # mw.__dict__[addonName][dialog] = None

    def webengine_render(self, path):
        """可能需要这个"""
        html = open(path, "r", encoding="utf8").read()
        self.webView1.setHtml(html)
        pass

    def fieli_get(self, path=None, sort=True):
        liname = os.listdir(path)
        if path == common_tools.G.src.path.version_dir:
            liname.sort(reverse=True, key=common_tools.funcs.version_cmpkey)
        li_dirfilename = [[filename, os.path.join(path, filename)] for filename in liname]
        return li_dirfilename


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # p = AnchorDialog("0")
    p = QMainWindow()
    p.setCentralWidget(QWebEngineView())
    # p =
    p.show()
    sys.exit(app.exec())
    pass
