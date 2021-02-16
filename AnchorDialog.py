"""
TODO:
    对话框,读取JSON,拖拽,双击修改,双击打开,右键删除,自动保存,
TODO 20210216180715 新建group存在bug,需要修改:当我删去旧的group,新命名不会回到旧的.

selfdata数据结构:
    menu:是一个列表, 由cardinfo和groupinfo构成
    groupinfo:是一个字典,每个键是一个groupname,对应一个列表,里面是cardinfo

model_dataJSON: HTMLmanage读取的HTML文本转换为JSON保存于此
model_dataobj: 从model_dataJSON 读取数据转换为对象属性,保存于此
            - groupinfo
                - group_name
                    - menuli:List[card_id]
                    - model_item:QStandardItem
                    - self_name:group_name
                ...
            - menuli: List[card_id or group_name, type]#Menuli 只提供一个引导作用.
            - cardinfo:Dict[card_id:pair]#大部分信息都在这里
linked_pairLi: 导出到HTML需要
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
        self.busy = False
        self.HTMLmanage = self.input.HTMLmanage
        self.cfg = self.baseinfo.config_obj
        self.pairdict: Dict = {}
        self.model_dataobj: Dict = {}  # 从model_dataJSON读取保存为对象模型.
        self.model_dataJSON: Dict[str, List[Dict]] = {}
        self.model_linked_pairLi: List[Pair] = []
        self.undo_stack: List[dict] = []
        self.init_UI()
        self.init_model()
        self.init_events()
        self.signup()
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
        # self.closeEvent = self.onClose
        self.anchorTree.dropEvent = self.onDrop
        self.anchorTree.customContextMenuRequested.connect(self.onAnchorTree_contextMenu)
        self.linkedEvent.connect(self.onRebuild)
        # self.model.dataChanged.connect(self.field_model_save)

    def onClose(self, QCloseEvent):
        """保存数据,并且归零"""
        self.dataJSON_model_load().field_pairLi_save()
        self.signout()

    def onRebuild(self):
        """重建模型,用于刷新"""
        self.init_model()

    def onDrop(self, *args, **kwargs):
        """掉落事件响应, 不涉及重写dataJSON"""

        def gowithcard(parent, item_target, item_finalLi):
            """对于卡片来说,group是最顶层,card 0, 1层都可以"""
            if item_target.self_attrs["character"] == "group":
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
            "group": gowithgroup
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
        list(map(lambda x: groupItemLi.append(x) if x[0].self_attrs["character"] == "group" else cardItemLi.append(x),
                 selectedItemLi))
        item_finalLi_ = groupItemLi if len(cardItemLi) == 0 else cardItemLi  # 要么全是card,要么全是group,优先考虑card
        item_finalLi = [self.itemChild_row_remove(i) for i in item_finalLi_]
        group_or_card = item_finalLi[0][0].self_attrs["character"]
        if item_target is not None:
            gogroupcard_dict[group_or_card](parent, item_target, item_finalLi)
        else:
            for i in item_finalLi: root.appendRow(i)
        j, emptyremoved = 0, False
        for i in range(root.rowCount()):
            if root.child(j, 0).self_attrs["character"] == "group" and root.child(j, 0).rowCount() == 0:
                root.takeRow(j)
                emptyremoved = True
            else:
                j += 1
            if j == root.rowCount(): break
        if emptyremoved:
            if root != self.model_rootNode:
                del self.model_dataobj["groupinfo"][root.text()]
            console(say("空组已移除")).talk.end()
        self.field_model_save_suite(nocheck=True)
        self.anchorTree.expandAll()

    def onAnchorTree_contextMenu(self, *args, **kwargs):
        """初始化右键菜单"""
        menu = self.anchorTree.contextMenu = QMenu()
        prefix = BaseInfo().consolerName
        menu.addAction(prefix + say("全部展开/折叠")).triggered.connect(self.view_expandCollapse_toggle)
        menu.addAction(prefix + say("新建组")).triggered.connect(self.itemgroup_create)
        if len(self.anchorTree.selectedIndexes()) > 0:
            self.dataJSON_model_load()
            menu.addMenu(prefix + say("选中链接"))
        menu.popup(QCursor.pos())
        menu.show()

    def itemChild_row_remove(self, item):
        """不需要parent,自己能产生parent"""
        parent = item[0].parent() if item[0].parent() is not None else self.model_rootNode
        return parent.takeRow(item[0].row())

    def itemChild_row_insert(self, parent, item_after, item_insertLi):
        """实现:1如果被插入对象是一个卡片,那么插入到下一排,2如果被插入对象是一个组,插入到组最后,
        插入方法是效率最低的那种:移除所有的,再重排回去"""
        templi, r = [], item_after.row()
        item_after_row = [parent.child(r, 0), parent.child(r, 1)]
        while parent.rowCount() > 0:
            row0 = parent.takeRow(0)
            templi.append(row0)
        [templi.remove(i) if i in templi else None for i in item_insertLi]
        if item_after_row[0] != None:
            index = templi.index(item_after_row)
        else:
            index = len(templi)
        templi = templi[0:index + 1] + item_insertLi + templi[index + 1:]
        for i in templi:
            parent.appendRow(i)

    def itemgroup_create(self):
        """create group to model"""
        newgroupname = "new_group"
        while newgroupname in self.model_dataobj["groupinfo"]:
            newgroupname = "new_" + newgroupname
        self.model_dataobj["groupinfo"][newgroupname] = {
            "menuli": [],
            "self_name": newgroupname,
            "model_item": None
        }
        group = QStandardItem(newgroupname)
        group.self_attrs = {
            "level": 0,
            "character": "group",
            "primData": self.model_dataobj["groupinfo"][newgroupname]
        }
        self.model_dataobj["groupinfo"][newgroupname]["model_item"] = group
        empty = QStandardItem("")
        empty.setFlags(empty.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDropEnabled)
        self.model_rootNode.appendRow([group, empty])
        # self.model_rootNode.self_attrs["primData"]["menuli"].append(groupname=newgroupname, type="groupinfo")

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
        self.model_rootNode.self_attrs = {"character": "group", "level": -1, "primData": None}
        self.model.setHorizontalHeaderLabels(["id", "desc"])
        self.anchorTree.setModel(self.model)
        self.model_dataobj_load()
        self.anchorTree.expandAll()
        self.treeIsExpanded = True

    def dataobj_field_load(self):
        """从笔记中读取保存好的JSON数据,需要input读取数据,HTML进行转化
        这里cardinfo是需要后期指定更新的,其他的不必更新,对应的东西会自己更新.
        """
        note = self.input.note_id_load(self.pair)
        self.HTMLmanage.clear().feed(note.fields[self.cfg.readDescFieldPosition])
        self.HTMLmanage.HTMLdata_load()
        pairli = self.HTMLmanage.card_linked_pairLi
        dataJSON = self.HTMLmanage.card_selfdata_dict
        cardinfo: Dict = {}
        for pair in pairli:
            cardinfo[pair.card_id] = pair
        self.model_dataJSON: Dict = dataJSON
        self.model_dataobj["groupinfo"] = {}
        for k, v in self.model_dataJSON["groupinfo"].items():
            self.model_dataobj["groupinfo"][k] = {"menuli": v, "model_item": None, "self_name": k}
        self.model_dataobj["menuli"] = [Pair(**pair) for pair in self.model_dataJSON["menuli"]]
        self.model_dataobj["cardinfo"] = cardinfo

    def dataObjCardinfo_model_load(self):
        """利用dataobj 将cardinfo中的数据更新掉"""
        root = self.model_rootNode
        cardinfo = self.model_dataobj["cardinfo"]
        for i in range(root.rowCount()):
            card, desc = root.child(i, 0), root.child(i, 1)
            if card.self_attrs["character"] == "card_id":
                cardinfo[card.text()].desc = desc.text()
            elif card.self_attrs["character"] == "group":
                for j in range(card.rowCount()):
                    subcard, subdesc = card.child(j, 0), card.child(j, 1)
                    cardinfo[subcard.text()].desc = subdesc.text()

    def pairli_selected_load(self):
        """读取选中的到datapairLi, 注意datapairLi的数据是变动流动的,所以不能长期保存数据,如果要调用必须先执行某行为
         考虑问题: 如何保证以后pair数据升级了还能保持对应?
         返回数据: 应该是一个flatten的pair列表,进一步操作要交给input manager.
         在进行读取之前, 要更新一次cardinfo的数据.
         """
        self.dataObjCardinfo_model_load()
        selectedItemLi_ = list(map(self.model.itemFromIndex, self.inputTree.selectedIndexes()))
        selectedItemLi = []
        for i in range(int(len(selectedItemLi_) / 2)):
            selectedItemLi.append([selectedItemLi_[2 * i], selectedItemLi_[2 * i + 1]])
        selectedItemLi.sort(key=lambda x: x[0].parent().row())
        pairLi = []
        for row in selectedItemLi:
            if row[0].self_attrs["character"] == "card_id":
                pairLi.append(row[0].self_attrs["primData"])
        self.model_linked_pairLi = pairLi
        return self

    def linkedPairli_model_load(self):
        """默认不涉及其他环节,单纯更新这个变量,所以调用他之前,要确保其他环节已经跟进."""
        temppairli = []
        cardinfo = self.model_dataobj["cardinfo"]
        root = self.model_rootNode
        for i in range(root.rowCount()):
            item = root.child(i, 0)
            if item.self_attrs["character"] == "card_id":
                temppairli.append(cardinfo[item.text()])
            elif item.self_attrs["character"] == "group":
                for j in range(item.rowCount()):
                    temppairli.append(cardinfo[item.child(j, 0).text()])
        self.model_linked_pairLi = temppairli

    def dataJSON_model_load(self):
        """从Model中读取,不更新cardinfo 因為他属于linkedpairli的结果.
        dataJSON:
            - menuli:List[card_id or name,type]
            - groupinfo
                - group_name:List[card_id]
                ...
        """
        root = self.model_rootNode
        tempdict = {
            "menuli": [],
            "groupinfo": {}
        }
        for i in range(root.rowCount()):
            item = root.child(i, 0)
            if item.self_attrs["character"] == "card_id":
                tempdict["menuli"].append(dict(card_id=item.text(), type="cardinfo"))
            elif item.self_attrs["character"] == "group":
                tempdict["menuli"].append(dict(groupname=item.text(), type="groupinfo"))
                tempdict["groupinfo"][item.text()] = []
                t = tempdict["groupinfo"][item.text()]
                for j in range(item.rowCount()):
                    t.append(item.child(j).text())
        self.model_dataJSON = tempdict
        return self

    def model_dataobj_load(self):
        """从JSON读取数据保存到模型中展示
        这里有两个数据类型:一个是对接HTML方面的pairdict,一个是对接View的model_item
        pairdict是一个查询字典,用来找卡片对的,他是HTML中linked_pairLi的映射.
        这里load时要做的事情是,把model_item和pairdict以及在本锚点管理器中用到的groupinfo关联起来,确保后面的联动修改.
        """
        self.dataobj_field_load()
        self.model_rootNode.clearData()
        self.model.removeRows(0, self.model.rowCount())
        menuli, groupinfo, root = self.model_dataobj["menuli"], self.model_dataobj["groupinfo"], self.model_rootNode
        root.self_attrs["primData"] = {"menuli": menuli, "groupinfo": groupinfo, "model_item": root}

        def carditem_make(pair, level=0, parent=root):
            item_id, item_desc = QStandardItem(pair.card_id), QStandardItem(pair.desc)
            item_id.setFlags(item_id.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDropEnabled)
            item_desc.setFlags(item_desc.flags() & ~Qt.ItemIsDropEnabled & ~Qt.ItemIsDragEnabled)
            item_id.self_attrs = {"character": "card_id", "level": level, "primData": pair}
            item_desc.self_attrs = {"character": "desc", "level": level}
            parent.appendRow([item_id, item_desc])

        for info in menuli:
            if info.type == "cardinfo":
                carditem_make(self.model_dataobj["cardinfo"][info.card_id])
            elif info.type == "groupinfo":
                item_group = QStandardItem(info.groupname)
                item_group.self_attrs = {"character": "group", "level": 0, "primData": groupinfo[info.groupname]}
                groupinfo[info.groupname]["model_item"] = item_group
                item_empty = QStandardItem("")
                item_empty.setFlags(item_empty.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDropEnabled)
                root.appendRow([item_group, item_empty])
                for ginfo in groupinfo[info.groupname]["menuli"]:
                    carditem_make(self.model_dataobj["cardinfo"][ginfo], parent=item_group, level=1)

    def itemgroupEmpty_check(self):
        """为空检查"""
        pass

    def itemgroup_children_move(self, groupA: QStandardItem, groupB: QStandardItem):
        """move a groupchild to another group,move GB'chilren to GA"""
        subitem_li = list(map(lambda x: self.item_remove(x), [groupB.child(i, 0) for i in range(groupB.rowCount())]))
        list(map(lambda x: groupA.appendRow(x), subitem_li))

    def modelChanged_check(self, *args, **kwargs):
        """进行检查,及时合并名字相同的组 参数1,2是topLeft,bottomRight,如果没有处理ondrop事件,则会顺到这里来解决"""
        e = args[0]  #
        item_src = self.model.itemFromIndex(e)
        groupinfo = self.model_dataobj["groupinfo"]
        cardinfo = self.model_dataobj["groupinfo"]
        character = item_src.self_attrs["character"]
        if character == "group":
            group_name_now = item_src.text()
            group_name_prev = item_src.self_attrs["primData"]["self_name"]
            if re.search(r"\W", group_name_now):
                console(say("抱歉,组名中暂时不能用空格与标点符号,否则会报错")).talk.end()
                item_src.setText(group_name_prev)
                return
            if group_name_now in groupinfo:
                item_target = groupinfo[group_name_now]["model_item"]
                self.itemgroup_children_move(item_target, item_src)
                self.model_rootNode.takeRow(item_src.row())
                del groupinfo[group_name_prev]
                console(say("同名组已合并")).talk.end()
            else:
                groupinfo[group_name_now] = groupinfo[group_name_prev]
                item_src.self_attrs["primData"]["self_name"] = group_name_now
            del groupinfo[group_name_prev]
        else:
            item_src.self_attrs["primData"].desc = item_src.text()

    def field_model_save_suite(self, *args, **kwargs):
        """把model读取为pairLi,保存到Field"""
        if "nocheck" not in kwargs:
            self.modelChanged_check(*args, **kwargs)
        self.dataObjCardinfo_model_load()
        self.dataJSON_model_load()
        self.linkedPairli_model_load()
        self.field_pairLi_save()

    @wrapper_webview_refresh
    @wrapper_browser_refresh
    def field_pairLi_save(self):
        """save pairli to field, 调用之前,请确保linked pairli 和 dataJSON已经更新完毕"""
        note = self.input.note_id_load(self.pair)
        self.HTMLmanage.clear().feed(note.fields[self.cfg.readDescFieldPosition])
        self.HTMLmanage.HTMLdata_load().card_selfdata_dict = self.model_dataJSON
        self.HTMLmanage.card_linked_pairLi = self.model_linked_pairLi
        note.fields[self.cfg.readDescFieldPosition] = self.HTMLmanage.HTMLdata_save().HTML_get().HTML_text
        note.flush()

    def item_remove(self, item: QStandardItem):
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
