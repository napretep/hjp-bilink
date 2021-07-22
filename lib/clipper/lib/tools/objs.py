import json
import os

from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog, QToolButton, \
    QDoubleSpinBox, QComboBox, QVBoxLayout, QFrame, QGridLayout, QWidget, QShortcut, QProgressBar, QStyledItemDelegate, \
    QItemDelegate

from . import funcs
from . import events, JSONschema_, SrcAdmin_


# import logging
#
# class Logger(object):
#     def __init__(self,text,loggername=None):
#

# from ..PageInfo import PageInfo

class CustomSignals(QObject):
    """用法: 在需要发射/接受信号的类中调用CustomSignals的类方法start(),并取出需要的信号绑定到本地变量,进行发射或接受"""
    instance = None
    linkedEvent = pyqtSignal()

    # on_macro_switch = pyqtSignal()
    # on_macro_start = pyqtSignal()
    # on_macro_stop = pyqtSignal()
    # on_macro_pause= pyqtSignal()

    on_anki_card_create = pyqtSignal(object)  # AnkiCardCreateEvent
    on_anki_card_created = pyqtSignal(object)  # AnkiCardCreatedEvent
    on_anki_field_insert = pyqtSignal(object)  # AnkiFieldInsertEvent
    # on_anki_field_inserted = pyqtSignal(object) #AnkiFieldInsertedEvent
    on_anki_browser_activate = pyqtSignal(object)  # AnkiBrowserActivateEvent
    on_anki_file_create = pyqtSignal(object)  # AnkiFileCreateEvent

    on_pagepicker_bookmark_open = pyqtSignal(object)  # OpenBookmarkEvent
    on_pagepicker_bookmark_clicked = pyqtSignal(object)  # BookmarkClickedEvent

    # PDFopen只用于打开PDF, 不参与分析的操作
    on_pagepicker_PDFopen = pyqtSignal(object)  # PDFOpenEvent
    on_pagepicker_PDFparse = pyqtSignal(object)  # PDFParseEvent
    on_pagepicker_PDFlayout = pyqtSignal(object)  # PDFlayoutEvent

    # 用于收集数据
    # on_pagepicker_Browser_pageselected = pyqtSignal(object)#PagePickerBrowserPageSelectedEvent
    on_pagepicker_close = pyqtSignal(object)  # PagePickerCloseEvent
    on_pagepicker_open = pyqtSignal(object)  # PagePickerOpenEvent

    on_pagepicker_rightpart_pageread = pyqtSignal(object)  # PagePickerRightPartPageReadEvent
    # click还管别的
    on_pagepicker_browser_pageclicked = pyqtSignal(object)  # PagePickerBrowserPageClickedEvent
    # select只管select
    on_pagepicker_browser_select = pyqtSignal(object)  # PagePickerBrowserSelectEvent

    on_pagepicker_browser_sceneClear = pyqtSignal(object)  # PagePickerBrowserSceneClear

    on_pagepicker_browser_select_send = pyqtSignal(object)  # PagePickerBrowserSelectSendEvent

    on_pagepicker_browser_progress = pyqtSignal(int)

    on_pagepicker_preivewer_read_page = pyqtSignal(object)  # PagePickerPreviewerReadPageEvent

    on_pagepicker_previewer_ratio_adjust = pyqtSignal(object)  # PagePickerPreviewerRatioAdjustEvent

    on_pagepicker_browser_frame_changed = pyqtSignal(object)  # PagePickerBrowserFrameChangedEvent

    # 涉及 pagenum,docname,ratio的更新变化
    on_pageItem_update = pyqtSignal(object)  # PageItemUpdateEvent

    on_pageItem_mouse_released = pyqtSignal(object)  # PageItemMouseReleasedEvent
    on_pageItem_clicked = pyqtSignal(object)  # PageItemClickEvent
    on_pageItem_clipbox_added = pyqtSignal(object)
    on_pageItem_resize_event = pyqtSignal(object)  # PageItemResizeEvent
    on_pageItem_changePage = pyqtSignal(object)  # PageItemChangeEvent
    on_pageItem_addToScene = pyqtSignal(object)  # PagePickerEvent
    on_pageItem_removeFromScene = pyqtSignal(object)
    on_pageItem_rubberBandRect_send = pyqtSignal(object)  # PageItemRubberBandRectSendEvent
    on_pageItem_needCenterOn = pyqtSignal(object)  # PageItemNeedCenterOnEvent
    on_pageItem_centerOn_process = pyqtSignal(object)  # PageItemCenterOnProcessEvent

    on_cardlist_dataChanged = pyqtSignal(object)  # CardListDataChangedEvent
    # 目前主要影响clipbox的toolsbar的cardcombox更新数据
    # 传送的数据用不起来
    on_ClipperExecuteProgresser_show = pyqtSignal()
    on_cardlist_deleteItem = pyqtSignal(object)
    on_cardlist_addCard = pyqtSignal(object)  # CardListAddCardEvent
    on_cardlist_selectItem = pyqtSignal(object)  # CardListSelectItemEvent
    # 涉及 QA,TextQA,Text,Card_id 四者的变化
    on_clipbox_toolsbar_update = pyqtSignal(object)  # ClipBoxToolsbarUpdateEvent

    on_clipbox_closed = pyqtSignal(object)
    on_clipboxstate_switch = pyqtSignal(object)  # ClipboxStateSwitchEvent
    on_clipboxstate_hide = pyqtSignal()
    on_clipboxCombox_updated = pyqtSignal(object)
    on_clipboxCombox_emptied = pyqtSignal()
    on_clipbox_create = pyqtSignal(object)  # ClipboxCreateEvent

    on_rightSideBar_settings_clicked = pyqtSignal(object)
    on_rightSideBar_refresh_clicked = pyqtSignal(object)
    on_rightSideBar_buttonGroup_clicked = pyqtSignal(object)  # RightSideBarButtonGroupEvent
    on_rightSideBar_cardModel_changed = pyqtSignal()  # RightSideBarModelChanged

    on_clipper_hotkey_next_card = pyqtSignal()
    on_clipper_hotkey_prev_card = pyqtSignal()
    on_clipper_hotkey_setA = pyqtSignal()
    on_clipper_hotkey_setQ = pyqtSignal()

    on_config_changed = pyqtSignal()
    on_config_reload = pyqtSignal()
    on_config_reload_end = pyqtSignal()
    on_config_ankidata_load = pyqtSignal(object)  # ConfigAnkiDataLoadEvent
    on_config_ankidata_load_end = pyqtSignal(object)  # ConfigAnkiDataLoadEndEvent

    on_PDFView_ResizeView = pyqtSignal(object)  # PDFViewResizeViewEvent
    on_PDFView_clicked = pyqtSignal(object)  # PDFViewClickedEvent

    on_get_clipper = pyqtSignal(object)  # GetClipperEvent
    on_clipper_closed = pyqtSignal()
    regist_dict = {}  # hashcode:[signal,connector]

    @classmethod
    def start(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        # print(cls.instance)
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class ConfigDict:
    class ClipBox:
        def __init__(self, data):
            self.A_map_Field = data["clipbox.A_map_Field"]["value"]
            self.Q_map_Field = data["clipbox.Q_map_Field"]["value"]
            self.macro = data["clipbox.macro"]["value"]
            self.newcard_deck_id = data["clipbox.newcard_deck_id"]["value"]
            self.newcard_model_id = data["clipbox.newcard_model_id"]["value"]
            self.textA_map_Field = data["clipbox.textA_map_Field"]["value"]
            self.textQ_map_Field = data["clipbox.textQ_map_Field"]["value"]

    class Output:
        def __init__(self, data):
            self.RatioFix = data["output.RatioFix"]["value"]
            self.needRatioFix = data["output.needRatioFix"]["value"]

    class PagePicker:
        def __init__(self, data):
            self.bottombar_default_path = data["pagepicker.bottombar_default_path"]["value"]
            self.bottombar_page_num = data["pagepicker.bottombar_page_num"]["value"]
            self.bottombar_page_ratio = data["pagepicker.bottombar_page_ratio"]["value"]
            self.browser_layout_col_per_row = data["pagepicker.browser_layout_col_per_row"]["value"]

    class MainView:
        def __init__(self, data):
            self.layout_col_per_row = data["mainview.layout_col_per_row"]["value"]
            self.layout_row_per_col = data["mainview.layout_row_per_col"]["value"]
            self.layout_mode = data["mainview.layout_mode"]["value"]

    def __init__(self):
        self.data = SrcAdmin.call().get_config("clipper")
        self.clipbox = self.ClipBox(self.data)
        self.pagepicker = self.PagePicker(self.data)
        self.mainview = self.MainView(self.data)
        self.output = self.Output(self.data)
        CustomSignals.start().on_config_changed.connect(self.load_data)

    def load_data(self):
        print("config_reloaded")
        self.data = SrcAdmin.call().get_config("clipper")
        self.clipbox = self.ClipBox(self.data)
        self.pagepicker = self.PagePicker(self.data)
        self.mainview = self.MainView(self.data)
        self.output = self.Output(self.data)


class SrcAdmin:
    """单例"""
    instance = None
    get = SrcAdmin_.Get._()
    imgDir = SrcAdmin_.IMGDir()
    jsonDir = SrcAdmin_.JSONDir()
    get_json = SrcAdmin_.Get._().json_dict
    get_config = SrcAdmin_.Get._().config_dict
    save_config = SrcAdmin_.Get._().save_dict
    DB = SrcAdmin_.DB()
    PDF_JSON = SrcAdmin_.PDFJSON().load()

    @classmethod
    def call(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class JSONschema:
    """JSON的数据规范"""
    type = JSONschema_.DataType()
    empty = JSONschema_.Empty()
    viewlayout_mode = JSONschema_.ViewLayout()
    needratiofix_mode = JSONschema_.NeedRatioFix()


class GridHDescUnit(QWidget):
    def __init__(self, parent=None, labelname=None, tooltip=None, widget=None):
        super().__init__(parent=parent)
        self.label = QLabel(parent)
        self.label.setText(labelname)
        self.label.setToolTip(tooltip)
        self.widget = widget
        self.H_layout = QHBoxLayout(self)
        self.H_layout.addWidget(self.label)
        self.H_layout.addWidget(self.widget)
        self.H_layout.setSpacing(0)
        self.setLayout(self.H_layout)
        self.widget.setParent(self)
        self.setContentsMargins(0, 0, 0, 0)

    def setDescText(self, txt):
        self.label.setText(txt)

    def setDescTooltip(self, txt):
        self.label.setToolTip(txt)


class NoRepeatShortcut(QShortcut):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAutoRepeat(False)


class ProgressBarBlackFont(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("text-align:center;color:black;")

    pass


class AllEventAdmin(object):
    from . import funcs

    def __init__(self, event_dict):
        self.event_dict = event_dict

    def bind(self):
        event_dict = self.funcs.event_handle_connect(self.event_dict)
        AllEvents.update(event_dict)
        # print(len(AllEvents))
        return self

    def unbind(self, classname=""):
        self.funcs.event_handle_disconnect(self.event_dict)
        if not classname == "":
            # print(f"{classname} all events unbind")
            pass
        return self


class UniversalProgresser(QDialog):
    on_close = pyqtSignal()  #

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.progressbar = ProgressBarBlackFont(self)
        self.signal_func_dict: "dict[str,list[callable,callable,Union[dict,None]]]" = None  # "signal_name":[signal,funcs,kwargs] 传入的信号与槽函数
        self.signal_sequence: "list[list[str]]" = None  # [["signal_name"]] 0,1,2 分别是前,中,后的回调函数.
        self.timer = QTimer()
        self.format_dict = {}
        self.event_dict = {}
        self.init_UI()
        self.show()

    def close_dely(self, dely=100):
        self.timer.singleShot(dely, self.close)

    def data_load(self, format_dict=None, signal_func_dict=None, signal_sequence=None):
        if self.signal_sequence is not None:
            raise ValueError("请先启动data_clear,再赋值")
        self.format_dict = format_dict
        self.signal_sequence = signal_sequence
        self.signal_func_dict = signal_func_dict
        if self.signal_sequence is not None:
            if len(self.signal_sequence) != 3:
                raise ValueError("signal_sequence 的元素必须是 3个数组")
        if self.signal_func_dict is not None:
            self.event_dict = {}
            for k, v in self.signal_func_dict.items():
                if len(v) != 3:
                    raise ValueError("signal_func_dict 的value必须是长度为3的数组")
                self.event_dict[v[0]] = v[1]
                if v[2] is not None:
                    v[2]["type"] = self.__class__.__name__
            self.all_event = AllEventAdmin(self.event_dict).bind()
        return self

    def data_clear(self):
        self.signal_func_dict = None  # "signal_name":[signal,func] 传入的信号与槽函数
        self.signal_sequence = None  # ["signal_name",{"args":[],"kwargs":{}]
        self.pdf_page_list = None  # [[pdfdir,pagenum]]
        self.all_event.unbind()
        return self

    def valtxt_set(self, value, format=None):
        """set value and format,"""
        if format is not None:
            self.progressbar.setFormat(format)
        self.progressbar.setValue(value)

    def init_UI(self):
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        glayout = QGridLayout(self)
        glayout.addWidget(self.progressbar, 0, 0, 1, 4)
        self.setLayout(glayout)


# class ColumnSpinboxDelegate(QStyledItemDelegate):
#     """先设计基本的SpinboxDelegate, 然后通过load_config 配置第几列,或多列的情况 """

class ColumnSpinboxDelegate(QItemDelegate):
    # class combox(QComboBox):
    #     def __init__(self):

    def __init__(self, columns, parent=None):
        super(ColumnSpinboxDelegate, self).__init__(parent)
        self.columns = columns

    def paint(self, painter, option, index):
        if index.column() in self.columns:
            value = index.model().data(index, Qt.DisplayRole)
            option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
            self.drawDisplay(painter, option, option.rect, str(value) if value is not None else None)
            self.drawFocus(painter, option, option.rect)
        else:
            super(ColumnSpinboxDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        if index.column() in self.columns:
            spinBox = QSpinBox(parent)
            spinBox.setRange(0, 2000)
            spinBox.editingFinished.connect(self.commitAndCloseEditor)
            return spinBox
        else:
            return super(ColumnSpinboxDelegate, self).createEditor(parent, option, index)

    def commitAndCloseEditor(self):
        spinBox = self.sender()
        self.commitData.emit(spinBox)
        self.closeEditor.emit(spinBox)

    def setEditorData(self, editor, index):
        if index.column() in self.columns:
            value = int(index.model().data(index, Qt.DisplayRole))
            editor.setValue(value if value is not None else 0)
        else:
            super(ColumnSpinboxDelegate, self).setEditorData(editor, index)


class Macro(QObject):
    stopState = 0
    runningState = 1
    pauseState = 2
    on_start = pyqtSignal()
    on_pause = pyqtSignal()
    on_switch = pyqtSignal()
    on_stop = pyqtSignal()

    def __init__(self, ):
        super().__init__()
        self.macrodata = None
        self.len = 1
        self.step = 0
        self.lastData = None
        self.QAvalue = {}
        self.state = self.stopState
        self.on_pause.connect(self.on_pause_handle)
        self.on_switch.connect(self.on_switch_handle)

    def start(self, macrodata):
        self.macrodata = macrodata
        self.len = len(macrodata)
        self.step = 0
        self.state = self.runningState
        from . import events
        e = events.CardListSelectItemEvent
        signals.on_cardlist_selectItem.emit(e(eventType=e.singleRowType, rowNum=0))

    def pickQA(self):

        instruct = self.macrodata[self.step % self.len][0:2]
        self.QAvalue["QA"] = instruct[0]
        self.QAvalue["textQA"] = instruct[1]
        self.step += 1
        if self.step % self.len == 0:
            signals.on_clipper_hotkey_next_card.emit()

    def get(self, QA):

        if QA not in self.QAvalue:
            self.pickQA()
        self.lastData = self.QAvalue.copy()
        return self.QAvalue.pop(QA)

    def stop(self):
        self.step = 0
        self.state = self.stopState

    def pause(self):
        self.state = self.pauseState

    def on_pause_handle(self):
        from . import funcs
        if self.state == self.pauseState:
            self.state = self.runningState
        elif self.state == self.runningState:
            self.state = self.pauseState
        # print(f"self.state={self.state}")
        funcs.show_clipbox_state()

    def on_switch_handle(self):
        from . import funcs
        if self.state == self.stopState:
            self.start(CONFIG.clipbox.macro)
        elif self.state == self.runningState:
            self.stop()
        # print(f"self.state={self.state}")
        funcs.show_clipbox_state()


CONFIG = ConfigDict()
signals = CustomSignals.start()
print, printer = funcs.logger(__name__)
macro = Macro()
AllEvents = {}
