# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'mywidgets.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/1 16:48'
"""
import os
import re
import urllib
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from typing import Union, Optional
import sys

from .language import Translate, rosetta
from . import configsModel

from .compatible_import import *
from . import funcs, baseClass
from aqt import mw, dialogs
from aqt.browser import Browser
from aqt.browser.previewer import Previewer
from aqt.operations.card import set_card_deck
from aqt.reviewer import Reviewer
from aqt.utils import tooltip, showInfo
from aqt.webview import AnkiWebView

if __name__ == "__main__":
    from lib.common_tools import G
else:
    from . import G

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *


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
        print(item.deck_name)

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


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     p = deck_chooser()
#     p.exec()
#     sys.exit(app.exec_())
#     pass

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
                # for tag_name in to_be_deleted:

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
        config:"list" = funcs.PDFLink.GetPathInfoFromPreset(pdffilepath)
        if config is not None:
            pdffilename = config[1]
        else:
            pdffilename = os.path.splitext(os.path.basename(pdffilepath))[0]
        # pdffilename, _ = config[1] if config is not None else os.path.splitext(os.path.basename(pdffilepath))
        self.widgets[Translate.pdf路径].blockSignals(True)
        self.widgets[Translate.pdf路径].setText(pdffilepath)
        self.widgets[Translate.pdf路径].blockSignals(False)
        self.widgets[Translate.pdf名字].setText(pdffilename)

    def get_url_name_num(self)->(str, str, str):
        return self.widgets[Translate.pdf路径].toPlainText(), \
               self.widgets[Translate.pdf名字].toPlainText(), \
               self.widgets[Translate.pdf页码].value()

    def on_confirm_clicked(self):
        self.needpaste = True
        clipboard = QApplication.clipboard()
        mmdata = QMimeData()
        pdfurl, pdfname, pdfpage = self.get_url_name_num()
        quote = re.sub(r"\\","/",pdfurl)    # f{pdfurl[:2]}{urllib.parse.quote(pdfurl[2:])} TODO 将来要适配mac系统的路径
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
        s = funcs.Config.get().PDFUrlLink_page_num_str.value
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
        colnames = ["PDFpath", "name", "style", "showPage"]

        def NewRow(self):
            w = self.NewRowFormWidget(self)
            w.widget.exec()
            self.AppendRow(w.colItems)
            self.SaveDataToConfigModel()

        def ShowRowEditor(self, row: "list[ConfigWidget.PDFUrlLinkBooklist.TableItem]"):
            # dialog = QDialog()
            # dialog.resize(300, 600)
            layout = QFormLayout()
            textItemList = list(map(lambda col: QTextEdit(col.text()), row[0:3]))

            list(map(lambda idx: textItemList[idx].textChanged.connect(
                    lambda: row[idx].setData(textItemList[idx].toPlainText(), ItemDataRole.DisplayRole)
            ), range(3)))
            funcs.Map.do(range(3), lambda idx: layout.addRow(self.colnames[idx], textItemList[idx]))
            layout.addRow(self.colnames[3], row[3].ShowAsWidget())
            self.rowEditor.setLayout(layout)
            self.rowEditor.exec()

        def SaveDataToConfigModel(self):
            newConfigItem = []
            for row in range(self.model.rowCount()):
                line = []
                for col in range(4):
                    item: "ConfigWidget.PDFUrlLinkBooklist.TableItem" = self.model.item(row, col)
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
            self.Item.setValue(newConfigItem)
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
                super().__init__(superior, colItems)

            def SetupEvent(self):
                funcs.Map.do(range(3), lambda idx: self.colWidgets[idx].textChanged.connect(lambda: self.colItems[idx].setText(self.colWidgets[idx].toPlainText())))
                self.colWidgets[3].clicked.connect(lambda: self.colItems[3].setText(str(self.colWidgets[3].isChecked())))

    class DescExtractPresetTable(baseClass.ConfigTableView):
        """模板Id:combo, field:受模板影响显示可选combo, length为spinbox, regexp为字符串用textedit

        """
        colnames = ["templateName", "fieldName", "length", "regexp", "autoUpdateDesc"]

        class colEnum:
            template = 1
            field = 2
            length = 3
            regexp = 4
            autoUpdateDesc= 5

        defaultRowData = [(-1, "ALL_TEMPLATES", colEnum.template),
                          ((-1, -1), "ALL_FIELDS", colEnum.field),
                          (32, "32", colEnum.length),
                          ("", "", colEnum.regexp),
                          (True,"True",colEnum.autoUpdateDesc)]

        def GetRowFromData(self, data: "list[str]"):
            if len(data)<len(self.colnames):
                data+=self.defaultRowData[len(data):]
            dataformat = self.DataFormat(*data)
            colType = self.colEnum
            return [
                    self.TableItem(self, dataformat.templateId, dataformat.templateName, colType.template),
                    self.TableItem(self, (dataformat.templateId, dataformat.fieldId), dataformat.fieldName, colType.field),
                    self.TableItem(self, dataformat.length, str(dataformat.length), colType.length),
                    self.TableItem(self, dataformat.regexp, dataformat.regexp, colType.regexp),
                    self.TableItem(self, dataformat.autoUpdateDesc, str(dataformat.autoUpdateDesc),colType.autoUpdateDesc)
            ]

        def NewRow(self):
            w = self.RowFormWidget(self)
            w.widget.exec()
            self.AppendRow(w.colItems)

        def ShowRowEditor(self, row: "list[ConfigWidget.DescExtractPresetTable.TableItem]"):
            self.RowFormWidget(self, row).widget.exec()
            self.SaveDataToConfigModel()

        def OnTemplateComboBoxChanged(self, item: "ConfigWidget.DescExtractPresetTable.TableItem", templateId):
            row = self.model.indexFromItem(item).row()
            # templateId = item.data(ItemDataRole.UserRole)
            fieldItem: "ConfigWidget.DescExtractPresetTable.TableItem" = self.model.item(row, 1)
            fieldItem.SetupFieldCombo(templateId)
            self.rowEditor.update()


        def SaveDataToConfigModel(self):
            data = []
            for row in range(self.model.rowCount()):
                rowdata = []
                for col in range(len(self.colnames)):
                    item: "ConfigWidget.DescExtractPresetTable.TableItem" = self.model.item(row, col)
                    value = item.GetValue()
                    rowdata.append(value)
                data.append(rowdata)
            self.Item.setValue(data)
            pass

        class TableItem(baseClass.ConfigTableView.TableItem):
            def __init__(self, superior, value, name, valueType):
                super().__init__(superior, name)
                self.superior: "ConfigWidget.DescExtractPresetTable" = superior
                self.valueType = valueType
                self.setData(value, ItemDataRole.UserRole)

            def SetupFieldCombo(self, templateId: "int", fieldId: "int" = None):
                """text=字段的名字, value=[模板id,字段id]"""
                colType = self.superior.colEnum

                if self.valueType == colType.field:
                    for i in range(self.innerWidget.count()):
                        self.innerWidget.removeItem(i)
                    self.innerWidget.clear()
                    print("self.valueType == colType.field,templateId=" + templateId.__str__() + " clear()")

                    if templateId > 0:
                        fields = funcs.CardTemplateOperation.GetModelFromId(templateId)["flds"]
                        self.innerWidget.addItem("ALL_FIELDS", (templateId, -1))
                        for _field in fields:
                            self.innerWidget.addItem(_field["name"], (templateId, _field["ord"]))
                        idx = fieldId if fieldId else 0
                    else:
                        self.innerWidget.addItem("ALL_FIELDS", (-1, -1))
                        self.innerWidget.addItem("front", (-1, -2))
                        self.innerWidget.addItem("back", (-1, -3))
                        idx = self.innerWidget.findData((-1, fieldId), ItemDataRole.UserRole) if fieldId else 0
                    self.innerWidget.setCurrentIndex(idx)

                    return

            def SetupTemplateCombo(self, templateId):
                """text=模板名字, value=模板Id"""
                data = self.data(ItemDataRole.UserRole)

                def CurIndexChanged(idx: "int"):
                    print(f"currentIndexChanged={idx}")
                    self.setData(self.innerWidget.itemData(idx, ItemDataRole.UserRole), ItemDataRole.UserRole)
                    self.setText(self.innerWidget.itemText(idx))
                    newTemplateId = self.innerWidget.itemData(idx, ItemDataRole.UserRole)
                    self.superior.OnTemplateComboBoxChanged(self, newTemplateId)
                    print(f"{newTemplateId}")

                templates = funcs.CardTemplateOperation.GetAllTemplates()
                self.innerWidget.addItem("ALL_TEMPLATES", -1)
                for template in templates:
                    self.innerWidget.addItem(template["name"], template["id"])
                idx = self.innerWidget.findData(data, ItemDataRole.UserRole)
                self.innerWidget.setCurrentIndex(idx)
                # self.innerWidget.currentIndexChanged.connect(lambda Idx: CurIndexChanged(Idx))
                return

            def ShowAsWidget(self):
                """"""
                self.widget = QWidget()
                layout = QVBoxLayout()
                colType = self.superior.colEnum
                data = self.data(ItemDataRole.UserRole)
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
                        self.innerWidget.setValue(data)
                        # self.innerWidget.valueChanged.connect(lambda val: self.setText(str(val)))
                    elif self.valueType == colType.regexp:
                        self.innerWidget = QTextEdit()
                        self.innerWidget.setText(data)
                    else:
                        self.innerWidget = QRadioButton()
                        self.innerWidget.setChecked(data)
                        # self.innerWidget.textChanged.connect(lambda : self.setText(self.innerWidget.toPlainText()))
                # layout.addWidget(self.innerWidget)
                # self.widget.setLayout(layout)
                return self.innerWidget

            def GetValue(self):
                colType = self.superior.colEnum
                if self.valueType == colType.field:
                    return self.data(ItemDataRole.UserRole)[1]
                elif self.valueType == colType.template:
                    return self.data(ItemDataRole.UserRole)
                elif self.valueType == colType.regexp:
                    return self.text()
                elif self.valueType == colType.autoUpdateDesc:
                    return self.text()=="True"
                else:
                    return int(self.text())

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

        class RowFormWidget(baseClass.ConfigTableNewRowFormView):
            def __init__(self, superior, colItems: "list[ConfigWidget.DescExtractPresetTable.TableItem]" = None):
                if not colItems:
                    colItems = funcs.Map.do(superior.defaultRowData, lambda data: superior.TableItem(superior, *data))
                super().__init__(superior, colItems)

            def SetupEvent(self):
                col0: "QComboBox" = self.colWidgets[0]
                col1: "QComboBox" = self.colWidgets[1]
                col2: "QSpinBox" = self.colWidgets[2]
                col3: "QTextEdit" = self.colWidgets[3]
                col4: "QRadioButton" = self.colWidgets[4]
                col0.currentIndexChanged.connect(lambda idx: OnCol0CurrentIndexChanged(idx))
                col1.currentIndexChanged.connect(lambda idx: OnCol1CurrentIndexChanged(idx))
                col2.valueChanged.connect(lambda val: self.colItems[2].setText(str(val)))
                col3.textChanged.connect(lambda: self.colItems[3].setText(col3.toPlainText()))
                col4.clicked.connect(lambda : self.colItems[4].setText(col4.isChecked().__str__()))
                def OnCol0CurrentIndexChanged(idx):
                    self.colItems[0].setData(col0.currentData(ItemDataRole.UserRole), ItemDataRole.UserRole)
                    self.colItems[0].setText(col0.currentText())
                    InitCol1(col0.currentData(ItemDataRole.UserRole))

                def OnCol1CurrentIndexChanged(idx):
                    self.colItems[1].setData(col1.currentData(ItemDataRole.UserRole), ItemDataRole.UserRole)
                    self.colItems[1].setText(col1.currentText())

                def InitCol1(tmplId):
                    col1.clear()
                    idx = 0
                    if tmplId > 0:
                        fields = funcs.CardTemplateOperation.GetModelFromId(tmplId)["flds"]
                        funcs.Map.do(fields, lambda _field: col1.addItem(_field["name"], (tmplId, _field["ord"])))
                        col1.addItem("ALL_FIELDS", (tmplId, -1))
                    else:
                        funcs.Map.do([("ALL_FIELDS", (-1, -1)), ("FRONT", (-1, -2)), ("BACK", (-1, -3))], lambda col1data: col1.addItem(col1data[0], col1data[1]))
                    col1.setCurrentIndex(idx)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = tag_chooser()
    f.show()
    sys.exit(app.exec_())
