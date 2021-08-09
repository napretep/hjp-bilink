# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'deck_chooser.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/6 16:26'
"""
import sys
from dataclasses import dataclass
from typing import Optional
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QIcon, QStandardItem
from PyQt5.QtWidgets import QDialog, QTreeView, QVBoxLayout, QWidget, QLabel, QToolButton, QHBoxLayout, QApplication, \
    QHeaderView
from aqt import mw


class CascadeStr:
    @dataclass
    class Node:
        item: "QStandardItem"
        children: "dict[str,CascadeStr.Node]"


class deck_chooser(QDialog):

    def __init__(self, pair_li: "list[G.objs.LinkDataPair]" = None):
        super().__init__()
        self.view = QTreeView(self)
        self.model = QStandardItemModel(self)
        self.model_rootNode: "Optional[QStandardItemModel.invisibleRootItem]" = None
        self.header = self.Header(self)
        self.header.button.clicked.connect(self.on_header_button_clicked_handle)
        self.view.clicked.connect(self.on_view_clicked_handle)
        self.model.dataChanged.connect(self.on_model_data_changed_handle)
        self.init_UI()
        self.init_model()

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        item: deck_chooser.Item = self.model.itemFromIndex(topLeft)
        print(item.deck_name)

    def on_view_clicked_handle(self, index):
        item: deck_chooser.Item = self.model.itemFromIndex(index)
        print(item.deck_id)

    def on_header_button_clicked_handle(self):
        if self.header.button.text() == self.header.deck_tree:
            self.header.button.setText(self.header.deck_list)
        else:
            self.header.button.setText(self.header.deck_tree)
        self.init_data()

    def init_model(self):
        self.view.setModel(self.model)
        self.model.setHorizontalHeaderLabels(["deckname", "button"])
        # self.view.header().setSectionResizeMode(QHeaderView.Interactive)
        self.view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.view.header().setSectionResizeMode(QHeaderView.Stretch)

        # self.view.header()
        self.init_data()
        # self.model.set
        self.view.setColumnWidth(1, 30)

    def init_data(self):
        self.model.clear()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model.setHorizontalHeaderLabels(["deckname", ""])
        if self.header.button.text() == self.Header.deck_tree:
            self.build_deck_tree()
        else:
            self.build_deck_list()

    def build_deck_list(self):
        deck_li: "list[deck_chooser.Id_deck]" = self.get_all_decks()
        for i in deck_li:
            item = self.Item(i.deck)
            item.deck_id = i.ID
            widget = self.Item("")
            self.model.appendRow([item, widget])
            button = QToolButton(self)
            button.setFixedWidth(25)
            self.view.setIndexWidget(widget.index(), button)

        pass

    def build_deck_tree(self):
        deck_li: "list[deck_chooser.Id_deck]" = self.get_all_decks()
        deck_dict = CascadeStr.Node(self.model_rootNode, {})
        for i in deck_li:
            deckname_li = i.deck.split("::")
            parent = deck_dict
            while deckname_li:
                deckname = deckname_li.pop(0)
                if deckname not in parent.children:
                    item = self.Item(deckname)
                    widget = self.Item("")
                    parent.item.appendRow([item, widget])
                    button = QToolButton(self)
                    button.setFixedWidth(25)
                    self.view.setIndexWidget(widget.index(), button)
                    parent.children[deckname] = CascadeStr.Node(item, {})
                    if not deckname_li:
                        item.deck_id = i.ID
                parent = parent.children[deckname]

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
            return mw.col.decks.all_names_and_ids()[0].name

    def init_UI(self):
        self.setWindowTitle("deck_chooser")
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
            self.desc = QLabel(deckname, self)
            self.desc.setWordWrap(True)
            self.button = QToolButton(self)
            self.button.setText(self.deck_tree)
            H_layout = QHBoxLayout(self)
            H_layout.addWidget(self.desc)
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

    @dataclass
    class Id_deck:
        deck: "str"
        ID: "int"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = deck_chooser()
    p.exec()
    sys.exit(app.exec_())
    pass
