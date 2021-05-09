from PyQt5.QtWidgets import QDialog
from aqt.utils import showInfo

from .UIdialog_storage_switcher import Ui_Dialog

class StorageSwitcherDialog(QDialog,Ui_Dialog):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.from_Li=["卡片字段存储","sqlite数据库存储","JSON文件存储"]
        self.to_Li=["卡片字段存储","sqlite数据库存储","JSON文件存储"]
        self.switchMode = ["数据覆盖","数据合并"]
        self.init_UI()
        self.init_model()
        self.init_events()
        self.show()

    def init_UI(self):
        self.setupUi(self)
        self.setWindowTitle("链接数据迁移对话框")
        self.label_comment.setText(
            """注意1:当数据从A转移到B，会删除A中的数据记录,\n注意2:先把想要转移的卡片插入到input""")
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
    def onButtonCorrectClicked(self):
        data_from = self.comboBox_from.currentText()
        data_to = self.comboBox_to.currentText()
        data_mode = self.comboBox_switchMode.currentText()
