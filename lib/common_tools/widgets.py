# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'mywidgets.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/1 16:48'
"""
import abc
import math
import os
import re
import urllib
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
import time, collections
from typing import Union, Optional
import sys
from ast import literal_eval
from .language import Translate, rosetta
from . import configsModel

from .compatible_import import *
from . import funcs, baseClass, hookers, funcs2

布局 = 框 = 0
组件 = 件 = 1
子代 = 子 = 2
占 = 占据 = 3
# from ..bilink.dialogs.linkdata_grapher import Grapher

if __name__ == "__main__":
    from lib.common_tools import G
else:
    from . import G

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *

译 = Translate


class SafeImport:
    @property
    def models(self):
        from . import models
        return models


safe = SafeImport()


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


class ProgressBarBlackFont(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setStyleSheet("text-align:center;color:black;")

    pass


class UniversalProgresser(QDialog):
    on_close = pyqtSignal()  #

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.progressbar = ProgressBarBlackFont(self)
        self.intro = QLabel("if crashed, press esc to quit", self)
        self.signal_func_dict: "Optional[dict[str,list[callable,callable,Union[dict,None]]]]" = None  # "signal_name":[signal,funcs,kwargs] 传入的信号与槽函数
        self.signal_sequence: "Optional[list[list[str]]]" = None  # [["signal_name"]] 0,1,2 分别是前,中,后的回调函数.
        self.timer = QTimer()
        self.format_dict = {}
        self.event_dict = {}
        self.init_UI()
        self.show()

    def close_dely(self, dely=100):
        self.timer.singleShot(dely, self.close)

    def data_load(self, format_dict=None, signal_func_dict=None, signal_sequence=None):
        from . import objs
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
            self.all_event = objs.AllEventAdmin(self.event_dict).bind()
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

    def value_set(self, event: "Progress"):
        if type(event) != int:  # 有些地方直接插入数字了
            self.progressbar.setValue(event.value)
            if event.text is not None:
                self.progressbar.setFormat(event.text)
        else:
            self.progressbar.setValue(event)

    def init_UI(self):
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        glayout = QGridLayout(self)
        glayout.addWidget(self.progressbar, 0, 0, 1, 4)
        glayout.addWidget(self.intro, 1, 0, 1, 1)
        self.setLayout(glayout)


class SupportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(G.src.ImgDir.heart))
        self.setWindowTitle("支持作者/support author")
        self.alipayPic = QPixmap(G.src.ImgDir.qrcode_alipay)
        self.alipaylabel = QLabel(self)
        self.alipaylabel.setPixmap(self.alipayPic)
        self.alipaylabel.setScaledContents(True)
        self.alipaylabel.setMaximumSize(300, 300)
        self.weixinpaylabel = QLabel(self)
        self.weixinpaylabel.setPixmap(QPixmap(G.src.ImgDir.qrcode_weixinpay))
        self.weixinpaylabel.setScaledContents(True)
        self.weixinpaylabel.setMaximumSize(300, 300)
        self.desclabel = QLabel(self)
        self.desclabel.setText("点赞、转发、分享给更多人，也是一种支持！")
        self.desclabel.setAlignment(Qt.AlignCenter)
        self.v_layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.weixinpaylabel)
        self.h_layout.setStretch(0, 1)
        self.h_layout.setStretch(1, 1)
        self.h_layout.addWidget(self.alipaylabel)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.desclabel)
        self.setMaximumSize(400, 400)
        self.setLayout(self.v_layout)
        self.show()


class SelectorProtoType(QDialog):
    """大部分待选表的一个原型"""

    def __init__(self, title_name="", separator="::", header_name=""):
        super().__init__()
        self.tree_structure = True
        self.window_title_name = title_name
        self.separator = separator
        self.model_header_name = header_name
        self.view = QTreeView(self)
        self.model = QStandardItemModel(self)
        self.model_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.header = self.Header(self)
        self.instruction = QLabel(译.双击以选中项)
        self.header.button.clicked.connect(self.on_header_button_clicked_handle)
        self.header.new_item_button.clicked.connect(self.on_header_new_item_button_clicked_handle)
        self.view.clicked.connect(self.on_view_clicked_handle)
        self.view.doubleClicked.connect(self.on_view_doubleclicked_handle)
        self.model.dataChanged.connect(self.on_model_data_changed_handle)
        self.init_UI()
        self.init_model()

    @abstractmethod
    def on_header_new_item_button_clicked_handle(self):
        raise NotImplementedError()

    # @abstractmethod
    # def on_item_button_clicked_handle(self, item: "deck_chooser.Item"):
    #     raise NotImplementedError()

    @abstractmethod
    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        raise NotImplementedError()

    @abstractmethod
    def on_view_clicked_handle(self, index):
        raise NotImplementedError()

    @abstractmethod
    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        raise NotImplementedError()

    @abstractmethod
    def on_view_doubleclicked_handle(self, index):
        raise NotImplementedError()

    def get_full_item_name(self, item: "SelectorProtoType.Item"):
        if self.header.button.text() == self.header.as_list:
            return item.text()
        s = ""
        parent = item
        while parent != self.model.invisibleRootItem():
            s = self.separator + parent.deck_name + s
            parent = parent.parent()
        s = s[2:]
        return s

    def on_header_button_clicked_handle(self):
        if self.tree_structure:
            if self.header.button.text() == self.header.as_tree:
                self.header.button.setText(self.header.as_list)
                self.header.button.setIcon(QIcon(G.src.ImgDir.list))
            else:
                self.header.button.setText(self.header.as_tree)
                self.header.button.setIcon(QIcon(G.src.ImgDir.tree))
        self.init_data()

    def init_model(self):
        self.view.setModel(self.model)
        self.model.setHorizontalHeaderLabels([self.model_header_name])
        self.view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.init_data()
        self.view.setColumnWidth(1, 30)

    def init_data(self):
        self.model.clear()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model.setHorizontalHeaderLabels([self.model_header_name])
        if self.tree_structure:
            if self.header.button.text() == self.Header.as_tree:
                self.build_as_tree()
            else:
                self.build_as_list()
        else:
            self.build_as_list()
        self.view.expandAll()

    def build_as_list(self):
        data_li: "list[SelectorProtoType.Id_name]" = self.get_all_data_items()
        for i in data_li:
            item = self.Item(i.name)
            item.data_id = i.ID
            self.model.appendRow([item])
        pass

    def build_as_tree(self):
        item_li: "list[SelectorProtoType.Id_name]" = self.get_all_data_items()
        data_dict = G.objs.Struct.TreeNode(self.model_rootNode, {})
        for i in item_li:
            data_name_li = i.name.split(self.separator)
            parent = data_dict
            while data_name_li:
                deckname = data_name_li.pop(0)
                if deckname not in parent.children:
                    item = self.Item(deckname)
                    parent.item.appendRow([item])
                    parent.children[deckname] = G.objs.Struct.TreeNode(item, {})
                    if not data_name_li:
                        item.data_id = i.ID
                parent = parent.children[deckname]

    def init_UI(self):
        self.setWindowTitle(self.window_title_name)
        self.setWindowIcon(QIcon(G.src.ImgDir.box))
        self.view.setIndentation(8)
        V_layout = QVBoxLayout(self)
        V_layout.addWidget(self.header)
        V_layout.addWidget(self.view)
        V_layout.addWidget(self.instruction, stretch=0)
        V_layout.setStretch(1, 1)
        V_layout.setStretch(0, 0)
        self.setLayout(V_layout)

    class Header(QWidget):
        as_tree, as_list = "as_tree", "as_list"

        def __init__(self, parent, deckname=""):
            super().__init__(parent)
            self.desc = QLabel("current item|" + deckname, self)
            self.desc.setWordWrap(True)
            self.button = QToolButton(self)
            self.button.setText(self.as_tree)
            self.button.setIcon(QIcon(G.src.ImgDir.tree))
            self.new_item_button = QToolButton(self)
            self.new_item_button.setIcon(QIcon(G.src.ImgDir.item_plus))
            H_layout = QHBoxLayout(self)
            H_layout.addWidget(self.desc)
            H_layout.addWidget(self.new_item_button)
            H_layout.addWidget(self.button)
            H_layout.setStretch(0, 1)
            H_layout.setStretch(1, 0)
            self.setLayout(H_layout)

        def set_header_label(self, data_name):
            self.desc.setText("current item|" + data_name)

    class Item(QStandardItem):
        def __init__(self, data_name):
            super().__init__(data_name)
            self.data_id: "Optional[int]" = None
            self.level: "Optional[int]" = None
            self.setFlags(self.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)

        @property
        def deck_name(self):
            return self.text()

        def parent(self) -> "SelectorProtoType.Item":
            parent: "SelectorProtoType.Item" = super().parent()
            if parent:
                return parent
            else:
                return self.model().invisibleRootItem()

    @dataclass
    class Id_name:
        name: "str"
        ID: "int|str"


class DeckSelectorProtoType(SelectorProtoType):
    def __init__(self, title_name="", separator="::", header_name=""):
        super().__init__(title_name, separator, header_name)

    def on_header_new_item_button_clicked_handle(self):
        new_item = self.Item(f"""new_deck_{datetime.now().strftime("%Y%m%d%H%M%S")}""")
        if self.view.selectedIndexes():
            item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(self.view.selectedIndexes()[0])
            parent_item = item.parent()
        else:
            parent_item = self.model.invisibleRootItem()
        parent_item.appendRow([new_item])
        self.view.edit(new_item.index())
        deck = mw.col.decks.add_normal_deck_with_name(self.get_full_item_name(new_item))
        new_item.deck_id = deck.id

    def on_view_doubleclicked_handle(self, index):
        raise NotImplementedError()

    # def on_item_button_clicked_handle(self, item: "deck_chooser.Item"):
    #     raise NotImplementedError()

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(topLeft)
        from . import funcs
        DeckId = funcs.Compatible.DeckId()
        new_deck_name = self.get_full_item_name(item)
        mw.col.decks.rename(DeckId(item.deck_id), new_deck_name)
        # print(item.deck_name)

    def on_view_clicked_handle(self, index):
        item: DeckSelectorProtoType.Item = self.model.itemFromIndex(index)
        # tooltip(self.get_full_item_name(item))

    def get_all_data_items(self):

        decks = mw.col.decks
        return [self.Id_name(name=i.name, ID=i.id) for i in decks.all_names_and_ids() if
                not decks.is_filtered(i.id)]


class deck_chooser_for_changecard(DeckSelectorProtoType):

    def __init__(self, pair_li: "list[G.objs.LinkDataPair]" = None, fromview: "AnkiWebView" = None):
        super().__init__(title_name="deck_chooser", header_name="deck_name")
        self.fromview: "None|AnkiWebView|Previewer|Reviewer" = fromview
        self.pair_li = pair_li
        self.header.set_header_label(self.curr_deck_name)

    @property
    def curr_deck_name(self):
        from . import funcs
        CardId = funcs.CardId
        if len(self.pair_li) == 1:
            did = mw.col.getCard(CardId(int(self.pair_li[0].card_id))).did
            name = mw.col.decks.get(did)["name"]
            return name
        else:
            return "many cards"

    def on_view_doubleclicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        from . import funcs
        # showInfo(self.fromview.__str__())
        DeckId = funcs.Compatible.DeckId()
        CardId = funcs.CardId
        browser: Browser = funcs.BrowserOperation.get_browser()

        if browser is None:
            dialogs.open("Browser", mw)
            browser = funcs.BrowserOperation.get_browser()
        for pair in self.pair_li:
            set_card_deck(parent=browser, card_ids=[CardId(pair.int_card_id)],
                          deck_id=DeckId(item.data_id)).run_in_background()
        browser.showMinimized()
        from ..bilink.dialogs.linkdata_grapher import Grapher
        if isinstance(self.fromview, AnkiWebView):
            parent: "Union[Previewer,Reviewer]" = self.fromview.parent()
            parent.activateWindow()
        elif isinstance(self.fromview, Grapher):
            self.fromview.activateWindow()
        QTimer.singleShot(100, funcs.LinkPoolOperation.both_refresh)
        self.close()


class universal_deck_chooser(DeckSelectorProtoType):
    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.结果 = item.data_id
        self.close()

    def __init__(self, ):
        super().__init__(title_name="deck chooser", header_name="deck name")
        self.结果 = -1


class universal_template_chooser(SelectorProtoType):
    def __init__(self, ):
        super().__init__(title_name="template chooser", header_name="template name")
        self.结果 = -1
        self.tree_structure = False
        self.header.button.hide()
        self.header.new_item_button.hide()

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        all_models = mw.col.models.all_names_and_ids()
        return [self.Id_name(name=i.name, ID=i.id) for i in all_models]
        pass

    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.结果 = item.data_id
        self.close()


class view_chooser(SelectorProtoType):
    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.编号 = item.data_id
        self.close()
        pass

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        gview_dict = funcs.GviewOperation.load_all_as_dict()
        return [self.Id_name(name=data.name, ID=uuid) for uuid, data in gview_dict.items()]
        pass

    def __init__(self, title_name="", separator="::", header_name=""):
        super().__init__(title_name, separator, header_name)
        self.header.new_item_button.hide()
        self.编号 = -1


class universal_field_chooser(SelectorProtoType):
    def __init__(self, 模板编号, title_name="", separator="::", header_name=""):
        self.模板编号: "int" = 模板编号
        self.tree_structure = False
        super().__init__("choose a field", separator, "field name")
        self.header.new_item_button.hide()
        self.header.button.hide()
        self.结果 = -1

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        字段名集 = mw.col.models.field_names(mw.col.models.get(self.模板编号))
        return [self.Id_name(name=字段名集[i], ID=i) for i in range(len(字段名集))]
        pass

    def on_view_doubleclicked_handle(self, index):
        item: "DeckSelectorProtoType.Item" = self.model.itemFromIndex(index)
        self.结果 = item.data_id
        self.close()
        pass


class multi_select_prototype(QDialog):
    def __init__(self, preset: "iter[str]" = None, separater="::", dialog_title="", new_item="new_tag"):
        super().__init__()
        self.分隔符 = separater
        self.标题栏名字 = dialog_title
        self.提供树结构 = True
        self.新项目名字 = new_item
        self.view_left = self.View(self)
        self.view_right = self.View(self)
        self.view_left.setContextMenuPolicy(Qt.CustomContextMenu)
        self.model_left = QStandardItemModel(self)
        self.model_right = QStandardItemModel(self)
        self.model_right_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.model_left_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.item_list = set() if not preset else set(preset)  # 最终选择的item在这里保存
        self.结果 = self.item_list
        self.left_button_group = self.button_group(self, 0, self.view_left, self.model_left)
        self.right_button_group = self.button_group(self, 1, self.view_right, self.model_right)
        self.init_UI()
        self.init_model()
        self.allevent = G.objs.AllEventAdmin([
                [self.model_left.dataChanged, self.on_model_left_datachanged_handle],
                [self.view_right.doubleClicked, self.on_view_right_doubleClicked_handle],
                # [self.view_left.customContextMenuRequested, self.on_view_show_context_menu]
        ]).bind()

    def on_view_right_doubleClicked_handle(self, index):
        self.right_button_group.on_item_add_handle()

    def on_model_left_datachanged_handle(self, index):
        """左边的数据改变了, 就要保存一次"""
        item: "multi_select_prototype.Item" = self.model_left.itemFromIndex(index)
        stack: "list[multi_select_prototype.Item]" = [item]
        while stack:
            it = stack.pop()
            if it.item_name is not None:
                old = it.item_name
                new = self.get_full_item_name(it)
                self.item_list.remove(old)
                self.item_list.add(new)
                it.set_item_name(new)
            for i in range(it.rowCount()):
                stack.append(it.child(i, 0))
        self.init_data_left()

    def init_UI(self):
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("item chooser")
        self.setWindowIcon(QIcon(G.src.ImgDir.tag))
        组件布局 = {框: QHBoxLayout(),
                子:  [{框: QVBoxLayout(),
                          子: [{件: self.view_left}, {件: self.left_button_group}]}
                             ,
                         {框: QVBoxLayout(),
                          子: [{件: self.view_right}, {件: self.right_button_group}]},],
                    }

        funcs.组件定制.组件组合(组件布局, self)
        pass

    def init_model(self):
        self.view_left.setModel(self.model_left)
        self.view_right.setModel(self.model_right)
        self.view_left.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view_right.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.init_data_left(init=True)
        self.init_data_right()

        pass

    def closeEvent(self, QCloseEvent):
        self.item_list = self.save()
        self.结果 = list(self.item_list)

    def save(self):
        stack: "list[multi_select_prototype.Item]" = [self.model_left.item(i, 0) for i in range(self.model_left.rowCount())]
        s = set()
        while stack:
            item = stack.pop()
            if item.item_name:
                s.add(self.get_full_item_name(item))
            for i in range(item.rowCount()):
                stack.append(item.child(i, 0))
        return s

    def get_full_item_name(self, item: "multi_select_prototype.Item"):
        text_li = []
        parent = item
        while parent:
            if parent.text() != "":
                text_li.append(parent.text())
            parent = parent.parent()
        text = self.分隔符.join(reversed(text_li))
        return text

    def get_all_items(self) -> 'set[str]':
        raise NotImplementedError()

    def build_as_tree(self, item_set: "set[str]", model: "QStandardItemModel", view: "multi_select_prototype.View",
                      button_group: "multi_select_prototype.button_group"):
        item_list = sorted(list(item_set))
        item_dict = G.objs.Struct.TreeNode(model.invisibleRootItem(), {})
        total_item = button_group.L_or_R == button_group.R
        for i in item_list:
            item_name_li = i.split(self.分隔符)
            parent = item_dict
            while item_name_li:
                item_name = item_name_li.pop(0)
                if item_name not in parent.children:
                    item = self.Item(item_name, total_item=total_item)
                    parent.item.appendRow([item])
                    parent.children[item_name] = G.objs.Struct.TreeNode(item, {})
                    if not item_name_li:
                        item.set_item_name(i)
                parent = parent.children[item_name]
        view.setDragDropMode(DragDropMode.NoDragDrop)
        view.setAcceptDrops(True)
        pass

    def build_as_list(self, item_set: "set[str]", model: "QStandardItemModel", view: "multi_select_prototype.View",
                      button_group: "multi_select_prototype.button_group"):
        item_list = sorted(list(item_set))
        total_item = button_group.L_or_R == button_group.R
        for i in item_list:
            item = self.Item(i, total_item=total_item)
            item.set_item_name(i)
            model.appendRow([item])
        view.setDragDropMode(DragDropMode.NoDragDrop)
        pass

    def init_data_left(self ,init=True):
        model, button_group, view = self.model_left, self.left_button_group, self.view_left
        model.clear()
        self.model_right_rootNode = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(["selected item"])
        if button_group.arrange_button.text() == button_group.as_tree:
            self.build_as_tree(self.item_list, model, view, button_group)
        else:
            self.build_as_list(self.item_list, model, view, button_group)
        self.view_left.expandAll()
        pass

    def init_data_right(self):
        model, button_group, view = self.model_right, self.right_button_group, self.view_right
        model.clear()
        self.model_left_rootNode = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(["all items"])
        item_list = self.get_all_items()
        if button_group.arrange_button.text() == button_group.as_tree:
            self.build_as_tree(item_list, model, view, button_group)
        else:
            self.build_as_list(item_list, model, view, button_group)
        self.view_right.expandAll()
        pass

    class button_group(QWidget):
        L, R = 0, 1
        as_tree, as_list = "as_tree", "as_list"

        def __init__(self, superior: "multi_select_prototype", L_or_R=0, fromView: "QTreeView" = None,
                     fromModel: "QStandardItemModel" = None):
            super().__init__()
            self.superior = superior
            self.fromView = fromView
            self.fromModel = fromModel
            self.L_or_R = L_or_R
            if self.L_or_R == self.R:
                self.left_button = funcs.组件定制.按钮_提示(触发函数=lambda:funcs.Utils.大文本提示框(译.说明_多选框的用法))
                self.middle_button= QPushButton(QIcon(G.src.ImgDir.correct), "")
            else:
                self.left_button= QPushButton(QIcon(G.src.ImgDir.item_plus), "")
                self.middle_button = QPushButton(QIcon(G.src.ImgDir.cancel), "")
            self.arrange_button = QPushButton(self)  # 大家都有一个排版系统
            self.arrange_button.setText(self.as_tree)
            self.button_Icon_switch()
            self.init_UI()
            self.init_event()

        def button_text_switch(self):
            if self.arrange_button.text() == self.as_tree:
                self.arrange_button.setText(self.as_list)
            else:
                self.arrange_button.setText(self.as_tree)
            self.button_Icon_switch()
            if self.L_or_R == self.L:
                self.superior.init_data_left()
            else:
                self.superior.init_data_right()

        def button_Icon_switch(self):
            if self.arrange_button.text() == self.as_tree:
                self.arrange_button.setIcon(QIcon(G.src.ImgDir.tree))
            else:
                self.arrange_button.setIcon(QIcon(G.src.ImgDir.list))

        def init_UI(self):
            funcs.组件定制.组件组合({框:QHBoxLayout(), 子:[{件:self.left_button}, {件:self.middle_button}, {件:self.arrange_button}]}, self)


        def init_event(self):
            if self.L_or_R == self.L:
                self.middle_button.clicked.connect(self.on_item_del_handle)
                self.left_button.clicked.connect(self.on_item_new_handle)
            elif self.L_or_R == self.R:
                self.middle_button.clicked.connect(self.on_item_add_handle)
            self.arrange_button.clicked.connect(self.button_text_switch)

        def on_item_new_handle(self, item_name=None, from_posi=None):
            if item_name:
                new_item = item_name
            else:
                new_item = f"""{self.superior.新项目名字}_{datetime.now().strftime("%Y%m%d%H%M%S")}"""
            if from_posi:
                item_parent = from_posi
                new_full_item = new_item
            else:
                if self.fromView.selectedIndexes():
                    item = self.fromModel.itemFromIndex(self.fromView.selectedIndexes()[0])
                    item_parent = item.parent()
                    new_full_item = self.superior.get_full_item_name(item) + self.superior.分隔符 + new_item
                else:
                    item_parent = self.fromModel.invisibleRootItem()
                    new_full_item = new_item
            new_item = self.superior.Item(new_item)
            new_item.set_item_name(new_full_item)
            item_parent.appendRow([new_item])
            self.superior.item_list = self.superior.save()
            self.fromView.edit(new_item.index())
            pass

        def on_item_del_handle(self):
            if self.fromView.selectedIndexes():
                item_li = [self.fromModel.itemFromIndex(index) for index in self.fromView.selectedIndexes()]

                stack = item_li
                while stack:
                    stack_item: "multi_select_prototype.Item" = stack.pop()
                    if stack_item.item_name:
                        self.superior.item_list.remove(stack_item.item_name)
                        stack_item.set_item_name(None)
                    for i in range(stack_item.rowCount()):
                        stack.append(stack_item.child(i, 0))
                self.superior.init_data_left()

        def on_item_add_handle(self):
            if self.fromView.selectedIndexes():
                item_li = [self.fromModel.itemFromIndex(index) for index in self.fromView.selectedIndexes()]
                for item in item_li:
                    # item:"tag_chooser.Item" = self.fromModel.itemFromIndex(self.fromView.selectedIndexes()[0])
                    item_name = self.superior.get_full_item_name(item)
                    if item_name not in self.superior.item_list:
                        self.superior.item_list.add(item_name)
                self.superior.init_data_left()

    class View(QTreeView):
        item_list, item_tree = 0, 1
        on_did_drop = pyqtSignal(object)

        @dataclass
        class DidDropEvent:
            index: "QModelIndex"
            old: "str"
            new: "str"

        def __init__(self, parent: "multi_select_prototype"):
            super().__init__(parent)
            self.superior: "multi_select_prototype" = parent
            self.viewmode: "Optional[int]" = None
            self.setDragDropOverwriteMode(False)
            self.setSelectionMode(QAbstractItemViewSelectMode.ExtendedSelection)
            # self.on_did_drop.connect(self.change_base_tag_after_dropEvent)

        def dropEvent(self, event: QtGui.QDropEvent) -> None:
            item_from: "list[multi_select_prototype.Item]" = [self.model().itemFromIndex(index) for index in
                                                             self.selectedIndexes()]
            item_to: "multi_select_prototype.Item" = self.model().itemFromIndex(self.indexAt(event.pos()))
            parent_from: "list[multi_select_prototype.Item]" = [item.parent() for item in item_from]
            parent_to: "multi_select_prototype.Item" = item_to.parent() if item_to is not None else self.model().invisibleRootItem()
            for i in range(len(parent_from)):
                item = parent_from[i].takeRow(item_from[i].row())
                if self.dropIndicatorPosition() == dropIndicatorPosition.OnItem:
                    item_to.appendRow(item)
                elif self.dropIndicatorPosition() == dropIndicatorPosition.OnViewport:
                    self.model().appendRow(item)
                elif self.dropIndicatorPosition() == dropIndicatorPosition.BelowItem:
                    parent_to.insertRow(item_to.row() + 1, item)
                elif self.dropIndicatorPosition() == dropIndicatorPosition.AboveItem:
                    parent_to.insertRow(item_to.row(), item)
            self.superior.item_list = self.superior.save()
            self.superior.init_data_left()

    class Item(QStandardItem):
        def __init__(self, item_name, total_item=False):
            super().__init__(item_name)
            self.item_id: "Optional[int]" = None
            self.level: "Optional[int]" = None
            if total_item:
                self.setFlags(self.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled & ~Qt.ItemIsEditable)
            self.last: "Optional[str]" = item_name
            self._item_name: "Optional[str]" = None

        @property
        def item_name(self):
            return self._item_name

        def set_item_name(self, name):
            self._item_name = name

        def parent(self) -> "multi_select_prototype.Item":
            if super().parent() is None:
                return self.model().invisibleRootItem()
            else:
                return super().parent()

    @dataclass
    class Id_name:
        name: "str"
        ID: "int"


class universal_tag_chooser(multi_select_prototype):
    def get_all_items(self) -> 'set[str]':
        return set(mw.col.tags.all())

    def __init__(self, preset: "iter[str]" = None):
        super().__init__(preset)



class tag_chooser_for_cards(universal_tag_chooser):
    def __init__(self, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None):
        super().__init__()
        self.pair_li = pair_li
        self.item_list = self.get_all_tags_from_pairli()
        self.init_data_left()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        s = self.save()
        from . import funcs
        CardId = funcs.CardId
        for pair in self.pair_li:
            note = mw.col.getCard(CardId(pair.int_card_id)).note()
            note.set_tags_from_str(" ".join(s))
            note.flush()
        from . import funcs
        funcs.LinkPoolOperation.both_refresh()



    def add_tag(self, tag_name: str):
        from . import funcs
        CardId = funcs.CardId
        if tag_name is None:
            return
        for pair in self.pair_li:
            note = mw.col.getCard(CardId(pair.int_card_id)).note()
            note.add_tag(tag_name)
            note.flush()

    def get_all_tags_from_pairli(self) -> 'set[str]':
        """多张卡片要取公共的"""
        tags = set()
        for pair in self.pair_li:
            tag = set(mw.col.getCard(pair.int_card_id).note().tags)
            if tags == set():
                tags |= tag
            else:
                tags &= tag
        return tags
        pass


class role_chooser_for_node(multi_select_prototype):

    def closeEvent(self, QCloseEvent):
        左侧表的字符串 = self.save()
        self.结果 = [self.角色表.index(角色名) for 角色名 in 左侧表的字符串 if 角色名 in self.角色表]

    def get_all_items(self) -> 'set[str]':
        return set(self.角色表)

    def __init__(self,preset,角色表:"list[str]"):
        self.角色表 = 角色表
        super().__init__([角色表[pos] for pos in preset if pos in range(len(角色表))],)
        self.left_button_group.left_button.hide()
        self.left_button_group.arrange_button.hide()
        self.right_button_group.arrange_button.hide()
        self.init_data_right()
        self.init_data_left()

class Dialog_PDFUrlTool(QDialog):

    def __init__(self):
        super().__init__()
        self.resize(500, 200)
        self.class_name = G.src.pdfurl_class_name
        layout = QFormLayout(self)
        self.setWindowTitle("PDFUrlTool")
        self.widgets = {
                Translate.pdf路径    : QTextEdit(self),
                Translate.pdf页码    : QSpinBox(self),
                Translate.pdf名字    : QTextEdit(self),
                Translate.pdf默认显示页码: QRadioButton(self),
                Translate.pdf样式    : QTextEdit(self),
                Translate.确定       : QToolButton(self)
        }
        self.widgets[Translate.pdf页码].setRange(0, 99999)
        list(map(lambda items: layout.addRow(items[0], items[1]), self.widgets.items()))
        self.needpaste = False
        self.widgets[Translate.pdf路径].textChanged.connect(lambda: self.on_pdfpath_changed(self.widgets[Translate.pdf路径].toPlainText()))
        self.widgets[Translate.确定].clicked.connect(lambda event: self.on_confirm_clicked())
        self.widgets[Translate.确定].setIcon(QIcon(G.src.ImgDir.correct))
        QShortcut(QKeySequence(Qt.Key_Enter), self).activated.connect(lambda: self.widgets[Translate.确定].click())
        # self.widgets[Translate.确定].clicked.connect()

    def on_pdfpath_changed(self, path):
        text = re.sub("^file:/{2,3}", "", urllib.parse.unquote(path))
        splitresult = re.split("#page=(\d+)$", text)
        if len(splitresult) > 1:
            self.widgets[Translate.pdf页码].setValue(int(splitresult[1]))
        pdffilepath = splitresult[0]
        config: "list" = funcs.PDFLink.GetPathInfoFromPreset(pdffilepath)
        if config is not None:
            pdffilename = config[1]
        else:
            pdffilename = os.path.splitext(os.path.basename(pdffilepath))[0]
        # pdffilename, _ = config[1] if config is not None else os.path.splitext(os.path.basename(pdffilepath))
        self.widgets[Translate.pdf路径].blockSignals(True)
        self.widgets[Translate.pdf路径].setText(pdffilepath)
        self.widgets[Translate.pdf路径].blockSignals(False)
        self.widgets[Translate.pdf名字].setText(pdffilename)

    def get_url_name_num(self) -> tuple[str, str, str]:
        return self.widgets[Translate.pdf路径].toPlainText(), \
               self.widgets[Translate.pdf名字].toPlainText(), \
               self.widgets[Translate.pdf页码].value()

    def on_confirm_clicked(self):
        self.needpaste = True
        clipboard = QApplication.clipboard()
        mmdata = QMimeData()
        pdfurl, pdfname, pdfpage = self.get_url_name_num()
        quote = re.sub(r"\\", "/", pdfurl)
        page_str = self.get_pdf_str(pdfpage) if self.widgets[Translate.pdf默认显示页码].isChecked() else ""
        style = self.widgets[Translate.pdf样式].toPlainText()
        bs = BeautifulSoup("", "html.parser")
        a_tag = bs.new_tag("a", attrs={
                "class": self.class_name,
                "style": style,
                "href" : f"file://{quote}#page={pdfpage}"
        })
        a_tag.string = pdfname + page_str
        mmdata.setHtml(a_tag.__str__())
        mmdata.setText(pdfurl)
        clipboard.setMimeData(mmdata)
        self.close()

    def get_pdf_str(self, page):
        from . import funcs, terms
        s = funcs.Config.get().PDFLink_pagenum_str.value
        return re.sub(f"{{{terms.PDFLink.page}}}", f"{page}", s)


def message_box_for_time_up(seconds):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(f"{seconds} {rosetta('秒')} {rosetta('时间到')},{rosetta('请选择后续操作')}:")
    msgBox.setWindowTitle("time up")
    msgBox.addButton(Translate.取消, QMessageBox.ButtonRole.NoRole)
    msgBox.addButton(Translate.重新计时, QMessageBox.ButtonRole.ResetRole)
    msgBox.addButton(Translate.默认操作, QMessageBox.ButtonRole.AcceptRole)
    msgBox.exec_()
    return msgBox.clickedButton().text()


class ConfigWidget:
    class PDFUrlLinkBooklist(baseClass.ConfigTableView):
        colnames = ["PDFpath", "name", "style", "showPage"]  # 就是表有几个列,分别叫什么
        defaultRowData = ["", "", "", False]

        def NewRow(self):  # 新增一行的函数
            w = self.NewRowFormWidget(self)
            w.widget.exec()
            if w.ok:
                self.AppendRow(w.colItems)
                self.SaveDataToConfigModel()

        def ShowRowEditor(self, row: "list[ConfigWidget.PDFUrlLinkBooklist.TableItem]"):
            w = self.NewRowFormWidget(self, row)
            w.widget.exec()
            if w.ok:
                w.setValueToTableRowFromForm()

        def SaveDataToConfigModel(self):

            newConfigItem = []
            for row in range(self.table_model.rowCount()):
                line = []
                for col in range(4):
                    item: "ConfigWidget.PDFUrlLinkBooklist.TableItem" = self.table_model.item(row, col)
                    if col in range(2):
                        if not re.search("\S", item.text()):
                            break
                        else:
                            line.append(item.text())
                    elif col == 3:
                        line.append(item.text() == "True")
                    else:
                        line.append(item.text())
                if len(line) > 0:
                    newConfigItem.append(line)
            self.ConfigModelItem.setValue(newConfigItem, 需要设值回到组件=False)
            pass

        def GetRowFromData(self, data: "list[str]"):
            # return [for itemname in data]
            return list(map(lambda itemname: ConfigWidget.PDFUrlLinkBooklist.TableItem(self, itemname), data))

        class TableItem(baseClass.ConfigTableView.TableItem):

            def __init__(self, superior, name):
                self.isBool = False
                if type(name) != str:
                    name = str(name)
                    self.isBool = True
                super().__init__(superior, name)
                self.superior: "ConfigWidget.DescExtractPresetTable" = superior

            def ShowAsWidget(self):
                if self.isBool:
                    widget = QRadioButton()
                    widget.setChecked(self.text() == "True")
                else:
                    widget = QTextEdit()
                    widget.setText(self.text())
                return widget

            def GetValue(self):
                return self.text()

            pass

        class NewRowFormWidget(baseClass.ConfigTableNewRowFormView):
            def __init__(self, superior: "ConfigWidget.PDFUrlLinkBooklist", colItems: "list[ConfigWidget.PDFUrlLinkBooklist.TableItem]" = None):
                if not colItems:
                    colItems = funcs.Map.do(superior.defaultRowData, lambda unit: superior.TableItem(superior, unit))
                # self.col0: "QTextEdit" = QTextEdit()
                # self.col1: "QTextEdit" = QTextEdit()
                # self.col2: "QTextEdit" = QTextEdit()
                # self.col3: "QRadioButton" = QRadioButton()
                self.colWidgets = [QTextEdit(),
                                   QTextEdit(),
                                   QTextEdit(),
                                   QRadioButton()]
                self.colItems = colItems
                super().__init__(superior, colItems, self.colWidgets)
                # funcs.Map.do(range(3), lambda idx: self.colWidgets[idx].textChanged.connect(lambda: self.colItems[idx].setText(self.__dict__[idx""].toPlainText())))
                # self.colWidgets[3].clicked.connect(lambda: self.colItems[3].setText(str(self.colWidgets[3].isChecked())))

            def SetupWidget(self):
                self.colWidgets[0].setText(self.colItems[0].text())
                self.colWidgets[1].setText(self.colItems[1].text())
                self.colWidgets[2].setText(self.colItems[2].text())
                self.colWidgets[3].setChecked(self.colItems[3].text() == "True")
                pass

            def SetupEvent(self):
                pass

            def setValueToTableRowFromForm(self):
                self.colItems[0].SetValue(self.colWidgets[0].toPlainText(), self.colWidgets[0].toPlainText())
                self.colItems[1].SetValue(self.colWidgets[1].toPlainText(), self.colWidgets[1].toPlainText())
                self.colItems[2].SetValue(self.colWidgets[2].toPlainText(), self.colWidgets[2].toPlainText())
                self.colItems[3].SetValue(f"{self.colWidgets[3].isChecked()}", self.colWidgets[3].isChecked())

    class DescExtractPresetTable(baseClass.ConfigTableView):
        """
        """

        def __init__(self, *args, **kwargs):
            from . import models
            self.默认属性字典: list[models.类型_属性项_描述提取规则] = []
            super().__init__(*args, **kwargs)
            self.初始化默认行()
            self.table_model.setHorizontalHeaderLabels(self.colnames)

        def 初始化默认行(self):
            from . import models
            默认模型 = models.类型_模型_描述提取规则()
            self.默认属性字典 = 默认模型.获取属性项有序列表_属性字典()

            self.defaultRowData = [(属性.组件显示值, 属性) for 属性 in self.默认属性字典]
            self.colnames = [列[1].展示名 for 列 in self.defaultRowData]
            funcs.Utils.print(self.colnames.__str__())
            return 默认模型

        def GetRowFromData(self, raw_data: "dict"):
            from . import models
            有序属性字典 = models.类型_模型_描述提取规则(数据源=raw_data).获取属性项有序列表_属性字典()
            return [self.TableItem(self, 属性.组件显示值, 属性) for 属性 in 有序属性字典]

        def NewRow(self):
            w = self.NewRowFormWidget(self)
            w.widget.exec()
            if w.ok:
                self.AppendRow(w.colItems)
                self.SaveDataToConfigModel()

        def ShowRowEditor(self, row: "list[ConfigWidget.DescExtractPresetTable.TableItem]"):
            w = self.NewRowFormWidget(self, colItems=row)
            w.widget.exec()
            if w.ok:
                # w.setValueToTableRowFromForm()  # 从新建表单设置回到表格 这一步是不需要的, 在onokclicked上已经完成了
                self.SaveDataToConfigModel()  # 从表格回到配置项

        #
        def SaveDataToConfigModel(self):

            data = []
            for row in range(self.table_model.rowCount()):
                item: ConfigWidget.DescExtractPresetTable.TableItem = self.table_model.item(row, 0)
                data.append(item.GetData().上级.数据源)
            self.ConfigModelItem.setValue(data, 需要设值回到组件=False)
            #     rowdata = []
            #     for col in range(len(self.colnames)):
            #         item: "ConfigWidget.DescExtractPresetTable.TableItem" = self.table_model.item(row, col)
            #         value = item.GetValue()
            #         rowdata.append(value)
            #     data.append(rowdata)
            # self.ConfigModelItem.setValue(data, 需要设值回到组件=False)
            pass

        #
        class TableItem(baseClass.ConfigTableView.TableItem):

            def GetData(self):
                from . import models
                data: models.类型_属性项_描述提取规则 = self.data()
                return data
                pass

            pass

        class NewRowFormWidget(baseClass.ConfigTableNewRowFormView):
            def SetupEvent(self):
                pass

            def SetupWidget(self):
                pass

            def setValueToTableRowFromForm(self):
                if self.isNew:
                    self.模型.数据源 = {}
                    [self.模型.数据源.__setitem__(字段名, 属性.值) for 字段名, 属性 in self.模型.属性字典.items()]
                for 列 in self.colItems:
                    属性项: safe.models.类型_属性项_描述提取规则 = 列.GetData()
                    列.setText(属性项.组件显示值)
                pass

            def __init__(self, 上级: "ConfigWidget.DescExtractPresetTable",
                         colItems: "ConfigWidget.DescExtractPresetTable.TableItem" = None):
                self.isNew = False
                self.superior: ConfigWidget.DescExtractPresetTable = 上级
                if not colItems:
                    self.isNew = True
                    self.模型 = 上级.初始化默认行()
                    colItems = [上级.TableItem(上级, 属性.组件显示值, 属性) for 属性 in 上级.默认属性字典]
                self.模型 = colItems[0].GetData().上级
                self.UI字典 = self.模型.创建UI字典()
                colWidget = [self.UI字典[属性[1].字段名] for 属性 in 上级.defaultRowData]
                super().__init__(上级, colItems, colWidget)
                模板选择组件: "自定义组件.视图结点属性.模板选择" = self.UI字典[self.模型.模板.字段名].核心组件
                字段选择组件: "自定义组件.视图结点属性.字段选择" = self.UI字典[self.模型.字段.字段名].核心组件
                模板选择组件.当完成选择.append(lambda 自己, 值: 字段选择组件.检查模板编号合法性(值))

    class GviewConfigApplyTable(baseClass.ConfigTableView):
        """
        """
        colnames = [译.视图名]
        defaultRowData = [("",)]
        IsList = True

        def NewRow(self):
            w = self.NewRowFormWidget(self)
            w.widget.exec()
            if w.ok and w.判断已选中:
                w.setValueToTableRowFromForm()
                self.AppendRow(w.colItems)
                self.SaveDataToConfigModel()
            pass

        def AppendRow(self, row: "list[baseClass.ConfigTableView.TableItem]"):
            self.table_model.appendRow(row)
            pass

        def ShowRowEditor(self, row: "list[ConfigWidget.GviewConfigApplyTable.TableItem]"):
            w = self.NewRowFormWidget(self, row)
            w.widget.exec()
            if w.ok and w.判断已选中:
                w.setValueToTableRowFromForm()
                self.SaveDataToConfigModel()

        def RemoveRow(self):
            from ..bilink.dialogs.linkdata_grapher import Grapher
            idx = self.viewTable.selectedIndexes()
            if len(idx) == 0:
                return
            取出的项 = self.table_model.takeRow(idx[0].row())[0]
            被删的视图标识: str = 取出的项.data()
            #
            上级的配置模型: "GviewConfigModel" = self.上级.参数模型
            调用者: Grapher.ToolBar = self.上级.调用者
            调用者视图标识 = 调用者.superior.data.gviewdata.uuid
            需要重启 = False
            funcs.GviewConfigOperation.指定视图配置(被删的视图标识)
            self.ConfigModelItem.value.remove(被删的视图标识)
            if 调用者视图标识 == 被删的视图标识:
                需要重启 = True
            if not funcs.objs.Record.GviewConfig.静态_存在于数据库中(上级的配置模型.uuid.value):
                self.上级.参数模型.元信息.确定保存到数据库 = False
                需要重启 = True
                pass
            if 需要重启:
                self.上级.close()
                调用者.openConfig()

        def SaveDataToConfigModel(self):
            """ """
            newConfigItem = []
            for row in range(self.table_model.rowCount()):
                item = self.table_model.item(row, 0)
                newConfigItem.append(item.data())
            self.ConfigModelItem.setValue(newConfigItem, 需要设值回到组件=False)
            pass

        def GetRowFromData(self, data: "list[str]"):
            # return [for itemname in data]
            return list(map(lambda itemname: ConfigWidget.GviewConfigApplyTable.TableItem(self, itemname), data))

        class TableItem(baseClass.ConfigTableView.TableItem):

            def __init__(self, superior: baseClass.ConfigTableNewRowFormView, uuid: "str"):
                """
                uuid: gviewUuid
                """
                from . import funcs
                if uuid == "":
                    name = ""
                else:
                    name = funcs.GviewOperation.load(uuid=uuid).name
                super().__init__(superior, name)

                self.superior: "ConfigWidget.GviewConfigApplyTable" = superior
                self.setData(uuid)

            def GetValue(self):
                return self.text()

            pass

        class NewRowFormWidget(baseClass.ConfigTableNewRowFormView):
            """

            """

            def GetColWidgets(self) -> "list[QWidget]":
                pass

            def SetupWidget(self):
                self.widget.setWindowTitle("choose a graph view")
                self.MakeInnerWidget()
                pass

            def MakeInnerWidget(self):
                """

                """
                B = G.objs.Bricks
                L = self.layout_dict
                layout, widget, kids = B.triple
                tableView: "baseClass.Standard.TableView" = L[kids][1][widget]
                searchStr: "QLineEdit" = L[kids][0][kids][0][widget]
                searchBtn: "QToolButton" = L[kids][0][kids][1][widget]
                searchBtn.setIcon(QIcon(G.src.ImgDir.open))
                searchStr.setPlaceholderText(Translate.由视图名搜索视图)
                return widget

            @property
            def 判断已选中(self):
                B = G.objs.Bricks
                L = self.layout_dict
                layout, widget, kids = B.triple
                tableView: "baseClass.Standard.TableView" = L[kids][1][widget]
                return len(tableView.selectedIndexes()) > 0

            def setValueToTableRowFromForm(self):
                """
                """
                if not self.tableView.selectedIndexes():
                    return

                选中项: "QStandardItem" = self.tableModel.itemFromIndex(self.tableView.selectedIndexes()[0])
                视图名, 视图标识 = 选中项.text(), 选中项.data()

                现配置模型: "configsModel.GviewConfigModel" = self.superior.上级.参数模型
                funcs.GviewConfigOperation.指定视图配置(视图记录=视图标识, 新配置记录=现配置模型.uuid.value)

                视图配置表的项 = self.superior.TableItem(self.superior, 视图标识)
                # 视图配置表的项.setData(视图标识)
                if self.isNew:
                    self.colItems = [视图配置表的项]
                else:
                    self.colItems[0].SetValue(视图名, 视图标识)
                pass

            def __init__(self, superior: "ConfigWidget.GviewConfigApplyTable", colItems: "list[ConfigWidget.GviewConfigApplyTable.TableItem]" = None):
                """处理单行打开的情况"""
                B = G.objs.Bricks
                layout, widget, kids = B.triple
                # if not colItems:
                #     colItems = funcs.Map.do(superior.defaultRowData, lambda data: superior.TableItem(superior, *data))
                self.tableView: "baseClass.Standard.TableView" = baseClass.Standard.TableView(title_name="123")
                self.tableModel: "QStandardItemModel" = funcs.组件定制.模型(["视图名/name of view"])
                self.searchStr: "QLineEdit" = QLineEdit()
                self.searchBtn: "QToolButton" = QToolButton()

                self.layout_dict = {layout: QVBoxLayout(), kids: [
                        {layout: QHBoxLayout(),
                         kids  : [
                                 {widget: self.searchStr},
                                 {widget: self.searchBtn}
                         ]},
                        {widget: self.tableView}
                ]}

                B = G.objs.Bricks
                L = self.layout_dict
                layout, widget, kids = B.triple

                self.layoutTree = self.InitLayout(self.layout_dict)[layout]
                self.containerWidget = QWidget()
                self.containerWidget.setLayout(self.layoutTree)
                self.colWidgets = [self.containerWidget]
                super().__init__(superior, colItems, self.colWidgets)

                self.SetupWidget()
                self.SetupEvent()

                pass

            def SetupEvent(self):
                """

                """

                def onClick(searchString: "str"):
                    if searchString == "" or not re.search(r"\S", searchString):
                        模糊搜索得到的视图表 = funcs.GviewOperation.load_all()
                    else:
                        关键词正则 = re.sub(r"\s", ".*", searchString)
                        DB, Logic = G.DB, G.objs.Logic
                        DB.go(DB.table_Gview)
                        模糊搜索得到的视图表 = DB.select(Logic.REGEX("name", 关键词正则)).return_all().zip_up().to_gview_record()
                    self.tableModel = funcs.组件定制.模型(["视图名/name of view"])
                    采用本配置的视图表 = self.superior.ConfigModelItem.value
                    [self.tableModel.appendRow([baseClass.Standard.Item(视图数据.name, data=视图数据.uuid)]) for 视图数据 in 模糊搜索得到的视图表 if 视图数据.uuid not in 采用本配置的视图表]
                    self.tableView.setModel(self.tableModel)

                self.tableView.setModel(self.tableModel)

                self.searchBtn.clicked.connect(lambda: onClick(self.searchStr.text()))
                # self.containerWidget.show()
                pass

    class GroupReviewConditionList(baseClass.ConfigTableView):
        """"""
        colnames = ["searchString"]
        IsList = True
        defaultRowData = [("",)]

        def NewRow(self):
            w = self.NewRowFormWidget(self)
            w.widget.exec()
            if w.ok:
                self.AppendRow(w.colItems)
                self.SaveDataToConfigModel()
            pass

        def ShowRowEditor(self, row: "list[baseClass.ConfigTableView.TableItem]"):
            w = self.NewRowFormWidget(self, row)
            w.widget.exec()
            if w.ok:
                self.SaveDataToConfigModel()
            pass

        def SaveDataToConfigModel(self):
            v = []
            [v.append(self.table_model.item(i, 0).text()) for i in range(self.table_model.rowCount())]
            self.ConfigModelItem.setValue(v, 需要设值回到组件=False)
            pass

        class NewRowFormWidget(baseClass.ConfigTableNewRowFormView):
            """输入文本即可,如果是gview开头则要检查是否存在"""

            def __init__(self, superior: "ConfigWidget.GroupReviewConditionList", colItems: "list[ConfigWidget.GroupReviewConditionList.TableItem]" = None):
                """注意,defaultRowData需要考虑superior.TableItem(superior, data)载入是否正确
                """
                self.col0: "QTextEdit" = QTextEdit()  # self.colWidgets[0]
                self.colWidgets = [QTextEdit()]
                super().__init__(superior, colItems)

            def SetupWidget(self):
                self.colWidgets[0].setText(self.colItems[0].text())
                pass

            def setValueToTableRowFromForm(self):
                self.colItems[0].SetValue(self.colWidgets[0].toPlainText(), self.colWidgets[0].toPlainText())
                pass

            def SetupEvent(self):
                pass

        class TableItem(baseClass.ConfigTableView.TableItem):

            def __init__(self, superior, name):
                self.isBool = False
                if type(name) != str:
                    name = str(name)
                    self.isBool = True
                super().__init__(superior, name)
                self.superior: "ConfigWidget.GroupReviewConditionList" = superior

            def ShowAsWidget(self):
                if self.isBool:
                    widget = QRadioButton()
                    widget.setChecked(self.text() == "True")
                else:
                    widget = QTextEdit()
                    widget.setText(self.text())
                return widget

            def GetValue(self):
                return self.text()

            pass

    class GviewConfigNodeFilter(baseClass.配置项单选型表格组件):
        """
        结点筛选器, 表格每一行对应一个筛选器,
        条件|选中
        """
        colnames = [译.选中, 译.过滤表达式]
        defaultRowData = ["", ""]

        def NewRowFormWidget(self, 上级, 行: "list[baseClass.ConfigTableView.TableItem]" = None, *args, **kwargs):
            说明 = 译.例子_结点过滤 + "\n" + funcs.GviewConfigOperation.获取eval可用变量与函数的说明()

            class edit_widget(baseClass.组件_表格型配置项_列编辑器_可执行字符串):
                def on_test(self):
                    # noinspection PyBroadException
                    try:
                        strings = self.布局[子代][0][组件].toPlainText()
                        literal = eval(strings, *funcs.GviewConfigOperation.获取eval可用变量与函数())

                        if type(literal) != bool:
                            self.设置说明栏("type error:" + 译.可执行字符串表达式的返回值必须是布尔类型)
                            return False
                        else:
                            self.设置说明栏("ok")
                            return True
                    except Exception as err:
                        self.设置说明栏("syntax error:" + err.__str__())
                        return False
                    pass

            return edit_widget(上级, 行, 说明)

    class GviewConfigCascadingSorter(baseClass.配置项单选型表格组件):
        colnames = [译.选中, 译.多级排序依据]
        defaultRowData = ["", ""]

        def NewRowFormWidget(self, 上级, 行: "list[baseClass.ConfigTableView.TableItem]" = None, *args, **kwargs):
            说明 = 译.例子_多级排序 + "\n" + funcs.GviewConfigOperation.获取eval可用变量与函数的说明()

            class edit_widget(baseClass.组件_表格型配置项_列编辑器_可执行字符串):
                def on_test(self):
                    _ = baseClass.枚举命名
                    locals_dict = funcs.GviewConfigOperation.获取eval可用字面量()

                    try:
                        strings = self.布局[子代][0][组件].toPlainText()
                        literal = eval(strings, {}, {**locals_dict, _.上升: _.上升, _.下降: _.下降})

                        if type(literal) != list:
                            self.设置说明栏("type error:" + 译.可执行字符串表达式的返回值必须是列表类型)
                            return False
                        elif len([tup for tup in literal if len(tup) != 2]) > 0:
                            self.设置说明栏("type error:" + 译.可执行字符串_必须是一个二元元组)
                            return False
                        elif len([tup for tup in literal if not (tup[0] in locals_dict and tup[1] in [_.上升, _.下降])]) > 0:
                            self.设置说明栏("type error:" + 译.可执行字符串_二元组中的变量名必须是指定名称)
                            return False
                        else:
                            self.设置说明栏("ok")
                            return True
                    except Exception as err:
                        self.设置说明栏("syntax error:" + err.__str__())
                        return False
                    pass

            return edit_widget(上级, 行, 说明)

    class GviewConfigWeightedSorter(baseClass.配置项单选型表格组件):
        colnames = [译.选中, 译.加权公式]
        defaultRowData = ["", ""]

        def NewRowFormWidget(self, 上级, 行: "list[baseClass.ConfigTableView.TableItem]" = None, *args, **kwargs):
            说明 = 译.例子_加权排序 + "\n" + funcs.GviewConfigOperation.获取eval可用变量与函数的说明()

            class edit_widget(baseClass.组件_表格型配置项_列编辑器_可执行字符串):
                def on_test(self):
                    globals_dict, locals_dict = funcs.GviewConfigOperation.获取eval可用变量与函数()
                    try:
                        strings = self.布局[子代][0][组件].toPlainText()
                        literal = eval(strings, globals_dict, locals_dict)
                        if type(literal) not in (int, float):
                            self.设置说明栏(译.可执行字符串_返回的值必须是数值类型)
                            return False
                        else:
                            self.设置说明栏("ok")
                            return True
                    except Exception as err:
                        self.设置说明栏("syntax error:" + err.__str__())
                        return False

            return edit_widget(上级, 行, 说明)

    class GviewNodeProperty(QDialog):
        class Enum:
            QLabel = "QLabel"
            QTextEdit = "QTextEdit"
            QRadioButton = "QRadioButton"
            QSlider = "QSlider"
            QCheckBox = "QCheckBox"
            QComboBox = "QComboBox"

        def node_property(self):

            pass

        def __init__(self, gview_data=None, node_uuid=None, superior=None):
            super().__init__()
            from ..bilink.dialogs.linkdata_grapher import Grapher
            self.superior: Grapher = superior
            self.major_layout = QFormLayout()
            self.gview_data: funcs.GViewData = gview_data
            self.node_uuid: str = node_uuid
            self.btn_ok = QPushButton(QIcon(G.src.ImgDir.correct), "")
            self.btn_ok.clicked.connect(self.save_quit)
            _ = ConfigWidget.GviewNodeProperty.Enum
            __ = baseClass.枚举命名
            self.prop_dict: "dict[str,dict]" = {  # 组件名:属性名:组件实例对象
                    _.QRadioButton: {__.结点.需要复习: QRadioButton(),
                                     __.结点.必须复习: QRadioButton(),
                                     __.结点.漫游起点: QRadioButton(),
                                     __.结点.主要结点: QRadioButton()},
                    _.QTextEdit   : {__.结点.描述: QTextEdit()},
                    _.QComboBox   : {__.结点.角色: {
                            __.结点.数据源: funcs.GviewConfigOperation.获取结点角色数据源(gview_data=self.gview_data),
                            __.组件    : QComboBox()

                    }},
                    _.QSlider     : {__.结点.优先级: {
                            __.范围: [-100, 100],
                            __.组件: QSlider()
                    }},
                    _.QLabel      : {__.结点.数据类型: QLabel(),
                                     __.结点.位置  : QLabel(),
                                     __.结点.上次编辑: QLabel(),
                                     __.结点.上次访问: QLabel(),
                                     __.结点.访问次数: QLabel(),
                                     __.结点.出度  : QLabel(),
                                     __.结点.入度  : QLabel(),
                                     }
            }
            node_data = self.gview_data.nodes[self.node_uuid]
            for w in self.prop_dict.keys():
                if w == _.QRadioButton:
                    for name in self.prop_dict[w].keys():
                        widget: QRadioButton = self.prop_dict[w][name]
                        widget.setChecked(node_data[name].值)
                        self.major_layout.addRow(name, widget)
                elif w == _.QTextEdit:
                    for name in self.prop_dict[w].keys():
                        widget: QTextEdit = self.prop_dict[w][name]
                        widget.setText(funcs.GviewOperation.获取视图结点描述(self.gview_data, self.node_uuid))
                        self.major_layout.addRow(name, widget)
                elif w == _.QComboBox:
                    for name in self.prop_dict[w].keys():
                        widget: QComboBox = self.prop_dict[w][name][__.组件]
                        data_source: list[str] = self.prop_dict[w][name][__.视图配置.结点角色表]
                        saved_value = node_data[name]

                        for idx in range(len(data_source)):
                            widget.addItem(data_source[idx], idx)
                        saved_value_idx = widget.findData(saved_value)
                        widget.addItem(QIcon(G.src.ImgDir.cancel), "", -1)
                        widget.setCurrentIndex(saved_value_idx if saved_value_idx != -1 else len(data_source))
                        self.major_layout.addRow(name, widget)
                elif w == _.QSlider:
                    for name in self.prop_dict[w].keys():
                        widget_QSlider: QSlider = self.prop_dict[w][name][__.组件]
                        data_range = self.prop_dict[w][name][__.范围]
                        saved_value = node_data[name]
                        widget_QSlider.setRange(data_range[0], data_range[1])
                        widget_QSlider.setValue(saved_value)
                        widget_QSlider.setToolTip(saved_value.__str__())
                        widget_QSlider.valueChanged.connect(lambda: widget_QSlider.setToolTip(widget_QSlider.value().__str__()))
                        self.major_layout.addRow(name, widget_QSlider)
                elif w == _.QLabel:
                    for name in self.prop_dict[w].keys():
                        widget: QLabel = self.prop_dict[w][name]
                        saved_value = node_data[name] if name in node_data else ""
                        if name in [__.结点.上次编辑, __.结点.上次访问]:
                            widget.setText(funcs.Utils.时间戳转日期(saved_value).__str__())
                        else:
                            widget.setText(saved_value.__str__())
                        self.major_layout.addRow(name, widget)
            self.major_layout.addRow("", self.btn_ok)
            self.setLayout(self.major_layout)

        def save_quit(self):
            _ = ConfigWidget.GviewNodeProperty.Enum
            __ = baseClass.枚举命名
            node_data = self.gview_data.nodes[self.node_uuid]
            for widget_type in self.prop_dict.keys():
                if widget_type == _.QRadioButton:
                    for name in self.prop_dict[widget_type].keys():
                        widget: QRadioButton = self.prop_dict[widget_type][name]
                        node_data[name] = widget.isChecked()
                elif widget_type == _.QSlider:
                    for name in self.prop_dict[widget_type].keys():
                        widget: QSlider = self.prop_dict[widget_type][name][__.组件]
                        node_data[name] = widget.value()
                elif widget_type == _.QComboBox:
                    for name in self.prop_dict[widget_type].keys():
                        widget: QComboBox = self.prop_dict[widget_type][name][__.组件]
                        node_data[name] = widget.currentData()
                elif widget_type == _.QTextEdit:
                    for name in self.prop_dict[widget_type].keys():
                        widget: QTextEdit = self.prop_dict[widget_type][name]
                        funcs.GviewOperation.设定视图结点描述(self.gview_data, self.node_uuid, widget.toPlainText())

            self.close()
            pass

        def save(self):

            pass

    class GviewConfigNodeRoleEnumEditor(baseClass.ConfigItemLabelView):
        """
        以不可编辑的label形式展示文本, 如果需要编辑, 点击按钮弹出特定的编辑器进行编辑
        这样做的目的是为了对编辑内容进行检测.
        """

        class 角色枚举编辑器(baseClass.可执行字符串编辑组件):

            def 设置当前配置项对应展示组件的值(self, value):
                """此处无用"""
                pass

            def __init__(self, 文本):
                super().__init__(文本)
                # self.布局[子代][2][组件].setText(译.说明_结点角色枚举)

            def on_help(self):
                self.设置说明栏(译.说明_结点角色枚举)

            def on_test(self):
                # noinspection PyBroadException
                try:
                    strings = self.布局[子代][0][组件].toPlainText()
                    literal = literal_eval(strings)
                    if type(literal) != list:
                        self.设置说明栏("type error:input must be a list")
                        return False
                    elif [i for i in literal if type(i) != str]:
                        self.设置说明栏("type error:every element of the list must be string")
                        return False
                    elif len(literal)!= len(set(literal)):
                        self.设置说明栏("value error:every element must be unique")
                    else:
                        self.设置说明栏("ok")
                        return True
                except Exception as err:
                    self.设置说明栏("syntax error:" + err.__str__())
                    return False

                #

                pass

            def on_ok(self):
                if self.on_test():
                    self.ok = True
                    self.合法字符串 = self.布局[子代][0][组件].toPlainText()
                    self.close()

                pass

        def on_edit_btn_clicked(self):
            w = self.角色枚举编辑器(self.label.text())
            w.exec()
            if w.ok:
                self.ConfigModelItem.setValue(w.合法字符串)

            pass

    class GviewConfigDeckChooser(baseClass.ConfigItemLabelView):

        def on_edit_btn_clicked(self):

            w = universal_deck_chooser()
            w.exec()
            self.ConfigModelItem.setValue(w.结果)
            pass

        def SetupData(self, raw_data):
            if raw_data != -1:
                self.label.setText(mw.col.decks.name(raw_data))
            else:
                self.label.setText("no default deck")
            pass

    class GlobalConfigDefaultViewChooser(baseClass.ConfigItemLabelView):
        """默认视图用的他"""

        def on_edit_btn_clicked(self):

            w = view_chooser()
            w.exec()
            self.SetupData(w.编号)
            self.ConfigModelItem.value = w.编号
            pass

        def SetupData(self, raw_data):
            if raw_data != -1:
                self.label.setText(funcs.GviewOperation.load(raw_data).name)
            else:
                self.label.setText("no default view")
            pass


class ReviewButtonForCardPreviewer:
    def __init__(self, papa, layout: "QGridLayout"):
        from . import hookers
        from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewer
        self.papa: "SingleCardPreviewer" = papa
        self.ease_button: "dict[int,QPushButton]" = {}
        self.review_buttons = self._create_review_buttons()
        self.due_info = self._create_due_info_widget()
        self.当完成复习 = hookers.当ReviewButtonForCardPreviewer完成复习()
        layout.addWidget(self.due_info, 0, 0, 1, 1)
        self.initEvent()

    def initEvent(self):
        G.signals.on_card_answerd.connect(self.handle_on_card_answerd)

        pass

    def handle_on_card_answerd(self, answer: "configsModel.AnswerInfoInterface"):
        # from ..bilink.dialogs.linkdata_grapher import GrapherRoamingPreviewer
        #
        # notself, equalId, isRoaming = answer.platform != self, answer.card_id == self.card().id, isinstance(self.papa.superior, GrapherRoamingPreviewer)
        # # print(f"handle_on_card_answerd,{notself},{equalId},{isRoaming}")
        # if notself and equalId and isRoaming:
        #     # print("handle_on_card_answerd>if>ok")
        #     self.papa.superior.nextCard()
        pass

    def card(self):
        return self.papa.card()

    def _create_review_buttons(self):
        enum = ["", "again", "hard", "good", "easy"]
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        sched = mw.col.sched

        button_num = sched.answerButtons(self.card())
        for i in range(button_num):
            ease = enum[i + 1] + ":" + sched.nextIvlStr(self.card(), i + 1)
            self.ease_button[i + 1] = QPushButton(ease)
            answer = lambda j: lambda: self._answerCard(j + 1)
            self.ease_button[i + 1].clicked.connect(answer(i))
            layout.addWidget(self.ease_button[i + 1])
        widget.setLayout(layout)
        return widget

    def _create_due_info_widget(self):
        """due info 包括
        1 label显示复习状态
        2 button点击开始复习(button根据到期情况,显示不同的提示文字)
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        widget.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.due_label = QLabel()
        self._setDueInfo()
        layout.addWidget(self.due_label)
        layout.addWidget(self.review_buttons)
        widget.setLayout(layout)
        return widget

    def _setDueInfo(self):
        now = datetime.now()
        lastDate, nextDate = self.realDue()
        due = now >= nextDate
        self.due_label.setText((f"{Translate.可复习}" if due else f"{Translate.未到期}") + f"\n{nextDate}"[:-10])
        self.due_label.setStyleSheet("background-color:" + ("red" if due else "green") + f";color:white")

    def realDue(self):
        # 由于card.due落后,所以直接从数据库去取
        """由于 card.due受各种因素影响, 因此 他不能被正确地记录, 因此我需要用别的东西来替代."""

        return funcs.CardOperation.getLastNextRev(self.card().id)

    def _answerCard(self, ease):
        say = rosetta

        sched = mw.col.sched
        signals = G.signals
        answer = configsModel.AnswerInfoInterface

        if self.card().timer_started is None:
            self.card().timer_started = time.time() - 60
        funcs.CardOperation.answer_card(self.card(), ease)
        # self.switch_to_due_info_widget()
        funcs.LinkPoolOperation.both_refresh()
        mw.col.reset()
        G.signals.on_card_answerd.emit(
                answer(platform=self, card_id=self.card().id, option_num=ease))
        self.update_info()
        self.当完成复习(self.card().id, ease, self.papa)

    def update_info(self):
        self._update_answer_buttons()
        self._update_due_info_widget()

    def _update_answer_buttons(self):
        enum = ["", "again", "hard", "good", "easy"]
        sched = mw.col.sched
        button_num = sched.answerButtons(self.card())
        for i in range(button_num):
            ease = enum[i + 1] + ":" + sched.nextIvlStr(self.card(), i + 1)
            self.ease_button[i + 1].setText(ease)

    def _update_due_info_widget(self):
        self._setDueInfo()

    def ifNeedFreeze(self):
        cfg = funcs.Config.get()
        if cfg.freeze_review.value:
            interval = cfg.freeze_review_interval.value
            self.freeze_answer_buttons()
            QTimer.singleShot(interval, lambda: self.recover_answer_buttons())

    def freeze_answer_buttons(self):
        for button in self.ease_button.values():
            button.setEnabled(False)
        tooltip(Translate.已冻结)

    def recover_answer_buttons(self):
        for button in self.ease_button.values():
            button.setEnabled(True)
        tooltip(Translate.已解冻)


class 自定义组件:
    class 视图结点属性:
        class 基类_项组件基础(QWidget):
            def __init__(self, 上级):
                super().__init__()
                from . import models
                self.上级: models.函数库_UI生成.组件 = 上级

            @abc.abstractmethod
            def setValue(self, value):
                raise NotImplementedError()
        class 基本选择类(基类_项组件基础):
            def __init__(self, 上级):
                super().__init__(上级)

                self.ui组件 = funcs.组件定制.文本框(开启自动换行=True)
                self.修改按钮 = funcs.组件定制.按钮_修改()
                self.修改按钮.clicked.connect(self.on_edit_button_clicked)
                self.当完成选择 = hookers.当全局配置_描述提取规则_模板选择器完成选择()
                funcs.组件定制.组件组合({框: QHBoxLayout(), 子: [
                        {件: self.ui组件, 占: 1}, {件: self.修改按钮, 占: 0}]},
                                self)
                self.ui组件.setText(self.get_name(self.上级.数据源.值))
                self.不选信息 = 译.不选等于全选

            def on_edit_button_clicked(self):
                w = self.chooser()
                w.exec()
                if (type(w.结果) in [int, float] and w.结果 < 0) or \
                        (type(w.结果) == list and len(w.结果) == 0):
                    showInfo(self.不选信息)

                self.setValue(w.结果)

            def setValue(self, value):
                self.ui组件.setText(self.get_name(value))
                self.上级.数据源.设值(value)
                self.当完成选择(self, value)
                pass

            def chooser(self): raise NotImplementedError()  # """打开某一种选择器"""

            def get_name(self, value): raise NotImplementedError()

        class 角色多选(基本选择类):
            """卡片角色多选"""
            def __init__(self,上级):
                super().__init__(上级)
                self.属性项: "safe.models.类型_视图结点属性项" = self.上级.数据源
                self.配置模型 = self.属性项.上级.数据源.模型.上级.config_model
                self.角色表 = eval(self.配置模型.data.node_role_list.value)
                self.值修正()
                self.不选信息 = 译.不选角色等于不选

            def 值修正(self):
                角色选中表:'list[str]' = self.属性项.值
                新表 = [角色 for 角色 in 角色选中表 if 角色 not in range(len(self.角色表))]
                self.属性项.设值(新表)

            def chooser(self):
                """需要获取到config,所以需要获取到view uuid"""
                return role_chooser_for_node(self.属性项.值,self.角色表)
                pass

            def get_name(self, value):
                return funcs2.逻辑.缺省值(value, lambda x: [self.角色表[idx] for idx in x if idx in range(len(self.角色表))],
                                     f"<img src='{funcs.G.src.ImgDir.cancel}' width=10 height=10> no role").__str__()



        class 牌组选择(基本选择类):

            def chooser(self): return universal_deck_chooser()

            def get_name(self, value): return mw.col.decks.name_if_exists(value) if value > 0 else "ALL DECKS"

            # def __init__(self, 上级):
            #     super().__init__(上级)
            #     self.ui组件.setText(self.get_name(self.上级.数据源.值))

        class 模板选择(基本选择类):

            def get_name(self, value): return mw.col.models.get(value)["name"] if value > 0 else "ALL TEMPLATES"

            def chooser(self): return universal_template_chooser()

            # def __init__(self, 上级):
            #     super().__init__(上级)
            #     self.ui组件.setText(self.get_name(self.上级.数据源.值))

        class 字段选择(基本选择类):
            def __init__(self, 上级, 模板编号):
                self.模板编号 = -1
                super().__init__(上级)
                self.检查模板编号合法性(模板编号)

            def 检查模板编号合法性(self, value):
                self.模板编号 = value
                if self.模板编号 < 0:
                    self.修改按钮.setEnabled(False)
                else:
                    self.修改按钮.setEnabled(True)
                self.ui组件.setText(self.get_name(self.上级.数据源.值))

            def chooser(self):
                return universal_field_chooser(self.模板编号)

            def get_name(self, value):
                return funcs.卡片字段操作.获取字段名(self.模板编号, value, "ALL FIELDS")

        class 标签选择(基本选择类):
            def chooser(self):
                return universal_tag_chooser(self.上级.数据源.值)
                pass

            def get_name(self, value):
                return funcs2.逻辑.缺省值(value, lambda x: x, "ALL TAGS").__str__()
                # if len(value)==0:
                #     return "ALL TAGS"
                # return value.__str__()
                # pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = tag_chooser_for_cards()
    f.show()
    sys.exit(app.exec_())
