# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'ABC.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/7/15 23:09'
"""
from .compatible_import import *
from . import funcs
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .configsModel import *


class CustomConfigItemView:

    @property
    def Item(self)->"ConfigModelItem":
        return self._item

    @Item.setter
    def Item(self, value:"ConfigModelItem"):
        self._item = value

    @property
    def Parent(self):
        return self._parent

    @Parent.setter
    def Parent(self, value):
        self._parent = value

    @property
    def View(self)->"QWidget":
        return self._view

    @View.setter
    def View(self, value:"QWidget"):
        self._view = value

    def __init__(self, configItem: "ConfigModelItem" = None, parent: "QWidget" = None, *args, **kwargs):
        self.Item: "ConfigModelItem" = configItem
        self.Parent: "QWidget" = parent
        self.View: "QWidget" = QWidget(parent)


class ConfigTableView(CustomConfigItemView):
    """只提供基础的表格功能, 双击修改行, 点加号增加空记录, 点减号减去对应行"""
    colnames = []
    defaultRowData = ["","","",False]
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
        raw_data = self.Item.value
        list(map(lambda row: self.AppendRow(self.GetRowFromData(row)), raw_data))

        pass

    def SetupEvent(self):
        self.btnAdd.clicked.connect(lambda: self.NewRow())
        self.btnDel.clicked.connect(lambda: self.RemoveRow())
        self.viewTable.doubleClicked.connect(self.OnViewTableDoubleClicked)
        pass

    def OnViewTableDoubleClicked(self, index: "QModelIndex"):
        row = index.row()
        self.ShowRowEditor([self.model.item(row, col) for col in range(4)])

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
        return list(map(lambda itemname: self.TableItem(self, itemname), data))

    def NewRow(self):
        raise NotImplementedError()

    def ShowRowEditor(self, row: "list[ConfigTableView.Item]"):
        raise NotImplementedError()

    def SaveDataToConfigModel(self):
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

        @abc.abstractmethod
        def ShowAsWidget(self): raise NotImplementedError()

class ConfigTableNewRowFormView:
    """服务于表格类型配置选项的表单"""
    def __init__(self, superior, colItems: "list[ConfigTableView.TableItem]" = None):
        self.superior: "ConfigTableView" = superior
        self.layout = QFormLayout()
        self.widget = QDialog()
        self.widget.setWindowTitle("new")
        self.widget.resize(500, 300)
        self.colItems: "list[ConfigTableView.TableItem]" = colItems
        self.colWidgets: "list[QWidget]" = funcs.Map.do(self.colItems, lambda item: item.ShowAsWidget())
        funcs.Map.do(range(len(self.superior.colnames)), lambda i: self.layout.addRow(self.superior.colnames[i], self.colWidgets[i]))
        self.widget.setLayout(self.layout)
        self.SetupEvent()

    @abc.abstractmethod
    def SetupEvent(self):raise NotImplementedError()