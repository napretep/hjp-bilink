from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QGridLayout
from .tools import objs, events, funcs, ALL
from . import ConfigTable_


class ConfigTable(QDialog):
    """
    line1 : 布局默认设置/set default layout property:方向/direction combox H/V,每行页数/pages per row spinbox
    line2 : 卡片默认设置/set default card property: 页码/pagenum spinbox , 画面比例/image ratio doublespinbox
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.config_dict = objs.SrcAdmin.get_config("clipper")
        self.schema = objs.JSONschema
        # self.G_layout_pos = [
        #     [(0, 0), (0, 1), (0, 2)],
        #     [(1, 0), (1, 1), (1, 2),
        #      (2, 1)],
        #     [(3, 0), (3, 1), (3, 2)],
        #     [(4, 2)]
        # ]
        # self.V_layout= QVBoxLayout(self)
        self.G_Layout = QGridLayout(self)
        # self.viewlayout: "ViewLayoutWidget" = ViewLayoutWidget(configtable=self)
        # self.pagepreset: "PagePresetWidget" = PagePresetWidget(configtable=self)
        self.tablayout = ConfigTable_.TabWidget(self)
        # self.outputpreset: "OutPutWidget" = OutPutWidget(configtable=self, gridposLi=self.G_layout_pos[2])
        self.buttonGroup = ConfigTable_.ButtonGroup(configtable=self)
        self.init_UI()
        self.init_events()
        self.show()

    def init_UI(self):
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.config))
        self.setWindowTitle("配置表/config")
        self.G_Layout.addWidget(self.tablayout, 0, 0)
        self.G_Layout.addWidget(self.buttonGroup, self.G_Layout.rowCount(), 0)
        self.setLayout(self.G_Layout)
        pass

    def init_events(self):
        ALL.signals.on_clipper_config_reload.connect(self.on_pagepicker_config_reload_handle)

    def on_pagepicker_config_reload_handle(self):
        self.config_dict = objs.SrcAdmin.get_config("clipper")
        ALL.signals.on_clipper_config_reload_end.emit()
        # print("发射on_pagepicker_config_reload_end")

    def init_data(self):
        pass
