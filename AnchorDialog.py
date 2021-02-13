"""
TODO:
    对话框,读取JSON,拖拽,双击修改,双击打开,右键删除,自动保存,
"""

from .inputObj import *
from .anchordialog_UI import Ui_anchor


class AnchorDialog(QDialog, Ui_anchor):
    """锚点数据调整的对话框"""
    linkedEvent = CustomSignals.start().linkedEvent

    def __init__(self, pair: Pair, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.input = Input()
        self.parent = parent
        self.model_subgroupdict = {}
        self.baseinfo = self.input.baseinfo
        self.customSignals = CustomSignals()
        self.pair = pair
        self.pair.desc = self.input.desc_extract(self.pair)
        self.signup()
        self.model_dataJSON: Dict[str, List[Dict]] = {}
        self.field_dataPairLi: List[Pair] = []
        self.HTMLmanage = self.input.HTMLmanage
        self.cfg = self.baseinfo.config_obj
        self.undo_stack: List[dict] = []
        self.init_UI()
        self.init_model()
        self.init_events()
        self.show()

    def signup(self):
        """注册到主窗口"""
        addonName = self.baseinfo.dialogName
        dialog = self.__class__.__name__
        card_id = self.pair.card_id
        mw.__dict__[addonName][dialog][card_id] = self

    def signout(self):
        """注销"""
        addonName = self.baseinfo.dialogName
        dialog = self.__class__.__name__
        card_id = self.pair.card_id
        mw.__dict__[addonName][dialog][card_id] = None

    def init_UI(self):
        self.setupUi(self)
        self.setWindowTitle(f"Anchor of [desc={self.pair.desc},card_id={self.pair.card_id}]")

    def init_events(self):
        """响应右键菜单,拖拽,绑定更新数据,思考如何实现变化后自动加载.如果实现不了,暂时先使用模态对话框 """
        self.closeEvent = self.onClose
        self.anchorTree.dropEvent = self.onDrop
        self.anchorTree.customContextMenuRequested.connect(self.onAnchorTree_contextMenu)
        self.linkedEvent.connect(self.onRebuild)
        self.model.dataChanged.connect(self.field_model_save)

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def onClose(self, QCloseEvent):
        """保存数据,并且归零"""
        self.pairLi_model_load().field_pairLi_save()
        self.signout()

    def onRebuild(self):
        self.init_model()

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def onDrop(self, *args, **kwargs):
        """掉落事件响应"""

        def gowithcard(parent, item_target, item_finalLi):
            """对于卡片来说,group是最顶层,card 0, 1层都可以"""
            if item_target.self_attrs["character"] == "subgroup":
                for row in item_finalLi:
                    item_target.appendRow(row)
            else:
                self.itemChild_row_insert(parent, item_target, item_finalLi)

        def gowithgroup(parent, item_target, item_finalLi):
            """对于组来说,不能放到1层,如果碰到1层应该上升层级"""
            if item_target.self_attrs["level"] == 1:
                item_target = parent
            parent = self.model_rootNode
            self.itemChild_row_insert(parent, item_target, item_finalLi)

        gogroupcard_dict = {
            "card_id": gowithcard,
            "subgroup": gowithgroup
        }

        e = args[0]
        drop_row = self.anchorTree.indexAt(e.pos())
        item_target = self.model.itemFromIndex(drop_row)
        root = self.model_rootNode
        if item_target is not None:
            parent = item_target.parent() if item_target.parent() is not None else self.model_rootNode
        else:
            parent = root

        selectedIndexesLi = self.anchorTree.selectedIndexes()
        selectedItemLi_ = list(map(self.model.itemFromIndex, selectedIndexesLi))
        selectedItemLi = []
        for i in range(int(len(selectedItemLi_) / 2)):
            selectedItemLi.append([selectedItemLi_[2 * i], selectedItemLi_[2 * i + 1]])
        groupItemLi, cardItemLi = [], []
        list(map(lambda x: groupItemLi.append(x) if x[0].self_attrs["character"] == "subgroup"
        else cardItemLi.append(x), selectedItemLi))
        item_finalLi_ = groupItemLi if len(cardItemLi) == 0 else cardItemLi  # 要么全是card,要么全是group,优先考虑card
        item_finalLi = [self.itemChild_row_remove(i) for i in item_finalLi_]
        group_or_card = item_finalLi[0][0].self_attrs["character"]
        if item_target is not None:
            gogroupcard_dict[group_or_card](parent, item_target, item_finalLi)
        else:
            for i in item_finalLi: root.appendRow(i)
        j, emptyremoved = 0, False
        for i in range(root.rowCount()):
            if root.child(j, 0).self_attrs["character"] == "subgroup" and root.child(j, 0).rowCount() == 0:
                del self.model_subgroupdict[root.child(j, 0).text()]
                root.takeRow(j)
                emptyremoved = True
            else:
                j += 1
            if j == root.rowCount(): break
        if emptyremoved: console(say("空组已移除")).talk.end()
        self.pairLi_model_load()
        self.field_pairLi_save()

    def onAnchorTree_contextMenu(self, *args, **kwargs):
        """初始化右键菜单"""
        menu = self.anchorTree.contextMenu = QMenu()
        prefix = BaseInfo().consolerName
        menu.addAction(prefix + say("全部展开/折叠")).triggered.connect(self.view_expandCollapse_toggle)
        menu.addAction(prefix + say("新建组")).triggered.connect(self.model_group_create)
        menu.popup(QCursor.pos())
        menu.show()

    def itemChild_row_remove(self, item):
        """不需要parent,自己能产生parent"""
        parent = item[0].parent() if item[0].parent() is not None else self.model_rootNode
        return parent.takeRow(item[0].row())

    def itemChild_row_insert(self, parent, item_after, item_insertLi):
        """自己实现了一个插入"""
        templi, r = [], item_after.row()
        item_after_row = [parent.child(r, 0), parent.child(r, 1)]
        while parent.rowCount() > 0:
            row0 = parent.takeRow(0)
            # if item_after == row0[0]:
            # showInfo(f"item_after={item_after.text()}  row0[0]={row0[0].text()}")
            templi.append(row0)
        [templi.remove(i) if i in templi else None for i in item_insertLi]
        # showInfo("item_after="+item_after.text()+"item_after_row="+item_after_row.__str__())
        if item_after_row[0] != None:
            index = templi.index(item_after_row)
        else:
            index = len(templi)
        templi = templi[0:index + 1] + item_insertLi + templi[index + 1:]
        for i in templi:
            parent.appendRow(i)

    def model_group_create(self):
        """create group to model"""
        newgroupname = "new_group"
        while newgroupname in self.model_subgroupdict:
            newgroupname = "new_" + newgroupname
        group = QStandardItem(newgroupname)
        group.self_attrs = {
            "level": 0,
            "character": "subgroup",
            "new": True
        }
        empty = QStandardItem("")
        empty.setFlags(empty.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDropEnabled)
        self.model_subgroupdict[group.text()] = group
        self.model_rootNode.appendRow([group, empty])

    def view_expandCollapse_toggle(self):
        if self.treeIsExpanded:
            root = self.model_rootNode
            tree = self.anchorTree
            list(map(lambda i: tree.collapse(root.child(i).index()), list(range(root.rowCount()))))
            self.treeIsExpanded = False
        else:
            self.anchorTree.expandAll()
            self.treeIsExpanded = True

    def init_model(self, *args, **kwargs):
        """模型数据的初始化"""
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model.setHorizontalHeaderLabels(["id", "desc"])
        self.anchorTree.setModel(self.model)
        self.model_JSON_load()
        self.anchorTree.expandAll()
        self.treeIsExpanded = True

    def JSON_field_load(self):
        """从笔记中读取保存好的JSON数据,需要input读取数据,HTML进行转化"""
        self.model_dataJSON = {}
        note = self.input.note_id_load(self.pair)
        self.HTMLmanage.clear().feed(note.fields[self.cfg.readDescFieldPosition])
        self.HTMLmanage.HTMLdata_load()
        for card_obj in self.HTMLmanage.card_linked_pairLi:
            subgroup = card_obj.subgroup if "subgroup" in card_obj else ""
            if subgroup not in self.model_dataJSON:
                self.model_dataJSON[subgroup] = []
            self.model_dataJSON[subgroup].append(card_obj.__dict__)

    def pairLi_model_load(self):
        """从Model中读取"""
        tempdict = []
        root = self.model_rootNode
        for i in range(root.rowCount()):
            if root.child(i, 0).self_attrs["character"] == "subgroup":
                group = root.child(i, 0)
                for j in range(group.rowCount()):
                    tempdict.append(
                        Pair(card_id=group.child(j, 0).text(),
                             desc=group.child(j, 1).text(),
                             subgroup=group.text(),
                             **group.child(j, 0).self_attrs["primData"]
                             )
                    )
            else:
                tempdict.append(Pair(card_id=root.child(i, 0).text(),
                                     desc=root.child(i, 1).text(),
                                     **root.child(i, 0).self_attrs["primData"]))
        self.field_dataPairLi = tempdict
        return self

    def model_JSON_load(self):
        """从JSON读取数据保存到模型中展示"""
        self.JSON_field_load()
        self.model_rootNode.clearData()
        self.model.removeRows(0, self.model.rowCount())
        index_dict = {}
        for subgroup, cardLi in self.model_dataJSON.items():
            for card in cardLi:
                item_id, item_desc = QStandardItem(card["card_id"]), QStandardItem(card["desc"])
                item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDropEnabled)
                item_desc.setFlags(item_desc.flags() & ~Qt.ItemIsDropEnabled & ~Qt.ItemIsDragEnabled)
                item_id.self_attrs, item_desc.self_attrs = {}, {}
                del card["card_id"]
                del card["desc"]
                item_id.self_attrs = {"character": "card_id"}
                item_desc.self_attrs = {"character": "desc"}
                if subgroup != "":
                    del card["subgroup"]
                    item_id.self_attrs["level"], item_desc.self_attrs["level"] = 1, 1
                    if subgroup not in index_dict:
                        item_subgroup = QStandardItem(subgroup)
                        item_subgroup.self_attrs = {}
                        item_subgroup.self_attrs["level"], item_subgroup.self_attrs["character"] = 0, "subgroup"
                        empty = QStandardItem("")
                        empty.setFlags(empty.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDropEnabled)
                        self.model.appendRow([item_subgroup, empty])
                        index_dict[subgroup] = item_subgroup
                    item_subgroup.appendRow([item_id, item_desc])
                else:
                    item_id.self_attrs["level"], item_desc.self_attrs["level"] = 0, 0
                    self.model.appendRow([item_id, item_desc])
                item_id.self_attrs["primData"] = card
        self.model_subgroupdict = index_dict

    def groupEmpty_check(self):
        """为空检查"""
        pass

    def modelChanged_check(self, *args, **kwargs):
        """进行检查,及时合并名字相同的组 参数1,2是topLeft,bottomRight,如果没有处理ondrop事件,则会顺到这里来解决"""
        e = args[0]  #
        item_src = self.model.itemFromIndex(e)
        f = self.model_subgroupdict
        chr, txt = item_src.self_attrs["character"], item_src.text()
        if chr == "subgroup":
            src_key = list(f.keys())[list(f.values()).index(item_src)]
            if re.search(r"\W", txt):
                console(say("抱歉,组名中暂时不能用空格与标点符号,否则会报错")).talk.end()
                item_src.setText(src_key)
                return
            del f[src_key]
            if txt in f:
                item_target = f[txt]
                subitem_li = list(
                    map(lambda x: self.QItem_remove(x), [item_src.child(i) for i in range(item_src.rowCount())]))
                list(map(lambda x: item_target.appendRow(x), subitem_li))
                self.model_rootNode.takeRow(item_src.row())
                console(say("同名组已合并")).talk.end()
            else:
                f[txt] = item_src

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def field_model_save(self, *args, **kwargs):
        """把model保存到Field"""
        self.modelChanged_check(*args, **kwargs)
        self.pairLi_model_load()
        self.field_pairLi_save()

    def field_pairLi_save(self):
        """save pairli to field"""
        note = self.input.note_id_load(self.pair)
        self.HTMLmanage.clear().feed(note.fields[self.cfg.readDescFieldPosition])
        self.HTMLmanage.HTMLdata_load().card_linked_pairLi = self.field_dataPairLi
        note.fields[self.cfg.readDescFieldPosition] = self.HTMLmanage.HTMLdata_save().HTML_get().HTML_text
        note.flush()

    def QItem_remove(self, item: QStandardItem):
        """移除孩子呗"""
        if type(item) == list:
            item = item[0]
        if item.parent() is not None:
            return item.parent().takeRow(item.row())
        else:
            return self.model_rootNode.takeRow(item.row())

    def item_delete(self):
        """删除item"""
        pass
