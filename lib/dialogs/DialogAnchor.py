"""
selfdata 数据结构:
    menu:是一个列表, 由cardinfo和groupinfo构成
    groupinfo:是一个字典,每个键是一个groupname,对应一个列表,里面是cardinfo

model_dataJSON: HTMLmanage读取的HTML文本转换为JSON保存于此,包含menuli和groupinfo的内容
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


基本功能:
    打开anchor
    数据载入-整理成树形结构
    anchor树可以拖拽调整
    自动保存
    自动更新
    重名检测
    手工链接
"""
from typing import Dict

from PyQt5 import QtWidgets

# from ...lib.obj import MenuAdder
from .DialogCardPrev import external_card_dialog
from .metaUIobj import SpecialTreeItem
from ..obj import MenuAdder
from ...lib.obj.inputObj import *
from ...lib.dialogs.UIdialog_Anchor import Ui_anchor
from ...lib.obj.linkData_reader import LinkDataReader





class AnchorDialog(QDialog, Ui_anchor):
    """锚点数据调整的对话框"""
    linkedEvent = CustomSignals.start().linkedEvent

    def __init__(self, pair: Pair, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.input = Input()
        self.pair = pair
        self.pair.desc = self.input.desc_extract(self.pair)
        self.data = LinkDataReader(pair.card_id).read()
        self.anchorDataIsEmpty = False
        self.parent = parent
        self.model_subgroupdict = {}
        self.baseinfo = self.input.baseinfo
        self.customSignals = CustomSignals()
        self.init_UI()
        self.init_lineEdit()
        self.init_model()
        self.init_events()
        self.signup()
        self.show()

    def init_var(self):
        """变量初始化"""
        self.data = LinkDataReader(self.pair.card_id).read()
        self.model = None
        self.model_rootNode = None

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
        """UI初始化"""
        self.setupUi(self)
        self.anchorTree.parent = self
        self.windowTitle_set()
        icondir = os.path.join(THIS_FOLDER, self.baseinfo.baseinfo["iconFile_anchor"])
        self.setWindowIcon(QIcon(icondir))
        self.setAcceptDrops(True)
        self.acceptDrops()
        self.anchorTree.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.anchorTree.setIndentation(8)

    def init_events(self):
        """响应右键菜单,拖拽,绑定更新数据,思考如何实现变化后自动加载.如果实现不了,暂时先使用模态对话框 """
        self.closeEvent = self.onClose
        self.anchorTree.doubleClicked.connect(self.onDoubleClick)
        self.anchorTree.dropEvent = self.onDrop
        self.anchorTree.customContextMenuRequested.connect(self.onAnchorTree_contextMenu)
        self.linkedEvent.connect(self.onRebuild)
        self.model.dataChanged.connect(self.data_model_save_suite)
        self.self_desc.textChanged.connect(lambda:self.data_model_save_suite(nocheck=True,setTitle=True))

    def init_lineEdit(self):
        text1 = self.data["self_data"]["desc"]
        text2 = text1 if text1!="" else self.input.desc_extract(self.pair)
        self.self_desc.setText(text2)

    def onClose(self, QCloseEvent):
        """保存数据,并且归零"""
        self.data_model_save_suite(nocheck=True)
        self.signout()

    def onRebuild(self):
        """重建模型,用于刷新"""
        self.init_var()
        self.init_lineEdit()
        self.init_model(rebuild=True)

    def onDrop(self, e):
        """
        利用光标偏移的结果是否还在原item中,判断属于何种插入方式.(上中下,底层)代码分别是1,0,-1,-2
        允许组嵌套,但不允许重复.
        """
        pos = e.pos()
        drop_index = self.anchorTree.indexAt(pos)
        item_target = self.model.itemFromIndex(drop_index)
        insert_posi = self.position_insert_check(pos, drop_index)
        item_target, insert_posi = self.item_target_recorrect(item_target, insert_posi)
        selected_row_li = self.rowli_index_make()
        # 下面是根据不同的插入情况做出选择。
        self.rowli_selected_insert(insert_posi, selected_row_li, item_target)
        self.anchorTree.expandAll()
        self.data_save()

    def rowli_selected_insert(self, insert_posi, selected_row_li, item_target):
        for row in selected_row_li: self.itemChild_row_remove(row)
        temp_rows_li = []
        if insert_posi == 0:  # 中间
            for row in selected_row_li:
                item_target.appendRow(row)
                row[0].level = item_target.level + 1
                row[1].level = item_target.level + 1
        elif insert_posi != -2:
            for row in selected_row_li:
                row[0].level = item_target.level
                row[1].level = item_target.level
            posi_row = item_target.row()
            parent = item_target.parent() if item_target.level > 0 else self.model_rootNode
            while parent.rowCount() > 0:
                temp_rows_li.append(parent.takeRow(0))
            if insert_posi == 1:  # 上面
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

    def rowli_index_make(self):
        """# 源item每次都会选择一行的所有列,而且所有列编成1维数组,所以需要下面的步骤重新组回来."""
        selected_indexes_li = self.anchorTree.selectedIndexes()
        selected_items_li = list(map(self.model.itemFromIndex, selected_indexes_li))
        selected_row_li = []
        for i in range(int(len(selected_items_li) / 2)):
            selected_row_li.append([selected_items_li[2 * i], selected_items_li[2 * i + 1]])
        return selected_row_li

    def position_insert_check(self, pos, drop_index):
        """测定插入位置"""
        index_height = self.anchorTree.rowHeight(drop_index)  #
        drop_index_offset_up = self.anchorTree.indexAt(pos - QPoint(0, index_height / 4))  # 高处为0
        drop_index_offset_down = self.anchorTree.indexAt(pos + QPoint(0, index_height / 4))
        insertPosi = 0  # 0中间,1上面,-1下面,-2底部
        if drop_index_offset_down == drop_index_offset_up:
            insertPosi = 0
        else:
            if drop_index != drop_index_offset_up:
                insertPosi = 1
            elif drop_index != drop_index_offset_down:
                insertPosi = -1
        return insertPosi

    def item_target_recorrect(self, item_target, insertPosi):
        """修正插入的对象和插入的位置"""
        # 拉到底部
        if item_target is None:
            insertPosi = -2
            item_target = self.model_rootNode
        # 卡片不允许成为组
        elif item_target.character == "card_id":
            if insertPosi == 0: insertPosi = -1
        # 目标item不能是第二列,如果是要调回第一列
        if item_target.column() > 0:
            if item_target.level == 0:
                item_target = self.model_rootNode.child(item_target.row(), 0)
            elif item_target.level > 0:
                item_target = item_target.parent().child(item_target.row(), 0)
        return item_target, insertPosi

    def onDoubleClick(self, index, *args, **kwargs):
        """双击事件响应"""
        item = self.model.itemFromIndex(index)
        if item.column() == 0 and item.character == "card_id":
            card = self.input.model.col.getCard(int(item.text()))
            external_card_dialog(card)

    def onAnchorTree_contextMenu(self, *args, **kwargs):
        """初始化右键菜单"""
        menu = self.anchorTree.contextMenu = QMenu()
        prefix = BaseInfo().consolerName
        menu.addAction(prefix + say("全部展开/折叠")).triggered.connect(self.view_expandCollapse_toggle)
        menu.addAction(prefix + say("新建组")).triggered.connect(self.itemgroup_create)
        if len(self.anchorTree.selectedIndexes()) > 0:
            self.data_selected_load()
            menu.addAction(prefix + say("选中删除")).triggered.connect(self.view_selected_delete)
            param = Params(menu=menu, parent=self.anchorTree, features=["prefix", "selected"],
                           actionTypes=["link", "browserinsert"])
            MenuAdder.func_menuAddHelper(**param.__dict__)
        param = Params(menu=menu, parent=self.anchorTree, features=["prefix"], actionTypes=["clear_open_input"])
        MenuAdder.func_menuAddHelper(**param.__dict__)
        menu.popup(QCursor.pos())
        menu.show()

    def view_selected_delete(self, *args, **kwargs):
        """选中的部分删除"""
        selectedIndexesLi = self.anchorTree.selectedIndexes()
        selectedItemLi_ = list(map(self.model.itemFromIndex, selectedIndexesLi))
        selectedItemLi = []
        for i in range(int(len(selectedItemLi_) / 2)):
            selectedItemLi.append([selectedItemLi_[2 * i], selectedItemLi_[2 * i + 1]])
        item_finalLi = [self.itemChild_row_remove(i) for i in selectedItemLi]
        self.data_model_save_suite(nocheck=True)
        console(say("已删除选中卡片")).talk.end()

    def itemChild_row_remove(self, item):
        """不需要parent,自己能产生parent"""
        parent = item[0].parent() if item[0].parent() is not None else self.model_rootNode
        return parent.takeRow(item[0].row())

    def itemgroup_create(self):
        """create group to model"""
        newgroupname = "new_group"
        while newgroupname in self.data["node"]:
            newgroupname = "new_" + newgroupname
        group = SpecialTreeItem(newgroupname, character="group", level=0, primData=[])
        empty = SpecialTreeItem("", character="empty", level=0, primData=group.primData)
        empty.setFlags(empty.flags() & ~Qt.ItemIsEditable)
        self.model_rootNode.appendRow([group, empty])
        self.data_save()

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
        # if "rebuild" in kwargs:
        #     showInfo("rebuild")
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.character = "group"
        self.model_rootNode.level = -1
        self.model_rootNode.primData = None
        # self.model_rootNode.self_attrs = {"character": "group", "level": -1, "primData": None}
        label_id = QStandardItem("card_id")
        label_desc = QStandardItem("desc")
        self.model.setHorizontalHeaderItem(0, label_id)
        self.model.setHorizontalHeaderItem(1, label_desc)
        self.model.horizontalHeaderItem(0)
        self.anchorTree.setModel(self.model)
        # self.model_dataobj_load()
        self.model_datadict_load()
        self.anchorTree.expandAll()
        self.treeIsExpanded = True

    def model_datadict_load(self):
        if len(self.data["link_list"]) == 0:
            return
        self.model_rootNode.clearData()
        self.model.removeRows(0, self.model.rowCount())
        mroot = self.model_rootNode
        root = self.data["root"]
        node = self.data["node"]
        for item in root:
            if "card_id" in item:
                self.create_carditem(item)
            elif "nodename" in item:
                self.create_groupitem(item)

    def create_groupitem(self, item, parent=None, level=0):
        if parent is None:
            parent = self.model_rootNode
        groupname = item["nodename"]
        groupli = self.data["node"][groupname]
        # item_group = QStandardItem(groupname)
        item_group = SpecialTreeItem(groupname, character="group", level=level, primData=groupli)
        # item_group.self_attrs = {"character": "group", "level": level, "primData": groupli}
        item_empty = SpecialTreeItem("", character="empty", level=level, primData=groupli)
        item_empty.setFlags(item_empty.flags()
                            & ~Qt.ItemIsEditable
                            # & ~Qt.ItemIsDropEnabled
                            & ~Qt.ItemIsDragEnabled)
        parent.appendRow([item_group, item_empty])
        for subitem in groupli:
            if "card_id" in subitem:
                self.create_carditem(subitem, parent=item_group, level=level + 1)
            elif "nodename" in subitem:
                self.create_groupitem(subitem, parent=item_group, level=level + 1)

    def create_carditem(self, item, parent=None, level=0):
        if parent is None:
            parent = self.model_rootNode
        cardinfo = self.data["node"][item["card_id"]]
        card_id, desc = cardinfo["card_id"], cardinfo["desc"]
        # item_id = QStandardItem(card_id)
        # item_id.self_attrs={"character":"card_id","level":level,"primData":cardinfo}
        # item_desc = QStandardItem(desc)
        # item_desc.self_attrs={"character":"desc","level":level,"primData":cardinfo}
        item_id, item_desc = \
            SpecialTreeItem(card_id, level=level, primData=cardinfo), \
            SpecialTreeItem(desc, character="desc", level=level, primData=cardinfo)
        item_desc.setFlags(item_desc.flags()
                           # &~Qt.ItemIsDropEnabled
                           & ~Qt.ItemIsDragEnabled)
        parent.appendRow([item_id, item_desc])


    def data_selected_load(self):
        """读取选中的到datapairLi, 注意datapairLi的数据是变动流动的,所以不能长期保存数据,如果要调用必须先执行某行为
         返回数据: 应该是一个flatten的pair列表,进一步操作要交给input manager.
         在进行读取之前, 要更新一次cardinfo的数据.
         """
        root = self.model_rootNode
        # self.data_model_update_suite()
        tempdict = self.data_model_load()
        selectedItemLi_ = list(map(self.model.itemFromIndex, self.anchorTree.selectedIndexes()))
        selectedItemLi = []
        for i in range(int(len(selectedItemLi_) / 2)):
            selectedItemLi.append([selectedItemLi_[2 * i], selectedItemLi_[2 * i + 1]])
        selectedItemLi.sort(key=lambda x: (x[0].parent() if x[0].parent() else root).row())
        data_li = []
        for row in selectedItemLi:
            if row[0].character=="card_id":
                data_li.append(tempdict["node"][row[0].text()])
        self.input.data = data_li
        return self

    def dataChanged_check(self, *args, **kwargs):
        """基本原理： 重命名group后， 将原先的group集A和当前修改过的group集B相减，得到的结果就是被修改的那个group，
        然后再B-A，如果为空集，说明修改不合法，还原，如果不是空集，说明改了新的名字，那么把旧的指向的列表给他，旧的删掉，留下新的。
        """
        e = args[0]  #
        item_src = self.model.itemFromIndex(e)
        tempdict = self.data_model_load()
        changed_set = set(filter(lambda x: type(tempdict["node"][x])==list ,tempdict["node"].keys()))
        origin_set = set(filter(lambda x: type(self.data["node"][x])==list ,self.data["node"].keys()))
        which_changed = origin_set-changed_set
        if which_changed == set():
            tooltip("无修改")
            return
        else:
            changed_name = changed_set-origin_set
            if changed_name == set() or len(changed_set)<len(origin_set): #说明重复
                item_src.setText(which_changed.pop())
                tooltip("组名重复")
            else: #一切正常再继续
                self.data_save()
                tooltip("修改成功")

    def data_model_save_suite(self, *args, **kwargs):
        """把model读取为pairLi,保存到Field"""
        if "nocheck" not in kwargs:
            self.dataChanged_check(*args, **kwargs)
        self.data_save()
        if "setTitle" in kwargs:
            self.windowTitle_set()

    def windowTitle_set(self):
        self.setWindowTitle("""Anchor of [desc={desc},card_id={card_id}]""".format(
            desc=self.input.desc_extract(self.pair), card_id=self.data["self_data"]["card_id"]))

    @wrapper_browser_refresh
    @wrapper_webview_refresh
    def data_save(self):
        tempdict = self.data_model_load()
        self.data["link_list"] = tempdict["link_list"]
        self.data["root"] = tempdict["root"]
        self.data["node"] = tempdict["node"]
        self.data["self_data"]=tempdict["self_data"]
        self.data = DataSyncer(self.data).sync().data
        LinkDataWriter(self.pair.card_id, self.data).write()

    def data_model_load(self):
        """从model中读取数据保存"""
        mroot = self.model_rootNode
        tempdict = {
            "self_data":{"card_id":self.pair.card_id,"desc":self.self_desc.text()},
            "link_list": [],
            "root": [],
            "node": {}
        }
        if mroot is None:
            return tempdict
        for i in range(mroot.rowCount()):
            child = mroot.child(i, 0)
            if child.character == "card_id":
                # if child.self_attrs["character"] == "card_id":
                self.data_model_load_card(child, tempdict)
            elif child.character == "group":
                # elif child.self_attrs["character"] == "group":
                self.data_model_load_group(child, tempdict)
        for i in tempdict["link_list"]:
            tempdict["node"][i["card_id"]]=i
        return tempdict

    def data_model_load_card(self, child, tempdict):
        cardinfo = child.primData
        # cardinfo = child.self_attrs["primData"]
        if child.level == 0:
            # if child.self_attrs["level"] == 0:
            tempdict["root"].append({"card_id": child.text()})
        else:
            parent = child.parent().text()
            tempdict["node"][parent].append({"card_id": child.text()})

        desc = child.parent().child(child.row(), 1) \
            if child.parent() is not None else self.model_rootNode.child(child.row(), 1)
        cardinfo["desc"] = desc.text()
        tempdict["link_list"].append(cardinfo)

    def data_model_load_group(self, child: SpecialTreeItem, tempdict):
        tempdict["node"][child.text()] = []
        if child.level == 0:
            # if child.self_attrs["level"] == 0:
            tempdict["root"].append({"nodename": child.text()})
        else:
            parent = child.parent().text()
            tempdict["node"][parent].append({"nodename": child.text()})
        for i in range(child.rowCount()):
            childchild = child.child(i, 0)
            if childchild.character == "card_id":
                # if child.self_attrs["character"] == "card_id":
                self.data_model_load_card(childchild, tempdict)
            elif childchild.character == "group":
                # elif child.self_attrs["character"] == "group":
                self.data_model_load_group(childchild, tempdict)

