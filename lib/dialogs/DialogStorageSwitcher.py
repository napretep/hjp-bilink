from PyQt5.QtWidgets import QDialog

from .UIdialog_storage_switcher import Ui_Dialog

class StorageSwitcherDialog(QDialog,Ui_Dialog):

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.init_UI()
        self.init_model()
        self.init_events()
        self.show()

    def init_UI(self):
        self.setupUi(self)
        pass
    def init_model(self):
        from_Li=["卡片字段存储","sqlite数据库存储","JSON文件存储"]
        to_Li=["卡片字段存储","sqlite数据库存储","JSON文件存储"]
        self.comboBox_from.addItems(from_Li)
        pass
    def init_events(self):
        pass