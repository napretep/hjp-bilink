import json
import os

from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog, QToolButton, \
    QDoubleSpinBox, QComboBox, QVBoxLayout, QFrame, QGridLayout, QWidget

from .funcs import str_shorten
from . import events, JSONschema_, SrcAdmin_
from ..PageInfo import PageInfo

class CustomSignals(QObject):
    """用法: 在需要发射/接受信号的类中调用CustomSignals的类方法start(),并取出需要的信号绑定到本地变量,进行发射或接受"""
    instance = None
    linkedEvent = pyqtSignal()

    on_pagepicker_close = pyqtSignal(object)  # PagePickerCloseEvent
    on_pagepicker_bookmark_open = pyqtSignal(object)  # OpenBookmarkEvent
    on_pagepicker_bookmark_clicked = pyqtSignal(object)  # BookmarkClickedEvent

    # PDFopen只用于打开PDF, 不参与分析的操作
    on_pagepicker_PDFopen = pyqtSignal(object)  # PDFOpenEvent
    on_pagepicker_PDFparse = pyqtSignal(object)  # PDFParseEvent
    on_pagepicker_PDFlayout = pyqtSignal(object)  # PDFlayoutEvent

    on_pagepicker_rightpart_pageread = pyqtSignal(object)  # PagePickerRightPartPageReadEvent
    # click还管别的
    on_pagepicker_leftpart_pageclicked = pyqtSignal(object)  # PagePickerLeftPartPageClickedEvent
    # select只管select
    on_pagepicker_leftpart_select = pyqtSignal(object)  # PagePickerLeftPartSelectEvent

    on_pagepicker_leftpart_sceneClear = pyqtSignal(object)  # PagePickerLeftPartSceneClear

    on_pageItem_clicked = pyqtSignal(object)  # PageItemClickEvent
    on_pageItem_clipbox_added = pyqtSignal(object)
    on_pageItem_resize_event = pyqtSignal(object)  # PageItemResizeEvent
    on_pageItem_resetSize_event = pyqtSignal(object)
    on_pageItem_nextPage_event = pyqtSignal(object)
    on_pageItem_prevPage_event = pyqtSignal(object)
    on_pageItem_changePage = pyqtSignal(object)  # PageItemChangeEvent
    on_pageItem_addToScene = pyqtSignal(object)  # PagePickerEvent
    on_pageItem_removeFromScene = pyqtSignal(object)

    on_pageItem_needCenterOn = pyqtSignal(object)  # PageItemNeedCenterOnEvent

    on_cardlist_dataChanged = pyqtSignal(object)  # CardListDataChangedEvent
    # 目前主要影响clipbox的toolsbar的cardcombox更新数据
    # 传送的数据用不起来

    on_cardlist_deleteItem = pyqtSignal(object)

    on_clipbox_closed = pyqtSignal(object)
    on_clipboxCombox_updated = pyqtSignal(object)
    on_clipboxCombox_emptied = pyqtSignal()

    on_rightSideBar_settings_clicked = pyqtSignal(object)
    on_rightSideBar_refresh_clicked = pyqtSignal(object)
    on_rightSideBar_buttonGroup_clicked = pyqtSignal(object)  # RightSideBarButtonGroupEvent

    on_clipper_hotkey_next_card = pyqtSignal()
    on_clipper_hotkey_prev_card = pyqtSignal()
    on_clipper_hotkey_setA = pyqtSignal()
    on_clipper_hotkey_setQ = pyqtSignal()

    on_PDFView_ResizeView = pyqtSignal(object)  # PDFViewResizeViewEvent



    @classmethod
    def start(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class SrcAdmin:
    """单例"""
    instance = None
    imgDir = SrcAdmin_.IMGDir()
    get_json = SrcAdmin_.Get._().json_dict

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

    def setDescText(self, txt):
        self.label.setText(txt)

    def setDescTooltip(self, txt):
        self.label.setToolTip(txt)
