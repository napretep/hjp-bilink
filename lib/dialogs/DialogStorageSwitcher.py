from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from aqt.utils import showInfo
from ..obj.inputObj import Input
from .UIdialog_storage_switcher import Ui_Dialog
from ..obj.linkData_reader import LinkDataReader
from ..obj.linkData_writer import LinkDataWriter


class StorageSwitcherDialog(QDialog,Ui_Dialog):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.from_Li=["卡片字段存储","sqlite数据库存储","JSON文件存储"]
        self.to_Li=["卡片字段存储","sqlite数据库存储","JSON文件存储"]
        self.switchMode = ["数据覆盖","数据合并"]
        self.storage_num = {
            "卡片字段存储":1, "sqlite数据库存储":0, "JSON文件存储":2
        }
        self.init_UI()
        self.init_model()
        self.init_events()
        self.show()

    def init_UI(self):
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle("链接数据迁移对话框")
        self.label_comment.setText(
            """注意1:当数据从A转移到B，会删除A中的数据记录,\n注意2:先把想要转移的卡片插入到input""")
        self.button_correct.setText("执行")
        pass
    def init_model(self):
        self.comboBox_from.addItems(self.from_Li)
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
        if data_mode == "数据覆盖":
            for id,data in cardinfo.items():
                L = LinkDataWriter(id, data)
                L.storageLocation = self.storage_num[data_to]
                L.write()
        # else:
