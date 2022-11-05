# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'ABC.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/7/15 23:09'

这个文件用于提供基类
"""
import typing

from .compatible_import import *
from . import funcs
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *


class ConfigTableNewRowFormView:
    """
    一个表格, 新增一行的时候, 调用这个组件会出来一个用户填写的表单, 填完点确定, 就会插入新的一行
    """

    def __init__(self, superior, colItems: "list[ConfigTableView.TableItem]" = None, colWidgets:"list[QWidget]"=None):
        self.superior: "ConfigTableView" = superior
        self.layout = QFormLayout()
        self.mainLayout = QVBoxLayout()
        self.ok = False
        self.okbtn = QToolButton()
        self.widget = QDialog()
        self.widget.setWindowTitle("new")
        self.widget.resize(500, 300)
        self.colItems: "list[ConfigTableView.TableItem]" = colItems
        # self.colWidgets: "list[QWidget]" = [] # funcs.Map.do(self.colItems, lambda item: item.ShowAsWidget())
        self.SetupUI()
        self.SetupWidget()
        self.SetupEvent()

    def SetupUI(self):
        from . import G
        hlayout = QHBoxLayout()
        self.okbtn.setIcon(QIcon(G.src.ImgDir.correct))

        self.mainLayout.addLayout(self.layout)
        hlayout.addWidget(self.okbtn)
        self.mainLayout.addLayout(hlayout)
        self.mainLayout.setAlignment(Qt.AlignRight)
        self.widget.setLayout(self.mainLayout)
        # funcs.Map.do(range(len(self.superior.colnames)), lambda i: self.layout.addRow(self.superior.colnames[i], self.__dict__[f"col{i}"]))
        self.okbtn.clicked.connect(self.OnOkClicked)
        [self.layout.addRow(self.superior.colnames[i], self.colWidgets[i]) for i in range(len(self.superior.colnames))]

    def OnOkClicked(self):
        self.ok = True
        self.setValueToTableRowFromForm()
        self.widget.reject()

    @abc.abstractmethod
    def SetupEvent(self):
        """建立链接"""
        raise NotImplementedError()

    @abc.abstractmethod
    def SetupWidget(self):
        """布置widget, 在这个新行编辑器中,你必须把每一列的初始值设置好"""
        pass

    @abc.abstractmethod
    def setValueToTableRowFromForm(self):
        """将值保存到行(self.colItems)中,他需要重载的原因是不同的表提取保存的数据类型形式各有不同"""
        pass

    # @abc.abstractmethod
    # def GetColWidgets(self) -> list[QWidget]:
    #     pass


class CustomConfigItemView:
    """提供了最基础的功能, 即访问父类,访问对应的配置项,以及访问UI组件"""

    @property
    def Item(self) -> "ConfigModelItem":
        return self._item

    @Item.setter
    def Item(self, value: "ConfigModelItem"):
        self._item = value

    @property
    def Parent(self):
        return self._parent

    @Parent.setter
    def Parent(self, value):
        self._parent = value

    @property
    def View(self) -> "QWidget":
        return self._view

    @View.setter
    def View(self, value: "QWidget"):
        self._view = value

    def __init__(self, configItem: "ConfigModelItem" = None, parent: "QWidget" = None, *args, **kwargs):
        self.ConfigModelItem: "ConfigModelItem" = configItem
        self.Parent: "QWidget" = parent
        self.View: "QWidget" = QWidget(parent)


class ConfigTableView(CustomConfigItemView):
    """只提供基础的表格功能, 双击修改行, 点加号增加空记录, 点减号减去对应行
    这个类自定义了配置表的基本功能, 把很多设置提前设置好减少代码量
    """
    colnames = []
    defaultRowData = [] # 默认行数据用来新建行,  (dataformat.templateId, dataformat.fieldId), dataformat.fieldName, colType.field)

    def __init__(self, configItem: "ConfigModelItem" = None, parent: "QWidget" = None, *args, **kwargs):
        super().__init__(configItem, parent)
        self.viewTable = QTableView(self.View)
        self.model = QStandardItemModel()
        self.modelRoot = self.model.invisibleRootItem()
        self.btnAdd = QPushButton("+")
        self.btnDel = QPushButton("-")
        self.btnDel.setMaximumWidth(30)
        self.btnAdd.setMaximumWidth(30)
        self.rowEditor = QDialog()
        self.rowEditor.resize(300, 600)

        self.SetupData()
        self.SetupView()
        self.SetupEvent()

    def SetupView(self):
        self.SetupLayout()
        self.viewTable.verticalHeader().setHidden(True)
        self.viewTable.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.viewTable.horizontalHeader().setStretchLastSection(True)
        self.viewTable.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.viewTable.setSelectionMode(QAbstractItemViewSelectMode.SingleSelection)
        self.viewTable.setSelectionBehavior(QAbstractItemViewSelectionBehavior.SelectRows)
        pass

    def SetupLayout(self):
        btnLayout = QVBoxLayout()
        btnLayout.addWidget(self.btnAdd)
        btnLayout.addWidget(self.btnDel)
        viewLayout = QHBoxLayout()
        viewLayout.addWidget(self.viewTable)
        viewLayout.addLayout(btnLayout)
        viewLayout.setStretch(0, 1)
        viewLayout.setStretch(1, 0)
        self.View.setLayout(viewLayout)

    def SetupData(self):

        self.model.setHorizontalHeaderLabels(self.colnames)
        self.viewTable.setModel(self.model)
        raw_data = self.ConfigModelItem.value
        list(map(lambda row: self.AppendRow(self.GetRowFromData(row)), raw_data))

        pass

    def SetupEvent(self):
        self.btnAdd.clicked.connect(lambda: self.NewRow())
        self.btnDel.clicked.connect(lambda: self.RemoveRow())
        self.viewTable.doubleClicked.connect(self.OnViewTableDoubleClicked)
        pass

    def OnViewTableDoubleClicked(self, index: "QModelIndex"):
        row = index.row()
        self.ShowRowEditor([self.model.item(row, col) for col in range(self.colnames.__len__())])

    def AppendRow(self, row: "list[ConfigTableView.Item]"):
        self.model.appendRow(row)
        self.SaveDataToConfigModel()
        pass

    def RemoveRow(self):
        idx = self.viewTable.selectedIndexes()
        if len(idx) == 0:
            return
        self.model.removeRow(idx[0].row(), idx[0].parent())
        self.SaveDataToConfigModel()

    def GetRowFromData(self, data: "list[str]"):
        """根据所获取的数据生成行, 由于这个组件通常用于列表类型的配置, 因此data通常是list结构"""
        return list(map(lambda itemname: self.TableItem(self, itemname), data))

    @abc.abstractmethod
    def NewRow(self):
        """新增一行通常要做一些特殊处理, 比如弹出一个表单让用户去填"""
        raise NotImplementedError()

    @abc.abstractmethod
    def ShowRowEditor(self, row: "list[ConfigTableView.Item]"):
        """接受参数是一行的数据, 显示一个组件, 用来编辑这一行的数据"""
        raise NotImplementedError()

    @abc.abstractmethod
    def SaveDataToConfigModel(self):
        """保存到self.ConfigModelItem中, 而非数据库或json文件之类的内存之外的东西中"""
        raise NotImplementedError()

    class TableItem(QStandardItem):

        def __init__(self, superior, name):
            self.superior: "ConfigTableView" = superior

            if type(name) != str:
                name = name.__str__()
            super().__init__(name)
            self.setToolTip(name)
            self.setEditable(False)
            self.widget = QWidget()
            self.innerWidget = QWidget()

        def ShowAsWidget(self):
            """这个数据项要展示为用户可操作的交互对象时,所用的组件"""
            return None

        def copySelf(self):
            return ConfigTableView.TableItem(self.superior, self.text())

        def SetValue(self, text, value=None):
            self.setText(text)
            self.setToolTip(text)
            self.setData(value, role=ItemDataRole.UserRole)


# class ConfigListView


class Geometry:
    class ArrowLine(QGraphicsLineItem):
        def __init__(self):
            super().__init__()
            self.triangle = []

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
