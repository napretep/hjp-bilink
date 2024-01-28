import os


from ..imports import *

from .Clipper import Clipper
from .Model import Entity
from .tools import events, funcs, objs
from ..imports import common_tools


class ConfigTable(QDialog):
    """
    line1 : 布局默认设置/set default layout property:方向/direction combox H/V,每行页数/pages per row spinbox
    line2 : 卡片默认设置/set default card property: 页码/pagenum spinbox , 画面比例/image ratio doublespinbox
    """
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

    def __init__(self, superior: Clipper, root: "Clipper"):
        super().__init__(parent=superior)
        self.superior = superior
        self.root = root
        self.G_Layout = QGridLayout(self)
        self.tablayout = self.TabWidget(self, root)
        self.buttonGroup = self.ButtonGroup(self, root)
        self.init_UI()
        self.allevent = objs.AllEventAdmin([
            [self.buttonGroup.reset_button.clicked, self.on_reset_button_clicked],
            [self.buttonGroup.correct_button.clicked, self.on_correct_button_clicked],
        ]).bind()

    def on_correct_button_clicked(self):
        self.buttonGroup.config_memo_save()
        self.root.E.config.save_data()
        self.root.E.config.load_data()
        # self.tablayout.close()
        # self.buttonGroup.close()
        self.close()
        pass

    def reject(self) -> None:
        self.close()
        super().reject()

    def on_reset_button_clicked(self):
        self.root.E.config.set_default()
        self.tablayout.reload_data()
        pass

    def init_UI(self):
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.config))
        self.setWindowTitle("配置表/config")
        self.G_Layout.addWidget(self.tablayout, 0, 0, 2, 1)
        self.G_Layout.addWidget(self.buttonGroup, 1, 1)
        self.setLayout(self.G_Layout)
        pass

    # def init_data(self):
    #     pass

    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     self.all_event.unbind(self.__class__.__name__)

    class TabWidget(QTabWidget):
        def __init__(self, superior: "ConfigTable", root):
            super().__init__(parent=superior)
            self.root = root
            self.superior = superior
            self.tab_viewlayout = self.MainViewLayoutWidget(self, self.root)
            self.tab_pagepicker = self.PagePickerPresetWidget(self, self.root)
            self.tab_output = self.OutPutWidget(self, self.root)
            self.tab_clipbox = self.ClipboxWidget(self, self.root)
            self.tab_map = {
                self.tab_viewlayout: "主视口/main viewport",
                self.tab_pagepicker: "页面选取器/pagepicker",
                self.tab_output: "输出预设/output preset",
                self.tab_clipbox: "选框预设/clipbox preset"
            }
            self.setTabBar(WestTabBar(self))
            self.setTabPosition(QTabWidget.West)
            for k, v in self.tab_map.items():
                self.addTab(k, v)

        def return_data(self):
            data = {}
            data["clipbox"] = self.tab_clipbox.return_data()
            data["pagepicker"] = self.tab_pagepicker.return_data()
            data["viewlayout"] = self.tab_viewlayout.return_data()
            data["output"] = self.tab_output.return_data()
            return data

        def reload_data(self):
            self.tab_clipbox.load_data()
            self.tab_output.load_data()
            self.tab_pagepicker.load_data()
            self.tab_viewlayout.load_data()

        def sub_widget_form_layout_setup(self, w_li, w_info_dict):
            h_layout = QFormLayout()
            for w in w_li:
                l = QLabel(w_info_dict[w][0])
                if len(w_info_dict[w]) > 1:
                    l.setToolTip(w_info_dict[w][1])
                h_layout.addRow(l, w)
            return h_layout

        class MainViewLayoutWidget(QWidget):
            def __init__(self, superior: "ConfigTable.TabWidget", root: "Clipper"):
                super().__init__(parent=superior)
                self.superior = superior
                self.root = root
                self.layoutVerticalColCountWidget = QSpinBox(self)
                self.layoutHorizontalRowCountWidget = QSpinBox(self)
                self.layoutModeWidget = QComboBox(self)
                self.schema = self.root.E.schema
                self.viewlayoutName = self.schema.viewlayout_mode
                self.viewlayout_mode = {
                    self.viewlayoutName.Vertical: ["垂直/vertical"],
                    self.viewlayoutName.Horizontal: ["水平/horizontal"],
                    self.viewlayoutName.Freemode: ["自由模式/free mode"]
                }
                self.txt_on_colrow_count = {  # 1 label name, 2 tooltip content
                    self.viewlayoutName.Vertical: ["每行列数\ncols per row", ConfigTable.pages_col_per_row],
                    self.viewlayoutName.Horizontal: ["每列行数\nrows per col", ConfigTable.pages_row_per_col]
                }
                self.widget_info_dict = {
                    self.layoutModeWidget: ["方向\ndirection:", ConfigTable.tooltip_layout],
                    self.layoutHorizontalRowCountWidget: self.txt_on_colrow_count[self.viewlayoutName.Horizontal],
                    self.layoutVerticalColCountWidget: self.txt_on_colrow_count[self.viewlayoutName.Vertical]
                }
                self.widgetLi = [
                    self.layoutModeWidget,
                    self.layoutVerticalColCountWidget,
                    self.layoutHorizontalRowCountWidget
                ]
                self.init_UI()
                self.load_data()
                self.all_event = objs.AllEventAdmin([
                    [self.layoutModeWidget.currentIndexChanged,self.on_layoutmodewidget_currentIndexChanged_handle],
                ]).bind()

            def init_UI(self):
                self.setLayout(self.superior.sub_widget_form_layout_setup(self.widgetLi, self.widget_info_dict))
                self.showhide_ColRow_count()
                self.layoutHorizontalRowCountWidget.setRange(1, 10)
                self.layoutVerticalColCountWidget.setRange(1, 10)
                self.layoutModeWidget.clear()
                for k, v in self.viewlayout_mode.items():
                    self.layoutModeWidget.addItem(v[0], userData=k)

            def load_data(self):
                config = self.root.E.config.mainview
                self.layoutHorizontalRowCountWidget.setValue(config.layout_row_per_col)
                self.layoutVerticalColCountWidget.setValue(config.layout_col_per_row)
                self.layoutModeWidget.setCurrentIndex(
                    self.layoutModeWidget.findData(config.layout_mode, role=Qt.ItemDataRole.UserRole))
                self.showhide_ColRow_count()

            def on_layoutmodewidget_currentIndexChanged_handle(self, index):
                self.showhide_ColRow_count()

            def showhide_ColRow_count(self):
                layoutmode = self.layoutModeWidget.currentData(Qt.ItemDataRole.UserRole)
                if layoutmode == self.viewlayoutName.Vertical:
                    self.layoutHorizontalRowCountWidget.setEnabled(False)
                    self.layoutVerticalColCountWidget.setEnabled(True)

                elif layoutmode == self.viewlayoutName.Horizontal:
                    self.layoutHorizontalRowCountWidget.setEnabled(True)
                    self.layoutVerticalColCountWidget.setEnabled(False)
                else:
                    self.layoutVerticalColCountWidget.setEnabled(False)
                    self.layoutHorizontalRowCountWidget.setEnabled(False)

            def return_data(self):
                data_map = {
                    "mainview.layout_col_per_row": self.layoutVerticalColCountWidget.value(),
                    "mainview.layout_mode": self.layoutModeWidget.currentData(Qt.ItemDataRole.UserRole),
                    "mainview.layout_row_per_col": self.layoutHorizontalRowCountWidget.value()
                }
                return data_map

        class PagePickerPresetWidget(QWidget):
            def __init__(self, superior: "ConfigTable.TabWidget", root: "Clipper"):
                super().__init__(parent=superior)
                self.superior = superior
                self.root = root
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
                self.schema = self.root.E.schema
                self.init_UI()
                self.load_data()
                self.all_event = objs.AllEventAdmin([
                    [self.defaultPathWidget.textChanged, self.on_defaultPathWidget_textChanged_handle],
                ]).bind()

            def init_UI(self):
                self.setLayout(self.superior.sub_widget_form_layout_setup(self.widgetLi, self.widget_info_dict))

            def on_defaultPathWidget_textChanged_handle(self, txt):
                if txt == "":
                    self.defaultPathWidget.setStyleSheet("background-color:white;")
                    return
                if os.path.exists(txt) and os.path.isdir(txt):
                    self.defaultPathWidget.setStyleSheet("background-color:white;")
                else:
                    self.defaultPathWidget.setStyleSheet("background-color:red;")

            def load_data(self):
                config = self.root.E.config.pagepicker
                self.defaultPathWidget.setText(config.bottombar_default_path)
                self.pagenumWidget.setValue(config.bottombar_page_num)
                self.imgRatioWidget.setValue(config.bottombar_page_ratio)
                self.col_per_row_widget.setValue(config.browser_layout_col_per_row)

            def return_data(self):
                data_map = {
                    "pagepicker.bottombar_default_path": self.defaultPathWidget.text(),
                    "pagepicker.bottombar_page_num": self.pagenumWidget.value(),
                    "pagepicker.bottombar_page_ratio": self.imgRatioWidget.value(),
                    "pagepicker.browser_layout_col_per_row": self.col_per_row_widget.value()
                }
                return data_map

        class OutPutWidget(QWidget):
            def __init__(self, superior: "ConfigTable.TabWidget", root: "Clipper"):
                super().__init__(parent=superior)
                self.superior = superior
                self.root = root
                self.schema = self.root.E.schema
                self.needRatioFixWidget = QComboBox(self)
                self.RatioFixWidget = QDoubleSpinBox(self)
                self.widget_clipper_close_after_insert = QCheckBox(self)
                self.widget_clipbox_close_after_insert = QCheckBox(self)
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
                self.load_data()
                self.all_event = objs.AllEventAdmin([
                    [self.widget_clipper_close_after_insert.stateChanged, self.on_widget_clipper_close_after_insert_stateChanged_handle],
                    [self.needRatioFixWidget.currentIndexChanged, self.on_needRatioFixWidget_currentIndexChanged_handle],
                ]).bind()

            def init_UI(self):
                self.setLayout(self.superior.sub_widget_form_layout_setup(self.widgetLi, self.widget_info_dict))
                for k, v in self.needratiofixvalue.items():
                    self.needRatioFixWidget.addItem(v, userData=k)

            def load_data(self):
                config = self.root.E.config.output
                index = self.needRatioFixWidget.findData(config.needRatioFix, role=Qt.ItemDataRole.UserRole)
                self.needRatioFixWidget.setCurrentIndex(index)
                self.RatioFixWidget.setValue(config.RatioFix)
                self.widget_clipbox_close_after_insert.setChecked(config.close_clipbox_after_insert)
                self.widget_clipper_close_after_insert.setChecked(config.close_clipper_after_insert)
                self.on_widget_clipper_close_after_insert_stateChanged_handle()
                self.spinbox_enable_switch(index)

            def on_needRatioFixWidget_currentIndexChanged_handle(self, index):
                self.spinbox_enable_switch(index)

            def on_widget_clipper_close_after_insert_stateChanged_handle(self, *args):
                if self.widget_clipper_close_after_insert.isChecked():
                    self.widget_clipbox_close_after_insert.setEnabled(False)
                else:
                    self.widget_clipbox_close_after_insert.setEnabled(True)

            def spinbox_enable_switch(self, index):
                if self.needRatioFixWidget.itemData(index, Qt.ItemDataRole.UserRole) == self.schema.needratiofix_mode.no:
                    self.RatioFixWidget.setDisabled(True)
                else:
                    self.RatioFixWidget.setDisabled(False)

            def return_data(self):
                data_map = {
                    "output.RatioFix": self.RatioFixWidget.value(),
                    "output.needRatioFix": self.needRatioFixWidget.currentData(Qt.ItemDataRole.UserRole),
                    "output.closeClipper": self.widget_clipper_close_after_insert.isChecked(),
                    "output.closeClipbox": self.widget_clipbox_close_after_insert.isChecked()
                }
                return data_map

        class ClipboxWidget(QWidget):
            def __init__(self, superior: "ConfigTable.TabWidget", root: "Clipper"):
                super().__init__(parent=superior)
                self.superior = superior
                self.root = root
                self.Q_widget = QSpinBox(self)
                self.A_widget = QSpinBox(self)
                self.comment_Q_widget = QSpinBox(self)
                self.comment_A_widget = QSpinBox(self)
                self.newcard_deck_id_widget = QComboBox(self)
                self.newcard_model_id_widget = QComboBox(self)
                self.macro_widget = self.ClipboxMacroWidget(self, self.root)
                self.deck_and_model_data_retrieved = False
                self.widget_info_dict = {
                    self.Q_widget: ["问题侧对应字段:\nfield that Q-side will insert:"],
                    self.A_widget: ["答案侧对应字段:\nfield that A-side will insert:"],
                    self.comment_Q_widget: ["评论问题侧对应字段:\nfield that comment-Q-side will insert:"],
                    self.comment_A_widget: ["评论答案侧对应字段:\nfield that comment-A-side will insert:"],
                    self.newcard_deck_id_widget: ["新卡片插入的牌组\ndeck that new card will insert :"],
                    self.newcard_model_id_widget: ["新卡片使用的类型\nmodel that used by new card"],
                    self.macro_widget: ["宏\nmacro"]
                }
                self.widgetLi = [self.Q_widget, self.A_widget,
                                 self.comment_Q_widget, self.comment_A_widget,
                                 self.newcard_deck_id_widget, self.newcard_model_id_widget]
                self.init_UI()
                self.load_data()

            def init_UI(self):
                formlayout = self.superior.sub_widget_form_layout_setup(self.widgetLi, self.widget_info_dict)
                VBoxLayout = QVBoxLayout(self)
                VBoxLayout.addLayout(formlayout)
                VBoxLayout.addWidget(self.macro_widget)
                self.setLayout(VBoxLayout)
                self.Q_widget.setRange(0, 999)
                self.A_widget.setRange(0, 999)
                self.comment_A_widget.setRange(0, 999)
                self.comment_Q_widget.setRange(0, 999)

            def load_data(self):
                config = self.root.E.config.clipbox
                self.Q_widget.setValue(config.Q_map_Field)
                self.A_widget.setValue(config.A_map_Field)
                self.comment_Q_widget.setValue(config.comment_Q_map_Field)
                self.comment_A_widget.setValue(config.comment_A_map_Field)
                # self.root.signals.on_config_ankidata_load_end.connect(self.on_config_ankidata_load_end_handle)
                # e = events.ConfigAnkiDataLoadEvent #不需要用信号也可以
                self._deck_load(common_tools.funcs.DeckOperation.get_all())
                self._model_load(common_tools.funcs.ModelOperation.get_all())
                self.deck_and_model_data_retrieved = True
                # self.root.signals.on_config_ankidata_load.emit(e(sender=self, eventType={e.deckType, e.modelType}))
                self.macro_widget.init_data(config.macro)

            def on_config_ankidata_load_end_handle(self, event: "events.ConfigAnkiDataLoadEndEvent"):
                # print(event.ankidata)
                if event.sender == self:
                    self._model_load(event.ankidata["model"])
                    self._deck_load(event.ankidata["deck"])
                    self.deck_and_model_data_retrieved = True
                self.root.signals.on_config_ankidata_load_end.disconnect(self.on_config_ankidata_load_end_handle)

            def _model_load(self, modeldata):
                config = self.root.E.config.clipbox
                for item in modeldata:
                    self.newcard_model_id_widget.addItem(item["name"], userData=item["id"])
                curr_data = config.newcard_model_id
                idx = self.newcard_model_id_widget.findData(curr_data, role=Qt.ItemDataRole.UserRole)
                if curr_data != 0 and idx > -1:
                    self.newcard_model_id_widget.setCurrentIndex(idx)
                else:
                    self.newcard_model_id_widget.setCurrentIndex(0)

            def _deck_load(self, deckdata):
                # print(deckdata)
                config = self.root.E.config.clipbox
                for item in deckdata:
                    self.newcard_deck_id_widget.addItem(item["name"], userData=item["id"])
                curr_data = config.newcard_deck_id
                idx = self.newcard_deck_id_widget.findData(curr_data, role=Qt.ItemDataRole.UserRole)
                if curr_data != 0 and idx > -1:
                    self.newcard_deck_id_widget.setCurrentIndex(idx)
                else:
                    self.newcard_deck_id_widget.setCurrentIndex(0)

            def return_data(self):
                data_map = {
                    "clipbox.macro": self.macro_widget.return_data(),
                    "clipbox.newcard_model_id": self.newcard_model_id_widget.currentData(Qt.ItemDataRole.UserRole),
                    "clipbox.newcard_deck_id": self.newcard_deck_id_widget.currentData(Qt.ItemDataRole.UserRole),
                    "clipbox.Q_map_Field": self.Q_widget.value(),
                    "clipbox.A_map_Field": self.A_widget.value(),
                    "clipbox.comment_A_map_Field": self.comment_A_widget.value(),
                    "clipbox.comment_Q_map_Field": self.comment_Q_widget.value()
                }
                if not self.deck_and_model_data_retrieved:
                    data_map.pop("clipbox.newcard_model_id")
                    data_map.pop("clipbox.newcard_deck_id")
                return data_map

            class ClipboxMacroWidget(QWidget):

                def __init__(self, superior: "ConfigTable.TabWidget.ClipboxWidget", root: "Clipper"):
                    super().__init__(superior)
                    self.G_Layout = QGridLayout(self)
                    self.description_widget = QLabel(self)
                    self.add_button = QToolButton(self)
                    self.del_button = QToolButton(self)
                    self.view = QTableView(self)
                    self.model = QStandardItemModel()
                    self.init_UI()
                    self.init_model()
                    self.event_dict = [
                        [self.add_button.clicked, self.on_add_button_clicked_handle],
                        [self.del_button.clicked, self.on_del_button_clicked_handle],
                        [self.model.dataChanged, self.on_model_data_changed_handle],
                    ]
                    self.all_event = objs.AllEventAdmin(self.event_dict)
                    self.all_event.bind()
                    self.data_changed = False

                def test(self):
                    self.model.appendRow(
                        [QStandardItem(str(self.model.rowCount() + 1)), QStandardItem("0"), QStandardItem("0")])

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
                    self.model.removeRows(0,self.model.rowCount())
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

    class ButtonGroup(QWidget):
        def __init__(self, superior: "ConfigTable", root: "Clipper"):
            super().__init__(parent=superior)
            self.superior = superior
            self.root = root
            self.reset_button = QToolButton(self)
            self.correct_button = QToolButton(self)
            self.h_layout = QVBoxLayout(self)
            self.init_UI()

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

        def config_memo_save(self):
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
            d = self.root.E.config.data
            tab_map = self.superior.tablayout.return_data()
            for tab, widget in tab_map.items():
                for k, v in widget.items():
                    d[k]["value"] = v
            self.root.E.config.save_data()
            self.root.E.signals.on_config_changed.emit()


class WestTabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r
            c = self.tabRect(i).center()

            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()
