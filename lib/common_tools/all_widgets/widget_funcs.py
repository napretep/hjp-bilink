from .basic_widgets import *
class 组件定制:
    # TODO 设计一个表格行编辑组件


    class 表格_单行行编辑组件:
        def __init__(self,单行组件:QWidget):
            self.表单=单行组件
            self.确认按钮被点击=False
            self.确认按钮 = 组件定制.按钮_确认(触发函数=self.当_确认按钮被点击)
            self.窗口=QDialog()
            self.布局={
                    布局:QVBoxLayout(),
                    子代:[
                            {组件:self.表单,占据:1},
                            {组件:self.确认按钮,占据:0}
                    ]
            }
            组件定制.组件组合(self.布局,self.窗口)

        def 当_确认按钮被点击(self):
            self.确认按钮被点击=True
            self.窗口.close()

    @staticmethod
    def 组件组合(组件树数据: "dict", 容器: "QWidget" = None) -> "QWidget|QDialog":
        if not 容器: 容器 = QWidget()
        基 = G.objs.Bricks
        布局, 组件, 子代, 占据 = 基.四元组

        def 子组合(组件树: "dict"):
            if 布局 in 组件树:
                the_layout: "QHBoxLayout|QVBoxLayout|QGridLayout" = 组件树[布局]
                the_layout.setContentsMargins(0, 0, 0, 0)
                for 孩子 in 组件树[子代]:
                    子组件 = 子组合(孩子)
                    if 布局 in 子组件:
                        the_layout.addLayout(子组件[布局])
                    else:
                        if isinstance(子组件[组件], QWidget):
                            the_layout.addWidget(子组件[组件], stretch=子组件[占据] if 占据 in 子组件 else 0)
                        else:
                            the_layout.addLayout(子组件[组件], stretch=子组件[占据] if 占据 in 子组件 else 0)

            return 组件树

        容器.setLayout(子组合(组件树数据)[布局])

        return 容器

    @staticmethod
    def 表格(单行选中=True, 不可修改=True):
        组件 = QTableView()
        if 单行选中:
            组件.setSelectionMode(QAbstractItemViewSelectMode.SingleSelection)
            组件.setSelectionBehavior(QAbstractItemViewSelectionBehavior.SelectRows)
        if 不可修改:
            组件.setEditTriggers(QAbstractItemView.NoEditTriggers)
        组件.horizontalHeader().setStretchLastSection(True)
        组件.verticalHeader().setHidden(True)
        组件.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        组件.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        return 组件

    @staticmethod
    def 模型(行标签: "list[str]" = None):
        组件 = QStandardItemModel()
        if 行标签:

            组件.setHorizontalHeaderLabels(行标签)
        return 组件

    @staticmethod
    def 单行输入框(占位符=None):
        组件 = QLineEdit()
        if 占位符:
            组件.setPlaceholderText(占位符)
        return 组件

    @staticmethod
    def 对话窗口(标题=None, 图标=None, 最大宽度=None, closeEvent=None, 尺寸=None, 宽度=None):
        组件 = QDialog()
        if 标题:
            组件.setWindowTitle(标题)
        if 图标:
            组件.setWindowIcon(图标)
        if 最大宽度:
            组件.setMaximumWidth(最大宽度)
        if closeEvent:
            组件.closeEvent = closeEvent
        if 尺寸:
            组件.resize(*尺寸)
        # 组件.adjustSize()

        return 组件

    @staticmethod
    def 文本框(文本="", 开启自动换行=True):
        组件 = QLabel(文本)
        组件.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        if 开启自动换行:
            组件.setWordWrap(True)
        return 组件

    @staticmethod
    def 按钮(图标地址=None, 文本=None, 触发函数=None):
        组件 = QPushButton()
        if 图标地址:
            组件.setIcon(QIcon(图标地址))
        if 文本:
            组件.setText(文本)
        if 触发函数:
            组件.clicked.connect(lambda:触发函数())
        return 组件

    @staticmethod
    def 长文本获取(预置内容=None, 标题=None, 获取回调: Callable[[str], Any] = None):
        布局, 组件, 子代 = 0, 1, 2
        result = []
        对话框布局 = {
                布局: QVBoxLayout(), 子代: [
                        {组件: QTextEdit(预置内容)},
                        {组件: QPushButton(QIcon(G.src.ImgDir.correct), "")}
                ]
        }
        对话框: "QDialog" = 组件定制.组件组合(对话框布局, 组件定制.对话窗口(标题))
        对话框布局[子代][1][组件].clicked.connect(lambda: [result.append(对话框布局[子代][0][组件].toPlainText()), 对话框.close()])

        对话框.exec()
        return result

    @staticmethod
    def 按钮_修改(文字="", 图标地址=None):
        # 组件 = QPushButton(QIcon(图标地址),文字)
        图标地址 = 图标地址 if 图标地址 else G.src.ImgDir.rename
        return 组件定制.按钮(图标地址, 文字)

    @staticmethod
    def 按钮_提示(文字="", 图标地址=None, 触发函数=None):
        图标地址 = 图标地址 if 图标地址 else G.src.ImgDir.info
        return 组件定制.按钮(图标地址, 文字, 触发函数)

    @staticmethod
    def 按钮_确认(文字="", 图标地址=None, 触发函数=None):
        图标地址 = 图标地址 if 图标地址 else G.src.ImgDir.correct
        return 组件定制.按钮(图标地址, 文字, 触发函数)
    class TableView(QTableView):
        def __init__(self, itemIsmovable=False, editable=False, itemIsselectable=False, title_name=""):
            super().__init__()
            if not editable:
                self.setEditTriggers(QAbstractItemView.NoEditTriggers)

            self.horizontalHeader().setStretchLastSection(True)

    class Item(QStandardItem):
        def __init__(self, name, data=None, movable=False, editable=False, selectable=False):
            super().__init__(name)
            if data:
                self.setData(data)

    class 配置表容器(QDialog):

        def __init__(我, 配置参数模型: "G.safe.configsModel.BaseConfigModel", 调用者=None):
            我.参数模型:G.safe.configsModel.BaseConfigModel = 配置参数模型
            我.调用者 = 调用者
            super().__init__()

