"""
这个是input 对话窗口
"""
import copy
import json
import time

from aqt import mw

from . import MenuAdder
from .input_UI import Ui_input
from .language import rosetta as say
from .inputObj import *


class InputDialog(QDialog, Ui_input):
    """INPUT对话窗口类"""
    model: Union[QStandardItemModel, QStandardItemModel]

    def __init__(self, parent=None):
        super().__init__(parent)
        mw.InputDialog = self
        self.fileHelper: Input = Input()
        self.model_dataSelected: List[List[Pair]] = []
        self.model_data: List[List[Pair]] = []
        self.UI_init()
        self.model_init()
        self.events_init()
        self.show()
        console("初始化完成!").log.end()

    def UI_init(self):
        """初始化UI"""
        self.setupUi(self)
        self.inputTree.customContextMenuRequested.connect(self.contextMenuOnInputTree)

    # noinspection PyAttributeOutsideInit
    def events_init(self):
        """事件的初始化"""
        self.closeEvent = self.onClose
        self.inputTree.doubleClicked.connect(self.onDoubleClick)
        self.inputTree.dropEvent = self.onDrop
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath(os.path.join(THIS_FOLDER, inputFileName))
        self.fileWatcher.fileChanged.connect(self.model_loadJSON)
        self.model.dataChanged.connect(self.tree_saveToFile)
        self.model.rowsRemoved.connect(self.tree_saveToFile)
        # self.model.layoutChanged.connect(self.tree_saveToFile)
        self.tagContent.textChanged.connect(self.tag_saveToFile)

    def model_init(self):
        """模型数据的初始化"""
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.setDropEnabled(False)
        self.model_rootNode.setEditable(False)
        self.model_rootNode.setSelectable(False)
        self.model_rootNode.setDragEnabled(False)
        self.model.setHorizontalHeaderLabels(["card_id|desc"])
        self.inputTree.setModel(self.model)
        self.model_loadJSON()

    def contextMenuOnInputTree(self):
        """初始化右键菜单"""
        menu = self.inputTree.contextMenu = QMenu()
        prefix = consolerName
        menu.addAction(prefix + say("全部展开/折叠")).triggered.connect(self.tree_toggleExpandCollapse)
        if len(self.inputTree.selectedIndexes()) > 0:
            menu.addAction(prefix + say("选中删除")).triggered.connect(self.tree_selectedDelete)
        menu.addAction("test").triggered.connect(self.tree_saveToFile)
        param = Params(menu=menu, parent=self.inputTree, need=("link", "clear_open", "prefix", "selected"))
        MenuAdder.func_menuAddHelper(param)
        menu.popup(QCursor.pos())
        menu.show()

    def onDrop(self):
        """掉落事件响应"""
        pass

    def onDoubleClick(self):
        """双击事件响应"""
        pass

    def onRowRemoved(self):
        """移除行时响应"""
        self.tree_saveToFile()

    def onClose(self, QCloseEvent):
        """关闭时要保存数据,QCloseEvent是有用的参数,不能删掉,否则会报错"""
        mw.InputDialog = None
        if len(self.model_data) > 0:
            self.tree_saveToFile()
        else:
            self.fileHelper.dataReset.dataSave.end()

    def tree_selectedDelete(self):
        """选中的部分删除"""
        indexLi = self.inputTree.selectedIndexes()
        for index in indexLi:
            item = self.model.itemFromIndex(index)
            row, col = item.row(), item.column()
            father = item.parent()
            if father is not None:
                father.removeRow(row)
            else:
                self.model_rootNode.removeRow(row)

    def tree_toggleExpandCollapse(self):
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

    def tree_saveToFile(self):
        """保存文件"""
        self.JSON_loadFromModel()
        self.fileHelper.data = self.model_data
        self.fileHelper.dataSave.end()
        console(f"tree_saveToFile:{self.fileHelper.data.__str__()}").log.end()

    def model_loadTag(self):
        self.tagContent.setText(self.fileHelper.dataLoad.tag)

    def model_loadJSON(self):
        """从JSON读取到模型"""
        self.model_data: List[List[Pair]] = self.fileHelper.dataLoad.val
        self.model_rootNode.clearData()
        self.model.removeRows(0, self.model.rowCount())
        for group in self.model_data:
            parent = QStandardItem("group")
            parent.level = 0
            parent.setFlags(parent.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsSelectable)
            self.model_rootNode.appendRow([parent])
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
                pairsItem.appendRow([child1])
                pairsItem.appendRow([child2])
        # self.tagContent.setText(self.fileHelper.tag)
        self.lastrowcount = self.model_rootNode.rowCount()
        self.inputTree.expandAll()
        self.treeIsExpanded = True
        self.model_loadTag()
        console("model_loadJSON" + self.model_data.__str__()).log.end()

    def JSON_loadFromModel(self):
        """从树中读取json"""
        self.model_data: List[List[Pair]] = self.fileHelper.dataReset.dataObj.val
        self.fileHelper.tag = self.tagContent.text()
        self.JSON_loadFromModel_sub()

    def JSON_loadFromModel_sub(self):
        """是一个子函数"""
        for i in range(self.model_rootNode.rowCount()):
            console("model_data=" + self.model_data.__str__()).log.end()
            console(f"self.model_rootNode.child({i.__str__()}).rowCount()=" + self.model_rootNode.child(
                i).rowCount().__str__()).log.end()
            if self.model_rootNode.child(i).rowCount() == 0:
                continue
            else:
                self.model_data.append([])
                for j in range(self.model_rootNode.child(i).rowCount()):
                    pair = Pair(card_id=self.model_rootNode.child(i).child(j).child(0).text(),
                                desc=self.model_rootNode.child(i).child(j).child(1).text())
                    self.model_data[-1].append(pair)

    def JSON_loadFromSelect(self):
        """从选中的项目中读取json"""
        pass

    def tag_saveToFile(self):
        """将json保存到文件"""
        self.fileHelper.tag = self.tagContent.text()
        self.fileHelper.dataSave.end()
        pass

