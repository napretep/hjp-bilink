# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'ABC.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/7/15 23:09'

这个文件用于提供基类,
"""
import typing,re

from .compatible_import import *
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *

class 视图结点类型:
    卡片="card"
    视图="view"

class 枚举命名:
    class 结点:
        角色 = "node_role"
        pass
    class 边:
        pass
    范围="range"
    组件="widget"
    值="value"
    数据源="data_source"
    位置 = "position"  # 用于gviewdata中结点的位置
    边名 = "edge_name"  # 用于gviewdata中边名的描述
    独立卡片预览器 = "independent previewer"
    数据类型="data_type"
    主要结点 = "major_node"
    创建时间 = "created_time"
    上次访问 = "last_visit"
    上次编辑 = "last_edit"
    访问次数 = "visit_count"
    视图卡片内容缓存 = "card_content_cache"
    结点访问次数 = "node_vist_count"
    结点上次访问 = "node_last_vist"
    结点上次编辑 = "node_last_edit"
    优先级 = "node_priority"
    需要复习 = "need_review"
    必须复习 = "must_review"
    漫游起点 = "roaming_start"
    结点描述 = "node_desc"



class ConfigTableNewRowFormView:
    """
    一个表格, 新增一行的时候, 调用这个组件会出来一个用户填写的表单, 填完点确定, 就会插入新的一行
    """

    def __init__(self, superior, colItems: "list[ConfigTableView.TableItem]" = None, colWidgets:"list[QWidget]"=None):
        self.superior: "ConfigTableView" = superior
        self.layout = QFormLayout()
        self.mainLayout = QVBoxLayout()
        self.ok = False
        self.isNew=False
        self.okbtn = QToolButton()
        self.widget = QDialog()
        self.widget.setWindowTitle("new")
        self.widget.resize(500, 300)
        if not colItems:
            from . import funcs
            colItems = funcs.Map.do(superior.defaultRowData, lambda data: superior.TableItem(superior, *data))
            self.isNew=True
        # colItems 是 配置项对应的table的Item, 在查看行组件中, 当完成操作点击确定, 会把 colItem对应的项加入到配置项对应的table中
        self.colItems: "list[ConfigTableView.TableItem]" = colItems


        self.SetupUI()
        self.SetupWidget()
        self.SetupEvent()

    def SetupUI(self):
        """在这里,每一列按照QFormLayout以名字-组件的方式添加,最后加上ok按钮"""
        from . import G
        hlayout = QHBoxLayout()
        self.okbtn.setIcon(QIcon(G.src.ImgDir.correct))

        self.mainLayout.addLayout(self.layout)
        hlayout.addWidget(self.okbtn)
        self.mainLayout.addLayout(hlayout)
        self.mainLayout.setAlignment(Qt.AlignRight)
        self.widget.setLayout(self.mainLayout)
        self.okbtn.clicked.connect(self.OnOkClicked)
        [self.layout.addRow(self.superior.colnames[i], self.colWidgets[i]) for i in range(len(self.superior.colnames))]

    def OnOkClicked(self):
        from . import funcs
        self.ok = True
        self.setValueToTableRowFromForm()
        # funcs.Utils.print("OnOkClicked",need_logFile=True)
        self.widget.close()

    @abc.abstractmethod
    def SetupEvent(self):
        """建立链接"""
        raise NotImplementedError()

    @abc.abstractmethod
    def SetupWidget(self):
        """布置新行的widget,把item的值转换成可在组件中展示的值."""
        pass

    @abc.abstractmethod
    def setValueToTableRowFromForm(self):
        """将值保存到行(self.colItems)中,他需要重载的原因是不同的表提取保存的数据类型形式各有不同"""
        pass

    def InitLayout(self, d: "dict"):
        """

        """
        from . import G
        B = G.objs.Bricks
        layout, widget, kids = B.triple
        if layout in d:
            the_layout: "QHBoxLayout|QVBoxLayout|QGridLayout" = d[layout]
            for kid in d[kids]:
                d1 = self.InitLayout(kid)
                if layout in d1:
                    the_layout.addLayout(d1[layout])
                else:
                    the_layout.addWidget(d1[widget])
        return d



class CustomConfigItemView(metaclass=abc.ABCMeta):
    """提供了最基础的功能, 即访问父类,访问对应的配置项,以及访问UI组件"""

    @abc.abstractmethod
    def SetupView(self):
        """这个用来规定View如何被组合"""
        raise NotImplementedError()
        pass

    @abc.abstractmethod
    def SetupData(self, raw_data):
        """raw_data是指保存下来的配置表项的值
        setupData的目标是将raw_data存储为ViewUI可以接受的值.

        """
        raise NotImplementedError()
        pass

    @property
    def View(self) -> "QWidget":
        """view 是 model item 对应的展示UI"""
        return self._view

    @View.setter
    def View(self, value: "QWidget"):
        self._view = value


    def __init__(self, configItem: "ConfigModelItem" = None, 上级: "Standard.配置表容器" = None, *args, **kwargs):
        self.ConfigModelItem: "ConfigModelItem" = configItem
        self.上级: "Standard.配置表容器" = 上级
        self.View: "QWidget" = QWidget(上级)

class ConfigTableView(CustomConfigItemView,metaclass=abc.ABCMeta):
    """只提供基础的表格功能, 双击修改行, 点加号增加空记录, 点减号减去对应行
    这个类自定义了配置表的基本功能, 把很多设置提前设置好减少代码量
    2023年2月6日18:31:46 这个东西非常复杂, 我后面需要写一个调用的结构图
    """
    colnames = []
    defaultRowData = [] # 默认行数据用来新建行,  (dataformat.templateId, dataformat.fieldId), dataformat.fieldName, colType.field)
    IsList = False #如果是列表, 则要改造成二维表实现表格.
    def __init__(self, configItem: "ConfigModelItem" = None, 上级: "Standard.配置表容器" = None, *args, **kwargs):
        super().__init__(configItem, 上级)
        self.viewTable = QTableView(self.View)
        self.table_model = QStandardItemModel()
        self.modelRoot = self.table_model.invisibleRootItem()
        self.btnAdd = QPushButton("+")
        self.btnDel = QPushButton("-")
        # self.btnDel.setMaximumWidth(30)
        # self.btnAdd.setMaximumWidth(30)
        self.rowEditor = QDialog()
        self.rowEditor.resize(300, 600)
        self.SetupData(self.ConfigModelItem.value)
        self.SetupView()
        self.SetupEvent()

    # def 值替换(self, 值):
    #     """直接换一套值, 通常发生在参数模型改变的情况下"""
    #
    #     pass

    def SetupView(self):
        self.SetupLayout()
        self.viewTable.verticalHeader().setHidden(True)
        self.viewTable.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.viewTable.horizontalHeader().setStretchLastSection(True)
        self.viewTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.viewTable.setSelectionMode(QAbstractItemViewSelectMode.SingleSelection)
        self.viewTable.setSelectionBehavior(QAbstractItemViewSelectionBehavior.SelectRows)
        pass

    def SetupLayout(self):
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnAdd)
        btnLayout.addWidget(self.btnDel)
        viewLayout = QVBoxLayout()
        viewLayout.addWidget(self.viewTable,stretch=0)
        viewLayout.addLayout(btnLayout,stretch=0)
        self.View.setLayout(viewLayout)

    def SetupData(self,raw_data):

        self.viewTable.setModel(self.table_model)
        self.table_model.clear()
        # raw_data = self.ConfigModelItem.value
        # print("uuid_list=",raw_data)
        if self.IsList:
            list(map(lambda row: self.AppendRow(self.GetRowFromData([row])), raw_data))
        else:
            list(map(lambda row: self.AppendRow(self.GetRowFromData(row)), raw_data))
        self.table_model.setHorizontalHeaderLabels(self.colnames)
        pass

    def SetupEvent(self):
        self.btnAdd.clicked.connect(lambda: self.NewRow())
        self.btnDel.clicked.connect(lambda: self.RemoveRow())
        self.viewTable.doubleClicked.connect(self.OnViewTableDoubleClicked)
        pass

    def OnViewTableDoubleClicked(self, index: "QModelIndex"):
        row = index.row()
        self.ShowRowEditor([self.table_model.item(row, col) for col in range(self.colnames.__len__())])

    def AppendRow(self, row: "list[ConfigTableView.Item]"):
        self.table_model.appendRow(row)
        pass

    def RemoveRow(self):
        idx = self.viewTable.selectedIndexes()
        if len(idx) == 0:
            return
        self.table_model.removeRow(idx[0].row(), idx[0].parent())
        self.SaveDataToConfigModel()

    def GetRowFromData(self, data: "list[str]"):
        """根据所获取的数据生成行, 由于这个组件通常用于列表类型的配置, 因此data通常是list结构"""
        # return list(map(lambda itemname: self.TableItem(self, itemname), data))
        return [self.TableItem(self, 项名) for 项名 in data]

    @abc.abstractmethod
    def NewRow(self):
        """点击+号调用的这个函数,
        调用后一般要弹出一个表单, 让用户填写
        目前, 解决方案已经很成熟,
        新行和双击读取的编辑器可以一致使用NewRowFormWidget
        NewRowFormWidget当初始化参数为空时, 就可以看做是新行
        全部记录保存在NewRowFormWidget.colItems中, 再从外部读取
        colItems 存的是表项值
        colWidgets 存的是用户交互的组件
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def ShowRowEditor(self, row: "list[ConfigTableView.Item]"):
        """
        双击弹出行修改编辑器
        接受参数是一行的数据, 显示一个组件, 用来编辑这一行的数据"""
        raise NotImplementedError()

    @abc.abstractmethod
    def SaveDataToConfigModel(self):
        """保存到self.ConfigModelItem中, 而非数据库或json文件之类的内存之外的东西中"""
        raise NotImplementedError()


    class TableItem(QStandardItem):

        def __init__(self, superior, name,value=None):
            if not isinstance(superior,ConfigTableView):
                raise ValueError(f"superior must be instance of Configtablevie not {superior}")
            self.superior: "ConfigTableView" = superior

            if type(name) != str:
                name = name.__str__()
            super().__init__(name)
            self.setToolTip(name)
            self.setEditable(False)
            self.widget = QWidget()
            self.innerWidget = QWidget()
            if value:
                self.setData(value)

        def ShowAsWidget(self):
            """这个数据项要展示为用户可操作的交互对象时,所用的组件"""
            return None

        def copySelf(self):
            return ConfigTableView.TableItem(self.superior, self.text())

        def SetValue(self, text, value=None):
            self.setText(text)
            self.setToolTip(text)
            self.setData(value)

class ConfigItemLabelView(CustomConfigItemView):
    """这个东西,是当配置项需要表示为
    一个Label + 一个edit按钮而设计的.
    Label读取保存的值, edit按钮点击后修改, 这样做的目的是用于检查输入的合法性.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = QLabel()
        self.edit_Btn = QPushButton("edit")
        self.SetupView()
        self.SetupEvent()
        self.SetupData(self.ConfigModelItem.value)

    def SetupView(self):
        layout = QVBoxLayout()
        layout.addWidget(self.label,stretch=0)
        layout.addWidget(self.edit_Btn,stretch=0)
        self.View.setLayout(layout)
        pass

    def SetupData(self, raw_data):
        if re.search(r"\S",raw_data):
            self.label.setText(raw_data)
        else:
            self.label.setText("[]")
        pass

    def SetupEvent(self):
        self.edit_Btn.clicked.connect(self.on_edit_btn_clicked)

    @abc.abstractmethod
    def on_edit_btn_clicked(self):
        raise NotImplementedError()

# def __init__(self):
    #     pass

class 可执行字符串编辑组件(QDialog):
    def __init__(self,预设文本=""):
        super().__init__()
        from . import funcs
        布局,组件,子代 = funcs.objs.Bricks.三元组
        self.布局 = {
                布局:QVBoxLayout(),
                子代:[
                    {组件:QTextEdit()},
                    {布局:QHBoxLayout(),
                     子代:
                         [{组件:QPushButton("help")},
                          {组件:QPushButton("test")},
                          {组件:QPushButton("ok")},
                          ]
                     },
                    {组件:QLabel()} # 用于展示信息
                ]
        }
        self.合法字符串 = "" # 可用可不用
        self.ok=False # 可用可不用
        f = [self.on_help,self.on_test,self.on_ok]
        funcs.组件定制.组件组合(self.布局,self)
        [self.布局[子代][1][子代][i][组件].clicked.connect(f[i]) for i in range(3)]
        label:QLabel=self.布局[子代][2][组件]
        label.setWordWrap(True)
        self.布局[子代][0][组件].setText(预设文本)
        self.setWindowTitle("excutable string validation")

    @abc.abstractmethod
    def on_help(self):
        """弹出提示"""
        raise NotImplementedError()

    @abc.abstractmethod
    def on_test(self):
        """进行语法检测"""
        raise NotImplementedError()

    @abc.abstractmethod
    def on_ok(self):
        """会调用on_test, 如果通过了,返回正确值, 不通过,则显示错误原因"""
        raise NotImplementedError()

    # def init_UI(self):



    pass

class Standard:
    class TableView(QTableView):
        def __init__(self,itemIsmovable=False,editable=False,itemIsselectable=False,title_name=""):
            super().__init__()
            if not editable:
                self.setEditTriggers(QAbstractItemView.NoEditTriggers)


            self.horizontalHeader().setStretchLastSection(True)

            # if title_name:
            #     model =QStandardItemModel()
            #     self.horizontalHeader().setModel(model)
            #     self.horizontalHeader().model().setHeaderData(0,Qt.Horizontal,title_name)

    class Item(QStandardItem):
        def __init__(self,name,data=None,movable=False,editable=False,selectable=False):
            super().__init__(name)
            if data:
                self.setData(data)

    class 配置表容器(QDialog):

        def __init__(我, 配置参数模型: "BaseConfigModel",调用者=None):
            我.参数模型 = 配置参数模型
            我.调用者 = 调用者
            super().__init__()


    # class Model(QStandardItemModel):
    #     def __init__(self,title_name=""):
    #         super().__init__()

class Geometry:
    class ArrowLine(QGraphicsLineItem):
        def __init__(self):
            super().__init__()
            self.triangle:"list[QPointF]" = []
            # self.arrowPoint= QPointF()
        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            super().paint(painter, option, widget)
            painter.setPen(self.pen())
            line = self.line()
            v = line.unitVector()  # 同向单位向量
            v.setLength(40)  # 设置单位向量长度
            v.translate(QPointF(line.dx() * 2 / 7, line.dy() * 2 / 7))  # dx,dy是直线作为向量的分解向量, 此步骤移动单位向量到 长2/5处

            n = v.normalVector()  # 获取到单位向量的法向量
            n.setLength(n.length() * 0.6)  # 设置法向量为原来的0.4倍
            n2 = n.normalVector().normalVector()  # 法向量的法向量,再求法向量,得到相反方向的法向量

            p1 = v.p2()  # 单位向量的终点
            p2 = n.p2()  # 法向量的终点
            p3 = n2.p2()  # 第二个法向量的终点
            self.triangle = [v.p2(), n.p2(), n2.p2()]
            painter.drawLine(line)
            painter.drawPolygon(p1, p2, p3)

        # def shape(self) -> QtGui.QPainterPath:
        #     super().shape()
        #     path = QPainterPath()
        #     path.addPolygon(QPolygonF(self.triangle))
        #     return path
