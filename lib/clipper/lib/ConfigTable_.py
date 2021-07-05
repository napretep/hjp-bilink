import json
import os
import sys
import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QSpinBox, QHBoxLayout, QFrame, QDoubleSpinBox, QToolButton, \
    QLineEdit, QTabWidget, QFormLayout, QTabBar, QStylePainter, QStyleOptionTab, QStyle, QProxyStyle, QStyleOption
from PyQt5.QtCore import Qt, QRect, QSize, QPoint
from .tools import funcs, objs, events, ALL

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


class BaseWidget(QWidget):
    def __init__(self, parent=None, configtable=None, gridposLi=None):
        super().__init__(parent=parent)
        self.configtable = configtable
        # self.config_dict = config_dict
        self.gridposLi = gridposLi


class ViewLayoutWidget(BaseWidget):
    def __init__(self, parent=None, configtable=None, gridposLi=None):
        super().__init__(parent=None, configtable=configtable, gridposLi=gridposLi)
        self.layoutVerticalColCountWidget = QSpinBox(self.configtable)
        self.layoutHorizontalRowCountWidget = QSpinBox(self.configtable)
        self.layoutModeWidget = QComboBox(self.configtable)
        self.layoutVerticalColCount_changed = False
        self.layoutHorizontalRowCount_changed = False
        self.layoutMode_changed = False
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
        self.init_events()

    def init_UI(self):
        # self.label_head.setText("布局预设/layout preset")
        # self.label_head.setToolTip("用来定义下一个页面出现的位置/define the position of next page to place")
        self.init_viewlayoutmodecombox()
        left = self.configtable.config_dict["viewlayout.col_per_row"]["constrain"]["data_range"]["left"]
        right = self.configtable.config_dict["viewlayout.col_per_row"]["constrain"]["data_range"]["right"]
        self.init_viewlayout_vertical_colcount(left, right)
        self.init_viewlyout_horizontal_rowcount(left, right)
        self.widgetLi = [
            # self.label_head,
            self.layoutmode,
            self.layoutVerticalColCount
        ]
        h_layout = QHBoxLayout(self)
        for w in self.widgetLi:
            h_layout.addWidget(w)
        self.setLayout(h_layout)
        # for i in range(len(self.widgetLi)):
        #     self.configtable.G_Layout.addWidget(self.widgetLi[i], self.gridposLi[i][0], self.gridposLi[i][1])
        # self.configtable.G_Layout.addWidget(self.layoutHorizontalRowCount, self.gridposLi[-1][0], self.gridposLi[-1][1])
        self.showhide_ColRow_count()

    def init_viewlyout_horizontal_rowcount(self, left, right):
        self.layoutHorizontalRowCountWidget.setRange(left, right if right != False else MAX_INT)
        self.layoutHorizontalRowCountWidget.setValue(self.configtable.config_dict["viewlayout.row_per_col"]["value"])
        self.layoutHorizontalRowCount = objs.GridHDescUnit(
            parent=self.configtable, labelname=self.txt_on_colrow_count[self.viewlayoutName.Horizontal][0],
            widget=self.layoutHorizontalRowCountWidget,
            tooltip=self.txt_on_colrow_count[self.viewlayoutName.Horizontal][1])

    def init_viewlayout_vertical_colcount(self, left, right):
        self.layoutVerticalColCountWidget.setRange(left, right if right != False else MAX_INT)
        self.layoutVerticalColCountWidget.setValue(self.configtable.config_dict["viewlayout.col_per_row"]["value"])
        self.layoutVerticalColCount = objs.GridHDescUnit(
            parent=self.configtable, labelname=self.txt_on_colrow_count[self.viewlayoutName.Vertical][0],
            widget=self.layoutVerticalColCountWidget, tooltip=self.txt_on_colrow_count[self.viewlayoutName.Vertical][1])

    def init_viewlayoutmodecombox(self):
        self.layoutModeWidget.clear()
        for val in self.configtable.config_dict["viewlayout.mode"]["constrain"]["data_range"]:
            self.layoutModeWidget.addItem(self.viewlayout_mode[val][0], userData=val)

        value = self.viewlayout_mode[self.configtable.config_dict["viewlayout.mode"]["value"]][0]
        self.layoutModeWidget.setCurrentIndex(self.layoutModeWidget.findText(value))
        self.layoutmode = objs.GridHDescUnit(parent=self.configtable, tooltip=tooltip_layout,
                                             labelname="方向/direction:", widget=self.layoutModeWidget)

    def init_events(self):
        self.layoutModeWidget.currentIndexChanged.connect(self.on_layoutmodewidget_currentIndexChanged_handle)
        self.layoutVerticalColCountWidget.valueChanged.connect(self.on_layoutVerticalColCountWidget_valueChanged_handle)
        self.layoutHorizontalRowCountWidget.valueChanged.connect(
            self.on_layoutHorizontalRowCountWidget_valueChanged_handle)
        ALL.signals.on_clipper_config_reload_end.connect(self.on_pagepicker_config_reload_end_handle)

    def on_pagepicker_config_reload_end_handle(self):
        print(f"{self.__class__.__name__} 接受on_pagepicker_config_reload_end_handle")
        self.init_UI()

    def on_layoutHorizontalRowCountWidget_valueChanged_handle(self, value):
        self.layoutHorizontalRowCount_changed = True

    def on_layoutVerticalColCountWidget_valueChanged_handle(self, value):
        self.layoutVerticalColCount_changed = True

    def on_layoutmodewidget_currentIndexChanged_handle(self, index):
        self.layoutMode_changed = True
        self.showhide_ColRow_count()

    def showhide_ColRow_count(self):
        layoutmode = self.layoutModeWidget.currentData(Qt.UserRole)
        if layoutmode == self.viewlayoutName.Vertical:
            self.layoutHorizontalRowCount.hide()
            self.layoutVerticalColCount.show()
            self.layoutVerticalColCount.widget.setValue(self.configtable.config_dict["viewlayout.col_per_row"]["value"])

        elif layoutmode == self.viewlayoutName.Horizontal:
            self.layoutHorizontalRowCount.show()
            self.layoutVerticalColCount.hide()
            self.layoutHorizontalRowCount.widget.setValue(
                self.configtable.config_dict["viewlayout.row_per_col"]["value"])

        else:
            self.layoutVerticalColCount.hide()
            self.layoutHorizontalRowCount.hide()


class PagePresetWidget(BaseWidget):
    """for pagepicker"""

    def __init__(self, parent=None, configtable=None, gridposLi=None):
        super().__init__(parent=None, configtable=configtable, gridposLi=gridposLi)
        # super().__init__(parent=parent)
        # self.label_head = QLabel(configtable)
        self.h_layout = QHBoxLayout(configtable)
        self.pagenumWidget = QSpinBox(self.configtable)
        self.imgRatioWidget = QDoubleSpinBox(self.configtable)
        self.defaultPathWidget = QLineEdit(self.configtable)
        self.defaultPath_changed = False
        self.pagenum_changed = False
        self.imgRatio_changed = False
        self.schema = objs.JSONschema
        self.layoutName = self.schema.viewlayout_mode
        self.init_UI()
        self.init_events()

    def init_pagenum(self):
        left, right = config_get_left_right(self.configtable.config_dict, "pagepicker.bottombar.page_ratio")
        # right = self.config_dict["page_num"]["constrain"]["data_range"]["right"]
        # left = self.config_dict["page_num"]["constrain"]["data_range"]["left"]
        self.pagenumWidget.setRange(left, right if right != False else MAX_INT)
        self.pagenumWidget.setValue(self.configtable.config_dict["pagepicker.bottombar.page_num"]["value"])
        self.pagenum = objs.GridHDescUnit(parent=self.configtable, labelname="页码/page num:", widget=self.pagenumWidget)

    def init_imgratio(self):
        left, right = config_get_left_right(self.configtable.config_dict, "pagepicker.bottombar.page_ratio")
        # right = self.config_dict["page_ratio"]["constrain"]["data_range"]["right"]
        # left = self.config_dict["page_ratio"]["constrain"]["data_range"]["left"]
        self.imgRatioWidget.setRange(left, right if right != False else MAX_INT)
        self.imgRatioWidget.setSingleStep(0.1)
        self.imgRatioWidget.setValue(self.configtable.config_dict["pagepicker.bottombar.page_ratio"]["value"])
        self.imgratio = objs.GridHDescUnit(parent=self.configtable, labelname="画面比例/image ratio:",
                                           widget=self.imgRatioWidget)

    def init_defaultpath(self):
        self.defaultPathWidget.setText(self.configtable.config_dict["pagepicker.bottombar.default_path"]["value"])
        self.defaultpath = objs.GridHDescUnit(
            parent=self.configtable, labelname="默认读取位置/default load path", widget=self.defaultPathWidget)

    def init_UI(self):
        # self.label_head.setText("页面预设/page preset")
        # self.label_head.setToolTip("用来定义如何从PDF中提取页面/define how to extract page from PDF")
        self.init_defaultpath()
        self.init_imgratio()
        self.init_pagenum()

        self.widgetLi = [
            # self.label_head,
            self.pagenum, self.imgratio, self.defaultpath
        ]
        f_layout = QFormLayout(self)
        for i in self.widgetLi:
            f_layout.addRow("test", i)
        self.setLayout(f_layout)

        # for i in range(len(self.widgetLi)):
        #     self.configtable.G_Layout.addWidget(self.widgetLi[i], self.gridposLi[i][0], self.gridposLi[i][1])

    def init_events(self):
        self.defaultPathWidget.textChanged.connect(self.on_defaultPathWidget_textChanged_handle)
        self.pagenumWidget.valueChanged.connect(self.on_pagenumWidget_valueChanged_handle)
        self.imgRatioWidget.valueChanged.connect(self.on_imgRatioWidget_valueChanged_handle)
        ALL.signals.on_clipper_config_reload_end.connect(self.on_pagepicker_config_reload_end_handle)

    def on_pagepicker_config_reload_end_handle(self):
        print(f"{self.__class__.__name__} 接受on_pagepicker_config_reload_end_handle")
        self.init_UI()

    def on_imgRatioWidget_valueChanged_handle(self, value):
        self.imgRatio_changed = True

    def on_pagenumWidget_valueChanged_handle(self, value):
        # print("on_pagenumWidget_valueChanged_handle")
        self.pagenum_changed = True

    def on_defaultPathWidget_textChanged_handle(self, txt):
        if txt == "":
            self.defaultPathWidget.setStyleSheet("background-color:white;")
            return
        if os.path.exists(txt):
            self.defaultPath_changed = True
            self.defaultPathWidget.setStyleSheet("background-color:white;")
        else:
            self.defaultPath_changed = False
            self.defaultPathWidget.setStyleSheet("background-color:red;")


class OutPutWidget(BaseWidget):
    def __init__(self, configtable=None, gridposLi=None):
        super().__init__(configtable=configtable, gridposLi=gridposLi)

        self.schema = objs.JSONschema
        self.label_head = QLabel(self.configtable)
        self.needratiofixcode = self.configtable.config_dict["output.needRatioFix"]["value"]
        self.needRatioFixWidget = QComboBox(self.configtable)
        self.needRatioFix_changed = False
        self.RatioFixWidget = QDoubleSpinBox(self.configtable)
        self.RatioFix_changed = False
        self.needratiofixvalue = {
            self.schema.needratiofix_mode.no: "不需要/don't need",
            self.schema.needratiofix_mode.yes: "需要/need"
        }
        self.init_UI()
        self.init_events()

    def init_UI(self):
        self.label_head.setText("输出预设/output preset")
        self.label_head.setToolTip("当我们裁剪完图片, 要保存到卡片中时, 需要一些设定. 比如图片最终的大小,保存的方式,等等\n"
                                   "When we have cropped the image and want to save it to the card, we need some Settings. Such as the final size of the image, the way to save, etc")
        self.init_RatioFix()
        self.init_needRatioFix()

        self.widgetLi = [self.label_head, self.needRatioFix, self.RatioFix]
        for i in range(len(self.widgetLi)):
            self.configtable.G_Layout.addWidget(self.widgetLi[i], self.gridposLi[i][0], self.gridposLi[i][1])

    def init_needRatioFix(self):
        self.needRatioFixWidget.clear()
        for k, v in self.needratiofixvalue.items():
            self.needRatioFixWidget.addItem(v, userData=k)
        self.needRatioFixWidget.setCurrentIndex(self.needRatioFixWidget.findData(self.needratiofixcode))
        self.needRatioFix = objs.GridHDescUnit(parent=self.configtable, labelname="比例修正/ratio fix",
                                               tooltip="final output ratio=(image ratio)*(zoom in/out ratio)*(output ratio)",
                                               widget=self.needRatioFixWidget)
        curr_index = self.needRatioFixWidget.currentIndex()
        self.spinbox_enable_switch(curr_index)

    def init_RatioFix(self):
        left, right = config_get_left_right(self.configtable.config_dict, "output.RatioFix")
        print(right)
        self.RatioFixWidget.setRange(left, right)
        self.RatioFixWidget.setSingleStep(0.1)
        self.RatioFixWidget.setValue(self.configtable.config_dict["output.RatioFix"]["value"])
        self.RatioFix = objs.GridHDescUnit(parent=self.configtable, labelname="修正数/output ratio",
                                           widget=self.RatioFixWidget)

    def init_events(self):
        self.needRatioFixWidget.currentIndexChanged.connect(self.on_needRatioFixWidget_currentIndexChanged_handle)
        self.RatioFixWidget.valueChanged.connect(self.on_RatioFixWidget_valueChanged_handle)
        ALL.signals.on_clipper_config_reload_end.connect(self.on_pagepicker_config_reload_end_handle)

    def on_pagepicker_config_reload_end_handle(self):
        print(f"{self.__class__.__name__} 接受on_pagepicker_config_reload_end_handle")
        self.init_UI()

    def on_RatioFixWidget_valueChanged_handle(self, value):
        self.RatioFix_changed = True

    def on_needRatioFixWidget_currentIndexChanged_handle(self, index):
        self.spinbox_enable_switch(index)
        self.needRatioFix_changed = True

    def spinbox_enable_switch(self, index):
        if self.needRatioFixWidget.itemData(index, Qt.UserRole) == self.schema.needratiofix_mode.no:
            self.RatioFixWidget.setDisabled(True)
        else:
            self.RatioFixWidget.setDisabled(False)


class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r
            c = self.tabRect(i).center()

            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


#
# class ProxyStyle(QtWidgets.QProxyStyle):
#     def drawControl(self, element, opt, painter, widget):
#         if element == QtWidgets.QStyle.CE_TabBarTabLabel:
#             ic = self.pixelMetric(QtWidgets.QStyle.PM_TabBarIconSize)
#             r = QtCore.QRect(opt.rect)
#             w =  0 if opt.icon.isNull() else opt.rect.width() + self.pixelMetric(QtWidgets.QStyle.PM_TabBarIconSize)
#             r.setHeight(opt.fontMetrics.width(opt.text)*2+20 + w)
#             r.moveBottom(opt.rect.bottom())
#             opt.rect = r
#         QtWidgets.QProxyStyle.drawControl(self, element, opt, painter, widget)
# QtWidgets.QApplication.setStyle(ProxyStyle())
class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tab_viewlayout = ViewLayoutWidget(parent=self, configtable=parent)
        self.tab_pagepreset = PagePresetWidget(parent=self, configtable=parent)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QTabWidget.West)
        self.addTab(self.tab_viewlayout, "主视口/main_viewport")
        self.addTab(self.tab_pagepreset, "页面选取器/pagepicker")
        # self.setTabToolTip(0,"用来定义下一个页面出现的位置/define the position of next page to place")
        # self.setTabToolTip(1,"用来定义如何从PDF中提取页面/define how to extract page from PDF")


class ButtonGroup(BaseWidget):
    def __init__(self, parent=None, configtable=None):
        super().__init__(configtable=configtable)
        self.reset_button = QToolButton(self)
        self.correct_button = QToolButton(self)
        self.h_layout = QHBoxLayout(self)
        self.init_UI()
        self.init_events()

    def init_UI(self):

        self.h_layout.setAlignment(Qt.AlignRight)
        self.reset_button.setIcon(QIcon(objs.SrcAdmin.imgDir.config_reset))
        self.reset_button.setIconSize(QSize(30, 30))
        self.reset_button.setStyleSheet("height:40px;width:40px")
        self.correct_button.setIcon(QIcon(objs.SrcAdmin.imgDir.correct))
        self.correct_button.setStyleSheet("height:40px;width:40px")
        self.correct_button.setIconSize(QSize(30, 30))
        self.h_layout.addWidget(self.reset_button)
        self.h_layout.addWidget(self.correct_button)
        self.setLayout(self.h_layout)

    def init_events(self):
        self.correct_button.clicked.connect(self.on_correct_button_clicked_handle)
        self.reset_button.clicked.connect(self.on_button_reset_clicked_handle)

    def on_button_reset_clicked_handle(self):
        data = json.dumps(objs.SrcAdmin.get_config("clipper.template"), ensure_ascii=False, sort_keys=True, indent=4,
                          separators=(',', ':'))
        path = objs.SrcAdmin.jsonDir.clipper
        objs.SrcAdmin.save_config(path, data)
        ALL.signals.on_clipper_config_reload.emit()
        print('发射on_pagepicker_config_reload')

    def on_correct_button_clicked_handle(self):
        print("correct_button clicked")
        self.config_memo_load()
        self.config_disk_save()
        ALL.signals.on_clipper_config_reload.emit()
        self.configtable.close()
        pass

    def config_memo_load(self):
        """从用户修改保存到原来读取的内存中
        pagepicker.browser.layout_col_per_row
        pagepicker.bottombar.default_path
        pagepicker.bottombar.page_ratio
        pagepicker.bottombar.page_num
        viewlayout.mode
        viewlayout.col_per_row
        viewlayout.row_per_col
        output.needRatioFix
        output.RatioFix
        """
        d = self.configtable.config_dict
        if self.configtable.pagepreset.defaultPath_changed:
            d["pagepicker.bottombar.default_path"]["value"] = self.configtable.pagepreset.defaultPathWidget.text()
        if self.configtable.pagepreset.imgRatio_changed:
            d["pagepicker.bottombar.page_ratio"]["value"] = self.configtable.pagepreset.imgRatioWidget.value()
        if self.configtable.pagepreset.pagenum_changed:
            d["pagepicker.bottombar.page_num"]["value"] = self.configtable.pagepreset.pagenumWidget.value()
            print(d["pagepicker.bottombar.page_num"]["value"])
        if self.configtable.viewlayout.layoutMode_changed:
            d["viewlayout.mode"]["value"] = self.configtable.viewlayout.layoutModeWidget.desc_item_uuid(Qt.UserRole)
        if self.configtable.viewlayout.layoutVerticalColCount_changed:
            d["viewlayout.col_per_row"]["value"] = self.configtable.viewlayout.layoutVerticalColCountWidget.value()
        if self.configtable.viewlayout.layoutHorizontalRowCount_changed:
            d["viewlayout.row_per_col"]["value"] = self.configtable.viewlayout.layoutHorizontalRowCountWidget.value()
        if self.configtable.outputpreset.needRatioFix_changed:
            d["output.needRatioFix"]["value"] = self.configtable.outputpreset.needRatioFixWidget.desc_item_uuid(
                Qt.UserRole)
        if self.configtable.outputpreset.RatioFix_changed:
            d["output.RatioFix"]["value"] = self.configtable.outputpreset.RatioFixWidget.value()

        pass

    def config_disk_save(self):
        """从内存中保存回磁盘"""
        data: "dict" = self.configtable.config_dict
        path = objs.SrcAdmin.jsonDir.clipper
        objs.SrcAdmin.save_config(path,
                                  json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':')))
        pass
