# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'mywidgets.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/1 16:48'
"""
import math
import os
import re
import urllib
from abc import ABC

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
from . import funcs, baseClass

布局 = 0
组件 = 1
子代 = 2
# from ..bilink.dialogs.linkdata_grapher import Grapher

if __name__ == "__main__":
    from lib.common_tools import G
else:
    from . import G

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *

译 = Translate


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


class deck_chooser(QDialog):

    def __init__(self, pair_li: "list[G.objs.LinkDataPair]" = None, fromview=None):
        super().__init__()
        self.fromview = fromview
        self.pair_li = pair_li
        self.view = QTreeView(self)
        self.model = QStandardItemModel(self)
        self.model_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.header = self.Header(self, deckname=self.curr_deck_name)
        self.header.button.clicked.connect(self.on_header_button_clicked_handle)
        self.header.new_dec_button.clicked.connect(self.on_header_new_dec_button_clicked_handle)
        self.view.clicked.connect(self.on_view_clicked_handle)
        self.view.doubleClicked.connect(self.on_view_doubleclicked_handle)
        self.model.dataChanged.connect(self.on_model_data_changed_handle)
        self.init_UI()
        self.init_model()

    def on_header_new_dec_button_clicked_handle(self):
        new_item = self.Item(f"""new_deck_{datetime.now().strftime("%Y%m%d%H%M%S")}""")
        if self.view.selectedIndexes():
            item: "deck_chooser.Item" = self.model.itemFromIndex(self.view.selectedIndexes()[0])
            parent_item = item.parent()
        else:
            parent_item = self.model.invisibleRootItem()
        parent_item.appendRow([new_item])
        self.view.edit(new_item.index())
        deck = mw.col.decks.add_normal_deck_with_name(self.get_full_deck_name(new_item))
        new_item.deck_id = deck.id

    def on_view_doubleclicked_handle(self, index):
        self.on_item_button_clicked_handle(self.model.itemFromIndex(index))

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

    def on_item_button_clicked_handle(self, item: "deck_chooser.Item"):
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
                          deck_id=DeckId(item.deck_id)).run_in_background()
        browser.showMinimized()
        from ..bilink.dialogs.linkdata_grapher import Grapher
        if isinstance(self.fromview, AnkiWebView):
            parent: "Union[Previewer,Reviewer]" = self.fromview.parent()
            parent.activateWindow()
        elif isinstance(self.fromview, Grapher):
            self.fromview.activateWindow()
        QTimer.singleShot(100, funcs.LinkPoolOperation.both_refresh)
        # QTimer.singleShot(100, lambda: funcs.BrowserOperation.search(f"""deck:{self.get_full_deck_name(item)}"""))
        self.close()

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        item: "deck_chooser.Item" = self.model.itemFromIndex(topLeft)
        from . import funcs
        DeckId = funcs.Compatible.DeckId()
        new_deck_name = self.get_full_deck_name(item)
        mw.col.decks.rename(DeckId(item.deck_id), new_deck_name)
        # print(item.deck_name)

    def on_view_clicked_handle(self, index):
        item: deck_chooser.Item = self.model.itemFromIndex(index)
        # tooltip(self.get_full_deck_name(item))

    def on_header_button_clicked_handle(self):
        if self.header.button.text() == self.header.deck_tree:
            self.header.button.setText(self.header.deck_list)
            self.header.button.setIcon(QIcon(G.src.ImgDir.list))
        else:
            self.header.button.setText(self.header.deck_tree)
            self.header.button.setIcon(QIcon(G.src.ImgDir.tree))
        self.init_data()

    def init_model(self):
        self.view.setModel(self.model)
        self.model.setHorizontalHeaderLabels(["deckname"])
        self.view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.init_data()
        self.view.setColumnWidth(1, 30)

    def init_data(self):
        self.model.clear()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model.setHorizontalHeaderLabels(["deckname"])
        if self.header.button.text() == self.Header.deck_tree:
            self.build_deck_tree()
        else:
            self.build_deck_list()
        self.view.expandAll()

    def build_deck_list(self):
        deck_li: "list[deck_chooser.Id_deck]" = self.get_all_decks()
        for i in deck_li:
            item = self.Item(i.deck)
            item.deck_id = i.ID
            self.model.appendRow([item])
        pass

    def build_deck_tree(self):
        deck_li: "list[deck_chooser.Id_deck]" = self.get_all_decks()
        deck_dict = G.objs.Struct.TreeNode(self.model_rootNode, {})
        for i in deck_li:
            deckname_li = i.deck.split("::")
            parent = deck_dict
            while deckname_li:
                deckname = deckname_li.pop(0)
                if deckname not in parent.children:
                    item = self.Item(deckname)
                    parent.item.appendRow([item])
                    parent.children[deckname] = G.objs.Struct.TreeNode(item, {})
                    if not deckname_li:
                        item.deck_id = i.ID
                parent = parent.children[deckname]

    def get_full_deck_name(self, item: "deck_chooser.Item"):
        if self.header.button.text() == self.header.deck_list:
            return item.text()
        s = ""
        parent = item
        while parent != self.model.invisibleRootItem():
            s = "::" + parent.deck_name + s
            parent = parent.parent()
        s = s[2:]
        return s

    def get_all_decks(self):
        if __name__ == "__main__":
            return [self.Id_deck(*i) for i in [
                    ['0总库', 1601526645310],
                    ['0活动', 1602850575642],
                    ['0活动::0dailynotes', 1604795557392],
                    ['0活动::0dailynotes::0文章', 1607826406813],
                    ['0活动::0dailynotes::1随记', 1607828983488],
                    ['0活动::1短期组', 1604795498696],
                    ['0活动::2中期组', 1604795524293],
                    ['0活动::3长期组', 1604795533215],
                    ['0活动::4手机组', 1605919084022],
                    ['PDF Review', 1610961897321],
                    ['废堆', 1602984243504],
                    ['测试用', 1608350433000],
                    ['睡眠组', 1604795430927],
                    ['老友记 Friends', 1610645864792],
                    ['老友记 Friends::Season 01', 1610645864791],
                    ['老友记 Friends::Season 01::Episode 01', 1610645864793],
                    ['考研词汇5500', 1610646719431],
                    ['考研词汇5500::3 Dictation', 1610646719432],
                    ['默认', 1]
            ]
                    ]
        else:
            decks = mw.col.decks
            return [self.Id_deck(deck=i.name, ID=i.id) for i in decks.all_names_and_ids() if
                    not decks.is_filtered(i.id)]

    def init_UI(self):
        self.setWindowTitle("deck_chooser")
        self.setWindowIcon(QIcon(G.src.ImgDir.box))
        self.view.setIndentation(8)
        V_layout = QVBoxLayout(self)
        V_layout.addWidget(self.header)
        V_layout.addWidget(self.view)
        V_layout.addWidget(QLabel(译.双击牌组即可修改卡片所属牌组),stretch=0)
        V_layout.setStretch(1, 1)
        V_layout.setStretch(0, 0)
        self.setLayout(V_layout)

    class Header(QWidget):
        deck_tree, deck_list = "deck_tree", "deck_list"

        def __init__(self, parent, deckname="test::test"):
            super().__init__(parent)
            self.desc = QLabel("current deck|   " + deckname, self)
            self.desc.setWordWrap(True)
            self.button = QToolButton(self)
            self.button.setText(self.deck_tree)
            self.button.setIcon(QIcon(G.src.ImgDir.tree))
            self.new_dec_button = QToolButton(self)
            self.new_dec_button.setIcon(QIcon(G.src.ImgDir.item_plus))
            H_layout = QHBoxLayout(self)
            H_layout.addWidget(self.desc)
            H_layout.addWidget(self.new_dec_button)
            H_layout.addWidget(self.button)
            H_layout.setStretch(0, 1)
            H_layout.setStretch(1, 0)
            self.setLayout(H_layout)

    class Item(QStandardItem):
        def __init__(self, deck_name):
            super().__init__(deck_name)
            self.deck_id: "Optional[int]" = None
            self.level: "Optional[int]" = None
            self.setFlags(self.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)

        @property
        def deck_name(self):
            return self.text()

        def parent(self) -> "deck_chooser.Item":
            parent = super().parent()
            if parent:
                return parent
            else:
                return self.model().invisibleRootItem()

    @dataclass
    class Id_deck:
        deck: "str"
        ID: "int"


class tag_chooser(QDialog):
    """添加后需要更新内容, 用 init_data_left方法"""

    def __init__(self, pair_li: "Optional[list[G.objs.LinkDataPair]]" = None):
        super().__init__()
        self.pair_li = pair_li
        self.view_left = self.View(self)
        self.view_right = self.View(self)
        self.view_left.setContextMenuPolicy(Qt.CustomContextMenu)
        self.model_left = QStandardItemModel(self)
        self.model_right = QStandardItemModel(self)
        self.model_right_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.model_left_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.tag_list = self.get_all_tags_from_pairli()
        self.left_button_group = self.button_group(self, 0, self.view_left, self.model_left)
        self.right_button_group = self.button_group(self, 1, self.view_right, self.model_right)
        self.init_UI()
        self.init_model()
        self.allevent = G.objs.AllEventAdmin([
                [self.model_left.dataChanged, self.on_model_left_datachanged_handle],
                [self.view_right.doubleClicked, self.on_view_right_doubleClicked_handle],
                # [self.view_left.customContextMenuRequested, self.on_view_show_context_menu]
        ]).bind()

    # def on_view_show_context_menu(self, pos: QtCore.QPoint):
    #     selected_items: "list[tag_chooser.Item]" = [ self.model_left.itemFromIndex(idx) for idx in  self.view_left.selectedIndexes()]
    #     selected_item = selected_items[0] if len(selected_items) > 0 else None
    #
    #     def add_syncReview_tag(item: 'Optional[tag_chooser.Item]'):
    #         tag_name = item.tag_name if item is not None else ""
    #         tag_name = "::".join(tag_name.split("::")[2:]) if  "hjp-bilink" in tag_name.split("::") else tag_name
    #         new_tag_name = G.src.autoreview_header + tag_name
    #         self.left_button_group.on_card_tag_new_handle(tag_name=new_tag_name,from_posi=self.model_left)
    #
    #     menu = self.view_left.contextMenu = QMenu()
    #     menu.addAction(Translate.添加同步复习标签).triggered.connect(lambda: add_syncReview_tag(selected_item))
    #     menu.popup(QCursor.pos())
    #     menu.show()

    def on_view_right_doubleClicked_handle(self, index):
        self.right_button_group.on_collection_tag_add_handle()

    def on_model_left_datachanged_handle(self, index):
        item: "tag_chooser.Item" = self.model_left.itemFromIndex(index)
        stack: "list[tag_chooser.Item]" = [item]
        while stack:
            it = stack.pop()
            if it.tag_name is not None:
                old = it.tag_name
                new = self.get_full_tag_name(it)
                self.tag_list.remove(old)
                self.tag_list.add(new)
                it.set_tag_name(new)
            for i in range(it.rowCount()):
                stack.append(it.child(i, 0))
        self.init_data_left()

    def init_UI(self):
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("tag chooser")
        self.setWindowIcon(QIcon(G.src.ImgDir.tag))
        h_box = QHBoxLayout(self)
        v1 = QVBoxLayout()
        v2 = QVBoxLayout()
        v1.addWidget(self.view_left)
        v1.addWidget(self.left_button_group)
        v2.addWidget(self.view_right)
        v2.addWidget(self.right_button_group)
        h_box.addLayout(v1)
        h_box.addLayout(v2)
        self.setLayout(h_box)
        pass

    def init_model(self):
        self.view_left.setModel(self.model_left)
        self.view_right.setModel(self.model_right)
        self.view_left.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view_right.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.init_data_left(init=True)
        self.init_data_right()

        pass

    def reject(self) -> None:
        self.close()
        super().reject()

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

    def save(self):
        stack: "list[tag_chooser.Item]" = [self.model_left.item(i, 0) for i in range(self.model_left.rowCount())]
        s = set()
        while stack:
            item = stack.pop()
            if item.tag_name:
                s.add(self.get_full_tag_name(item))
            for i in range(item.rowCount()):
                stack.append(item.child(i, 0))
        return s

    def get_full_tag_name(self, item: "tag_chooser.Item"):
        text_li = []
        parent = item
        while parent:
            if parent.text() != "":
                text_li.append(parent.text())
            parent = parent.parent()
        text = "::".join(reversed(text_li))
        return text

    def add_tag(self, tag_name: str):
        from . import funcs
        CardId = funcs.CardId
        if tag_name is None:
            return
        for pair in self.pair_li:
            note = mw.col.getCard(CardId(pair.int_card_id)).note()
            note.add_tag(tag_name)
            note.flush()

    def get_all_tags_from_collection(self) -> 'list[str]':
        if __name__ == "__main__":
            return ['0dailynotes',
                    '0dailynotes::1随记',
                    '0dailynotes::2项目',
                    '0dailynotes::2项目::0文章',
                    '0dailynotes::2项目::hjp-bilink',
                    '0dailynotes::2项目::hjp-bilink::开发目标',
                    '0dailynotes::3笔记',
                    '0dailynotes::time::2020::12::13',
                    '0dailynotes::time::2020::12::14',
                    '总结::笔记',
                    '总结::证明方法',
                    '总结::证明方法::反证法',
                    '总结::证明方法::多项式与解空间',
                    '总结::证明方法::扩基',
                    '总结::证明方法::找同构映射的方法',
                    '总结::证明方法::数学归纳法',
                    '总结::证明方法::矩阵分解',
                    '总结::证明方法::逆射证明',
                    '总结::重要结论',
                    '总结::难点必背',
                    '总结::难点必背::不等式',
                    '总结::难点必背::中值定理',
                    '总结::难点必背::可积性定理',
                    '总结::难点必背::实数理论',
                    '总结::难点必背::等式',
                    '总结::难点必背::高代::AB可交换',
                    '总结::难点必背::高代::上下三角矩阵',
                    '总结::难点必背::高代::互素因子与直和',
                    '总结::难点必背::高代::同构（可逆）',
                    '总结::难点必背::高代::名词',
                    '总结::难点必背::高代::域扩张',
                    '总结::难点必背::高代::矩阵乘法',
                    '总结::难点必背::高代::线性空间',
                    '数学::习题',
                    '数学::习题::数学分析::华师初试题::2005',
                    '数学::习题::数学分析::华师初试题::2006',
                    '数学::习题::数学分析::华师初试题::2007',
                    '数学::习题::数学分析::华师初试题::2008',
                    '数学::习题::数学分析::华师初试题::2009',
                    '数学::习题::数学分析::华师初试题::2010',
                    '数学::习题::数学分析::华师初试题::2011',
                    '数学::习题::数学分析::华师初试题::2012',
                    '数学::习题::数学分析::华师初试题::2013',
                    '数学::习题::数学分析::华师初试题::2014',
                    '数学::习题::数学分析::华师初试题::2015',
                    '数学::习题::数学分析::华师初试题::2016',
                    '数学::习题::数学分析::华师初试题::2017',
                    '数学::习题::数学分析::华师初试题::2018',
                    '数学::习题::数学分析::华师初试题::2019',
                    '数学::习题::数学分析::华科初试题::2020',
                    '数学::习题::数学分析::湘潭大学初试题::1997',
                    '数学::习题::数学分析::湘潭大学初试题::1998',
                    '数学::习题::数学分析::湘潭大学初试题::1999',
                    '数学::习题::数学分析::湘潭大学初试题::2000',
                    '数学::习题::数学分析::湘潭大学初试题::2001',
                    '数学::习题::数学分析::湘潭大学初试题::2002',
                    '数学::习题::数学分析::湘潭大学初试题::2003',
                    '数学::习题::数学分析::湘潭大学初试题::2004',
                    '数学::习题::数学分析::湘潭大学初试题::2005',
                    '数学::习题::数学分析::湘潭大学初试题::2006',
                    '数学::习题::数学分析::湘潭大学初试题::2007',
                    '数学::习题::数学分析::湘潭大学初试题::2008',
                    '数学::习题::数学分析::湘潭大学初试题::2009',
                    '数学::习题::数学分析::湘潭大学初试题::2010',
                    '数学::习题::数学分析::湘潭大学初试题::2011',
                    '数学::习题::数学分析::湘潭大学初试题::2012',
                    '数学::习题::数学分析::湘潭大学初试题::2013',
                    '数学::习题::数学分析::湘潭大学初试题::2014',
                    '数学::习题::数学分析::湘潭大学初试题::2015',
                    '数学::习题::数学分析::湘潭大学初试题::2016',
                    '数学::习题::数学分析::湘潭大学初试题::2017',
                    '数学::习题::数学分析::湘潭大学初试题::2018',
                    '数学::习题::数学分析::湘潭大学初试题::2020',
                    '数学::习题::无答案',
                    '数学::习题::疑问',
                    '数学::习题::面试题',
                    '数学::习题::高等代数::华师初试题::2004',
                    '数学::习题::高等代数::华师初试题::2005',
                    '数学::习题::高等代数::华师初试题::2006',
                    '数学::习题::高等代数::华师初试题::2007',
                    '数学::习题::高等代数::华师初试题::2008',
                    '数学::习题::高等代数::华师初试题::2009',
                    '数学::习题::高等代数::华师初试题::2010',
                    '数学::习题::高等代数::华师初试题::2011',
                    '数学::习题::高等代数::华师初试题::2012',
                    '数学::习题::高等代数::华师初试题::2013',
                    '数学::习题::高等代数::华师初试题::2014',
                    '数学::习题::高等代数::华师初试题::2015',
                    '数学::习题::高等代数::华师初试题::2016',
                    '数学::习题::高等代数::华师初试题::2017',
                    '数学::习题::高等代数::华师初试题::2018',
                    '数学::习题::高等代数::华师初试题::2019',
                    '数学::习题::高等代数::湘潭大学初试题::1997',
                    '数学::习题::高等代数::湘潭大学初试题::1998',
                    '数学::习题::高等代数::湘潭大学初试题::1999',
                    '数学::习题::高等代数::湘潭大学初试题::2001',
                    '数学::习题::高等代数::湘潭大学初试题::2002',
                    '数学::习题::高等代数::湘潭大学初试题::2003',
                    '数学::习题::高等代数::湘潭大学初试题::2004',
                    '数学::习题::高等代数::湘潭大学初试题::2005',
                    '数学::习题::高等代数::湘潭大学初试题::2006',
                    '数学::习题::高等代数::湘潭大学初试题::2007',
                    '数学::习题::高等代数::湘潭大学初试题::2008',
                    '数学::习题::高等代数::湘潭大学初试题::2009',
                    '数学::习题::高等代数::湘潭大学初试题::2010',
                    '数学::习题::高等代数::湘潭大学初试题::2011',
                    '数学::习题::高等代数::湘潭大学初试题::2012',
                    '数学::习题::高等代数::湘潭大学初试题::2013',
                    '数学::习题::高等代数::湘潭大学初试题::2014',
                    '数学::习题::高等代数::湘潭大学初试题::2015',
                    '数学::习题::高等代数::湘潭大学初试题::2016',
                    '数学::习题::高等代数::湘潭大学初试题::2017',
                    '数学::习题::高等代数::湘潭大学初试题::2018',
                    '数学::习题::高等代数::湘潭大学初试题::2020',
                    '数学::课本::复变',
                    '数学::课本::复变::华科应用复分析',
                    '数学::课本::复变::复变函数@钟玉泉',
                    '数学::课本::复变::复变函数与积分变换_华科李红',
                    '数学::课本::复变::复变函数与积分变换_焦红伟PDF',
                    '数学::课本::复变::慕课国防科大',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::01朴素集合论',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::02拓扑空间与连续映射',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::04连通性',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::05可数性公理',
                    '数学::课本::拓扑::点集拓扑讲义@熊金城::07紧致性',
                    ]
        else:
            return mw.col.tags.all()

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

    def build_tag_tree(self, tag_set: "set[str]", model: "QStandardItemModel", view: "tag_chooser.View",
                       button_group: "tag_chooser.button_group"):
        tag_list = sorted(list(tag_set))
        tag_dict = G.objs.Struct.TreeNode(model.invisibleRootItem(), {})
        total_tag = button_group.L_or_R == button_group.R
        for i in tag_list:
            tagname_li = i.split("::")
            parent = tag_dict
            while tagname_li:
                tagname = tagname_li.pop(0)
                if tagname not in parent.children:
                    item = self.Item(tagname, total_tag=total_tag)
                    parent.item.appendRow([item])
                    parent.children[tagname] = G.objs.Struct.TreeNode(item, {})
                    if not tagname_li:
                        item.set_tag_name(i)
                parent = parent.children[tagname]
        view.setDragDropMode(DragDropMode.NoDragDrop)
        view.setAcceptDrops(True)
        pass

    def build_tag_list(self, tag_set: "set[str]", model: "QStandardItemModel", view: "tag_chooser.View",
                       button_group: "tag_chooser.button_group"):
        tag_list = sorted(list(tag_set))
        total_tag = button_group.L_or_R == button_group.R
        for i in tag_list:
            item = self.Item(i, total_tag=total_tag)
            item.set_tag_name(i)
            model.appendRow([item])
        view.setDragDropMode(DragDropMode.NoDragDrop)
        pass

    def init_data_left(self, init=False):
        model, button_group, view = self.model_left, self.left_button_group, self.view_left
        model.clear()
        self.model_right_rootNode = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(["selected tag"])
        # tag_list = self.get_all_tags_from_pairli() if init else self.save()
        if button_group.arrange_button.text() == button_group.tag_tree:
            self.build_tag_tree(self.tag_list, model, view, button_group)
        else:
            self.build_tag_list(self.tag_list, model, view, button_group)
        self.view_left.expandAll()
        pass

    def init_data_right(self):
        model, button_group, view = self.model_right, self.right_button_group, self.view_right
        model.clear()
        self.model_left_rootNode = model.invisibleRootItem()
        model.setHorizontalHeaderLabels(["all tags"])
        tag_list = self.get_all_tags_from_collection()
        if button_group.arrange_button.text() == button_group.tag_tree:
            self.build_tag_tree(tag_list, model, view, button_group)
        else:
            self.build_tag_list(tag_list, model, view, button_group)
        self.view_right.expandAll()
        pass

    @property
    def curr_tag_name(self):
        return "tag_name"

        # class Tag_list(list):
        #     def append(self, item) -> None:
        #         super().append(item)
        #         self
        #         self.sort()

        pass

    class button_group(QWidget):
        L, R = 0, 1
        tag_tree, tag_list = "tag_tree", "tag_list"

        def __init__(self, superior: "tag_chooser", L_or_R=0, fromView: "QTreeView" = None,
                     fromModel: "QStandardItemModel" = None):
            super().__init__()
            self.superior = superior
            self.fromView = fromView
            self.fromModel = fromModel
            self.L_or_R = L_or_R
            self.func_button = QToolButton(self)  # 左边是del, 右边是 add
            self.func2_button = QToolButton(self)  # 左边是new, 右边要hide
            self.func2_button.hide()
            self.arrange_button = QToolButton(self)  # 大家都有一个排版系统
            H_layout = QHBoxLayout(self)
            H_layout.addWidget(self.func2_button)
            H_layout.addWidget(self.func_button)
            H_layout.addWidget(self.arrange_button)

            self.setLayout(H_layout)
            self.arrange_button.setText(self.tag_tree)
            self.button_Icon_switch()
            self.init_UI()
            self.init_event()

        def button_text_switch(self):
            if self.arrange_button.text() == self.tag_tree:
                self.arrange_button.setText(self.tag_list)
            else:
                self.arrange_button.setText(self.tag_tree)
            self.button_Icon_switch()
            if self.L_or_R == self.L:
                self.superior.init_data_left()
            else:
                self.superior.init_data_right()

        def button_Icon_switch(self):
            if self.arrange_button.text() == self.tag_tree:
                self.arrange_button.setIcon(QIcon(G.src.ImgDir.tree))
            else:
                self.arrange_button.setIcon(QIcon(G.src.ImgDir.list))

        def init_UI(self):
            if self.L_or_R == self.L:
                self.func_button.setIcon(QIcon(G.src.ImgDir.cancel))
                self.func2_button.setIcon(QIcon(G.src.ImgDir.item_plus))
                self.func2_button.show()
            elif self.L_or_R == self.R:
                self.func_button.setIcon(QIcon(G.src.ImgDir.correct))

        def init_event(self):
            if self.L_or_R == self.L:
                self.func_button.clicked.connect(self.on_card_tag_del_handle)
                self.func2_button.clicked.connect(self.on_card_tag_new_handle)
            elif self.L_or_R == self.R:
                self.func_button.clicked.connect(self.on_collection_tag_add_handle)
            self.arrange_button.clicked.connect(self.button_text_switch)

        def on_card_tag_new_handle(self, tag_name=None, from_posi=None):
            if tag_name:
                new_tag = tag_name
            else:
                new_tag = f"""new_tag_{datetime.now().strftime("%Y%m%d%H%M%S")}"""
            if from_posi:
                item_parent = from_posi
                new_full_tag = new_tag
            else:
                if self.fromView.selectedIndexes():
                    item = self.fromModel.itemFromIndex(self.fromView.selectedIndexes()[0])
                    item_parent = item.parent()
                    new_full_tag = self.superior.get_full_tag_name(item) + "::" + new_tag
                else:
                    item_parent = self.fromModel.invisibleRootItem()
                    new_full_tag = new_tag
            new_item = self.superior.Item(new_tag)
            new_item.set_tag_name(new_full_tag)
            item_parent.appendRow([new_item])
            self.superior.tag_list = self.superior.save()
            self.fromView.edit(new_item.index())
            pass

        def on_card_tag_del_handle(self):
            if self.fromView.selectedIndexes():
                item_li = [self.fromModel.itemFromIndex(index) for index in self.fromView.selectedIndexes()]

                stack = item_li
                while stack:
                    stack_item: "tag_chooser.Item" = stack.pop()
                    if stack_item.tag_name:
                        # to_be_deleted.append(stack_item.tag_name)
                        self.superior.tag_list.remove(stack_item.tag_name)
                        stack_item.set_tag_name(None)
                    for i in range(stack_item.rowCount()):
                        stack.append(stack_item.child(i, 0))
                self.superior.init_data_left()

        def on_collection_tag_add_handle(self):
            if self.fromView.selectedIndexes():
                item_li = [self.fromModel.itemFromIndex(index) for index in self.fromView.selectedIndexes()]
                for item in item_li:
                    # item:"tag_chooser.Item" = self.fromModel.itemFromIndex(self.fromView.selectedIndexes()[0])
                    tag_name = self.superior.get_full_tag_name(item)
                    if tag_name not in self.superior.tag_list:
                        self.superior.tag_list.add(tag_name)
                self.superior.init_data_left()

    class View(QTreeView):
        tag_list, tag_tree = 0, 1
        on_did_drop = pyqtSignal(object)

        @dataclass
        class DidDropEvent:
            index: "QModelIndex"
            old: "str"
            new: "str"

        def __init__(self, parent: "tag_chooser"):
            super().__init__(parent)
            self.superior: "tag_chooser" = parent
            self.viewmode: "Optional[int]" = None
            self.setDragDropOverwriteMode(False)
            self.setSelectionMode(QAbstractItemViewSelectMode.ExtendedSelection)
            # self.on_did_drop.connect(self.change_base_tag_after_dropEvent)

        def dropEvent(self, event: QtGui.QDropEvent) -> None:
            item_from: "list[tag_chooser.Item]" = [self.model().itemFromIndex(index) for index in
                                                   self.selectedIndexes()]
            item_to: "tag_chooser.Item" = self.model().itemFromIndex(self.indexAt(event.pos()))
            parent_from: "list[tag_chooser.Item]" = [item.parent() for item in item_from]
            parent_to: "tag_chooser.Item" = item_to.parent() if item_to is not None else self.model().invisibleRootItem()
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
            self.superior.tag_list = self.superior.save()
            self.superior.init_data_left()

    class Item(QStandardItem):
        def __init__(self, tag_name, total_tag=False):
            super().__init__(tag_name)
            self.tag_id: "Optional[int]" = None
            self.level: "Optional[int]" = None
            if total_tag:
                self.setFlags(self.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled & ~Qt.ItemIsEditable)
            self.last: "Optional[str]" = tag_name
            self._tag_name: "Optional[str]" = None

        @property
        def tag_name(self):
            return self._tag_name

        def set_tag_name(self, name):
            self._tag_name = name

        def parent(self) -> "tag_chooser.Item":
            if super().parent() is None:
                return self.model().invisibleRootItem()
            else:
                return super().parent()

    @dataclass
    class Id_tag:
        tag: "str"
        ID: "int"


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

    def get_url_name_num(self) -> (str, str, str):
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
                super().__init__(superior, colItems)
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
        提取描述方式预设表
        模板Id:combo, field:受模板影响显示可选combo, length为spinbox, regexp为字符串用textedit

        """
        colnames = ["templateName", "fieldName", "length", "regexp", "autoUpdateDesc"]

        class colEnum:
            template = 1
            field = 2
            length = 3
            regexp = 4
            autoUpdateDesc = 5

        defaultRowData = [(-1, "ALL_TEMPLATES", colEnum.template),
                          ((-1, -1), "ALL_FIELDS", colEnum.field),  # (dataformat.templateId, dataformat.fieldId), dataformat.fieldName, colType.field)
                          (32, "32", colEnum.length),
                          ("", "", colEnum.regexp),
                          (True, "True", colEnum.autoUpdateDesc)]

        def GetRowFromData(self, data: "list[str]"):
            """这里data是一行对象"""
            if len(data) < len(self.colnames):
                data += self.defaultRowData[len(data):]
            dataformat = self.DataFormat(*data)
            colType = self.colEnum
            return [
                    self.TableItem(self, dataformat.templateId, dataformat.templateName, colType.template),
                    self.TableItem(self, (dataformat.templateId, dataformat.fieldId), dataformat.fieldName, colType.field),
                    self.TableItem(self, dataformat.length, str(dataformat.length), colType.length),
                    self.TableItem(self, dataformat.regexp, dataformat.regexp, colType.regexp),
                    self.TableItem(self, dataformat.autoUpdateDesc, str(dataformat.autoUpdateDesc), colType.autoUpdateDesc)
            ]

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
                w.setValueToTableRowFromForm()  # 从新建表单设置回到表格
                self.SaveDataToConfigModel()  # 从表格回到配置项

        def OnTemplateComboBoxChanged(self, item: "ConfigWidget.DescExtractPresetTable.TableItem", templateId):
            row = self.table_model.indexFromItem(item).row()
            # templateId = item.data(ItemDataRole.UserRole)
            fieldItem: "ConfigWidget.DescExtractPresetTable.TableItem" = self.table_model.item(row, 1)
            fieldItem.SetupFieldCombo(templateId)
            self.rowEditor.update()

        def SaveDataToConfigModel(self):
            data = []
            for row in range(self.table_model.rowCount()):
                rowdata = []
                for col in range(len(self.colnames)):
                    item: "ConfigWidget.DescExtractPresetTable.TableItem" = self.table_model.item(row, col)
                    value = item.GetValue()
                    rowdata.append(value)
                data.append(rowdata)
            self.ConfigModelItem.setValue(data, 需要设值回到组件=False)
            pass

        class TableItem(baseClass.ConfigTableView.TableItem):
            """他是大表的项"""

            def __init__(self, superior, value, name, valueType):
                super().__init__(superior, name)
                self.superior: "ConfigWidget.DescExtractPresetTable" = superior
                self.valueType = valueType
                self.setData(value, ItemDataRole.UserRole)

            def SetupFieldCombo(self, templateId: "int", fieldId: "int" = None):
                """text=字段的名字, value=[模板id,字段id]"""
                colType = self.superior.colEnum
                # print("call: SetupFieldCombo")
                if self.valueType == colType.field:
                    for i in range(self.innerWidget.count()):
                        self.innerWidget.removeItem(i)
                    self.innerWidget.clear()
                    # print("self.valueType == colType.field,templateId=" + templateId.__str__() + " clear()")

                    if templateId > 0:
                        fields = funcs.CardTemplateOperation.GetModelFromId(templateId)["flds"]
                        self.innerWidget.addItem("ALL_FIELDS", (templateId, -1))
                        for _field in fields:
                            # print(f"templateId={templateId}, fieldId={_field['ord']}")
                            self.innerWidget.addItem(_field["name"], (templateId, _field["ord"]))
                            # self.innerWidget
                        idx = sum([i + 1 if self.innerWidget.itemData(i, role=ItemDataRole.UserRole) == (templateId, fieldId) else 0 for i in range(self.innerWidget.count())]) - 1 if fieldId is not None else 0
                        # print(f"templateId > 0, fieldId={fieldId},idx={idx}")
                    else:
                        self.innerWidget.addItem("ALL_FIELDS", (-1, -1))
                        self.innerWidget.addItem("front", (-1, -2))
                        self.innerWidget.addItem("back", (-1, -3))
                        idx = sum([i + 1 if self.innerWidget.itemData(i, role=ItemDataRole.UserRole) == (-1, fieldId) else 0 for i in range(self.innerWidget.count())]) - 1 if fieldId is not None else 0
                        if idx == -1:
                            idx = 0
                        # print(f"templateId <= 0, fieldId={fieldId},idx={idx}")
                    self.innerWidget.setCurrentIndex(idx)

                    return

            def SetupTemplateCombo(self, templateId):
                """text=模板名字, value=模板Id"""
                data = self.data(ItemDataRole.UserRole)

                def CurIndexChanged(idx: "int"):
                    # print(f"currentIndexChanged={idx}")
                    self.setData(self.innerWidget.itemData(idx, ItemDataRole.UserRole), ItemDataRole.UserRole)
                    self.setText(self.innerWidget.itemText(idx))
                    newTemplateId = self.innerWidget.itemData(idx, ItemDataRole.UserRole)
                    self.superior.OnTemplateComboBoxChanged(self, newTemplateId)
                    # print(f"{newTemplateId}")

                templates = funcs.CardTemplateOperation.GetAllTemplates()
                self.innerWidget.addItem("ALL_TEMPLATES", -1)
                for template in templates:
                    self.innerWidget.addItem(template["name"], template["id"])
                idx = self.innerWidget.findData(data)
                self.innerWidget.setCurrentIndex(idx)

                return

            def ShowAsWidget(self):
                """"""
                self.widget = QWidget()
                layout = QVBoxLayout()
                colType = self.superior.colEnum
                data = self.data(ItemDataRole.UserRole)
                # print(f"ShowAsWidget: data={data},self.valueType={self.valueType},self.text={self.text()}")
                if self.valueType in [colType.field, colType.template]:
                    self.innerWidget = QComboBox()
                    if self.valueType == colType.field:
                        templateId, fieldId = data
                        self.SetupFieldCombo(templateId, fieldId)

                        def CurIndexChanged(idx: "int"):
                            self.setData(self.innerWidget.itemData(idx), ItemDataRole.UserRole)
                            self.setText(self.innerWidget.itemText(idx))
                        # self.innerWidget.currentIndexChanged.connect(lambda Idx: CurIndexChanged(Idx))

                    else:
                        templateId = data
                        self.SetupTemplateCombo(templateId)
                else:
                    if self.valueType == colType.length:
                        self.innerWidget = QSpinBox()
                        self.innerWidget.setValue(int(data))
                        # self.innerWidget.valueChanged.connect(lambda val: self.setText(str(val)))
                    elif self.valueType == colType.regexp:
                        self.innerWidget = QTextEdit()
                        self.innerWidget.setText(data)
                    else:
                        self.innerWidget = QRadioButton()
                        self.innerWidget.setChecked(data == "True")
                        # self.innerWidget.textChanged.connect(lambda : self.setText(self.innerWidget.toPlainText()))
                # layout.addWidget(self.innerWidget)
                # self.widget.setLayout(layout)
                return self.innerWidget

            def GetValue(self):
                colType = self.superior.colEnum
                if self.valueType == colType.field:
                    return self.data(ItemDataRole.UserRole)[1]  # 1表示保存field id
                elif self.valueType == colType.template:
                    return self.data(ItemDataRole.UserRole)  # template id
                elif self.valueType == colType.regexp:
                    return self.text()
                elif self.valueType == colType.autoUpdateDesc:
                    return self.text() == "True"
                else:
                    return int(self.text())

        class RowItem:
            def __init__(self, itemLi: "list[ConfigWidget.DescExtractPresetTable.TableItem]"):
                pass

        class DataFormat:
            templateId: "int"
            fieldId: "int"
            length: "int"
            regexp: "str"

            def __init__(self, templateId, fieldId, length, regexp, autoUpdateDesc):
                self.templateId = templateId
                self.fieldId = fieldId
                self.autoUpdateDesc = autoUpdateDesc
                if templateId < 0:
                    self.model = None
                    self.templateName = "ALL_TEMPLATES"
                else:
                    self.model = funcs.CardTemplateOperation.GetModelFromId(templateId)
                    if not self.model:
                        self.templateId = -1
                        self.templateName = "ALL_TEMPLATES"
                    else:
                        self.templateName = self.model["name"]

                if self.model:
                    self.fieldName = self.model["flds"][self.fieldId]["name"]
                elif self.fieldId < 0:
                    self.fieldName = "ALL_FIELDS"
                else:
                    self.fieldName = self.fieldId.__str__()

                self.length = length
                self.regexp = regexp

        class NewRowFormWidget(baseClass.ConfigTableNewRowFormView):
            def __init__(self, superior: "ConfigWidget.DescExtractPresetTable", colItems: "list[ConfigWidget.DescExtractPresetTable.TableItem]" = None):
                self.colWidgets = [QComboBox(),
                                   QComboBox(),
                                   QSpinBox(),
                                   QTextEdit(),
                                   QRadioButton()
                                   ]
                super().__init__(superior, colItems)

            def SetupWidget(self):
                self.SetupTemplateCombox()
                self.SetupFieldCombox()
                self.SetupLengthSpinbox()
                self.SetupRegexTextedit()
                self.SetupSyncRadiobutton()

            # def SetupUI(self):
            #     from . import G
            #     hlayout = QHBoxLayout()
            #     self.okbtn.setIcon(QIcon(G.src.ImgDir.correct))
            #
            #     self.mainLayout.addLayout(self.layout)
            #     hlayout.addWidget(self.okbtn)
            #     self.mainLayout.addLayout(hlayout)
            #     self.mainLayout.setAlignment(Qt.AlignRight)
            #     self.widget.setLayout(self.mainLayout)
            #     funcs.Map.do(range(len(self.superior.colnames)), lambda i: self.layout.addRow(self.superior.colnames[i], self.__dict__[f"col{i}"]))

            def SetupTemplateCombox(self):
                templateId = self.colItems[0].data(role=ItemDataRole.UserRole)

                templates = funcs.CardTemplateOperation.GetAllTemplates()
                self.colWidgets[0].addItem("ALL_TEMPLATES", -1)
                for template in templates:
                    self.colWidgets[0].addItem(template["name"], template["id"])
                idx = self.colWidgets[0].findData(templateId)
                self.colWidgets[0].setCurrentIndex(idx)
                pass

            def SetupFieldCombox(self, templateId=None, fieldId=None):
                templateId = self.colItems[0].data(role=ItemDataRole.UserRole) if templateId is None else templateId
                fieldId = self.colItems[1].data(role=ItemDataRole.UserRole)[1] if fieldId is None else fieldId
                self.colWidgets[1].clear()

                if templateId > 0:
                    fields = funcs.CardTemplateOperation.GetModelFromId(templateId)["flds"]
                    self.colWidgets[1].addItem("ALL_FIELDS", (templateId, -1))
                    for _field in fields:
                        # print(f"templateId={templateId}, fieldId={_field['ord']}")
                        self.colWidgets[1].addItem(_field["name"], (templateId, _field["ord"]))
                        # self.innerWidget
                    idx = sum([i + 1 if self.colWidgets[1].itemData(i, role=ItemDataRole.UserRole) == (templateId, fieldId) else 0 for i in range(self.colWidgets[1].count())]) - 1 if fieldId is not None else 0
                else:
                    self.colWidgets[1].addItem("ALL_FIELDS", (-1, -1))
                    self.colWidgets[1].addItem("front", (-1, -2))
                    self.colWidgets[1].addItem("back", (-1, -3))
                    idx = sum([i + 1 if self.colWidgets[1].itemData(i, role=ItemDataRole.UserRole) == (-1, fieldId) else 0 for i in range(self.colWidgets[1].count())]) - 1 if fieldId is not None else 0
                    if idx == -1:
                        idx = 0
                self.colWidgets[1].setCurrentIndex(idx)

                pass

            def SetupLengthSpinbox(self):
                self.colWidgets[2].setValue(self.colItems[2].data(role=ItemDataRole.UserRole))
                pass

            def SetupRegexTextedit(self):
                self.colWidgets[3].setText(self.colItems[3].data(role=ItemDataRole.UserRole))
                pass

            def SetupSyncRadiobutton(self):
                self.colWidgets[4].setChecked(self.colItems[4].data(role=ItemDataRole.UserRole))
                pass

            def SetupEvent(self):
                self.okbtn.clicked.connect(self.OnOkClicked)
                self.colWidgets[0].currentIndexChanged.connect(lambda idx: self.SetupFieldCombox(self.colWidgets[0].currentData(), -1))
                pass

            def setValueToTableRowFromForm(self):
                self.colItems[0].SetValue(self.colWidgets[0].currentText(), self.colWidgets[0].currentData(ItemDataRole.UserRole))
                self.colItems[1].SetValue(self.colWidgets[1].currentText(), self.colWidgets[1].currentData(ItemDataRole.UserRole))
                self.colItems[2].SetValue(self.colWidgets[2].text(), self.colWidgets[2].value())
                self.colItems[3].SetValue(self.colWidgets[3].toPlainText(), self.colWidgets[3].toPlainText())
                self.colItems[4].SetValue(f"{self.colWidgets[4].isChecked()}", self.colWidgets[4].isChecked())

    class GviewConfigApplyTable(baseClass.ConfigTableView):
        """
        TODO: 需要的功能: 增删改gview的uuid和名字列表
        TODO: 保存的时候要保存item.data(), 展示时, 展示为item.text()要分开
        TODO: 当应用表中点击删除项的时候, 如果是最后一项了, 也就是说删了以后, 表空了, 则立即将当前配置删除, 并将视图的config置空, 重新载入
        TODO: 当应用表中点击删除项的时候, 如果点击的是视图本身, 则立即发动视图的config置空, 重新载入配置表

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
                super().__init__(superior, colItems)

                self.SetupWidget()
                self.SetupEvent()

                pass

            def SetupEvent(self):
                """
                laterDO: 在搜索框中按回车触发搜索事件 (这个好像不是很重要)

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
            说明 = 译.例子_多级排序+"\n"+funcs.GviewConfigOperation.获取eval可用变量与函数的说明()
            class edit_widget(baseClass.组件_表格型配置项_列编辑器_可执行字符串):
                def on_test(self):
                    _ = baseClass.枚举命名
                    locals_dict = funcs.GviewConfigOperation.获取eval可用字面量()

                    try:
                        strings = self.布局[子代][0][组件].toPlainText()
                        literal = eval(strings, {}, {**locals_dict,_.上升:_.上升,_.下降:_.下降})

                        if type(literal) != list:
                            self.设置说明栏("type error:" + 译.可执行字符串表达式的返回值必须是列表类型)
                            return False
                        elif len([tup for tup in literal if len(tup) != 2]) > 0:
                            self.设置说明栏("type error:" + 译.可执行字符串_必须是一个二元元组)
                            return False
                        elif len([tup for tup in literal if not (tup[0] in locals_dict and tup[1] in [_.上升,_.下降])]) > 0:
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
                        widget.setChecked(node_data[name])
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

    # class CustomConfigItemLabelView(baseClass.CustomConfigItemView):
    #     def __init__(self,配置项,上级):
    #         super().__init__(配置项,上级)
    #         self.View =


class ReviewButtonForCardPreviewer:
    def __init__(self, papa, layout: "QGridLayout"):
        from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewer
        self.papa: "SingleCardPreviewer" = papa
        self.ease_button: "dict[int,QPushButton]" = {}
        self.review_buttons = self._create_review_buttons()
        self.due_info = self._create_due_info_widget()
        layout.addWidget(self.due_info, 0, 0, 1, 1)
        self.initEvent()

    def initEvent(self):
        G.signals.on_card_answerd.connect(self.handle_on_card_answerd)
        self
        pass

    def handle_on_card_answerd(self, answer: "configsModel.AnswerInfoInterface"):
        from ..bilink.dialogs.linkdata_grapher import GrapherRoamingPreviewer

        notself, equalId, isRoaming = answer.platform != self, answer.card_id == self.card().id, isinstance(self.papa.superior, GrapherRoamingPreviewer)
        # print(f"handle_on_card_answerd,{notself},{equalId},{isRoaming}")
        if notself and equalId and isRoaming:
            # print("handle_on_card_answerd>if>ok")
            self.papa.superior.nextCard()
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
        class 角色多选(QComboBox):
            def __init__(self, 项):
                super().__init__()
                """根据配置中的安排加载对应的多选框"""
                from . import funcs, models
                self.项: models.类型_视图结点属性项 = 项
                视图配置id = self.项.上级.数据源.视图数据.config
                self.待选角色表 = []
                if 视图配置id:
                    字面量 = funcs.GviewConfigOperation.从数据库读(视图配置id).data.node_role_list.value
                    self.待选角色表 = literal_eval(字面量)
                # self.下拉选框 = QComboBox()
                [self.addItem(self.待选角色表[i], i) for i in range(len(self.待选角色表))]
                self.addItem(QIcon(funcs.G.src.ImgDir.close), 译.无角色, -1)
                self.setCurrentIndex(self.findData(self.项.值, role=Qt.UserRole))
                item_set_value = lambda value: self.项.设值(value)
                self.currentIndexChanged.connect(lambda x: item_set_value(self.currentData()))
                pass

        # class 优先级(QWidget):
        #     def __init__(self, 项):
        #         """优先级是个滑动条, 要显示滑动的数值,每次滑动完都要保存"""
        #         super().__init__()
        #         from . import funcs, models
        #         self.项: models.类型_视图结点属性项 = 项
        #         self.拖动条 = QSlider()
        #         self.数值显示 = QLabel()
        #         if self.项.有限制:
        #             self.拖动条.setRange(self.项.限制[0],self.项.限制[1])
        #         funcs.组件定制.组件组合({布局:QHBoxLayout(),子代:[self.数值显示,self.拖动条]},self)
        #
        #         def item_set_value(value):
        #             self.项.设值(value)
        #             self.数值显示.setText(value.__str__())
        #         self.拖动条.valueChanged.connect(item_set_value)
        #
        #
        #         pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = tag_chooser()
    f.show()
    sys.exit(app.exec_())
