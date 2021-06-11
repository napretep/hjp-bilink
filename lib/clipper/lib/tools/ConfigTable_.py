import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QSpinBox, QHBoxLayout, QFrame, QDoubleSpinBox, QToolButton
from PyQt5.QtCore import Qt, QRect, QSize

MAX_INT = 2147483646


def config_get_left_right(config, itemname):
    left = config[itemname]["constrain"]["data_range"]["left"]
    right = config[itemname]["constrain"]["data_range"]["left"]
    return left, right


class BaseWidget:
    def __init__(self, config_dict=None, configtable=None, level=None):
        self.configtable = configtable
        self.config_dict = config_dict
        self.level = level


class GridHDescUnit(QWidget):
    def __init__(self, parent=None, labelname=None, widget=None):
        super().__init__(parent=parent)
        self.label = QLabel(parent)
        self.label.setText(labelname)
        self.widget = widget
        self.H_layout = QHBoxLayout(self)
        self.H_layout.addWidget(self.label)
        self.H_layout.addWidget(self.widget)
        self.setLayout(self.H_layout)


class ViewLayoutWidget(BaseWidget):
    def __init__(self, parent=None, config_dict=None, configtable=None, level=None):
        super().__init__(config_dict=config_dict, configtable=configtable, level=level)
        self.label_head = QLabel(configtable)
        from .objs import JSONschema
        self.schema = JSONschema
        self.viewlayoutName = self.schema.viewlayout_mode
        self.viewlayout_mode = {
            self.viewlayoutName.Vertical: "垂直/vertical",
            self.viewlayoutName.Horizontal: "水平/horizontal",
            self.viewlayoutName.Freemode: "自由模式/free mode"
        }
        self.txt_on_colrow_count = {
            self.viewlayoutName.Vertical: "每行列数/cols per row",
            self.viewlayoutName.Horizontal: "每列行数/rows per col"
        }

        self.init_UI()

    def init_UI(self):
        self.label_head.setText("默认布局/default layout")
        self.init_viewlayoutmodecombox()
        left = self.config_dict["viewlayout_column_count"]["constrain"]["data_range"]["left"]
        right = self.config_dict["viewlayout_column_count"]["constrain"]["data_range"]["right"]
        self.init_viewlayout_vertical_colcount(left, right)
        self.init_viewlyout_horizontal_rowcount(left, right)
        self.widgetLi = [
            self.label_head,
            self.layoutmode,
            self.layoutVerticalColCount
        ]

        for i in range(len(self.widgetLi)):
            self.configtable.G_Layout.addWidget(self.widgetLi[i], 0, i)
        self.showhide_ColRow_count()

    def init_viewlyout_horizontal_rowcount(self, left, right):
        layoutHorizontalRowCount = QSpinBox(self.configtable)
        layoutHorizontalRowCount.setRange(left, right if right != False else MAX_INT)
        layoutHorizontalRowCount.setValue(self.config_dict["viewlayout_row_count"]["value"])
        self.layoutHorizontalRowCount = GridHDescUnit(
            parent=self.configtable, labelname=self.txt_on_colrow_count[self.viewlayoutName.Horizontal],
            widget=layoutHorizontalRowCount)

    def init_viewlayout_vertical_colcount(self, left, right):
        layoutVerticalColCount = QSpinBox(self.configtable)
        layoutVerticalColCount.setRange(left, right if right != False else MAX_INT)
        layoutVerticalColCount.setValue(self.config_dict["viewlayout_column_count"]["value"])
        self.layoutVerticalColCount = GridHDescUnit(
            parent=self.configtable, labelname=self.txt_on_colrow_count[self.viewlayoutName.Vertical],
            widget=layoutVerticalColCount)

    def init_viewlayoutmodecombox(self):
        layoutmodewidget = QComboBox(self.configtable)
        for val in self.config_dict["viewlayout_mode"]["constrain"]["data_range"]:
            layoutmodewidget.addItem(self.viewlayout_mode[val])
        value = self.viewlayout_mode[self.config_dict["viewlayout_mode"]["value"]]
        layoutmodewidget.setCurrentIndex(layoutmodewidget.findText(value))
        self.layoutmode = GridHDescUnit(parent=self.configtable, labelname="方向/direction:", widget=layoutmodewidget)

    def showhide_ColRow_count(self):
        layoutmode = self.config_dict["viewlayout_mode"]["value"]
        if layoutmode == self.viewlayoutName.Vertical:
            self.layoutHorizontalRowCount.hide()
            self.layoutVerticalColCount.show()
            self.layoutVerticalColCount.widget.setValue(self.config_dict["viewlayout_column_count"]["value"])
            self.configtable.G_Layout.addWidget(self.layoutVerticalColCount, 0, 2)
        elif layoutmode == self.viewlayoutName.Horizontal:
            self.layoutHorizontalRowCount.show()
            self.layoutVerticalColCount.hide()
            self.layoutHorizontalRowCount.widget.setValue(self.config_dict["viewlayout_row_count"]["value"])
            self.configtable.G_Layout.addWidget(self.layoutHorizontalRowCount, 0, 2)
        else:
            self.layoutVerticalColCount.hide()
            self.layoutHorizontalRowCount.hide()


class PagePresetWidget(BaseWidget):
    def __init__(self, parent=None, config_dict=None, configtable=None, level=None):
        super().__init__(config_dict=config_dict, configtable=configtable, level=level)
        # super().__init__(parent=parent)
        self.label_head = QLabel(configtable)
        self.label_body1 = QLabel(configtable)
        self.label_body2 = QLabel(configtable)
        # self.pagenum = QSpinBox(configtable)
        # self.imgratio = QDoubleSpinBox(configtable)
        self.h_layout = QHBoxLayout(configtable)

        from .objs import JSONschema
        self.schema = JSONschema
        self.layoutName = self.schema.viewlayout_mode
        self.init_UI()

    def init_UI(self):
        self.label_head.setText("页面预设/page preset")
        pagenum = QSpinBox(self.configtable)
        right = self.config_dict["page_num"]["constrain"]["data_range"]["right"]
        left = self.config_dict["page_num"]["constrain"]["data_range"]["left"]
        pagenum.setRange(left, right if right != False else MAX_INT)
        pagenum.setValue(self.config_dict["page_num"]["value"])
        self.pagenum = GridHDescUnit(parent=self.configtable, labelname="页码/page num:", widget=pagenum)

        imgratio = QDoubleSpinBox(self.configtable)
        right = self.config_dict["page_ratio"]["constrain"]["data_range"]["right"]
        left = self.config_dict["page_ratio"]["constrain"]["data_range"]["left"]
        imgratio.setRange(left, right if right != False else MAX_INT)
        imgratio.setValue(self.config_dict["page_ratio"]["value"])
        self.imgratio = GridHDescUnit(parent=self.configtable, labelname="画面比例/image ratio:", widget=imgratio)
        self.widgetLi = [
            self.label_head, self.pagenum, self.imgratio
        ]
        for i in range(len(self.widgetLi)):
            self.configtable.G_Layout.addWidget(self.widgetLi[i], self.level, i)


class OutPutWidget(BaseWidget):
    def __init__(self, parent=None, config_dict=None, configtable=None, level=0):
        super().__init__(config_dict=config_dict, configtable=configtable, level=level)
        from .objs import JSONschema
        self.schema = JSONschema
        self.label_head = QLabel(self.configtable)
        self.needratiofixcode = self.config_dict["output_needRatioFix"]["value"]
        self.Combox_needRatioFix = QComboBox(self.configtable)
        self.needratiofixvalue = {
            self.schema.needratiofix_mode.no: "不需要/don't need",
            self.schema.needratiofix_mode.yes: "需要/need"
        }
        self.DBspinbox_RatioFix = QDoubleSpinBox(self.configtable)
        self.init_UI()

    def init_UI(self):
        self.label_head.setText("输出预设/output preset")
        for k, v in self.needratiofixvalue.items():
            self.Combox_needRatioFix.addItem(v, userData=k)
        self.Combox_needRatioFix.setCurrentIndex(self.Combox_needRatioFix.findData(self.needratiofixcode))
        self.needRatioFix = GridHDescUnit(parent=self.configtable, labelname="比例修正/need factor",
                                          widget=self.Combox_needRatioFix)
        left, right = config_get_left_right(self.config_dict, "output_RatioFix")
        value = self.config_dict["output_RatioFix"]["value"]
        self.DBspinbox_RatioFix.setRange(left, right)
        self.DBspinbox_RatioFix.setValue(20.0)
        self.RatioFix = GridHDescUnit(parent=self.configtable, labelname="修正数/factor number",
                                      widget=self.DBspinbox_RatioFix)
        self.RatioFix.widget.setValue(20.0)
        self.widgetLi = [self.label_head, self.needRatioFix, self.RatioFix]
        self.configtable.G_Layout.addWidget(self.label_head, self.level, 0)
        self.configtable.G_Layout.addWidget(self.needRatioFix, self.level, 1)
        self.configtable.G_Layout.addWidget(self.RatioFix, self.level, 2)


class ButtonGroup(QWidget):
    def __init__(self, parent=None, configtable=None):
        super().__init__(parent=parent)
        self.configtable = configtable
        self.reset_button = QToolButton(self)
        self.correct_button = QToolButton(self)
        self.h_layout = QHBoxLayout(self)
        self.init_UI()

    def init_UI(self):
        from .objs import SrcAdmin
        self.h_layout.setAlignment(Qt.AlignRight)
        self.reset_button.setIcon(QIcon(SrcAdmin.imgDir.config_reset))
        self.reset_button.setIconSize(QSize(30, 30))
        self.reset_button.setStyleSheet("height:40px;width:40px")
        self.correct_button.setIcon(QIcon(SrcAdmin.imgDir.correct))
        self.correct_button.setStyleSheet("height:40px;width:40px")
        self.correct_button.setIconSize(QSize(30, 30))
        self.h_layout.addWidget(self.reset_button)
        self.h_layout.addWidget(self.correct_button)
        self.setLayout(self.h_layout)
