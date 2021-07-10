from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QGridLayout
from .tools import objs, events, funcs, ALL
from . import ConfigTable_
print, printer = funcs.logger(__name__)

class ConfigTable(QDialog):
    """
    line1 : 布局默认设置/set default layout property:方向/direction combox H/V,每行页数/pages per row spinbox
    line2 : 卡片默认设置/set default card property: 页码/pagenum spinbox , 画面比例/image ratio doublespinbox
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.config_dict = objs.SrcAdmin.get_config("clipper")
        self.schema = objs.JSONschema

        self.G_Layout = QGridLayout(self)

        self.tablayout = ConfigTable_.TabWidget(self)
        self.buttonGroup = ConfigTable_.ButtonGroup(configtable=self)
        self.init_UI()
        self.event_dict = {
            ALL.signals.on_config_reload: self.on_config_reload_handle
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
        # self.init_events()
        self.show()
        print("__init__")

    def init_UI(self):
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.config))
        self.setWindowTitle("配置表/config")
        self.G_Layout.addWidget(self.tablayout, 0, 0, 2, 1)
        self.G_Layout.addWidget(self.buttonGroup, 1, 1)
        self.setLayout(self.G_Layout)
        pass

    def on_config_reload_handle(self):
        self.config_dict = objs.SrcAdmin.get_config("clipper")
        ALL.signals.on_config_reload_end.emit()

    def init_data(self):
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.all_event.unbind(self.__class__.__name__)
