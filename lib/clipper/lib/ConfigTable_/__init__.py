import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QSpinBox, QHBoxLayout, QFrame, QDoubleSpinBox, QToolButton
from PyQt5.QtCore import Qt, QRect, QSize
from ..tools import funcs, objs, events

MAX_INT = 2147483646
pages_col_per_row = """
1 col per row:
page1
↓
page2
↓
page3

2 cols per row:
page1,page2
↓
page3,page4
↓
page5,page6
↓
"""
pages_row_per_col = """
1 row per col:
page1 → page2 → page3

2 rows per col
page1 → page3 → page5
page2 → page4 → page6
"""
tooltip_layout = """
vertical:
page1
↓
page2
↓
page3
horizontal:
page1→page2→page3
"""


def config_get_left_right(config, itemname):
    left = config[itemname]["constrain"]["data_range"]["left"]
    right = config[itemname]["constrain"]["data_range"]["right"]
    return left, right


class BaseWidget:
    def __init__(self, config_dict=None, configtable=None, gridposLi=None):
        self.configtable = configtable
        self.config_dict = config_dict
        self.gridposLi = gridposLi


class ViewLayoutWidget(BaseWidget):
    def __init__(self, config_dict=None, configtable=None, gridposLi=None):
        super().__init__(config_dict=config_dict, configtable=configtable, gridposLi=gridposLi)
        self.label_head = QLabel(configtable)

        self.schema = objs.JSONschema
        self.viewlayoutName = self.schema.viewlayout_mode
        self.viewlayout_mode = {
            self.viewlayoutName.Vertical: ["垂直/vertical"],
            self.viewlayoutName.Horizontal: ["水平/horizontal"],
            self.viewlayoutName.Freemode: ["自由模式/free mode"]
        }
        self.txt_on_colrow_count = {  # 1 label name, 2 tooltip content
            self.viewlayoutName.Vertical: ["每行列数/cols per row", pages_col_per_row],
            self.viewlayoutName.Horizontal: ["每列行数/rows per col", pages_row_per_col]
        }

        self.init_UI()

    def init_UI(self):
        self.label_head.setText("默认布局/default layout")
        self.label_head.setToolTip("用来定义下一个页面出现的位置/define the position of next page to place")
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
            self.configtable.G_Layout.addWidget(self.widgetLi[i], self.gridposLi[i][0], self.gridposLi[i][1])
        self.configtable.G_Layout.addWidget(self.layoutHorizontalRowCount, self.gridposLi[-1][0], self.gridposLi[-1][1])
        self.showhide_ColRow_count()

    def init_viewlyout_horizontal_rowcount(self, left, right):
        layoutHorizontalRowCount = QSpinBox(self.configtable)
        layoutHorizontalRowCount.setRange(left, right if right != False else MAX_INT)
        layoutHorizontalRowCount.setValue(self.config_dict["viewlayout_row_count"]["value"])
        self.layoutHorizontalRowCount = objs.GridHDescUnit(
            parent=self.configtable, labelname=self.txt_on_colrow_count[self.viewlayoutName.Horizontal][0],
            widget=layoutHorizontalRowCount, tooltip=self.txt_on_colrow_count[self.viewlayoutName.Horizontal][1])

    def init_viewlayout_vertical_colcount(self, left, right):
        layoutVerticalColCount = QSpinBox(self.configtable)
        layoutVerticalColCount.setRange(left, right if right != False else MAX_INT)
        layoutVerticalColCount.setValue(self.config_dict["viewlayout_column_count"]["value"])
        self.layoutVerticalColCount = objs.GridHDescUnit(
            parent=self.configtable, labelname=self.txt_on_colrow_count[self.viewlayoutName.Vertical][0],
            widget=layoutVerticalColCount, tooltip=self.txt_on_colrow_count[self.viewlayoutName.Vertical][1])

    def init_viewlayoutmodecombox(self):
        layoutmodewidget = QComboBox(self.configtable)
        for val in self.config_dict["viewlayout_mode"]["constrain"]["data_range"]:
            layoutmodewidget.addItem(self.viewlayout_mode[val][0])
        value = self.viewlayout_mode[self.config_dict["viewlayout_mode"]["value"]][0]
        layoutmodewidget.setCurrentIndex(layoutmodewidget.findText(value))
        self.layoutmode = objs.GridHDescUnit(parent=self.configtable, tooltip=tooltip_layout,
                                             labelname="方向/direction:", widget=layoutmodewidget)

    def showhide_ColRow_count(self):
        layoutmode = self.config_dict["viewlayout_mode"]["value"]
        if layoutmode == self.viewlayoutName.Vertical:
            self.layoutHorizontalRowCount.hide()
            self.layoutVerticalColCount.show()
            self.layoutVerticalColCount.widget.setValue(self.config_dict["viewlayout_column_count"]["value"])

        elif layoutmode == self.viewlayoutName.Horizontal:
            self.layoutHorizontalRowCount.show()
            self.layoutVerticalColCount.hide()
            self.layoutHorizontalRowCount.widget.setValue(self.config_dict["viewlayout_row_count"]["value"])

        else:
            self.layoutVerticalColCount.hide()
            self.layoutHorizontalRowCount.hide()


class PagePresetWidget(BaseWidget):
    def __init__(self, config_dict=None, configtable=None, gridposLi=None):
        super().__init__(config_dict=config_dict, configtable=configtable, gridposLi=gridposLi)
        # super().__init__(parent=parent)
        self.label_head = QLabel(configtable)
        self.h_layout = QHBoxLayout(configtable)

        self.schema = objs.JSONschema
        self.layoutName = self.schema.viewlayout_mode
        self.init_UI()

    def init_UI(self):
        self.label_head.setText("页面预设/page preset")
        self.label_head.setToolTip("用来定义如何从PDF中提取页面/define how to extract page from PDF")
        pagenum = QSpinBox(self.configtable)
        right = self.config_dict["page_num"]["constrain"]["data_range"]["right"]
        left = self.config_dict["page_num"]["constrain"]["data_range"]["left"]
        pagenum.setRange(left, right if right != False else MAX_INT)
        pagenum.setValue(self.config_dict["page_num"]["value"])

        self.pagenum = objs.GridHDescUnit(parent=self.configtable, labelname="页码/page num:", widget=pagenum)
        imgratio = QDoubleSpinBox(self.configtable)
        right = self.config_dict["page_ratio"]["constrain"]["data_range"]["right"]
        left = self.config_dict["page_ratio"]["constrain"]["data_range"]["left"]
        imgratio.setRange(left, right if right != False else MAX_INT)
        imgratio.setSingleStep(0.1)
        imgratio.setValue(self.config_dict["page_ratio"]["value"])
        self.imgratio = objs.GridHDescUnit(parent=self.configtable, labelname="画面比例/image ratio:", widget=imgratio)
        self.widgetLi = [
            self.label_head, self.pagenum, self.imgratio
        ]
        for i in range(len(self.widgetLi)):
            self.configtable.G_Layout.addWidget(self.widgetLi[i], self.gridposLi[i][0], self.gridposLi[i][1])


class OutPutWidget(BaseWidget):
    def __init__(self, config_dict=None, configtable=None, gridposLi=None):
        super().__init__(config_dict=config_dict, configtable=configtable, gridposLi=gridposLi)

        self.schema = objs.JSONschema
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
        self.label_head.setToolTip("当我们裁剪完图片, 要保存到卡片中时, 需要一些设定. 比如图片最终的大小,保存的方式,等等\n"
                                   "When we have cropped the image and want to save it to the card, we need some Settings. Such as the final size of the image, the way to save, etc")
        self.init_RatioFix()
        self.init_needRatioFix()

        self.widgetLi = [self.label_head, self.needRatioFix, self.RatioFix]
        for i in range(len(self.widgetLi)):
            self.configtable.G_Layout.addWidget(self.widgetLi[i], self.gridposLi[i][0], self.gridposLi[i][1])

    def init_RatioFix(self):
        for k, v in self.needratiofixvalue.items():
            self.Combox_needRatioFix.addItem(v, userData=k)
        self.Combox_needRatioFix.setCurrentIndex(self.Combox_needRatioFix.findData(self.needratiofixcode))
        self.needRatioFix = objs.GridHDescUnit(parent=self.configtable, labelname="比例修正/ratio fix",
                                               tooltip="final output ratio=(image ratio)*(zoom in/out ratio)*(output ratio)",
                                               widget=self.Combox_needRatioFix)

    def init_needRatioFix(self):
        left, right = config_get_left_right(self.config_dict, "output_RatioFix")
        print(right)
        self.DBspinbox_RatioFix.setRange(left, right)
        self.DBspinbox_RatioFix.setSingleStep(0.1)
        self.DBspinbox_RatioFix.setValue(self.config_dict["output_RatioFix"]["value"])
        self.RatioFix = objs.GridHDescUnit(parent=self.configtable, labelname="修正数/output ratio",
                                           widget=self.DBspinbox_RatioFix)

class ButtonGroup(QWidget):
    def __init__(self, parent=None, configtable=None):
        super().__init__(parent=parent)
        self.configtable = configtable
        self.reset_button = QToolButton(self)
        self.correct_button = QToolButton(self)
        self.h_layout = QHBoxLayout(self)
        self.init_UI()

    def init_UI(self):
        from ..tools.objs import SrcAdmin
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
