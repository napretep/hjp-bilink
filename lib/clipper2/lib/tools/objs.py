import dataclasses
import json
import os
import sys
from collections import OrderedDict
from typing import Any

from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread, QTimer
from PyQt5.QtGui import QIcon, QStandardItem
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog, QToolButton, \
    QDoubleSpinBox, QComboBox, QVBoxLayout, QFrame, QGridLayout, QWidget, QShortcut, QProgressBar, QStyledItemDelegate, \
    QItemDelegate
from aqt.utils import showInfo

from . import funcs
from . import events, JSONschema_, SrcAdmin_
from ...imports import common_tools

class CustomSignals(QObject):
    """用法: 在需要发射/接受信号的类中调用CustomSignals的类方法start(),并取出需要的信号绑定到本地变量,进行发射或接受"""
    instance = None
    linkedEvent = pyqtSignal()

    # on_pagepicker_PDFopen 是打开PDF的入口, 不参与分析的操作
    on_pagepicker_PDFopen = pyqtSignal(object)  # PDFOpenEvent
    # 打开pagepicker, 会根据打开时的情况选择各种方案
    on_pagepicker_open = pyqtSignal(object)  # PagePickerOpenEvent

    on_pagepicker_browser_loadframe = pyqtSignal(object)  # PagePickerBrowserLoadFrameEvent

    on_pageItem_addToScene = pyqtSignal(object)  # PagePickerEvent

    on_pageitem_close = pyqtSignal(object)  # PageItemCloseEvent

    on_pageItem_resize_event = pyqtSignal(object)  # PageItemResizeEvent

    on_clipbox_create = pyqtSignal(object)  # ClipboxCreateEvent
    on_clipbox_card_change = pyqtSignal(object)  # ClipboxCardChange
    on_clipbox_del_card = pyqtSignal(object)  # ClipboxDelCard

    on_rightSideBar_buttonGroup_clicked = pyqtSignal(object)  # RightSideBarButtonGroupEvent

    on_clipper_hotkey_next_card = pyqtSignal()
    on_clipper_hotkey_prev_card = pyqtSignal()
    on_clipper_hotkey_setA = pyqtSignal()
    on_clipper_hotkey_setQ = pyqtSignal()
    on_clipper_hotkey_press = pyqtSignal(object)  # ClipperHotkeyPressEvent

    on_cardlist_selectRow = pyqtSignal(object)

    on_anki_card_create = pyqtSignal(object)  # AnkiCardCreateEvent
    on_anki_card_created = pyqtSignal(object)  # AnkiCardCreatedEvent
    on_anki_field_insert = pyqtSignal(object)  # AnkiFieldInsertEvent
    on_anki_file_create = pyqtSignal(object)  # AnkiFileCreateEvent

    on_config_ankidata_load = pyqtSignal(object)  # ConfigAnkiDataLoadEvent
    on_config_ankidata_load_end = pyqtSignal(object)  # ConfigAnkiDataLoadEndEvent

    # -----------------------------------------下面的是旧的未经改造的-----------------------------------------------------
    # on_anki_field_inserted = pyqtSignal(object) #AnkiFieldInsertedEvent
    on_anki_browser_activate = pyqtSignal(object)  # AnkiBrowserActivateEvent
    # 发射rubberbandrect信号就是为了添加
    on_pdfview_rubberBandRect_send = pyqtSignal(object)  # PageItemRubberBandRectSendEvent
    on_pagepicker_bookmark_open = pyqtSignal(object)  # OpenBookmarkEvent
    on_pagepicker_bookmark_clicked = pyqtSignal(object)  # BookmarkClickedEvent

    on_pagepicker_PDFparse = pyqtSignal(object)  # PDFParseEvent
    on_pagepicker_PDFlayout = pyqtSignal(object)  # PDFlayoutEvent

    on_pagepicker_close = pyqtSignal(object)  # PagePickerCloseEvent

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

    on_pageItem_changePage = pyqtSignal(object)  # PageItemChangeEvent

    on_pageItem_removeFromScene = pyqtSignal(object)

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


    on_rightSideBar_settings_clicked = pyqtSignal(object)
    on_rightSideBar_refresh_clicked = pyqtSignal(object)

    on_rightSideBar_cardModel_changed = pyqtSignal()  # RightSideBarModelChanged



    on_config_changed = pyqtSignal()
    on_config_reload = pyqtSignal()
    on_config_reload_end = pyqtSignal()


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
    """每次想读取的时候都要运行一遍"""

    class ClipBox:
        def __init__(self, data):
            self.A_map_Field = data["clipbox.A_map_Field"]["value"]
            self.Q_map_Field = data["clipbox.Q_map_Field"]["value"]
            self.macro = data["clipbox.macro"]["value"]
            self.newcard_deck_id = data["clipbox.newcard_deck_id"]["value"]
            self.newcard_model_id = data["clipbox.newcard_model_id"]["value"]
            self.comment_A_map_Field = data["clipbox.comment_A_map_Field"]["value"]
            self.comment_Q_map_Field = data["clipbox.comment_Q_map_Field"]["value"]

    class Output:
        def __init__(self, data):
            self.RatioFix = data["output.RatioFix"]["value"]
            self.needRatioFix = data["output.needRatioFix"]["value"]
            self.close_clipper_after_insert = data["output.closeClipper"]["value"]
            self.close_clipbox_after_insert = data["output.closeClipbox"]["value"]

    class PagePicker:
        def __init__(self, data):
            self.bottombar_default_path: "str" = data["pagepicker.bottombar_default_path"]["value"]
            self.bottombar_page_num = data["pagepicker.bottombar_page_num"]["value"]
            self.bottombar_page_ratio = data["pagepicker.bottombar_page_ratio"]["value"]
            self.browser_layout_col_per_row = data["pagepicker.browser_layout_col_per_row"]["value"]
            self.changepage_ratio_choose = data["pagepicker.changepage_ratio_choose"]["value"]

    class MainView:
        def __init__(self, data):
            self.layout_col_per_row = data["mainview.layout_col_per_row"]["value"]
            self.layout_row_per_col = data["mainview.layout_row_per_col"]["value"]
            self.layout_mode = data["mainview.layout_mode"]["value"]

    def __init__(self):
        self.data = self.load_json()
        self.clipbox = self.ClipBox(self.data)
        self.pagepicker = self.PagePicker(self.data)
        self.mainview = self.MainView(self.data)
        self.output = self.Output(self.data)
        CustomSignals.start().on_config_changed.connect(self.load_data)

    def load_json(self):
        clipper_dir = SrcAdmin.call().jsonDir.clipper
        if not os.path.exists(clipper_dir):
            # showInfo("not exists: %s" % clipper_dir)
            template_dir = SrcAdmin.call().jsonDir.clipper_template
            template_json = json.load(open(template_dir,"r", encoding="utf-8"))
            json.dump(template_json,open(clipper_dir,"w", encoding="utf-8"),indent=4, ensure_ascii=False)
        clipper_json = json.load(open(clipper_dir,"r", encoding="utf-8"))
        return clipper_json

    def load_data(self):
        self.data = self.load_json()
        self.clipbox = self.ClipBox(self.data)
        self.pagepicker = self.PagePicker(self.data)
        self.mainview = self.MainView(self.data)
        self.output = self.Output(self.data)
    #
    # @property
    # def data(self):
    #     return self.load_json()

    def save_data(self, data=None):
        if data is None:
            data = self.data
        json.dump(data, open(SrcAdmin.get.json_dir("clipper"), "w", encoding="utf-8"), ensure_ascii=False,
                  sort_keys=True, indent=4)

    def set_default(self):
        data = json.load(open(SrcAdmin.get.json_dir("clipper.template"), "r", encoding="utf-8"))
        self.save_data(data)
        self.load_data()

class SrcAdmin:
    """单例"""
    from ...imports import common_tools
    instance = None
    get = SrcAdmin_.Get._()
    imgDir = common_tools.G.src.ImgDir
    jsonDir = SrcAdmin_.JSONDir()
    get_json = SrcAdmin_.Get._().json_dict
    get_config = SrcAdmin_.Get._().config_dict
    save_config = SrcAdmin_.Get._().save_dict

    # DB = SrcAdmin_.DB()
    DB = common_tools.objs.DB_admin()
    # PDF_JSON = SrcAdmin_.PDFJSON().load()

    @classmethod
    def call(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class JSONschema:
    """
    JSON的数据规范
    访问json的一个数据的constrain,先确定,type和是否为空,
    然后根据type,选择range的读取方式,
    1 不限定步伐范围形式, -->直接就可以做,范围显示为左右两个值的限定
    2 限定步伐范围形式 -->也直接可以做,因为是数字,范围显示为一个数组
    3 特殊意义数字迭代形式 -->需要结合特殊意义来看
    """

    class DataType:
        int = 0
        float = 1
        iterobj = 2  # 特殊意义的数字
        iternum = 3  # 寻常的数字
        string = 4

    class Empty:
        notAllow = 0
        allow = 1

    # 下面这些就是特殊意义的数字
    class ViewLayout:
        Horizontal = 0
        Vertical = 1
        Freemode = 2

    class NeedRatioFix:
        no = 0
        yes = 1

    class ChangePageRatioChoose:
        old, new = 0, 1

    type = DataType()
    empty = Empty()
    changepage_ratio_choose = ChangePageRatioChoose()
    viewlayout_mode = ViewLayout()
    needratiofix_mode = NeedRatioFix()


class GridHDescUnit(QWidget):
    def __init__(self, parent=None, labelname=None, tooltip=None, widget=None):
        super().__init__(parent)
        self.label = QLabel(self)
        self.label.setText(labelname)
        self.label.setToolTip(tooltip)
        self.widget = widget
        self.H_layout = QGridLayout(self)
        self.H_layout.addWidget(self.label, 0, 0)
        self.H_layout.addWidget(self.widget, 0, 1)
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


UniversalProgresser = common_tools.widgets.UniversalProgresser

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
    """
    启动方式: 通过emit发射switch信号开启/关闭,发射pause信号暂停/继续,其他的不用管

    """
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
        CustomSignals.start().on_cardlist_selectRow.emit(0)

    def pickQA(self):
        instruct = self.macrodata[self.step % self.len][0:2]
        self.QAvalue["QA"] = instruct[0]
        self.QAvalue["commentQA"] = instruct[1]
        self.step += 1
        if self.step % self.len == 0:
            from . import events
            e = events.ClipperHotkeyPressEvent
            CustomSignals.start().on_clipper_hotkey_press.emit(e(type=e.defaultType.nextcard))

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
        if self.state == self.pauseState:
            self.state = self.runningState
        elif self.state == self.runningState:
            self.state = self.pauseState

    def on_switch_handle(self):
        if self.state == self.stopState:
            self.start(CONFIG.clipbox.macro)
        elif self.state == self.runningState:
            self.stop()


@dataclasses.dataclass
class Pair:
    card_id: "str" = None
    desc: "str" = None


@dataclasses.dataclass
class PDFinfoRecord:
    uuid: "str"
    pdf_path: "str"
    ratio: "float"
    offset: "int"


@dataclasses.dataclass
class ClipboxRecord:
    uuid: "str"
    x: "float"
    y: "float"
    w: "float"
    h: "float"
    QA: "int"
    commentQA: "int"
    card_id: "str"
    ratio: "float"
    pagenum: "int"
    pdfuuid: "str"
    comment: "str" = ""


@dataclasses.dataclass
class PageInfo:
    pdf_path: "str"
    pagenum: "int"
    ratio: "float"


@dataclasses.dataclass
class Position:
    x: "float"
    y: "float"


@dataclasses.dataclass
class Progress:
    value: "int"
    text: "str" = None
    data: "Any" = None

CONFIG = ConfigDict()
# signals = CustomSignals.start()
print, printer = funcs.logger(__name__)
macro = Macro()
AllEvents = {}
