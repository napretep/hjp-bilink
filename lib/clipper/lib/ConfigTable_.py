import json
import os
import sys
import time
import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QSpinBox, QHBoxLayout, QFrame, QDoubleSpinBox, QToolButton, \
    QLineEdit, QTabWidget, QFormLayout, QTabBar, QStylePainter, QStyleOptionTab, QStyle, QProxyStyle, QStyleOption, \
    QVBoxLayout, QGridLayout, QTableView, QHeaderView, QAbstractItemView, QCheckBox
from PyQt5.QtCore import Qt, QRect, QSize, QPoint, pyqtSignal
from .tools import funcs, objs, events, ALL

print, printer = funcs.logger(__name__)

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
    def __init__(self, parent=None, configtable=None):
        super().__init__(parent=parent)
        self.configtable = configtable
        # self.config_dict = config_dict
        self.widget_info_dict = {}
        self.widgetLi = []

    def form_layout_setup(self):
        h_layout = QFormLayout()
        for w in self.widgetLi:
            l = QLabel(self.widget_info_dict[w][0])
            if len(self.widget_info_dict[w]) > 1:
                l.setToolTip(self.widget_info_dict[w][1])
            h_layout.addRow(l, w)
        return h_layout


class MainViewLayoutWidget(BaseWidget):
    def __init__(self, parent=None, configtable=None):
        super().__init__(parent=None, configtable=configtable)
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
            self.viewlayoutName.Vertical: ["每行列数\ncols per row", pages_col_per_row],
            self.viewlayoutName.Horizontal: ["每列行数\nrows per col", pages_row_per_col]
        }
        self.widget_info_dict = {
            self.layoutModeWidget: ["方向\ndirection:", tooltip_layout],
            self.layoutHorizontalRowCountWidget: self.txt_on_colrow_count[self.viewlayoutName.Horizontal],
            self.layoutVerticalColCountWidget: self.txt_on_colrow_count[self.viewlayoutName.Vertical]
        }
        self.widgetLi = [
            self.layoutModeWidget,
            self.layoutVerticalColCountWidget,
            self.layoutHorizontalRowCountWidget
        ]
        self.init_UI()
        self.init_data()
        self.event_dict = {
            self.layoutModeWidget.currentIndexChanged: self.on_layoutmodewidget_currentIndexChanged_handle,
            self.layoutVerticalColCountWidget.valueChanged: self.on_layoutVerticalColCountWidget_valueChanged_handle,
            self.layoutHorizontalRowCountWidget.valueChanged:
                self.on_layoutHorizontalRowCountWidget_valueChanged_handle,
            ALL.signals.on_config_reload_end: self.on_config_reload_end_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def init_UI(self):
        self.setLayout(self.form_layout_setup())
        self.showhide_ColRow_count()

    def init_viewlyout_horizontal_rowcount(self, left, right):
        self.layoutHorizontalRowCountWidget.setRange(left, right if right != False else MAX_INT)
        self.layoutHorizontalRowCountWidget.setValue(
            self.configtable.config_dict["mainview.layout_row_per_col"]["value"])

    def init_viewlayout_vertical_colcount(self, left, right):
        self.layoutVerticalColCountWidget.setRange(left, right if right != False else MAX_INT)
        self.layoutVerticalColCountWidget.setValue(self.configtable.config_dict["mainview.layout_col_per_row"]["value"])

    def init_viewlayoutmodecombox(self):
        self.layoutModeWidget.clear()
        for val in self.configtable.config_dict["mainview.layout_mode"]["constrain"]["data_range"]:
            self.layoutModeWidget.addItem(self.viewlayout_mode[val][0], userData=val)

        value = self.viewlayout_mode[self.configtable.config_dict["mainview.layout_mode"]["value"]][0]
        self.layoutModeWidget.setCurrentIndex(self.layoutModeWidget.findText(value))

    def init_data(self):
        self.init_viewlayoutmodecombox()
        left = self.configtable.config_dict["mainview.layout_col_per_row"]["constrain"]["data_range"]["left"]
        right = self.configtable.config_dict["mainview.layout_col_per_row"]["constrain"]["data_range"]["right"]
        self.init_viewlayout_vertical_colcount(left, right)
        self.init_viewlyout_horizontal_rowcount(left, right)
        self.showhide_ColRow_count()

    def on_config_reload_end_handle(self):
        self.init_data()

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
            self.layoutHorizontalRowCountWidget.setEnabled(False)
            self.layoutVerticalColCountWidget.setEnabled(True)
            self.layoutVerticalColCountWidget.setValue(
                self.configtable.config_dict["mainview.layout_col_per_row"]["value"])

        elif layoutmode == self.viewlayoutName.Horizontal:
            self.layoutHorizontalRowCountWidget.setEnabled(True)
            self.layoutVerticalColCountWidget.setEnabled(False)
            self.layoutHorizontalRowCountWidget.setValue(
                self.configtable.config_dict["mainview.layout_row_per_col"]["value"])

        else:
            self.layoutVerticalColCountWidget.setEnabled(False)
            self.layoutHorizontalRowCountWidget.setEnabled(False)

    def return_data(self):
        data_map = {
            "mainview.layout_col_per_row": self.layoutVerticalColCountWidget.value(),
            "mainview.layout_mode": self.layoutModeWidget.currentData(Qt.UserRole),
            "mainview.layout_row_per_col": self.layoutHorizontalRowCountWidget.value()
        }
        return data_map


class PagePickerPresetWidget(BaseWidget):
    """for pagepicker"""

    def __init__(self, parent=None, configtable=None):
        super().__init__(parent=parent, configtable=configtable)
        # self.f_layout = QFormLayout(self)
        self.pagenumWidget = QSpinBox(self)
        self.imgRatioWidget = QDoubleSpinBox(self)
        self.defaultPathWidget = QLineEdit(self)
        self.col_per_row_widget = QSpinBox(self)
        self.widget_info_dict = {
            self.pagenumWidget: ["默认页码\ndefault page num:"],
            self.imgRatioWidget: ["默认画面比例\ndefault image ratio:"],
            self.defaultPathWidget: ["默认读取位置\ndefault load path"],
            self.col_per_row_widget: ["浏览窗一行的列数\ncol per row of browser"]
        }
        self.widgetLi = [
            self.pagenumWidget, self.imgRatioWidget, self.defaultPathWidget, self.col_per_row_widget
        ]
        self.defaultPath_changed = False
        self.pagenum_changed = False
        self.imgRatio_changed = False
        self.col_per_row_changed = False
        self.schema = objs.JSONschema
        self.init_UI()
        self.init_data()
        self.event_dict = {
            self.defaultPathWidget.textChanged: self.on_defaultPathWidget_textChanged_handle,
            self.pagenumWidget.valueChanged: self.on_pagenumWidget_valueChanged_handle,
            self.imgRatioWidget.valueChanged: self.on_imgRatioWidget_valueChanged_handle,
            ALL.signals.on_config_reload_end: self.on_config_reload_end_handle,
            self.col_per_row_widget.valueChanged: self.on_per_row_widget_valueChanged_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def init_pagenum(self):
        left, right = config_get_left_right(self.configtable.config_dict, "pagepicker.bottombar_page_num")
        self.pagenumWidget.setRange(left, right if right != False else MAX_INT)
        self.pagenumWidget.setValue(self.configtable.config_dict["pagepicker.bottombar_page_num"]["value"])

    def init_imgratio(self):
        left, right = config_get_left_right(self.configtable.config_dict, "pagepicker.bottombar_page_ratio")
        self.imgRatioWidget.setRange(left, right if right != False else MAX_INT)
        self.imgRatioWidget.setSingleStep(0.1)
        self.imgRatioWidget.setValue(self.configtable.config_dict["pagepicker.bottombar_page_ratio"]["value"])

    def init_col_per_row(self):
        self.col_per_row_val = self.configtable.config_dict["pagepicker.browser_layout_col_per_row"]["value"]
        left, right = config_get_left_right(self.configtable.config_dict, "pagepicker.browser_layout_col_per_row")
        self.col_per_row_widget.setRange(left, right if right != False else MAX_INT)
        self.col_per_row_widget.setValue(self.col_per_row_val)

    def init_defaultpath(self):
        self.defaultPathWidget.setText(self.configtable.config_dict["pagepicker.bottombar_default_path"]["value"])

    def init_UI(self):
        self.setLayout(self.form_layout_setup())

    def init_data(self):
        self.init_defaultpath()
        self.init_imgratio()
        self.init_pagenum()
        self.init_col_per_row()

    def on_config_reload_end_handle(self):
        self.init_data()

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

    def on_per_row_widget_valueChanged_handle(self, value):
        if self.col_per_row_val != value:
            self.col_per_row_val = value
        self.col_per_row_changed = True

    def __setattr__(self, key, value):
        if key == "col_per_row_val" and "col_per_row_widget" in self.__dict__:
            self.col_per_row_widget.setValue(value)
        self.__dict__[key] = value

    def return_data(self):
        data_map = {
            "pagepicker.bottombar_default_path": self.defaultPathWidget.text(),
            "pagepicker.bottombar_page_num": self.pagenumWidget.value(),
            "pagepicker.bottombar_page_ratio": self.imgRatioWidget.value(),
            "pagepicker.browser_layout_col_per_row": self.col_per_row_widget.value()
        }
        return data_map


class OutPutWidget(BaseWidget):
    def __init__(self, parent=None, configtable=None):
        super().__init__(parent=parent, configtable=configtable)
        self.schema = objs.JSONschema
        self.needratiofixcode = self.configtable.config_dict["output.needRatioFix"]["value"]
        self.needRatioFixWidget = QComboBox(self.configtable)
        self.needRatioFix_changed = False
        self.RatioFixWidget = QDoubleSpinBox(self.configtable)
        self.RatioFix_changed = False
        self.widget_clipper_close_after_insert = QCheckBox(self.configtable)
        self.widget_clipbox_close_after_insert = QCheckBox(self.configtable)
        self.widget_info_dict = {
            self.needRatioFixWidget: ["比例修正\nratio fix",
                                      "final output ratio=(image load ratio)*(zoom in/out ratio)*(output ratio)"],
            self.RatioFixWidget: ["修正数\noutput ratio", ""],
            self.widget_clipbox_close_after_insert: ["输出完成后,关闭选框\n"
                                                     "When the output is complete, close the clipbox", ""],
            self.widget_clipper_close_after_insert: ["输出完成后,关闭clipper\n"
                                                     "When the output is complete, close the clipper", ""]
        }
        self.widgetLi = [self.needRatioFixWidget,
                         self.RatioFixWidget,
                         self.widget_clipper_close_after_insert,
                         self.widget_clipbox_close_after_insert
                         ]
        self.needratiofixvalue = {
            self.schema.needratiofix_mode.no: "不需要/don't need",
            self.schema.needratiofix_mode.yes: "需要/need"
        }
        self.init_UI()
        self._init_data()
        self.event_dict = {
            self.needRatioFixWidget.currentIndexChanged: self.on_needRatioFixWidget_currentIndexChanged_handle,
            self.RatioFixWidget.valueChanged: self.on_RatioFixWidget_valueChanged_handle,
            ALL.signals.on_config_reload_end: self.on_config_reload_end_handle,
            ALL.signals.on_config_changed: self.on_config_changed_handle,
            self.widget_clipper_close_after_insert.stateChanged: self.on_widget_clipper_close_after_insert_stateChanged_handle,

        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def on_widget_clipper_close_after_insert_stateChanged_handle(self, *args):
        if self.widget_clipper_close_after_insert.isChecked():
            self.widget_clipbox_close_after_insert.setEnabled(False)
        else:
            self.widget_clipbox_close_after_insert.setEnabled(True)

    def on_config_changed_handle(self):
        print("on_config_changed_handle")
        ALL.signals.on_config_reload.emit()

    def init_UI(self):

        self.setLayout(self.form_layout_setup())

    def init_needRatioFix(self):
        self.needRatioFixWidget.clear()
        for k, v in self.needratiofixvalue.items():
            self.needRatioFixWidget.addItem(v, userData=k)
        self.needRatioFixWidget.setCurrentIndex(self.needRatioFixWidget.findData(self.needratiofixcode))

        curr_index = self.needRatioFixWidget.currentIndex()
        self.spinbox_enable_switch(curr_index)

    def init_RatioFix(self):
        left, right = config_get_left_right(self.configtable.config_dict, "output.RatioFix")
        self.RatioFixWidget.setRange(left, right)
        self.RatioFixWidget.setSingleStep(0.1)
        self.RatioFixWidget.setValue(self.configtable.config_dict["output.RatioFix"]["value"])

    def _init_data(self):
        self.init_RatioFix()
        self.init_needRatioFix()
        self.init_close()

    def init_close(self):
        val = self.configtable.config_dict["output.closeClipper"]["value"]
        self.widget_clipper_close_after_insert.setChecked(val)
        if val:
            self.widget_clipbox_close_after_insert.setEnabled(False)
        val = self.configtable.config_dict["output.closeClipbox"]["value"]
        self.widget_clipbox_close_after_insert.setChecked(val)

    def on_config_reload_end_handle(self):
        self._init_data()

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

    # def api_widget_clipper_close_after_insert_value(self):

    def return_data(self):
        data_map = {
            "output.RatioFix": self.RatioFixWidget.value(),
            "output.needRatioFix": self.needRatioFixWidget.currentData(Qt.UserRole),
            "output.closeClipper": self.widget_clipper_close_after_insert.isChecked(),
            "output.closeClipbox": self.widget_clipbox_close_after_insert.isChecked()
        }
        return data_map

class ClipboxMacroWidget(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.G_Layout = QGridLayout(self)
        self.description_widget = QLabel(self)
        self.add_button = QToolButton(self)
        self.del_button = QToolButton(self)
        self.view = QTableView(self)
        self.model = QStandardItemModel()
        self.init_UI()
        self.init_model()
        self.event_dict = {
            self.add_button.clicked: self.on_add_button_clicked_handle,
            self.del_button.clicked: self.on_del_button_clicked_handle,
            self.model.dataChanged: self.on_model_data_changed_handle
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
        self.data_changed = False

    def test(self):
        self.model.appendRow([QStandardItem(str(self.model.rowCount() + 1)), QStandardItem("0"), QStandardItem("0")])

    def steps_recount(self):
        count = self.model.rowCount()
        for i in range(count):
            item = self.model.item(i)
            item.setText(str(item.row() + 1))

    def on_model_data_changed_handle(self):
        self.data_changed = True

    def on_add_button_clicked_handle(self):
        # print("on_add_button_clicked_handle")
        self.model.appendRow(self.new_row())
        # print(self.return_data())
        pass

    def on_del_button_clicked_handle(self):
        selectli = self.view.selectedIndexes()
        if len(selectli) > 0:
            item = [self.model.itemFromIndex(idx) for idx in selectli][0]
            self.model.removeRow(item.row())
        self.steps_recount()

    def new_row(self):
        return [QStandardItem(str(self.model.rowCount() + 1)), QStandardItem("0"), QStandardItem("0")]

    def init_UI(self):
        self.add_button.setText("+")
        self.del_button.setText("-")
        self.description_widget.setText("宏:请在下表中设置宏的一个周期内的所有步骤\n"
                                        "macro: Please set all steps of the macro in a cycle in the table below\n"
                                        "每完成一个周期,程序就会自动切换到下一张卡片\n"
                                        "Each time a cycle is completed, the addon will auto switches to the next card")
        self.G_Layout.addWidget(self.description_widget, 0, 0, 1, 3)
        self.G_Layout.addWidget(self.view, 1, 0, 3, 1)
        self.G_Layout.addWidget(self.add_button, 1, 1)
        self.G_Layout.addWidget(self.del_button, 1, 2)
        self.setLayout(self.G_Layout)
        self.view.verticalHeader().hide()
        self.model.setHorizontalHeaderLabels(["step", "QA_map_Field", "commentQA_map_Field"])
        header = self.view.horizontalHeader()
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.view.setColumnWidth(0, 20)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)

    def init_model(self):
        self.view.setModel(self.model)
        self.view.setItemDelegate(objs.ColumnSpinboxDelegate([1, 2]))
        pass

    def init_data(self, data):
        rows = len(data)
        for row in range(rows):
            rowitem = [QStandardItem(str(row + 1))] + [QStandardItem(str(i)) for i in data[row]]
            self.model.appendRow(rowitem)

    def return_data(self):
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        data = []
        for row in range(rows):
            rowdata = []
            for col in range(cols):
                if col == 0:
                    continue
                rowdata.append(int(self.model.item(row, col).data(Qt.DisplayRole)))
            data.append(rowdata)
        return data

class ClipboxWidget(BaseWidget):
    def __init__(self, parent=None, configtable=None):
        super().__init__(parent=parent, configtable=configtable)
        # 基本变量声明
        self.deck_and_model_data_retrieved = False
        self.Q_widget = QSpinBox(self)
        self.A_widget = QSpinBox(self)
        self.text_Q_widget = QSpinBox(self)
        self.text_A_widget = QSpinBox(self)
        self.newcard_deck_id_widget = QComboBox(self)
        self.newcard_model_id_widget = QComboBox(self)
        self.macro_widget = ClipboxMacroWidget(self)  # 是一个复杂的对象.
        self.widget_info_dict = {
            self.Q_widget: ["问题侧对应字段:\nfield that Q-side will insert:"],
            self.A_widget: ["答案侧对应字段:\nfield that A-side will insert:"],
            self.text_Q_widget: ["评论问题侧对应字段:\nfield that comment-Q-side will insert:"],
            self.text_A_widget: ["评论答案侧对应字段:\nfield that comment-A-side will insert:"],
            self.newcard_deck_id_widget: ["新卡片插入的卡组\ndeck that new card will insert :"],
            self.newcard_model_id_widget: ["新卡片使用的类型\nmodel that used by new card"],
            self.macro_widget: ["宏\nmacro"]
        }
        self.widgetLi = [self.Q_widget, self.A_widget,
                         self.text_Q_widget, self.text_A_widget,
                         self.newcard_deck_id_widget, self.newcard_model_id_widget]

        self.init_UI()

    def init_UI(self):
        formlayout = self.form_layout_setup()
        VBoxLayout = QVBoxLayout(self)
        VBoxLayout.addLayout(formlayout)
        VBoxLayout.addWidget(self.macro_widget)
        self.setLayout(VBoxLayout)

    def _init_data(self):
        c = self.configtable.config_dict
        self.macro_widget.init_data(c["clipbox.macro"]["value"])
        self.data_map = {
            "clipbox.Q_map_Field": self.Q_widget,
            "clipbox.A_map_Field": self.A_widget,
            "clipbox.textA_map_Field": self.text_A_widget,
            "clipbox.textQ_map_Field": self.text_Q_widget
        }
        for k, v in self.data_map.items():
            v.setValue(c[k]["value"])
            v.setRange(0, MAX_INT)
        ALL.signals.on_config_ankidata_load_end.connect(self.on_config_ankidata_load_end_handle)
        e = events.ConfigAnkiDataLoadEvent
        ALL.signals.on_config_ankidata_load.emit(
            e(sender=self, eventType={e.deckType, e.modelType})
        )

    def on_config_ankidata_load_end_handle(self, event: "events.ConfigAnkiDataLoadEndEvent"):
        # print(event.ankidata)
        if event.sender == self:
            self._model_load(event.ankidata["model"])
            self._deck_load(event.ankidata["deck"])
            self.deck_and_model_data_retrieved = True
        ALL.signals.on_config_ankidata_load_end.disconnect(self.on_config_ankidata_load_end_handle)

    def _model_load(self, modeldata):

        for item in modeldata:
            self.newcard_model_id_widget.addItem(item["name"], userData=item["id"])
        c = self.configtable.config_dict
        curr_data = c["clipbox.newcard_model_id"]["value"]
        idx = self.newcard_model_id_widget.findData(curr_data, role=Qt.UserRole)
        if curr_data != 0 and idx > -1:
            self.newcard_model_id_widget.setCurrentIndex(idx)
        else:
            self.newcard_model_id_widget.setCurrentIndex(0)

    def _deck_load(self, deckdata):
        # print(deckdata)
        for item in deckdata:
            self.newcard_deck_id_widget.addItem(item["name"], userData=item["id"])
        c = self.configtable.config_dict
        curr_data = c["clipbox.newcard_deck_id"]["value"]
        idx = self.newcard_deck_id_widget.findData(curr_data, role=Qt.UserRole)
        if curr_data != 0 and idx > -1:
            self.newcard_deck_id_widget.setCurrentIndex(idx)
        else:
            self.newcard_deck_id_widget.setCurrentIndex(0)

    def return_data(self):
        data_map = {
            "clipbox.macro": self.macro_widget.return_data(),
            "clipbox.newcard_model_id": self.newcard_model_id_widget.currentData(Qt.UserRole),
            "clipbox.newcard_deck_id": self.newcard_deck_id_widget.currentData(Qt.UserRole),
            "clipbox.Q_map_Field": self.Q_widget.value(),
            "clipbox.A_map_Field": self.A_widget.value(),
            "clipbox.textA_map_Field": self.text_A_widget.value(),
            "clipbox.textQ_map_Field": self.text_Q_widget.value()
        }
        if not self.deck_and_model_data_retrieved:
            data_map.pop("clipbox.newcard_model_id")
            data_map.pop("clipbox.newcard_deck_id")
        return data_map

class WestTabBar(QtWidgets.QTabBar):
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

class TabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_viewlayout = MainViewLayoutWidget(parent=self, configtable=parent)
        self.tab_pagepicker = PagePickerPresetWidget(parent=self, configtable=parent)
        self.tab_output = OutPutWidget(parent=self, configtable=parent)
        self.tab_clipbox = ClipboxWidget(parent=self, configtable=parent)
        self.tab_map = {
            self.tab_viewlayout: "主视图/main view",
            self.tab_pagepicker: "页面选取器/pagepicker",
            self.tab_output: "输出预设/output preset",
            self.tab_clipbox: "选框预设/clipbox preset"
        }
        self.setTabBar(WestTabBar(self))
        self.setTabPosition(QTabWidget.West)
        for k, v in self.tab_map.items():
            self.addTab(k, v)
        self.init_data()

    def init_data(self):
        self.tab_clipbox._init_data()

    def return_data(self):
        data = {}
        data["clipbox"] = self.tab_clipbox.return_data()
        data["pagepicker"] = self.tab_pagepicker.return_data()
        data["viewlayout"] = self.tab_viewlayout.return_data()
        data["output"] = self.tab_output.return_data()
        return data

class ButtonGroup(BaseWidget):
    def __init__(self, parent=None, configtable=None):
        super().__init__(configtable=configtable)
        self.reset_button = QToolButton(self)
        self.correct_button = QToolButton(self)
        self.h_layout = QVBoxLayout(self)
        self.init_UI()
        self.event_dict = {
            self.correct_button.clicked: self.on_correct_button_clicked_handle,
            self.reset_button.clicked: self.on_button_reset_clicked_handle
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def init_UI(self):

        self.h_layout.setAlignment(Qt.AlignRight)
        self.reset_button.setToolTip("reset the configuration")
        self.reset_button.setIcon(QIcon(objs.SrcAdmin.imgDir.config_reset))
        self.reset_button.setIconSize(QSize(30, 30))
        self.reset_button.setStyleSheet("height:40px;width:40px")
        self.correct_button.setToolTip("correct and quit")
        self.correct_button.setIcon(QIcon(objs.SrcAdmin.imgDir.correct))
        self.correct_button.setStyleSheet("height:40px;width:40px")
        self.correct_button.setIconSize(QSize(30, 30))
        self.h_layout.addWidget(self.reset_button)
        self.h_layout.addWidget(self.correct_button)
        self.setLayout(self.h_layout)


    def on_button_reset_clicked_handle(self):
        data = json.dumps(objs.SrcAdmin.get_config("clipper.template"), ensure_ascii=False, sort_keys=True, indent=4,
                          separators=(',', ':'))
        path = objs.SrcAdmin.jsonDir.clipper
        objs.SrcAdmin.save_config(path, data)
        ALL.signals.on_config_reload.emit()
        print('发射on_pagepicker_config_reload')

    def on_correct_button_clicked_handle(self):
        # print("correct_button clicked")
        self.config_memo_load()
        self.config_disk_save()

        ALL.signals.on_config_changed.emit()
        self.configtable.close()
        pass

    def config_memo_load(self):
        """从用户修改保存到原来读取的内存中, 注意, 只要有修改, 就会变成true, 而且只要点确定就会关闭, 因此不必恢复成 false
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
        tab = self.configtable.tablayout
        tab_map = tab.return_data()
        for tab, widget in tab_map.items():
            for k, v in widget.items():
                d[k]["value"] = v

        # # config_map={
        # #     "pagepicker.bottombar.default_path":tab.tab_pagepicker.defaultPathWidget.text(),
        # #     "pagepicker.bottombar.page_ratio": tab.tab_pagepicker.imgRatioWidget.value(),
        # #     "pagepicker.bottombar.page_num":tab.tab_pagepicker.,
        # #            "mainview.layout_mode",
        # #            "mainview.layout_col_per_row",
        # #            "mainview.layout_row_per_col",
        # #            "output.needRatioFix",
        # #            "output.RatioFix",
        # #            "pagepicker.browser.layout_col_per_row",
        # # }
        # if self.configtable.tablayout.tab_pagepicker.defaultPath_changed:
        #     d["pagepicker.bottombar.default_path"][
        #         "value"] = self.configtable.tablayout.tab_pagepicker.defaultPathWidget.text()
        # if self.configtable.tablayout.tab_pagepicker.imgRatio_changed:
        #     d["pagepicker.bottombar.page_ratio"][
        #         "value"] = self.configtable.tablayout.tab_pagepicker.imgRatioWidget.value()
        # if self.configtable.tablayout.tab_pagepicker.pagenum_changed:
        #     d["pagepicker.bottombar.page_num"][
        #         "value"] = self.configtable.tablayout.tab_pagepicker.pagenumWidget.value()
        # if self.configtable.tablayout.tab_viewlayout.layoutMode_changed:
        #     d["mainview.layout_mode"]["value"] = self.configtable.tablayout.tab_viewlayout.layoutModeWidget.currentData(
        #         Qt.UserRole)
        # if self.configtable.tablayout.tab_viewlayout.layoutVerticalColCount_changed:
        #     d["mainview.layout_col_per_row"][
        #         "value"] = self.configtable.tablayout.tab_viewlayout.layoutVerticalColCountWidget.value()
        # if self.configtable.tablayout.tab_viewlayout.layoutHorizontalRowCount_changed:
        #     d["mainview.layout_row_per_col"][
        #         "value"] = self.configtable.tablayout.tab_viewlayout.layoutHorizontalRowCountWidget.value()
        # if self.configtable.tablayout.tab_output.needRatioFix_changed:
        #     d["output.needRatioFix"]["value"] = self.configtable.tablayout.tab_output.needRatioFixWidget.currentData(
        #         Qt.UserRole)
        # if self.configtable.tablayout.tab_output.RatioFix_changed:
        #     d["output.RatioFix"]["value"] = self.configtable.tablayout.tab_output.RatioFixWidget.value()
        # if self.configtable.tablayout.tab_pagepicker.col_per_row_changed:
        #     d["pagepicker.browser.layout_col_per_row"]["value"] = tab.tab_pagepicker.col_per_row_val
        # pass

    def config_disk_save(self):
        """从内存中保存回磁盘"""
        data: "dict" = self.configtable.config_dict
        path = objs.SrcAdmin.jsonDir.clipper
        objs.SrcAdmin.save_config(path,
                                  json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':')))
        pass
