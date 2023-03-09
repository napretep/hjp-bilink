# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'basic_widgets.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 20:43'
"""
from abc import abstractmethod
from dataclasses import dataclass

from ..compatible_import import *
from .. import funcs,baseClass,hookers,funcs2
布局 = 框 = 0
组件 = 件 = 1
子代 = 子 = 2
占 = 占据 = 3
译 = funcs.译
G = funcs.G
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

