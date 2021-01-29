"""
这个是input 对话窗口
"""
import copy
import json

from aqt import mw

from . import MenuAdder
from .inputUI import Ui_input
from .language import rosetta as say
from .utils import *


class InputDialog(QDialog, Ui_input):
    """INPUT对话窗口类"""
    model: Union[QStandardItemModel, QStandardItemModel]

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        mw.InputDialog = self
        self.selectedData = copy.deepcopy(inputSchema)
        self.data = copy.deepcopy(inputSchema)
        self.UI_init()
        self.model_init()
        self.events_init()
        self.show()

    def UI_init(self):
        """初始化UI"""
        self.setupUi(self)
        self.inputTree.customContextMenuRequested.connect(self.contextMenuOnInputTree)


    # noinspection PyAttributeOutsideInit
    def events_init(self):
        """事件的初始化"""
        self.closeEvent = self.onclose
        self.inputTree.doubleClicked.connect(self.onDoubleClick)
        self.inputTree.dropEvent = self.onDrop
        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath(os.path.join(THIS_FOLDER, inputFileName))
        self.fileWatcher.fileChanged.connect(self.model_loadJSON)
        self.model.dataChanged.connect(self.JSON_saveToFile)
        self.tagContent.textChanged.connect(self.JSON_saveToFile)

    def model_init(self):
        """模型数据的初始化"""
        self.model = QStandardItemModel()
        self.rootNode = self.model.invisibleRootItem()
        self.rootNode.setDropEnabled(False)
        self.rootNode.setEditable(False)
        self.rootNode.setSelectable(False)
        self.rootNode.setDragEnabled(False)
        self.model.setHorizontalHeaderLabels(["card_id+desc"])
        self.inputTree.setModel(self.model)
        self.model_loadJSON()

    def contextMenuOnInputTree(self):
        """初始化右键菜单"""
        Menu = self.inputTree.contextMenu = QMenu(self)
        prefix = consolerName
        menuli = list(map(lambda x: prefix + say(x), ["全部展开/折叠", "选中删除"]))
        funcli = [self.view_expandCollapseToggle, self.view_selectedDelete]
        list(map(lambda x, y: Menu.addAction(x).triggered.connect(y), menuli, funcli))
        MenuAdder.func_menuAddHelper(Menu, self, need=("link", "clear/open", "prefix", "selected"))

    def onDrop(self):
        """掉落事件"""
        pass

    def onclose(self, QCloseEvent):
        """关闭时要保存数据"""
        mw.InputDialog = None

    def onDoubleClick(self):
        """双击事件响应"""
        pass

    def view_selectedDelete(self):
        """选中的部分删除"""

    def view_expandCollapseToggle(self):
        """切换展开与收起"""

    def model_loadJSON(self):
        """从JSON读取到模型"""

    def JSON_loadFromFile(self):
        """从文件中读取json对象"""
        self.data: json = json.load(open(os.path.join(THIS_FOLDER, inputFileName), "r", encoding="utf-8"))

    def JSON_loadFromTree(self):
        """从树中读取json"""
        pass

    def JSON_loadFromSelect(self):
        """从选中的项目中读取json"""
        pass

    def JSON_saveToFile(self):
        """将json保存到文件"""
        pass
