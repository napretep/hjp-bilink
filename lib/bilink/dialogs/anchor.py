# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'anchor.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/1 15:33'
"""
import os
import sys
from typing import Union
from ..imports import *
import json


if __name__ == "__main__":
    from lib import common_tools
    from lib.common_tools.language import rosetta as say
else:
    from ..imports import common_tools, say
    from .. import linkdata_admin

    # from .tools import funcs
    pass


# say = common_tools.language.rosetta


class AnchorDialog(QDialog):
    # 0中间,1上面,-1下面,-2底部
    class POS:
        mid, up, down, bottom = 0, 1, -1, -2

    def __init__(self, card_id, parent=None):
        super().__init__(parent)
        self.card_id = card_id
        # self.linkdata = linkdata_admin.read_card_link_info(str(card_id))
        self.attr = self.Attr(card_id, parent)
        self.state = self.State()
        self.view = QTreeView(self)
        self.model = QStandardItemModel(self)
        # seself.bottomlf.self_desc=QLineEdit(self)
        self.bottom = AnchorDialog.Bottom()
        self.self_desc = common_tools.widgets.GridHDescUnit(parent=self, labelname="self_describe:",
                                                            tooltip="self_describe是这张卡片的名字\n"
                                                                    "self_describe is the name of the card, ",
                                                            widget=self.bottom )
        # self.bottom = QWidget(self)
        self.init_UI()
        self.init_model()
        self.allevent = common_tools.objs.AllEventAdmin([
            [self.view.doubleClicked, self.on_view_doubleclicked_handle],
            [self.view.clicked, self.on_view_clicked_handle],
            [self.view.customContextMenuRequested, self.on_view_show_context_menu],
            [common_tools.G.signals.on_bilink_link_operation_end, self.on_bilink_link_operation_end_handle],
            [self.model.dataChanged, self.on_model_data_changed_handle],
            # self.view.dataChanged:self.on_view_data_changed_handle,#没用,还会报错
            [self.bottom.line.textChanged, self.on_self_desc_text_changed_handle],
            [self.bottom.cbox.clicked,self.on_bottom_cbox_clicked_handle]
        ]).bind()
        self.view.dropEvent = self.on_view_drop
        self.signup()

    def on_bottom_cbox_clicked_handle(self):
        From = common_tools.objs.LinkDescFrom
        if self.bottom.cbox.isChecked():
            self.attr.linkdata.self_data.get_desc_from = From.Field
            tooltip("sync with Field")
        else:
            self.attr.linkdata.self_data.get_desc_from = From.DB
            tooltip("read from DB")

        self.model_data_save()

    def on_view_clicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        print(item)

    def on_view_doubleclicked_handle(self, index: "QModelIndex"):
        item: "AnchorDialog.Item" = self.model.itemFromIndex(index)
        if item.character == item.card_id:
            card_id = item.text()
            common_tools.funcs.Dialogs.open_custom_cardwindow(card_id)

    def on_view_show_context_menu(self, pos: QtCore.QPoint):
        def expand_switch(self: "AnchorDialog"):
            if self.state.view_is_expanded:
                self.view.collapseAll()
            else:
                self.view.expandAll()

        def new_group(self: "AnchorDialog"):
            group = self.Item("new_group", self.Item.group, 0, primData=common_tools.funcs.UUID.by_random())
            item = self.Item("", self.Item.empty, 0, None)
            self.model.appendRow([group, item])

        def delete_selected(self: "AnchorDialog"):
            selected: "list[QModelIndex]" = sorted(self.view.selectedIndexes(), key=lambda x: x.row())
            pindex_li: "list[QPersistentModelIndex]" = [QPersistentModelIndex(index) for index in selected]
            for i in range(0, len(selected), 2):
                item = self.model.itemFromIndex(QModelIndex(pindex_li[i]))
                parent = item.parent() if item.parent() is not None else self.model_rootNode
                # parent = self.model.itemFromIndex(pindex_li[i].parent())
                parent.takeRow(pindex_li[i].row())
            # self.empty_group_check()
            self.model_data_save()

        menu = self.view.contextMenu = QMenu()
        menu.addAction(say("全部展开/折叠")).triggered.connect(lambda: expand_switch(self))
        menu.addAction(say("新建组")).triggered.connect(lambda: new_group(self))

        selected: "list[AnchorDialog.Item]" = self.view.selectedIndexes()
        pair_li = []
        pair = common_tools.objs.LinkDataPair
        for i in range(len(selected)):
            item: "AnchorDialog.Item" = self.model.itemFromIndex(selected[i])
            if item.character == self.Item.card_id:
                desc: "AnchorDialog.Item" = self.model.itemFromIndex(selected[i + 1])
                pair_li.append(pair(card_id=item.text(), desc=desc.text()))  # print(card_id_li)
        if len(selected) > 0:
            selected_menu = menu.addMenu(say("选中操作"))
            selected_menu.addAction(say("删除选中")).triggered.connect(lambda: delete_selected(self))
            if len(pair_li) > 0:
                if __name__ == "__main__":
                    from lib.common_tools.menu import maker, T
                else:
                    from ...common_tools.menu import maker, T
                maker(T.anchor_selected_context)(self.view, selected_menu, pair_li=pair_li, needPrefix=False)

        menu.popup(QCursor.pos())
        menu.show()
        pass

    def on_self_desc_text_changed_handle(self,s):
        print(s)
        self.attr.linkdata.self_data.desc=self.bottom.line.text()

        self.bottom.cbox.setChecked(False)
        self.model_data_save()
        self.setWindowTitle(f"""anchor of [desc={self.bottom.line.text()},card_id={self.card_id}]""")


    def on_bilink_link_operation_end_handle(self):
        self.model_data_load()

    def on_model_data_changed_handle(self):
        self.model_data_save()

    def on_view_drop(self, event: "QtGui.QDropEvent"):
        def on_view_drop_rowli_selected_insert(self, insert_posi, selected_row_li, item_target: "AnchorDialog.Item"):
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
                for row in selected_row_li:
                    row[0].level = self.model_rootNode.level + 1
                    row[1].level = self.model_rootNode.level + 1
                    self.model_rootNode.appendRow(row)

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

        def on_view_drop_rowli_index_make(self):
            """# 源item每次都会选择一行的所有列,而且所有列编成1维数组,所以需要下面的步骤重新组回来."""
            selected_indexes_li = self.view.selectedIndexes()
            selected_items_li = list(map(self.model.itemFromIndex, selected_indexes_li))
            selected_row_li = []
            for i in range(int(len(selected_items_li) / 2)):
                selected_row_li.append([selected_items_li[2 * i], selected_items_li[2 * i + 1]])
            return selected_row_li

        def on_view_drop_item_target_recorrect(self, item_target: "AnchorDialog.Item", insertPosi):
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
            if item_target.character == AnchorDialog.Item.card_id:
                if insertPosi == self.POS.mid: insertPosi = self.POS.down
            return item_target, insertPosi

        pos = event.position().toPoint() if common_tools.compatible_import.Anki.isQt6 else event.pos()
        drop_index = self.view.indexAt(pos)
        item_target = self.model.itemFromIndex(drop_index)  #
        selected_row_li: "list[list[AnchorDialog.Item]]" = on_view_drop_rowli_index_make(self)
        item_source = selected_row_li[0][0]
        insert_posi = on_view_drop_position_insert_check(self, pos, drop_index)
        item_target, insert_posi = on_view_drop_item_target_recorrect(self, item_target, insert_posi)
        parent = item_target
        while parent is not None:
            if parent == item_source:
                return
            else:
                parent = parent.parent()
        on_view_drop_rowli_selected_insert(self, insert_posi, selected_row_li, item_target)
        self.model_data_save()
        self.view.expandAll()

    def itemChild_row_remove(self, item):
        """不需要parent,自己能产生parent"""
        parent = item[0].parent() if item[0].parent() is not None else self.model
        return parent.takeRow(item[0].row())

    def data_model_load(self):
        """model->data"""
        def load_group(self: "AnchorDialog", parent: "AnchorDialog.Item", tempdict, nodeuuid: "str"):
            total_row = parent.rowCount()
            for i in range(total_row):
                item0: "AnchorDialog.Item" = parent.child(i, 0)
                item1: "AnchorDialog.Item" = parent.child(i, 1)
                if item0.character == self.Item.card_id:
                    tempdict["link_list"].append({"card_id": item0.text(), "desc": item1.text()})
                    tempdict["node"][nodeuuid]["children"].append({"card_id": item0.text()})
                elif item0.character == self.Item.group:
                    tempdict["node"][nodeuuid]["children"].append({"nodeuuid": item0.primData})
                    tempdict["node"][item0.primData] = {"name": item0.text(), "children": []}
                    load_group(self, item0, tempdict, item0.primData)

        total_row = self.model.rowCount()
        tempdict = linkdata_admin.get_template(self.card_id, desc=self.bottom.line.text())
        tempdict["backlink"] = self.attr.linkdata.backlink
        tempdict["version"] = self.attr.linkdata.version
        tempdict["self_data"] = self.attr.linkdata.self_data.to_self_dict()# {"card_id":self.card_id,"desc":self.self_desc.text()}

        for i in range(total_row):
            item0: "AnchorDialog.Item" = self.model.item(i, 0)
            item1: "AnchorDialog.Item" = self.model.item(i, 1)
            if item0.character == self.Item.card_id:
                tempdict["root"].append({"card_id": item0.text()})
                tempdict["link_list"].append({"card_id": item0.text(), "desc": item1.text()})
            elif item0.character == self.Item.group:
                tempdict["root"].append({"nodeuuid": item0.primData})
                tempdict["node"][item0.primData] = {"name": item0.text(), "children": []}
                load_group(self, item0, tempdict, item0.primData)
        return tempdict
        pass

    def model_data_load(self):
        """data->model"""
        From = common_tools.objs.LinkDescFrom
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["card", "desc"])
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.character = -1
        self.model_rootNode.level = -1
        self.model_rootNode.primData = None
        desc2 = common_tools.funcs.CardOperation.desc_extract(self.card_id)
        self.bottom.line.setText(desc2)
        self.bottom.cbox.setChecked(self.attr.linkdata.self_data.get_desc_from==From.Field)
        def load_group(self, item: "common_tools.objs.LinkDataNode", parent: "AnchorDialog.Item"):
            if item.card_id:
                desc2 = common_tools.funcs.CardOperation.desc_extract(item.card_id)
                descitem = self.Item(desc2, self.Item.desc, parent.level + 1)
                carditem = self.Item(item.card_id, self.Item.card_id, parent.level + 1)
                parent.appendRow([carditem, descitem])
                self.card_mapping(item.card_id,carditem)
            elif item.nodeuuid:
                groupitem = self.Item(self.attr.linkdata.node[item.nodeuuid].name, self.Item.group, parent.level + 1,
                                      primData=item.nodeuuid)
                emptyitem = self.Item("", self.Item.empty, parent.level + 1)
                parent.appendRow([groupitem, emptyitem])
                for subitem in self.attr.linkdata.node[item.nodeuuid].children:
                    load_group(self, subitem, groupitem)

        for item in self.attr.linkdata.root:
            if item.card_id:
                desc2 = common_tools.funcs.CardOperation.desc_extract(item.card_id)
                descitem = self.Item(desc2, self.Item.desc, 0)
                carditem = self.Item(item.card_id, self.Item.card_id, 0)
                self.model.appendRow([carditem, descitem])
                self.card_mapping(item.card_id,carditem)
            elif item.nodeuuid:
                groupitem = self.Item(self.attr.linkdata.node[item.nodeuuid].name, self.Item.group, 0,
                                      primData=item.nodeuuid)
                emptyitem = self.Item("", self.Item.empty, 0)
                self.model.appendRow([groupitem, emptyitem])
                for subitem in self.attr.linkdata.node[item.nodeuuid].children:
                    load_group(self, subitem, groupitem)

        pass

    def model_data_save(self):
        """model->data"""
        from .. import linkdata_admin
        data = json.dumps(self.data_model_load())
        print(data)
        linkdata_admin.write_card_link_info(self.card_id, data)
        common_tools.funcs.LinkPoolOperation.both_refresh(0,2)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.signout()
        self.model_data_save()
        common_tools.funcs.CardOperation.refresh()
    def reject(self) -> None:
        self.close()
        super().reject()

    def signup(self):
        """注册到主窗口"""

        card_id = self.card_id
        common_tools.G.mw_anchor_window[card_id] = self
        # mw.__dict__[addonName][dialog][card_id] = self

    def signout(self):
        """注销"""

        card_id = self.card_id
        common_tools.G.mw_anchor_window[card_id] = None

    def setupBottom(self):
        bottom= QWidget()

    def card_mapping(self,card_id,item):
        self.attr.card_dict[card_id] = item

    def init_UI(self):
        self.setAttribute(Qt.WA_DeleteOnClose, on=True)
        self.setWindowIcon(QIcon(common_tools.G.src.ImgDir.anchor))
        self.setWindowTitle(f"""anchor of [desc={self.attr.linkdata.self_data.desc},card_id={self.card_id}]""")
        self.setAcceptDrops(True)
        self.view.setSelectionMode(common_tools.compatible_import.QAbstractItemViewSelectMode.ExtendedSelection)
        self.view.setDragDropMode(common_tools.compatible_import.DragDropMode.DragDrop)
        self.view.setIndentation(8)
        self.view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setContentsMargins(0,0,0,0)
        func_wrapper = common_tools.wrappers.func_wrapper
        self.view.expandAll = func_wrapper(after=[lambda: self.state.__setattr__("view_is_expanded", True)])(
            self.view.expandAll)
        self.view.collapseAll = func_wrapper(after=[lambda: self.state.__setattr__("view_is_expanded", False)])(
            self.view.collapseAll)
        v = QVBoxLayout(self)
        v.addWidget(self.view)
        v.addWidget(self.self_desc)
        self.setLayout(v)

        self.resize(600, 400)

    def init_model(self):
        self.view.setModel(self.model)
        self.model_data_load()
        self.view.expandAll()

    class Bottom(QWidget):
        def __init__(self):
            super().__init__()
            self.line = QLineEdit(self)
            self.cbox = QRadioButton(common_tools.funcs.Translate.自动更新描述)
            self.setContentsMargins(0,0,0,0)
            self.cbox.setContentsMargins(0,0,0,0)
            self.line.setContentsMargins(0,0,0,0)
            h_layout = QHBoxLayout(self)
            h_layout.setContentsMargins(0,0,0,0)
            h_layout.addWidget(self.line,stretch=29)
            h_layout.addWidget(self.cbox,stretch=1)
            self.setLayout(h_layout)

    class Attr:
        def __init__(self, card_id, parent):
            self.linkdata = linkdata_admin.read_card_link_info(str(card_id))
            self.card_dict: "dict[str,Union[AnchorDialog.Item,QStandardItem]]" = {}  # 卡片与对应的结点, 必须是唯一的.这个数据需要更新
            self.parent = parent

    class State:
        anchorDataIsEmpty = False
        view_is_expanded = False

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
            if character in {self.card_id, self.empty}: self.setFlags(self.flags() & ~Qt.ItemIsEditable)
            if character in {self.desc, self.empty}: self.setFlags(self.flags() & ~Qt.ItemIsDropEnabled)

        def __repr__(self):
            return f"""<{self.text()},{self.chara[self.character]},level={self.level}>"""



if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = AnchorDialog("0")
    # p=VersionDialog()
    p.exec()
    sys.exit(app.exec_())
    pass
