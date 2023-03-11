# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'basic_widgets.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 20:43'
"""
from datetime import datetime

"""
注意: basic中尽量不直接引用其他包, 要用safe的方法
"""
from abc import abstractmethod
from dataclasses import dataclass

from ..compatible_import import *
from ..language import Translate
from .. import G
布局 = 框 = 0
组件 = 件 = 1
子代 = 子 = 2
占 = 占据 = 3
译 = Translate

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



class SimpleSelectorProtoType(SelectorProtoType):

    def on_header_new_item_button_clicked_handle(self):
        pass

    def on_model_data_changed_handle(self, topLeft, bottomRight, roles):
        pass

    def on_view_clicked_handle(self, index):
        pass

    def get_all_data_items(self) -> "list[SelectorProtoType.Id_name]":
        raise NotImplementedError()

    def on_view_doubleclicked_handle(self, index):
        raise NotImplementedError()


class multi_select_prototype(QDialog):
    """TODO item要使用 id_name的格式"""
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
                子: [{框: QVBoxLayout(),
                     子: [{件: self.view_left}, {件: self.left_button_group}]}
                        ,
                    {框: QVBoxLayout(),
                     子: [{件: self.view_right}, {件: self.right_button_group}]}, ],
                }

        G.safe.funcs.组件定制.组件组合(组件布局, self)
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

    def init_data_left(self, init=True):
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
                self.left_button = G.safe.funcs.组件定制.按钮_提示(触发函数=lambda: G.safe.funcs.Utils.大文本提示框(译.说明_多选框的用法))
                self.middle_button = QPushButton(QIcon(G.src.ImgDir.correct), "")
            else:
                self.left_button = QPushButton(QIcon(G.src.ImgDir.item_plus), "")
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
            G.safe.funcs.组件定制.组件组合({框: QHBoxLayout(), 子: [{件: self.left_button}, {件: self.middle_button}, {件: self.arrange_button}]}, self)

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
        ID: "int|str"


