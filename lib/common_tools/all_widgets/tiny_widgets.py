from ..compatible_import import *
from ..widgets import view_config_chooser
from .. import G

class 视图:
    class 新建视图(QDialog):
        def __init__(self):
            super().__init__()
            self.视图的名字=""
            self.选中的配置=None
            self.确认建立=False


        # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

