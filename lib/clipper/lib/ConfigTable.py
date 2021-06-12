from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QGridLayout
from .tools import objs, events, funcs
from .ConfigTable_ import ViewLayoutWidget, PagePresetWidget, OutPutWidget, ButtonGroup


class ConfigTable(QDialog):
    """
    line1 : 布局默认设置/set default layout property:方向/direction combox H/V,每行页数/pages per row spinbox
    line2 : 卡片默认设置/set default card property: 页码/pagenum spinbox , 画面比例/image ratio doublespinbox
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.config_dict = objs.SrcAdmin.get_json("config.json")
        self.schema = objs.JSONschema
        self.G_layout_pos = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(3, 2)]
        ]
        # self.V_layout= QVBoxLayout(self)
        self.G_Layout = QGridLayout(self)
        self.viewlayout = ViewLayoutWidget(config_dict=self.config_dict, configtable=self,
                                           gridposLi=self.G_layout_pos[0])
        self.pagepreset = PagePresetWidget(config_dict=self.config_dict, configtable=self,
                                           gridposLi=self.G_layout_pos[1])
        self.outputpreset = OutPutWidget(config_dict=self.config_dict, configtable=self, gridposLi=self.G_layout_pos[2])
        self.buttonGroup = ButtonGroup(configtable=self)
        self.init_UI()
        self.show()

    def init_UI(self):
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.config))
        self.setWindowTitle("config")
        self.G_Layout.addWidget(self.buttonGroup, self.G_Layout.rowCount(), 2)
        self.setLayout(self.G_Layout)
        pass

    def init_data(self):
        pass
