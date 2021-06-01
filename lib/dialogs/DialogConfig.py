"""
配置文件的窗口
"""
from ..obj.languageObj import rosetta as say
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
        self.cfg = Config()
        self.configJSON: dict = self.read_userconfig()
        self.configSchema = self.read_schemaJSON()
        self.model_dataJSON = {}
        self.translate_back={}
        self.schema = {}
        self.wiget_dict = {}
        self.init_UI()
        # self.init_model()
        self.init_events()

    def read_userconfig(self):
        path = os.path.join(THIS_FOLDER,self.cfg.base_cfg["configFileName"])
        json_str = open(path, "r", encoding="utf-8").read()
        return json.loads(json_str)

    def read_schemaJSON(self):
        path = os.path.join(THIS_FOLDER, self.cfg.base_cfg["configSchemaFileName"])
        json_str = open(path, "r", encoding="utf-8").read()
        return json.loads(json_str)

    def init_UI(self):
        self.setupUi(self)
        self.setWindowTitle("configuration")
        iconDir = os.path.join(THIS_FOLDER, self.cfg.base_cfg["iconFile_config"])
        self.setWindowIcon(QIcon(iconDir))
        user_configable = self.configSchema["user_configable"]
        allow_empty = self.configSchema["data_schema"]["allow_empty"] #允许为空则必为string
        data_range = self.configSchema["data_schema"]["data_range"]
        non_negative_int = self.configSchema["data_schema"]["data_type"]["non_negative_int"]
        filename = self.configSchema["data_schema"]["data_type"]["filename"]
        string = self.configSchema["data_schema"]["data_type"]["string"]
        for k, v in self.configJSON.items():
            if k in user_configable:
                label=QtWidgets.QLabel(self)
                label.setText(say(k))
                self.translate_back[say(k)]=k
                h_layout = QtWidgets.QHsayBoxLayout(self)
                h_layout.addWidget(label)
                if k in string:
                    wiget = QtWidgets.QLineEdit(self)
                    wiget.setText(v)
                    self.wiget_dict[k] = wiget
                elif k in data_range:
                    self.schema[k]={}
                    wiget = QtWidgets.QComboBox(self)
                    count = 0
                    out = 0
                    for h,j in data_range[k].items():
                        wiget.addItem(say(h))
                        wiget.setItemData(count,j)
                        if v == j:out=count
                        count+=1
                    wiget.setCurrentIndex(out)
                    self.wiget_dict[k] = wiget
                elif k in non_negative_int:
                    wiget = QtWidgets.QSpinBox(self)
                    self.wiget_dict[k] = wiget
                    wiget.setValue(v)
                elif k in filename:
                    h_layout2 = QtWidgets.QHBoxLayout(self)
                    wiget = QPushButton(self)
                    self.wiget_dict[k]={}
                    self.wiget_dict[k]["button"] = wiget
                    wiget.setText(say("选择文件"))
                    wiget.setObjectName("openfiledialog")
                    label2 = QtWidgets.QLabel(self)
                    if len(v)>10:
                        label2.setText(v[0:5]+"..."+v[-5:])
                    else:
                        label2.setText(v)
                    label2.setToolTip(v)

                    self.wiget_dict[k]["label"]=label2
                    h_layout2.addWidget(wiget)
                    h_layout2.addWidget(label2)
                    wiget = h_layout2

                if isinstance(wiget,QtWidgets.QHBoxLayout):
                    h_layout.addLayout(wiget)
                else:
                    h_layout.addWidget(wiget)

                h_layout.setStretch(0,2)
                h_layout.setStretch(1,1)
                self.v_layout.addLayout(h_layout)
        self.setWindowModality(Qt.ApplicationModal)

    def init_data(self):
        pass

    def init_events(self):
        self.wiget_dict["anchorCSSFileName"]["button"].clicked.connect(self.slot_btn_openfiledialog)
        self.closeEvent=self.onClose

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def onClose(self,QCloseEvent):
        for k,v in self.wiget_dict.items():
            if isinstance(v,QComboBox):
                self.configJSON[k]=v.currentData()
            elif isinstance(v,dict):
                self.configJSON[k]=v["label"].toolTip()
            elif isinstance(v,QtWidgets.QLineEdit):
                self.configJSON[k]=v.text()
        path = os.path.join(THIS_FOLDER,self.cfg.base_cfg["configFileName"])
        s = json.dumps(self.configJSON,ensure_ascii=False,indent=4)
        f = open(path, "w", encoding="utf-8")
        f.write(s)
        f.close()

    def slot_btn_openfiledialog(self):
        fileName_choose, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
            say("选取文件"),USER_FOLDER,"All Files (*);;Text Files (*.txt *.css)"
        )
        fileName_choose= fileName_choose.__str__()
        label =self.wiget_dict["anchorCSSFileName"]["label"]
        if len(fileName_choose)>10:
            label.setText(fileName_choose[0:5]+"..."+fileName_choose[-5:])
        else:
            label.setText(fileName_choose)
        self.wiget_dict["anchorCSSFileName"]["label"].setToolTip(fileName_choose)
