"""
这个是input 对话窗口 DONE,还没做完.
"""

from . import MenuAdder
from .inputdialog_UI import Ui_input
from .inputObj import *


class InputDialog(QDialog, Ui_input):
    """INPUT对话窗口类"""
    model: Union[QStandardItemModel, QStandardItemModel]

    def __init__(self, parent=None):
        super().__init__(parent)
        mw.InputDialog = self
        self.input: Input = Input()
        self.model_dataSelected: List[List[Pair]] = []
        self.model_data: List[List[Pair]] = []
        self.UI_init()
        self.model_init()
        self.events_init()
        self.show()
        console("初始化完成!").log.end()

    # @debugWatcher
    def UI_init(self, *args, **kwargs):
        """初始化UI"""
        self.setupUi(self)
        self.inputTree.parent = self
        self.inputTree.customContextMenuRequested.connect(self.contextMenuOnInputTree)

    # noinspection PyAttributeOutsideInit
    # @debugWatcher
    def events_init(self, *args, **kwargs):
        """事件的初始化"""
        self.closeEvent = self.onClose
        self.inputTree.doubleClicked.connect(self.onDoubleClick)
        self.inputTree.dropEvent = self.onDrop
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath(os.path.join(THIS_FOLDER, inputFileName))
        self.fileWatcher.fileChanged.connect(self.model_loadFromJSON)
        self.model.dataChanged.connect(self.model_saveToFile)
        self.tagContent.textChanged.connect(self.tag_saveToFile)

    # @debugWatcher
    def model_init(self, *args, **kwargs):
        """模型数据的初始化"""
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.setDropEnabled(False)
        self.model_rootNode.setEditable(False)
        self.model_rootNode.setSelectable(False)
        self.model_rootNode.setDragEnabled(False)
        self.model.setHorizontalHeaderLabels(["card_id", "desc"])
        self.inputTree.setModel(self.model)
        self.model_loadFromJSON()


    # @debugWatcher
    def contextMenuOnInputTree(self, *args, **kwargs):
        """初始化右键菜单"""
        menu = self.inputTree.contextMenu = QMenu()
        prefix = consolerName
        menu.addAction(prefix + say("全部展开/折叠")).triggered.connect(self.view_toggleExpandCollapse)
        if len(self.inputTree.selectedIndexes()) > 0:
            self.JSON_loadFromSelected()
            menu.addAction(prefix + say("选中删除")).triggered.connect(self.view_selectedDelete)
            param = Params(menu=menu, parent=self.inputTree, features=["prefix", "selected"], actionTypes=["link"])
            MenuAdder.func_menuAddHelper(**param.__dict__)
        param = Params(menu=menu, parent=self.inputTree, features=["prefix"], actionTypes=["link", "clear_open"])
        MenuAdder.func_menuAddHelper(**param.__dict__)
        menu.popup(QCursor.pos())
        menu.show()

    # @debugWatcher
    def onDrop(self, *args, **kwargs):
        """掉落事件响应"""
        e = args[0]

        def removeChild(item: QStandardItem):
            """移除孩子呗"""
            return item.parent().takeRow(item.row())

        selectedIndexesLi = self.inputTree.selectedIndexes()
        selectedItemLi = list(map(self.model.itemFromIndex, selectedIndexesLi))
        drop_row = self.inputTree.indexAt(e.pos())
        targetItem = self.model.itemFromIndex(drop_row)
        if targetItem is not None:
            if targetItem.parent() is not None:
                targetItem = targetItem.parent()
                if targetItem.parent() is not None:
                    targetItem = targetItem.parent()
            if targetItem.column() > 0:
                if targetItem.parent() is None:
                    parent = self.model_rootNode
                else:
                    parent = targetItem.parent()
                row = targetItem.row()
                targetItem = parent.child(row, 0)

        else:
            group = QStandardItem("group")
            group.level = 0
            group.setFlags(group.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsSelectable)
            self.model_rootNode.appendRow(group)
            targetItem = group
        removedItemLi = list(map(lambda x: removeChild(x), selectedItemLi))  # takeRow先取出后appenrow,这个顺序非常重要!!!!
        nothin = list(map(lambda x: targetItem.appendRow(x), removedItemLi))
        self.model_saveToFile()

    # @debugWatcher
    def onDoubleClick(self, index, *args, **kwargs):
        """双击事件响应"""
        item = self.model.itemFromIndex(index)
        if cardPrevDialog is not None and item.level == 2 and item.character == "card_id":
            card = self.input.model.col.getCard(int(item.text()))
            cardPrevDialog(card)

    # @debugWatcher
    def onRowRemoved(self, *args, **kwargs):
        """移除行时响应"""
        self.model_saveToFile()

    # @debugWatcher
    def onClose(self, QCloseEvent):
        """关闭时要保存数据,QCloseEvent是有用的参数,不能删掉,否则会报错"""
        mw.InputDialog = None
        if len(self.model_data) > 0:
            self.model_saveToFile()
        else:
            self.input.dataReset().dataSave().end()

    # @debugWatcher
    def view_selectedDelete(self, *args, **kwargs):
        """选中的部分删除"""
        indexLi = self.inputTree.selectedIndexes()
        for i in range(len(indexLi)):
            index = self.inputTree.selectedIndexes()[0]
            item = self.model.itemFromIndex(index)
            row, father = item.row(), item.parent()
            father.takeRow(row)
            if father.rowCount() == 0:
                self.model_rootNode.takeRow(father.row())
        self.model_saveToFile()
        console(say("已删除选中卡片")).talk.end()

    # @debugWatcher
    def view_toggleExpandCollapse(self, *args, **kwargs):
        """切换input对话框的折叠和展开状态"""
        if self.treeIsExpanded:
            root = self.model_rootNode
            tree = self.inputTree
            groupLi = [root.child(i) for i in range(root.rowCount())]
            for group in groupLi:
                list(map(lambda x: tree.collapse(x.index()), [group.child(i) for i in range(group.rowCount())]))
            self.treeIsExpanded = False
        else:
            self.inputTree.expandAll()
            self.treeIsExpanded = True

    # @debugWatcher
    def model_saveToFile(self, *args, **kwargs):
        """保存文件"""
        self.JSON_loadFromModel()
        self.input.data = self.model_data if self.model_data != [] else self.input.initDict
        self.input.dataSave().end()

    # @debugWatcher
    def model_loadTag(self, *args, **kwargs):
        self.tagContent.setText(self.input.dataLoad().tag)

    # @debugWatcher
    def model_loadFromJSON(self, *args, **kwargs):
        """从JSON读取到模型"""
        self.model_data: List[List[Pair]] = self.input.dataLoad().val()
        self.model_rootNode.clearData()
        self.model.removeRows(0, self.model.rowCount())
        for group in self.model_data:
            parent = QStandardItem("group")
            parent.level = 0
            parent.setFlags(parent.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsSelectable)
            emptyNode = QStandardItem("")
            emptyNode.setFlags(
                emptyNode.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsSelectable & ~Qt.ItemIsDropEnabled)
            self.model_rootNode.appendRow([parent, emptyNode])
            # self.model_rootNode.child(parent.row(), 1) = None
            for pair in group:
                pairsItem = QStandardItem("pair")
                pairsItem.level = 1
                pairsItem.setFlags(pairsItem.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDropEnabled)
                parent.appendRow([pairsItem])
                child1 = QStandardItem(pair.card_id)
                child2 = QStandardItem(pair.desc)
                child2.setFlags(child1.flags() & ~Qt.ItemIsDropEnabled & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsSelectable)
                child1.setFlags(child2.flags() & ~Qt.ItemIsDropEnabled & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsSelectable &
                                ~Qt.ItemIsEditable)  # 不可拖拽不可选中不可编辑
                child1.level = child2.level = 2
                child1.character = "card_id"
                child2.character = "desc"
                pairsItem.appendRow([child1, child2])
        self.lastrowcount = self.model_rootNode.rowCount()
        self.inputTree.expandAll()
        self.treeIsExpanded = True
        self.model_loadTag()

    # @debugWatcher
    def JSON_loadFromModel(self, *args, **kwargs):
        """从树中读取json"""

        self.model_data: List[List[Pair]] = self.input.dataReset().dataObj().val()
        self.input.tag = self.tagContent.text()
        self.JSON_loadFromModel_sub()

    # @debugWatcher
    def JSON_loadFromModel_sub(self, *args, **kwargs):
        """是一个子函数"""
        for i in range(self.model_rootNode.rowCount()):
            # console("model_data=" + self.model_data.__str__()).log.end()
            # console(f"self.model_rootNode.child({i.__str__()}).rowCount()=" + self.model_rootNode.child(
            #     i).rowCount().__str__()).log.end()
            if self.model_rootNode.child(i).rowCount() == 0:
                continue
            else:
                self.model_data.append([])
                group = self.model_rootNode.child(i)
                for j in range(group.rowCount()):
                    pair_ = group.child(j)
                    pair = Pair(card_id=pair_.child(0, 0).text(), desc=pair_.child(0, 1).text())
                    self.model_data[-1].append(pair)

    # @debugWatcher
    def JSON_loadFromSelected(self):
        """从选中的项目中读取出JSON列表,保存在InputObj的data中,他只要不存到本地就没事情"""
        itemLi: List[QStandardItem] = [self.model.itemFromIndex(i) for i in self.inputTree.selectedIndexes()]
        itemLi.sort(key=lambda x: x.parent().row())
        pairLi = [[Pair(card_id=itemLi[0].child(0, 0).text(), desc=itemLi[0].child(0, 1).text())]]

        def areducer(x, y):
            """用来做事情"""
            if x is None or y is None:
                return None
            p = Pair(card_id=y.child(0, 0).text(), desc=y.child(0, 1).text())
            pairLi[-1].append(p) if x.parent().row() == y.parent().row() else pairLi.append([p])
            return y

        reduce(lambda x, y: areducer(x, y), itemLi)
        # showInfo(pairLi.__str__())
        self.input.data = pairLi
        self.input.tag = self.tagContent.text()

    # @debugWatcher
    def tag_saveToFile(self, *args, **kwargs):
        """将json保存到文件"""
        self.input.tag = self.tagContent.text()
        self.input.dataSave().end()
