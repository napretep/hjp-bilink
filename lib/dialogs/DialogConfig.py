"""
配置文件的窗口
"""
from ...lib.obj.utils import wrapper_webview_refresh, wrapper_browser_refresh
from PyQt5 import QtCore, QtGui, QtWidgets
from ...lib.obj.inputObj import *
# from ...lib.dialogs.UIdialog_Config import Ui_config
class Ui_config(object):
    def setupUi(self,config):
        config.setObjectName("config")
        self.v_layout = QtWidgets.QVBoxLayout(config)


class ConfigDialog(QDialog, Ui_config):
    """
    配置文件的对话框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.baseInfo = BaseInfo()
        self.configJSON: dict = {}
        self.configSchema = self.baseInfo.configSchemaJSON
        self.model_dataJSON = {}
        self.init_UI()
        self.init_model()
        self.init_events()

    def init_UI(self):
        self.setupUi(self)
        self.textBrowser.setHtml(self.baseInfo.configHTMLFile)
        self.configTable.setAlternatingRowColors(True)
        self.configTable.verticalHeader().hide()
        self.configTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        iconDir = os.path.join(THIS_FOLDER, self.baseInfo.baseinfo["iconFile_config"])
        self.setWindowIcon(QIcon(iconDir))

    def init_events(self, *args, **kwargs):
        """事件的初始化"""
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath(self.baseInfo.configDir)
        self.fileWatcher.fileChanged.connect(self.model_JSON_load)
        self.model.dataChanged.connect(self.file_model_save)

    def init_model(self, *args, **kwargs):
        """模型数据的初始化"""
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model.setHorizontalHeaderLabels(["key", "value"])
        self.configTable.setModel(self.model)
        self.model_JSON_load()

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def onClose(self, QCloseEvent):
        """关闭时要保存数据,QCloseEvent是有用的参数,不能删掉,否则会报错"""
        self.JSON_model_load()
        self.file_model_save()

    def model_JSON_load(self):
        """从configJSON读取信息"""
        self.configJSON = self.baseInfo.configJSON
        self.model.removeRows(0, self.model.rowCount())
        for k, v in self.configJSON.items():
            if k in self.configSchema["user_configable"]:
                itemk = QStandardItem(k)
                itemk.setFlags(itemk.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsSelectable)
                self.model.appendRow([itemk, QStandardItem(str(v))])

    def JSON_model_load(self, *args, **kwargs):
        """从树中读取json"""
        for i in range(self.model_rootNode.rowCount()):
            k = self.model_rootNode.child(i, 0).text()
            v = self.model_rootNode.child(i, 1).text()
            self.model_dataJSON[k] = v

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def file_model_save(self, topLeft, *args, **kwargs):
        """保存文件"""
        item = self.model.itemFromIndex(topLeft)
        k = self.model_rootNode.child(item.row(), 0).text()
        v = self.model_rootNode.child(item.row(), 1).text()
        isSafe = self.safe_check(k, v)
        if isSafe:
            self.configJSON[k] = self.value
            json.dump(self.configJSON, open(self.baseInfo.configDir, "w", encoding="utf-8"), indent=4,
                      ensure_ascii=False)
        else:
            self.model_JSON_load()

    def safe_check(self, key, value):
        """检查数据合法性,
        non_negative_int,检查数字合法性, filename检查文件名合法性
        默认都填入字符串,
        """
        console(f"key={key},val={value}").log.end()
        data_schema = self.configSchema["data_schema"]
        if value == "" and key in data_schema["allow_empty"]:
            self.value = value
            return True
        else:
            if key in data_schema["data_type"]["non_negative_int"]:
                try:
                    value = int(value)
                except:
                    tooltip(say(f"{value}不是正整数,不能成为{key}的值"))
                    return False
                if value < 0:
                    tooltip(say(f"{value}不是正整数,不能成为{key}的值"))
                    return False
            if key in data_schema["data_type"]["filename"]:
                if not os.path.exists(os.path.join(USER_FOLDER, value)):
                    tooltip(say(f"""{value}文件不存在"""))
                    return False
            if key in data_schema["data_range"]:
                if value not in data_schema["data_range"][key]:
                    tooltip(say(f"""{value}不能成为{key}的值,合法值为{data_schema["data_range"][key].__str__()}"""))
                    return False
        self.value = value
        return True
