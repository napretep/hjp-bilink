"""
配置文件的窗口
"""

import json

from .inputObj import *
from .config_UI import Ui_Form


class ConfigDialog(QDialog, Ui_Form):
    """
    配置文件的对话框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.configJSON: dict = {}
        self.setupUi(self)
        self.input = Input()
        self.model_init()
        self.events_init()

    def events_init(self, *args, **kwargs):
        """事件的初始化"""
        self.closeEvent = self.onClose
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath(self.input.configDir)
        self.fileWatcher.fileChanged.connect(self.model_loadFromJSON)
        self.model.dataChanged.connect(self.model_saveToFile)

    def model_init(self, *args, **kwargs):
        """模型数据的初始化"""
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["key", "value"])
        self.configTable.setModel(self.model)
        self.model_loadFromJSON()

    def onClose(self, QCloseEvent):
        """关闭时要保存数据,QCloseEvent是有用的参数,不能删掉,否则会报错"""
        self.JSON_loadFromModel()
        self.model_saveToFile()

    def model_loadFromJSON(self):
        """从configJSON读取信息"""
        self.configJSON = json.load(open(self.input.configDir, "r", encoding="utf-8"))
        self.model.removeRows(0, self.model.rowCount())
        for k, v in self.configJSON.items():
            self.model.appendRow([QStandardItem(k), QStandardItem(str(v))])

    def JSON_loadFromModel(self, *args, **kwargs):
        """从树中读取json"""

    def model_saveToFile(self, *args, **kwargs):
        """保存文件"""
