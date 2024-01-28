# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'linkpool.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/1 15:36'
"""
import os
import sys

from ..imports import common_tools
Anki = common_tools.compatible_import.Anki
if Anki.isQt6:
    from PyQt6 import QtGui, QtCore
    from PyQt6.QtCore import Qt, QPoint, QModelIndex, QFileSystemWatcher, QPersistentModelIndex
    from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QCursor
    from PyQt6.QtWidgets import QDialog, QAbstractItemView, QApplication, QHBoxLayout, QTreeView, QLineEdit, \
        QVBoxLayout, \
        QHeaderView, QMenu
else:
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtCore import Qt, QPoint, QModelIndex, QFileSystemWatcher, QPersistentModelIndex
    from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QCursor
    from PyQt5.QtWidgets import QDialog, QAbstractItemView, QApplication, QHBoxLayout, QTreeView, QLineEdit, QVBoxLayout, \
QHeaderView, QMenu
import json

if __name__ == "__main__":
    from lib import common_tools
    from lib.common_tools.language import rosetta as say
else:
    from ..imports import common_tools, say

    # from .tools import funcs
    pass


# say = common_tools.language.rosetta

class LinkPoolDialog(QDialog):
    class POS:
        mid, up, down, bottom = 0, 1, -1, -2

    def __init__(self, data=None):
        super().__init__()
        self.argument_data = data
        self.view = QTreeView(self)
        self.model = QStandardItemModel(self)
        self.model_rootNode = None
        self.tag = common_tools.widgets.GridHDescUnit(parent=self, labelname="tag:",
                                                      tooltip="在这里编辑执行链接操作时要添加的标签,如果为空则默认添加时间戳\n"
                                                              "Edit the tag that to be inserted during the link operation, "
                                                              "and add a timestamp by default if it is empty",
                                                      widget=QLineEdit())
        self.state = self.State()
        self.init_UI()
        self.init_model()
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath(common_tools.G.src.path.linkpool_file)
        # .connect(self.model_dataobj_load)
        self.allevent = common_tools.objs.AllEventAdmin([
            [self.model.dataChanged, self.on_model_data_changed_handle],
            [self.fileWatcher.fileChanged, self.on_file_changed_handle],
            [self.tag.widget.textChanged, self.on_model_data_changed_handle],
            [self.view.doubleClicked, self.on_view_doubleclicked_handle],
            [self.view.clicked, self.on_view_clicked_handle],
            [self.view.customContextMenuRequested, self.on_view_show_context_menu],
        ]).bind()
        self.view.dropEvent = self.on_view_drop

    def on_view_doubleclicked_handle(self, index):
        item: "LinkPoolDialog.Item" = self.model.itemFromIndex(index)
        # showInfo(f"{item.character},{item.text()}")
        if item.character == item.card_id:
            card_id = item.text()
            common_tools.funcs.Dialogs.open_custom_cardwindow(card_id)

    def on_view_clicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        print(item)

    def on_view_show_context_menu(self, pos):
        def expand_switch(self: "LinkPoolDialog"):
            if self.state.view_is_expanded:
                self.view.collapseAll()
            else:
                self.view.expandAll()

        def delete_selected(self: "LinkPoolDialog"):
            selected: "list[QModelIndex]" = sorted(self.view.selectedIndexes(), key=lambda x: x.row())
            pindex_li: "list[QPersistentModelIndex]" = [QPersistentModelIndex(index) for index in selected]
            for i in range(0, len(selected), 2):
                parent = self.model.itemFromIndex(pindex_li[i].parent())
                parent.takeRow(pindex_li[i].row())
            self.empty_group_check()
            self.model_data_save()

        menu = self.view.contextMenu = QMenu()
        menu.addAction(say("全部展开/折叠")).triggered.connect(lambda: expand_switch(self))

        selected: "list[LinkPoolDialog.Item]" = self.view.selectedIndexes()
        pair_li = []
        pair = common_tools.objs.LinkDataPair
        for i in range(len(selected)):
            item: "LinkPoolDialog.Item" = self.model.itemFromIndex(selected[i])
            if item.character == self.Item.card_id:
                desc: "LinkPoolDialog.Item" = self.model.itemFromIndex(selected[i + 1])
                pair_li.append(pair(card_id=item.text(), desc=desc.text()))

        if __name__ == "__main__":
            from lib.common_tools.menu import maker, T
        else:
            from ...common_tools.menu import maker, T
        global_menu = menu.addMenu(say("全局操作"))
        tag = self.tag.widget.text()
        maker(T.linkpool_context)(self.view, global_menu, pair_li=self.pair_li, needPrefix=False, tag=tag)
        if len(pair_li) > 0:
            selected_menu = menu.addMenu(say("选中操作"))
            selected_menu.addAction(say("删除选中")).triggered.connect(lambda: delete_selected(self))
            maker(T.linkpool_selected_context)(self.view, selected_menu, pair_li=pair_li, needPrefix=False, tag=tag)

        menu.popup(QCursor.pos())
        menu.show()

    def on_file_changed_handle(self):
        self.model_data_load(self.data_read())
        self.view.expandAll()

    @property
    def pair_li(self):
        data = self.data_read()
        d = []
        for group in data["IdDescPairs"]:
            for pair in group:
                d.append(common_tools.objs.LinkDataPair(**pair))
        return d

    def data_read(self):
        if self.argument_data is not None:
            data = self.argument_data
        else:
            data = json.load(open(common_tools.G.src.path.linkpool_file, "r", encoding="utf8"))
        return data

    def on_view_drop(self, event: "QtGui.QDropEvent"):
        def on_view_drop_rowli_index_make(self):
            selected_indexes_li = self.view.selectedIndexes()
            selected_items_li = list(map(self.model.itemFromIndex, selected_indexes_li))
            selected_row_li = []
            for i in range(int(len(selected_items_li) / 2)):
                selected_row_li.append([selected_items_li[2 * i], selected_items_li[2 * i + 1]])
            return selected_row_li

        def on_view_drop_position_insert_check(self, pos, drop_index):
            """测定插入位置"""
            index_height = self.view.rowHeight(drop_index)  #
            drop_index_offset_up = self.view.indexAt(pos - QPoint(0, int(index_height / 4)))  # 高处为0
            drop_index_offset_down = self.view.indexAt(pos + QPoint(0, int(index_height / 4)))
            insertPosi = self.POS.mid  # 0中间,1上面,-1下面,-2底部
            if drop_index_offset_down == drop_index_offset_up:
                insertPosi = self.POS.mid
            else:
                if drop_index != drop_index_offset_up:
                    insertPosi = self.POS.up
                elif drop_index != drop_index_offset_down:
                    insertPosi = self.POS.down
            return insertPosi

        def on_view_drop_item_target_recorrect(self, item_target: "LinkPoolDialog.Item", insertPosi):
            """修正插入的对象和插入的位置"""
            # 拉到底部
            if item_target is None:
                insertPosi = self.POS.bottom
                item_target = self.model_rootNode
            else:
                parent = item_target.parent()
                if parent is None:
                    item_target = self.model.item(item_target.row(), 0)
                else:
                    item_target = parent.child(item_target.row(), 0)
            if item_target.character == LinkPoolDialog.Item.card_id:
                if insertPosi == self.POS.mid: insertPosi = self.POS.down
            if item_target.character == LinkPoolDialog.Item.group:
                if insertPosi == self.POS.down:
                    item_target = item_target.child(0)
                    insertPosi = self.POS.up
                elif insertPosi == self.POS.up:
                    if item_target.row() > 0:
                        parent = self.model.item(item_target.row() - 1, 0)
                        item_target = parent.child(parent.rowCount() - 1)
                        insertPosi = self.POS.down
                    else:
                        group = self.Item("group", self.Item.group, 0, None)
                        empty = self.Item("", self.Item.empty, 0, None)
                        insertPosi = self.POS.mid
                        self.model.insertRow(0, [group, empty])
                        item_target = self.model.item(0)
            return item_target, insertPosi

        def on_view_drop_rowli_selected_insert(self, insert_posi, selected_row_li, item_target: "LinkPoolDialog.Item"):
            for row in selected_row_li: self.itemChild_row_remove(row)  # 将他们从原来的位置取出
            temp_rows_li = []
            if insert_posi == self.POS.mid:  # 中间
                for row in selected_row_li:
                    row[0].level = item_target.level + 1
                    row[1].level = item_target.level + 1
                    item_target.appendRow(row)
            elif insert_posi != self.POS.bottom:
                for row in selected_row_li:  # 不在中间,不在底边,就在上下两边,因此是同级的
                    row[0].level = item_target.level
                    row[1].level = item_target.level
                posi_row = item_target.row()
                parent = item_target.parent() if item_target.parent() else self.model_rootNode
                while parent.rowCount() > 0:
                    temp_rows_li.append(parent.takeRow(0))
                if insert_posi == self.POS.up:  # 上面
                    final_rows_li = temp_rows_li[0:posi_row] + selected_row_li + temp_rows_li[posi_row:]
                else:
                    final_rows_li = temp_rows_li[0:posi_row + 1] + selected_row_li + temp_rows_li[posi_row + 1:]
                for row in final_rows_li:
                    parent.appendRow(row)
            else:
                group: "LinkPoolDialog.Item" = self.Item("group", self.Item.group, 0, None)
                empty = self.Item("", self.Item.empty, 0, None)
                for row in selected_row_li:
                    row[0].level = 1
                    row[1].level = 1
                    group.appendRow(row)
                    # self.model_rootNode.appendRow(row)
                self.model.appendRow([group, empty])
        # from PyQt6.QtGui import QDropEvent

        pos = event.position().toPoint() if common_tools.compatible_import.Anki.isQt6 else event.pos()
        drop_index = self.view.indexAt(pos)
        item_target = self.model.itemFromIndex(drop_index)  #
        insert_posi = on_view_drop_position_insert_check(self, pos, drop_index)
        item_target, insert_posi = on_view_drop_item_target_recorrect(self, item_target, insert_posi)
        selected_row_li: "list[list[LinkPoolDialog.Item]]" = on_view_drop_rowli_index_make(self)
        item_source = selected_row_li[0][0]
        parent = item_target
        while parent is not None:
            if parent == item_source:
                return
            else:
                parent = parent.parent()
        on_view_drop_rowli_selected_insert(self, insert_posi, selected_row_li, item_target)
        self.empty_group_check()
        self.model_data_save()
        self.view.expandAll()
        pass

    def empty_group_check(self):
        total = self.model.rowCount()
        for i in range(total - 1, -1, -1):
            if self.model.item(i, 0).rowCount() == 0:
                self.model.takeRow(i)

    def itemChild_row_remove(self, item):
        """不需要parent,自己能产生parent"""
        parent = item[0].parent() if item[0].parent() is not None else self.model_rootNode
        return parent.takeRow(item[0].row())

    def on_model_data_changed_handle(self):
        self.model_data_save()
        pass

    def init_UI(self):

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, on=True)
        self.setWindowTitle(common_tools.funcs.译.双链分组器)
        self.setWindowIcon(QIcon(common_tools.G.src.ImgDir.input))
        self.setAcceptDrops(True)
        self.view.setSelectionMode(common_tools.compatible_import.QAbstractItemViewSelectMode.ExtendedSelection)
        self.view.setDragDropMode(common_tools.compatible_import.DragDropMode.DragDrop)
        self.view.setIndentation(8)
        self.view.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        V = QVBoxLayout(self)
        V.addWidget(self.view)
        V.addWidget(self.tag)
        self.setLayout(V)
        func_wrapper = common_tools.wrappers.func_wrapper
        self.view.expandAll = func_wrapper(after=[lambda: self.state.__setattr__("view_is_expanded", True)])(
            self.view.expandAll)
        self.view.collapseAll = func_wrapper(after=[lambda: self.state.__setattr__("view_is_expanded", False)])(
            self.view.collapseAll)
        self.resize(600, 400)

    def init_model(self):
        self.view.setModel(self.model)
        self.model_data_load(self.data_read())
        self.view.expandAll()

    def model_data_load(self, data: "dict" = None):
        self.model.clear()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.character = -1
        self.model_rootNode.level = -1
        self.model_rootNode.primData = None
        self.model.setHorizontalHeaderLabels(["card_id", "desc"])
        self.tag.widget.setText(data["addTag"])
        data1 = data["IdDescPairs"]
        for group in data1:
            groupitem = self.Item("group", self.Item.group, 0)
            empty = self.Item("", self.Item.empty, 0)
            for pair in group:
                carditem = self.Item(pair["card_id"], self.Item.card_id, 1)
                descitem = self.Item(pair["desc"], self.Item.desc, 1)
                groupitem.appendRow([carditem, descitem])
            self.model.appendRow([groupitem, empty])

    def model_data_save(self):
        data = self.data_model_load()
        self.fileWatcher.blockSignals(True)
        try:
            json.dump(data, open(common_tools.G.src.path.linkpool_file, "w", encoding="utf-8"),
                      ensure_ascii=False, sort_keys=True, indent=4)
        except Exception:
            print("json读取错误")

        self.fileWatcher.blockSignals(False)

    def data_model_load(self):
        d = []
        total = self.model.rowCount()
        for i in range(total):
            group = []
            groupitem = self.model.item(i, 0)
            childtotal = groupitem.rowCount()

            for j in range(childtotal):
                group.append({
                    "card_id": groupitem.child(j, 0).text(),
                    "desc": groupitem.child(j, 1).text(),
                    "dir": "→"
                })
            d.append(group)
        return {
            "IdDescPairs": d,
            "addTag": self.tag.widget.text()
        }

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.model_data_save()
        common_tools.G.mw_linkpool_window = None

    def reject(self) -> None:
        self.close()
        self.reject()

    class Item(QStandardItem):
        card_id, desc, group, empty = 0, 1, 2, 3
        chara = {
            card_id: "card_id", desc: "desc", group: "group", empty: "empty"
        }

        def __init__(self, name, character, level=0, primData=None):
            super().__init__(name)
            self.character = character
            self.level = level
            self.primData = primData

            if character in {self.card_id, self.empty, self.group}: self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if character in {self.desc, self.empty}: self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            if character in {self.group, self.empty, self.desc}: self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            if character in {self.group, self.empty}: self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        def __repr__(self):
            return f"""<{self.text()},{self.chara[self.character]},level={self.level}>"""

    class State:
        anchorDataIsEmpty = False
        view_is_expanded = False

    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = {
        "IdDescPairs": [
            [
                {
                    "card_id": "1627401415334",
                    "desc": "[[link:1627437000208_[[link:1627",
                    "dir": "→"
                }
            ],
            [
                {
                    "card_id": "1627401416855",
                    "desc": " [[link:1627401415334__]] [[link",
                    "dir": "→"
                }
            ],
            [
                {
                    "card_id": "1627437000208",
                    "desc": "[[link:1627437000208_123123_]]12",
                    "dir": "→"
                }
            ],
            [
                {
                    "card_id": "1627437034945",
                    "desc": "",
                    "dir": "→"
                }
            ]
        ],
        "addTag": "没关系"
    }
    p = LinkPoolDialog()
    p.exec()
    sys.exit(app.exec_())
    pass
