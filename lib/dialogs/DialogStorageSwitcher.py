from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from aqt.utils import showInfo
from ..obj.inputObj import Input
from .UIdialog_storage_switcher import Ui_Dialog
from ..obj.linkData_deleter import LinkDataDeleter
from ..obj.linkData_reader import LinkDataReader
from ..obj.linkData_writer import LinkDataWriter
from ..obj.languageObj import rosetta as say
from ..obj.utils import wrapper_webview_refresh,wrapper_browser_refresh

class StorageSwitcherDialog(QDialog,Ui_Dialog):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.to_Li=[say(i) for i in ["卡片字段存储","sqlite数据库存储","JSON文件存储"]]
        self.switchMode = [say("数据覆盖"),say("数据合并")]
        self.storage_num = {
            say(self.to_Li[0]):1,say(self.to_Li[0]):0,say(self.to_Li[0]):2
        }
        self.init_UI()
        self.init_model()
        self.init_events()
        self.show()

    def init_UI(self):
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(say("链接数据迁移对话框"))
        self.label_comment.setText(
            f"""{say("注意1:当数据从A转移到B，会删除A中的数据记录")},\n{say("注意2:先把想要转移的卡片插入到input")}""")
        self.button_correct.setText(say("执行"))
        self.label_from.setText(say('从'))
        self.label_to.setText(say("转移到"))
        self.label_switchMode.setText(say("写入模式"))

        pass
    def init_model(self):
        self.comboBox_from.addItems(self.to_Li)
        self.comboBox_to.addItems(self.to_Li[1:])
        self.comboBox_switchMode.addItems(self.switchMode)
        pass
    def init_events(self):
        self.comboBox_from.currentIndexChanged.connect(self.onFromChanged)
        self.button_correct.clicked.connect(self.onButtonCorrectClicked)
        pass

    def onFromChanged(self,index):
        text = self.comboBox_from.currentText()
        self.comboBox_to.clear()
        for i in self.to_Li:
            if text !=i:
                self.comboBox_to.addItem(i)

    @wrapper_browser_refresh
    @wrapper_webview_refresh
    def onButtonCorrectClicked(self, ):
        data_from = self.comboBox_from.currentText()
        data_to = self.comboBox_to.currentText()
        data_mode = self.comboBox_switchMode.currentText()
        #三步走: 1读取,2写入,3删除
        card_li = [item.card_id for item in Input().dataflat_]
        cardinfo = {}
        for card_id in card_li:
            L = LinkDataReader(card_id)
            L.storageLocation = self.storage_num[data_from]
            cardinfo[card_id] = L.read()
        if data_mode == say("数据覆盖"):
            for card_idA,data in cardinfo.items():
                L = LinkDataWriter(card_idA, data)
                L.storageLocation = self.storage_num[data_to]
                L.write()
        else:
            for card_idA,data in cardinfo.items():
                L = LinkDataReader(card_idA)
                L.storageLocation = self.storage_num[data_to]
                linkdata_A =L.read()
                linklist_A_li  = [i["card_id"] for i in linkdata_A["link_list"]]
                root_A_li = [ i["card_id"] if "card_id" in i else i["nodename"]
                        for i in linkdata_A["root"]]

                for i in data["link_list"]:
                    if i["card_id"] not in linklist_A_li:
                        linkdata_A["link_list"].append(i)
                    else:
                        index = linklist_A_li.index(i["card_id"])
                        linkdata_A[index]["desc"]=i["desc"]
                for i in data["root"]:
                    info  = i["card_id"] if "card_id" in i else i["nodename"]
                    if info not in root_A_li:
                        linkdata_A["root"].append(i)
                for k,v in data["node"].keys():
                    if type(v)==list:
                        if k in linkdata_A["node"]:
                            linkdata_A["node"][k]+=v
                        else:
                            linkdata_A["node"][k]=v
                L = LinkDataWriter(card_idA,linkdata_A)
                L.storageLocation = self.storage_num[data_to]
                L.write()
        for card_id in card_li:
            L = LinkDataDeleter(card_id)
            L.storageLocation = self.storage_num[data_from]
            L.delete()

        showInfo("OK!")