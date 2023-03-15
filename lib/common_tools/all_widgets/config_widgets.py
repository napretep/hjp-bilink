from ast import literal_eval

from .basic_widgets import *

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

    def __init__(self, configItem: "G.safe.baseClass.ConfigModelItem" = None, 上级: "G.safe.funcs.组件定制.配置表容器" = None, *args, **kwargs):
        self.ConfigModelItem: G.safe.baseClass.ConfigModelItem = configItem
        self.上级: G.safe.funcs.组件定制.配置表容器 = 上级
        self.View: "QWidget" = QWidget(上级)


class ConfigTableView(CustomConfigItemView, metaclass=abc.ABCMeta):
    """只提供基础的表格功能, 双击修改行, 点加号增加空记录, 点减号减去对应行
    这个类自定义了配置表的基本功能, 把很多设置提前设置好减少代码量
    2023年2月6日18:31:46 这个东西非常复杂, 我后面需要写一个调用的结构图
    这个东西是表格型配置项的UI,
    需要考虑的东西:
    1 设计列名, 缺省行数据
    2 判断表格形式, 单列表,/单选表
    数据加载:
    3 数据从 配置项上保存的raw_data 转换成 表格展示的值 需要通过setupData实现
        3.1 setupdata 中 需要用到 GetRowFromData 来具体地转换数据源为一行数据的形式,
        3.2 GetRowFromData 中 需要指定 表格的项(TableItem) 如果有特殊需要, 需要指定, 没有特殊需要, 可以用预置的
    新建/修改数据:
    4 点击加号新建数据, 会调用 NewRow->NewRowFormWidget(superior, colitems, colWidgets)->setValueToTableRowFromForm->SaveDataToConfigModel
        4.1 NewRowFormWidget 通常继承自 ConfigTableNewRowFormView
        4.2 NewRowFormWidget 通常需要三个参数, 1 调用者, 2 colitems 行数据, 3 colWidgets 行数据对应的组件, 你需要把这三个都传入
        4.3 新建时, colitems 为None, 函数会调用默认的行来创建, 修改时, 直接把行对应的组件保存到 colitems中即可.
        4.4 保存时, 点击ok按钮会发生,
        4.4.1 先调用 setValueToTableRowFromForm 将colWidgets的值转移到colitems中, 然后关闭自己
        4.4.2 再在NewRow函数中,用函数 SaveDataToConfigModel 保存到配置模型上

    """
    colnames = []
    defaultRowData = []  # 默认行数据用来新建行,  (dataformat.templateId, dataformat.fieldId), dataformat.fieldName, colType.field)
    IsList = False  # 如果是列表, 则要改造成二维表实现表格.
    IsSelectTable = False

    def __init__(self, configItem: "ConfigModelItem" = None, 上级: "Standard.配置表容器" = None, *args, **kwargs):
        super().__init__(configItem, 上级)
        self.btnLayout = QHBoxLayout()
        self.viewTable = QTableView(self.View)
        self.table_model = QStandardItemModel()
        self.modelRoot = self.table_model.invisibleRootItem()
        self.btnAdd = QPushButton("+")
        self.btnDel = QPushButton("-")
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
        self.btnLayout.addWidget(self.btnAdd)
        self.btnLayout.addWidget(self.btnDel)
        viewLayout = QVBoxLayout()
        viewLayout.addWidget(self.viewTable, stretch=0)
        viewLayout.addLayout(self.btnLayout, stretch=0)
        self.View.setLayout(viewLayout)
        self.View.layout()

    def SetupData(self, raw_data: "list[Any]"):
        funcs = G.safe.funcs
        # funcs.Utils.print(raw_data)
        self.viewTable.setModel(self.table_model)
        self.table_model.clear()
        if self.IsList:
            list(map(lambda row: self.AppendRow(self.GetRowFromData([row])), raw_data))
        elif self.IsSelectTable:
            [self.AppendRow(self.GetRowFromData(["", row])) for row in raw_data[0]]
            if raw_data[1] > -1:
                item = self.table_model.item(raw_data[1], 0)
                if item: item.setText("✔")
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

    def SelectRow(self, rownum):
        row = self.table_model.index(rownum, 1)

        self.viewTable.setCurrentIndex(row)
        self.viewTable.selectionModel().clearSelection()
        self.viewTable.selectionModel().select(self.viewTable.currentIndex(), QItemSelectionModel.Select)

    def RemoveRow(self):
        idx = self.viewTable.selectedIndexes()
        if len(idx) == 0:
            return
        self.table_model.removeRow(idx[0].row(), idx[0].parent())
        self.SaveDataToConfigModel()

    def GetRowFromData(self, data: "list[str]"):
        """
        make TableRow from raw_data
        根据所获取的数据生成行, 由于这个组件通常用于列表类型的配置, 因此data通常是list结构
        如果有特殊结构请自己处理
        """
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

    class TableItem(QStandardItem, ):

        def __init__(self, superior: "ConfigTableView", name, value=None):
            if not isinstance(superior, ConfigTableView):
                raise ValueError(f"superior must be instance of Configtableview not {superior}")
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
            """这个数据项要展示为用户可操作的交互对象时,所用的组件,
            这个功能现在已经废弃了
            """
            return None

        def copySelf(self):
            return ConfigTableView.TableItem(self.superior, self.text())

        def SetValue(self, text, value=None):
            self.setText(text)
            self.setToolTip(text)
            self.setData(value)

        def GetData(self):
            raise NotImplementedError()


class ConfigTableNewRowFormView:
    """
    一个表格, 新增一行的时候, 调用这个组件会出来一个用户填写的表单, 填完点确定, 就会插入新的一行
    第一个参数superior是自己的调用方,
    第二个参数colItems当不为空,则代表修改一行, 将该行数据获取填入, 为空则代表新建一行, 使用默认数据填入,
    第三个参数colWidgets表示每个列所对应的组件, 如果没有提供, 则需要自己继承后__init__新建的时候创建
    """
    def __init__(self, superior:"ConfigTableView", colItems: "list[ConfigTableView.TableItem]" = None, colWidgets: "list[QWidget]" = None):
        self.superior: "ConfigTableView" = superior
        funcs = G.safe.funcs
        self.layout = QFormLayout()
        # self.mainLayout = QVBoxLayout()
        self.ok = False
        self.isNew = False
        self.okbtn = funcs.组件定制.按钮_确认()
        self.widget = QDialog()
        self.widget.setWindowTitle("new")
        # self.widget.resize(500, 300)
        if not colItems:
            funcs = G.safe.funcs
            colItems = funcs.Map.do(superior.defaultRowData, lambda data: superior.TableItem(superior, *data))
            self.isNew = True
        # colItems 是 配置项对应的table的Item, 在查看行组件中, 当完成操作点击确定, 会把 colItem对应的项加入到配置项对应的table中
        self.colItems: "list[ConfigTableView.TableItem]" = colItems
        self.colWidgets: "list[QWidget]"=colWidgets

        self.SetupUI()
        self.SetupWidget()
        self.SetupEvent()

    def SetupUI(self):
        """在这里,每一列按照QFormLayout以名字-组件的方式添加,最后加上ok按钮"""

        # hlayout = QHBoxLayout()

        # self.mainLayout.addLayout(self.layout)
        # hlayout.addWidget(self.okbtn)
        # self.mainLayout.addLayout(hlayout)
        # self.mainLayout.setAlignment(Qt.AlignRight)
        self.okbtn.clicked.connect(self.OnOkClicked)
        if self.colWidgets:
            self.setUpColWidgets()
        self.layout.addRow("",self.okbtn)
        self.widget.setLayout(self.layout)

    def setUpColWidgets(self):
        [self.layout.addRow(self.superior.colnames[i], self.colWidgets[i]) for i in range(len(self.superior.colnames))]

    def OnOkClicked(self):

        self.ok = True
        self.setValueToTableRowFromForm()
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
        layout.addWidget(self.label, stretch=0)
        layout.addWidget(self.edit_Btn, stretch=0)
        self.View.setLayout(layout)
        pass

    def SetupData(self, raw_data):
        if re.search(r"\S", raw_data):
            self.label.setText(raw_data)
        else:
            self.label.setText("[]")
        pass

    def SetupEvent(self):
        self.edit_Btn.clicked.connect(self.on_edit_btn_clicked)

    @abc.abstractmethod
    def on_edit_btn_clicked(self):
        raise NotImplementedError()

class 配置项单选型表格组件(ConfigTableView):
    IsSelectTable = True

    @abc.abstractmethod
    def NewRowFormWidget(self, *args, **kwargs):
        raise NotImplementedError()

    def NewRow(self):

        w = self.NewRowFormWidget(self)
        w.exec()
        if w.ok:
            self.AppendRow(w.colItems)
            self.SaveDataToConfigModel()
            if self.table_model.rowCount() > 0:
                self.set_row_selected(self.table_model.rowCount() - 1)
            else:
                self.set_row_selected(0)
        pass

    def ShowRowEditor(self, row: "list[baseClass.ConfigTableView.TableItem]" = None):
        w = self.NewRowFormWidget(self, row)
        w.exec()
        if w.ok:
            self.SaveDataToConfigModel()

    def SaveDataToConfigModel(self):
        value = [[self.table_model.item(rownum, 1).text() for rownum in range(self.table_model.rowCount())], self.current_selected_row]
        self.ConfigModelItem.setValue(value, False)

        pass

    def set_row_selected(self, 指定行=None):
        for rownum in range(self.table_model.rowCount()):
            item = self.table_model.item(rownum, 0)
            item.setText("")
        # showInfo(self.table_model.rowCount().__str__())
        idxs = self.viewTable.selectedIndexes() if 指定行 is None else [self.table_model.index(指定行, 0)]
        if idxs:
            item = self.table_model.itemFromIndex(idxs[0])
            item.setText("✔")
            self.current_selected_row = item.row()
        else:

            self.current_selected_row = -1
        # showInfo(self.current_selected_row.__str__())
        self.SaveDataToConfigModel()

    def RemoveRow(self):
        super().RemoveRow()
        self.current_selected_row = -1
        for row in range(self.table_model.rowCount()):
            item = self.table_model.item(row, 0)
            if item.text() == "✔":
                self.current_selected_row = row

    def __init__(self, *args, **kwargs):
        self.current_selected_row = -1
        self.select_btn = QPushButton("select")
        self.select_btn.clicked.connect(self.set_row_selected)
        super().__init__(*args, **kwargs)
        self.btnLayout.addWidget(self.select_btn)
        self.current_selected_row = self.ConfigModelItem.value[1]

class 组件_表格型配置项_列编辑器_可执行字符串(可执行字符串编辑组件):
    """
    colItems是表格的列展示项集
    """

    def __init__(self, 上级, 行: "list[ConfigTableView.TableItem]" = None, 说明="", *args, **kwargs):
        # from .widgets import GviewConfigNodeFilter
        self.上级: 配置项单选型表格组件 = 上级
        if not 行:
            super().__init__()
        else:
            super().__init__(行[1].text())
        self.说明 = 说明
        # self.布局[子代][2][组件].setText(说明)
        self.colItems = [self.上级.TableItem(self.上级, i) for i in self.上级.defaultRowData] if not 行 else 行

    def on_test(self):
        raise NotImplementedError()

    def 设置当前配置项对应展示组件的值(self,value=None):
        self.colItems[1].setText(self.布局[子代][0][组件].toPlainText())
        pass

class PDFUrlLinkBooklist(ConfigTableView):
    colnames = ["PDFpath", "name", "style", "showPage"]  # 就是表有几个列,分别叫什么
    defaultRowData = ["", "", "", False]

    def NewRow(self):  # 新增一行的函数
        w = self.NewRowFormWidget(self)
        w.widget.exec()
        if w.ok:
            self.AppendRow(w.colItems)
            self.SaveDataToConfigModel()

    def ShowRowEditor(self, row: "list[PDFUrlLinkBooklist.TableItem]"):
        w = self.NewRowFormWidget(self, row)
        w.widget.exec()
        if w.ok:
            w.setValueToTableRowFromForm()

    def SaveDataToConfigModel(self):

        newConfigItem = []
        for row in range(self.table_model.rowCount()):
            line = []
            for col in range(4):
                item: "PDFUrlLinkBooklist.TableItem" = self.table_model.item(row, col)
                if col in range(2):
                    if not re.search("\S", item.text()):
                        break
                    else:
                        line.append(item.text())
                elif col == 3:
                    line.append(item.text() == "True")
                else:
                    line.append(item.text())
            if len(line) > 0:
                newConfigItem.append(line)
        self.ConfigModelItem.setValue(newConfigItem, 需要设值回到组件=False)
        pass

    def GetRowFromData(self, data: "list[str]"):
        # return [for itemname in data]
        return list(map(lambda itemname: PDFUrlLinkBooklist.TableItem(self, itemname), data))

    class TableItem(ConfigTableView.TableItem):

        def __init__(self, superior, name):
            self.isBool = False
            if type(name) != str:
                name = str(name)
                self.isBool = True
            super().__init__(superior, name)
            self.superior: "DescExtractPresetTable" = superior

        def ShowAsWidget(self):
            if self.isBool:
                widget = QRadioButton()
                widget.setChecked(self.text() == "True")
            else:
                widget = QTextEdit()
                widget.setText(self.text())
            return widget

        def GetValue(self):
            return self.text()

        pass

    class NewRowFormWidget(ConfigTableNewRowFormView):
        def __init__(self, superior: "PDFUrlLinkBooklist",
                     colItems: "list[PDFUrlLinkBooklist.TableItem]" = None):
            if not colItems:
                colItems = G.safe.funcs.Map.do(superior.defaultRowData, lambda unit: superior.TableItem(superior, unit))
            # self.col0: "QTextEdit" = QTextEdit()
            # self.col1: "QTextEdit" = QTextEdit()
            # self.col2: "QTextEdit" = QTextEdit()
            # self.col3: "QRadioButton" = QRadioButton()
            self.colWidgets = [QTextEdit(),
                               QTextEdit(),
                               QTextEdit(),
                               QRadioButton()]
            self.colItems = colItems
            super().__init__(superior, colItems, self.colWidgets)
            # funcs.Map.do(range(3), lambda idx: self.colWidgets[idx].textChanged.connect(lambda: self.colItems[idx].setText(self.__dict__[idx""].toPlainText())))
            # self.colWidgets[3].clicked.connect(lambda: self.colItems[3].setText(str(self.colWidgets[3].isChecked())))

        def SetupWidget(self):
            self.colWidgets[0].setText(self.colItems[0].text())
            self.colWidgets[1].setText(self.colItems[1].text())
            self.colWidgets[2].setText(self.colItems[2].text())
            self.colWidgets[3].setChecked(self.colItems[3].text() == "True")
            pass

        def SetupEvent(self):
            pass

        def setValueToTableRowFromForm(self):
            self.colItems[0].SetValue(self.colWidgets[0].toPlainText(), self.colWidgets[0].toPlainText())
            self.colItems[1].SetValue(self.colWidgets[1].toPlainText(), self.colWidgets[1].toPlainText())
            self.colItems[2].SetValue(self.colWidgets[2].toPlainText(), self.colWidgets[2].toPlainText())
            self.colItems[3].SetValue(f"{self.colWidgets[3].isChecked()}", self.colWidgets[3].isChecked())


class DescExtractPresetTable(ConfigTableView):
    """
    """

    def __init__(self, *args, **kwargs):
        # from . import models
        self.默认属性字典: list[G.safe.models.类型_属性项_描述提取规则] = []
        super().__init__(*args, **kwargs)
        self.初始化默认行()
        self.table_model.setHorizontalHeaderLabels(self.colnames)

    def 初始化默认行(self):
        默认模型 = G.safe.models.类型_模型_描述提取规则()
        self.默认属性字典 = 默认模型.获取属性项有序列表_属性字典()

        self.defaultRowData = [(属性.组件显示值, 属性) for 属性 in self.默认属性字典]
        self.colnames = [列[1].展示名 for 列 in self.defaultRowData]
        G.safe.funcs.Utils.print(self.colnames.__str__())
        return 默认模型

    def GetRowFromData(self, raw_data: "dict"):
        # from . import models
        有序属性字典 = G.safe.models.类型_模型_描述提取规则(数据源=raw_data).获取属性项有序列表_属性字典()
        return [self.TableItem(self, 属性.组件显示值, 属性) for 属性 in 有序属性字典]

    def NewRow(self):
        w = self.NewRowFormWidget(self)
        w.widget.exec()
        if w.ok:
            self.AppendRow(w.colItems)
            self.SaveDataToConfigModel()

    def ShowRowEditor(self, row: "list[DescExtractPresetTable.TableItem]"):
        w = self.NewRowFormWidget(self, colItems=row)
        w.widget.exec()
        if w.ok:
            # w.setValueToTableRowFromForm()  # 从新建表单设置回到表格 这一步是不需要的, 在onokclicked上已经完成了
            self.SaveDataToConfigModel()  # 从表格回到配置项

    #
    def SaveDataToConfigModel(self):

        data = []
        for row in range(self.table_model.rowCount()):
            item: DescExtractPresetTable.TableItem = self.table_model.item(row, 0)
            data.append(item.GetData().上级.数据源)
        self.ConfigModelItem.setValue(data)
        #     rowdata = []
        #     for col in range(len(self.colnames)):
        #         item: "DescExtractPresetTable.TableItem" = self.table_model.item(row, col)
        #         value = item.GetValue()
        #         rowdata.append(value)
        #     data.append(rowdata)
        # self.ConfigModelItem.setValue(data, 需要设值回到组件=False)
        pass

    #
    class TableItem(ConfigTableView.TableItem):

        def GetData(self):
            # from . import models
            data: G.safe.models.类型_属性项_描述提取规则 = self.data()
            return data
            pass

        pass

    class NewRowFormWidget(ConfigTableNewRowFormView):
        def SetupEvent(self):
            pass

        def SetupWidget(self):
            pass

        def setValueToTableRowFromForm(self):
            # if self.isNew:
            #     self.模型.数据源 = {}
            #     [self.模型.数据源.__setitem__(字段名, 属性.值) for 字段名, 属性 in self.模型.属性字典.items()]
            for 列 in self.colItems:
                属性项: G.safe.models.类型_属性项_描述提取规则 = 列.GetData()
                列.setText(属性项.组件显示值)
            pass

        def __init__(self, 上级: "DescExtractPresetTable",
                     colItems: "List[DescExtractPresetTable.TableItem]" = None):
            self.isNew = False
            self.superior: DescExtractPresetTable = 上级
            if not colItems:
                self.isNew = True
                self.模型 = 上级.初始化默认行()
                colItems = [上级.TableItem(上级, 属性.组件显示值, 属性) for 属性 in 上级.默认属性字典]
                self.UI字典 = self.模型.创建UI字典()
                colWidget = [self.UI字典[属性[1].字段名] for 属性 in 上级.defaultRowData]
            else:
                self.模型 = colItems[0].GetData().上级
                self.UI字典 = self.模型.创建UI字典()
                colWidget = [self.UI字典[属性[1].字段名] for 属性 in 上级.defaultRowData]
            super().__init__(上级, colItems, colWidget)
            模板选择组件: "属性项组件.模板选择" = self.UI字典[self.模型.模板.字段名].核心组件
            字段选择组件: "属性项组件.字段选择" = self.UI字典[self.模型.字段.字段名].核心组件
            模板选择组件.当完成赋值.append(lambda 自己, 值: 字段选择组件.检查模板编号合法性(值))


class GviewConfigApplyTable(ConfigTableView):
    """
    """
    colnames = [译.视图名]
    defaultRowData = [("",)]
    IsList = True

    def NewRow(self):
        w = self.NewRowFormWidget(self)
        w.widget.exec()
        if w.ok and w.判断已选中:
            w.setValueToTableRowFromForm()
            self.AppendRow(w.colItems)
            self.SaveDataToConfigModel()
        pass

    def AppendRow(self, row: "list[ConfigTableView.TableItem]"):
        self.table_model.appendRow(row)
        pass

    def ShowRowEditor(self, row: "list[GviewConfigApplyTable.TableItem]"):
        w = self.NewRowFormWidget(self, row)
        w.widget.exec()
        if w.ok and w.判断已选中:
            w.setValueToTableRowFromForm()
            self.SaveDataToConfigModel()

    def RemoveRow(self):
        # from ..bilink.dialogs.linkdata_grapher import Grapher
        Grapher = G.safe.linkdata_grapher.Grapher
        idx = self.viewTable.selectedIndexes()
        if len(idx) == 0:
            return
        取出的项 = self.table_model.takeRow(idx[0].row())[0]
        被删的视图标识: str = 取出的项.data()
        #
        上级的配置模型: G.safe.configsModel.GviewConfigModel = self.上级.参数模型
        调用者: Grapher.ToolBar = self.上级.调用者
        调用者视图标识 = 调用者.superior.data.gviewdata.uuid
        需要重启 = False
        G.safe.funcs.GviewConfigOperation.指定视图配置(被删的视图标识)
        self.ConfigModelItem.value.remove(被删的视图标识)
        if 调用者视图标识 == 被删的视图标识:
            需要重启 = True
        if not G.objs.Record.GviewConfig.静态_存在于数据库中(上级的配置模型.uuid.value):
            self.上级.参数模型.元信息.确定保存到数据库 = False
            需要重启 = True
            pass
        if 需要重启:
            self.上级.close()
            调用者.openConfig()

    def SaveDataToConfigModel(self):
        """ """
        newConfigItem = []
        for row in range(self.table_model.rowCount()):
            item = self.table_model.item(row, 0)
            newConfigItem.append(item.data())
        self.ConfigModelItem.setValue(newConfigItem, 需要设值回到组件=False)
        pass

    def GetRowFromData(self, data: "list[str]"):
        # return [for itemname in data]
        return list(map(lambda itemname: GviewConfigApplyTable.TableItem(self, itemname), data))

    class TableItem(ConfigTableView.TableItem):

        def __init__(self, superior: ConfigTableNewRowFormView, uuid: "str"):
            """
            uuid: gviewUuid
            """
            if uuid == "":
                name = ""
            else:
                name = G.safe.funcs.GviewOperation.load(uuid=uuid).name
            super().__init__(superior, name)

            self.superior: "GviewConfigApplyTable" = superior
            self.setData(uuid)

        def GetValue(self):
            return self.text()

        pass

    class NewRowFormWidget(ConfigTableNewRowFormView):
        """

        """

        def GetColWidgets(self) -> "list[QWidget]":
            pass

        def SetupWidget(self):
            self.widget.setWindowTitle("choose a graph view")
            self.MakeInnerWidget()
            pass

        def MakeInnerWidget(self):
            """

            """
            B = G.objs.Bricks
            L = self.layout_dict
            layout, widget, kids = B.triple
            tableView: "Standard.TableView" = L[kids][1][widget]
            searchStr: "QLineEdit" = L[kids][0][kids][0][widget]
            searchBtn: "QToolButton" = L[kids][0][kids][1][widget]
            searchBtn.setIcon(QIcon(G.src.ImgDir.open))
            searchStr.setPlaceholderText(Translate.由视图名搜索视图)
            return widget

        @property
        def 判断已选中(self):
            B = G.objs.Bricks
            L = self.layout_dict
            layout, widget, kids = B.triple
            tableView: "Standard.TableView" = L[kids][1][widget]
            return len(tableView.selectedIndexes()) > 0

        def setValueToTableRowFromForm(self):
            """
            """
            if not self.tableView.selectedIndexes():
                return

            选中项: "QStandardItem" = self.tableModel.itemFromIndex(self.tableView.selectedIndexes()[0])
            视图名, 视图标识 = 选中项.text(), 选中项.data()

            现配置模型: "G.safe.configsModel.GviewConfigModel" = self.superior.上级.参数模型
            G.safe.funcs.GviewConfigOperation.指定视图配置(视图记录=视图标识, 新配置记录=现配置模型.uuid.value)

            视图配置表的项 = self.superior.TableItem(self.superior, 视图标识)
            # 视图配置表的项.setData(视图标识)
            if self.isNew:
                self.colItems = [视图配置表的项]
            else:
                self.colItems[0].SetValue(视图名, 视图标识)
            pass

        def __init__(self, superior: "GviewConfigApplyTable",
                     colItems: "list[GviewConfigApplyTable.TableItem]" = None):
            """处理单行打开的情况"""
            B = G.objs.Bricks
            layout, widget, kids = B.triple
            # if not colItems:
            #     colItems = funcs.Map.do(superior.defaultRowData, lambda data: superior.TableItem(superior, *data))
            self.tableView: G.safe.funcs.组件定制.TableView = G.safe.funcs.组件定制.TableView(title_name="123")
            self.tableModel: "QStandardItemModel" = G.safe.funcs.组件定制.模型(["视图名/name of view"])
            self.searchStr: "QLineEdit" = QLineEdit()
            self.searchBtn: "QToolButton" = QToolButton()

            self.layout_dict = {layout: QVBoxLayout(), kids: [
                {layout: QHBoxLayout(),
                 kids: [
                     {widget: self.searchStr},
                     {widget: self.searchBtn}
                 ]},
                {widget: self.tableView}
            ]}

            B = G.objs.Bricks
            L = self.layout_dict
            layout, widget, kids = B.triple

            self.layoutTree = self.InitLayout(self.layout_dict)[layout]
            self.containerWidget = QWidget()
            self.containerWidget.setLayout(self.layoutTree)
            self.colWidgets = [self.containerWidget]
            super().__init__(superior, colItems, self.colWidgets)

            self.SetupWidget()
            self.SetupEvent()

            pass

        def SetupEvent(self):
            """

            """

            def onClick(searchString: "str"):
                if searchString == "" or not re.search(r"\S", searchString):
                    模糊搜索得到的视图表 = G.safe.funcs.GviewOperation.load_all()
                else:
                    关键词正则 = re.sub(r"\s", ".*", searchString)
                    DB, Logic = G.DB, G.objs.Logic
                    DB.go(DB.table_Gview)
                    模糊搜索得到的视图表 = DB.select(
                        Logic.REGEX("name", 关键词正则)).return_all().zip_up().to_gview_record()
                self.tableModel = G.safe.funcs.组件定制.模型(["视图名/name of view"])
                采用本配置的视图表 = self.superior.ConfigModelItem.value
                [self.tableModel.appendRow([G.safe.funcs.组件定制.Item(视图数据.name, data=视图数据.uuid)]) for 视图数据 in
                 模糊搜索得到的视图表 if 视图数据.uuid not in 采用本配置的视图表]
                self.tableView.setModel(self.tableModel)

            self.tableView.setModel(self.tableModel)

            self.searchBtn.clicked.connect(lambda: onClick(self.searchStr.text()))
            # self.containerWidget.show()
            pass


class GroupReviewConditionList(ConfigTableView):
    """"""
    colnames = ["searchString"]
    IsList = True
    defaultRowData = [("",)]

    def NewRow(self):
        w = self.NewRowFormWidget(self)
        w.widget.exec()
        if w.ok:
            self.AppendRow(w.colItems)
            self.SaveDataToConfigModel()
        pass

    def ShowRowEditor(self, row: "list[ConfigTableView.TableItem]"):
        w = self.NewRowFormWidget(self, row)
        w.widget.exec()
        if w.ok:
            self.SaveDataToConfigModel()
        pass

    def SaveDataToConfigModel(self):
        v = []
        [v.append(self.table_model.item(i, 0).text()) for i in range(self.table_model.rowCount())]
        self.ConfigModelItem.setValue(v, 需要设值回到组件=False)
        pass

    class NewRowFormWidget(ConfigTableNewRowFormView):
        """输入文本即可,如果是gview开头则要检查是否存在"""

        def __init__(self, superior: "GroupReviewConditionList",
                     colItems: "list[GroupReviewConditionList.TableItem]" = None):
            """注意,defaultRowData需要考虑superior.TableItem(superior, data)载入是否正确
            """
            self.col0: "QTextEdit" = QTextEdit()  # self.colWidgets[0]
            self.colWidgets = [QTextEdit()]
            super().__init__(superior, colItems)

        def SetupWidget(self):
            self.colWidgets[0].setText(self.colItems[0].text())
            pass

        def setValueToTableRowFromForm(self):
            self.colItems[0].SetValue(self.colWidgets[0].toPlainText(), self.colWidgets[0].toPlainText())
            pass

        def SetupEvent(self):
            pass

    class TableItem(ConfigTableView.TableItem):

        def __init__(self, superior, name):
            self.isBool = False
            if type(name) != str:
                name = str(name)
                self.isBool = True
            super().__init__(superior, name)
            self.superior: "GroupReviewConditionList" = superior

        def ShowAsWidget(self):
            if self.isBool:
                widget = QRadioButton()
                widget.setChecked(self.text() == "True")
            else:
                widget = QTextEdit()
                widget.setText(self.text())
            return widget

        def GetValue(self):
            return self.text()

        pass


class GviewConfigNodeFilter(配置项单选型表格组件):
    """
    结点筛选器, 表格每一行对应一个筛选器,
    条件|选中
    """
    colnames = [译.选中, 译.过滤表达式]
    defaultRowData = ["", ""]

    def NewRowFormWidget(self, 上级, 行: "list[ConfigTableView.TableItem]" = None, *args, **kwargs):
        说明 = 译.例子_结点过滤 + "\n" + G.safe.funcs.GviewConfigOperation.获取eval可用变量与函数的说明()

        class edit_widget(组件_表格型配置项_列编辑器_可执行字符串):
            def on_test(self):
                # noinspection PyBroadException
                try:
                    strings = self.布局[子代][0][组件].toPlainText()
                    literal = eval(strings, *G.safe.funcs.GviewConfigOperation.获取eval可用变量与函数())

                    if type(literal) != bool:
                        self.设置说明栏("type error:" + 译.可执行字符串表达式的返回值必须是布尔类型)
                        return False
                    else:
                        self.设置说明栏("ok")
                        return True
                except Exception as err:
                    self.设置说明栏("syntax error:" + err.__str__())
                    return False
                pass

        return edit_widget(上级, 行, 说明)


class GviewConfigCascadingSorter(配置项单选型表格组件):
    colnames = [译.选中, 译.多级排序依据]
    defaultRowData = ["", ""]

    def NewRowFormWidget(self, 上级, 行: "list[ConfigTableView.TableItem]" = None, *args, **kwargs):
        说明 = 译.例子_多级排序 + "\n" + G.safe.funcs.GviewConfigOperation.获取eval可用变量与函数的说明()

        class edit_widget(组件_表格型配置项_列编辑器_可执行字符串):
            def on_test(self):
                _ = G.safe.baseClass.枚举命名
                locals_dict = G.safe.funcs.GviewConfigOperation.获取eval可用字面量()

                try:
                    strings = self.布局[子代][0][组件].toPlainText()
                    literal = eval(strings, {}, {**locals_dict, _.上升: _.上升, _.下降: _.下降})

                    if type(literal) != list:
                        self.设置说明栏("type error:" + 译.可执行字符串表达式的返回值必须是列表类型)
                        return False
                    elif len([tup for tup in literal if len(tup) != 2]) > 0:
                        self.设置说明栏("type error:" + 译.可执行字符串_必须是一个二元元组)
                        return False
                    elif len(
                            [tup for tup in literal if not (tup[0] in locals_dict and tup[1] in [_.上升, _.下降])]) > 0:
                        self.设置说明栏("type error:" + 译.可执行字符串_二元组中的变量名必须是指定名称)
                        return False
                    else:
                        self.设置说明栏("ok")
                        return True
                except Exception as err:
                    self.设置说明栏("syntax error:" + err.__str__())
                    return False
                pass

        return edit_widget(上级, 行, 说明)


class GviewConfigWeightedSorter(配置项单选型表格组件):
    colnames = [译.选中, 译.加权公式]
    defaultRowData = ["", ""]

    def NewRowFormWidget(self, 上级, 行: "list[ConfigTableView.TableItem]" = None, *args, **kwargs):
        说明 = 译.例子_加权排序 + "\n" + G.safe.funcs.GviewConfigOperation.获取eval可用变量与函数的说明()

        class edit_widget(组件_表格型配置项_列编辑器_可执行字符串):
            def on_test(self):
                globals_dict, locals_dict = G.safe.funcs.GviewConfigOperation.获取eval可用变量与函数()
                try:
                    strings = self.布局[子代][0][组件].toPlainText()
                    literal = eval(strings, globals_dict, locals_dict)
                    if type(literal) not in (int, float):
                        self.设置说明栏(译.可执行字符串_返回的值必须是数值类型)
                        return False
                    else:
                        self.设置说明栏("ok")
                        return True
                except Exception as err:
                    self.设置说明栏("syntax error:" + err.__str__())
                    return False

        return edit_widget(上级, 行, 说明)


class GviewNodeProperty(QDialog):
    class Enum:
        QLabel = "QLabel"
        QTextEdit = "QTextEdit"
        QRadioButton = "QRadioButton"
        QSlider = "QSlider"
        QCheckBox = "QCheckBox"
        QComboBox = "QComboBox"

    def node_property(self):

        pass

    def __init__(self, gview_data=None, node_uuid=None, superior=None):
        super().__init__()
        # from ..bilink.dialogs.linkdata_grapher import Grapher
        Grapher = G.safe.linkdata_grapher.Grapher
        self.superior: Grapher = superior
        self.major_layout = QFormLayout()
        self.gview_data: G.safe.funcs.GViewData = gview_data
        self.node_uuid: str = node_uuid
        self.btn_ok = QPushButton(QIcon(G.src.ImgDir.correct), "")
        self.btn_ok.clicked.connect(self.save_quit)
        _ = GviewNodeProperty.Enum
        __ = G.safe.baseClass.枚举命名
        self.prop_dict: "dict[str,dict]" = {  # 组件名:属性名:组件实例对象
            _.QRadioButton: {__.结点.需要复习: QRadioButton(),
                             __.结点.必须复习: QRadioButton(),
                             __.结点.漫游起点: QRadioButton(),
                             __.结点.主要结点: QRadioButton()},
            _.QTextEdit: {__.结点.描述: QTextEdit()},
            _.QComboBox: {__.结点.角色: {
                __.结点.数据源: G.safe.funcs.GviewConfigOperation.获取结点角色数据源(gview_data=self.gview_data),
                __.组件: QComboBox()

            }},
            _.QSlider: {__.结点.优先级: {
                __.范围: [-100, 100],
                __.组件: QSlider()
            }},
            _.QLabel: {__.结点.数据类型: QLabel(),
                       __.结点.位置: QLabel(),
                       __.结点.上次编辑: QLabel(),
                       __.结点.上次访问: QLabel(),
                       __.结点.访问次数: QLabel(),
                       __.结点.出度: QLabel(),
                       __.结点.入度: QLabel(),
                       }
        }
        node_data = self.gview_data.nodes[self.node_uuid]
        for w in self.prop_dict.keys():
            if w == _.QRadioButton:
                for name in self.prop_dict[w].keys():
                    widget: QRadioButton = self.prop_dict[w][name]
                    widget.setChecked(node_data[name].值)
                    self.major_layout.addRow(name, widget)
            elif w == _.QTextEdit:
                for name in self.prop_dict[w].keys():
                    widget: QTextEdit = self.prop_dict[w][name]
                    widget.setText(G.safe.funcs.GviewOperation.获取视图结点描述(self.gview_data, self.node_uuid))
                    self.major_layout.addRow(name, widget)
            elif w == _.QComboBox:
                for name in self.prop_dict[w].keys():
                    widget: QComboBox = self.prop_dict[w][name][__.组件]
                    data_source: list[str] = self.prop_dict[w][name][__.视图配置.结点角色表]
                    saved_value = node_data[name]

                    for idx in range(len(data_source)):
                        widget.addItem(data_source[idx], idx)
                    saved_value_idx = widget.findData(saved_value)
                    widget.addItem(QIcon(G.src.ImgDir.cancel), "", -1)
                    widget.setCurrentIndex(saved_value_idx if saved_value_idx != -1 else len(data_source))
                    self.major_layout.addRow(name, widget)
            elif w == _.QSlider:
                for name in self.prop_dict[w].keys():
                    widget_QSlider: QSlider = self.prop_dict[w][name][__.组件]
                    data_range = self.prop_dict[w][name][__.范围]
                    saved_value = node_data[name]
                    widget_QSlider.setRange(data_range[0], data_range[1])
                    widget_QSlider.setValue(saved_value)
                    widget_QSlider.setToolTip(saved_value.__str__())
                    widget_QSlider.valueChanged.connect(
                        lambda: widget_QSlider.setToolTip(widget_QSlider.value().__str__()))
                    self.major_layout.addRow(name, widget_QSlider)
            elif w == _.QLabel:
                for name in self.prop_dict[w].keys():
                    widget: QLabel = self.prop_dict[w][name]
                    saved_value = node_data[name] if name in node_data else ""
                    if name in [__.结点.上次编辑, __.结点.上次访问]:
                        widget.setText(G.safe.funcs.Utils.时间戳转日期(saved_value).__str__())
                    else:
                        widget.setText(saved_value.__str__())
                    self.major_layout.addRow(name, widget)
        self.major_layout.addRow("", self.btn_ok)
        self.setLayout(self.major_layout)

    def save_quit(self):
        _ = GviewNodeProperty.Enum
        __ = G.safe.baseClass.枚举命名
        node_data = self.gview_data.nodes[self.node_uuid]
        for widget_type in self.prop_dict.keys():
            if widget_type == _.QRadioButton:
                for name in self.prop_dict[widget_type].keys():
                    widget: QRadioButton = self.prop_dict[widget_type][name]
                    node_data[name] = widget.isChecked()
            elif widget_type == _.QSlider:
                for name in self.prop_dict[widget_type].keys():
                    widget: QSlider = self.prop_dict[widget_type][name][__.组件]
                    node_data[name] = widget.value()
            elif widget_type == _.QComboBox:
                for name in self.prop_dict[widget_type].keys():
                    widget: QComboBox = self.prop_dict[widget_type][name][__.组件]
                    node_data[name] = widget.currentData()
            elif widget_type == _.QTextEdit:
                for name in self.prop_dict[widget_type].keys():
                    widget: QTextEdit = self.prop_dict[widget_type][name]
                    G.safe.funcs.GviewOperation.设定视图结点描述(self.gview_data, self.node_uuid, widget.toPlainText())

        self.close()
        pass

    def save(self):

        pass


class GviewConfigNodeRoleEnumEditor(ConfigItemLabelView):
    """
    以不可编辑的label形式展示文本, 如果需要编辑, 点击按钮弹出特定的编辑器进行编辑
    这样做的目的是为了对编辑内容进行检测.
    """

    class 角色枚举编辑器(可执行字符串编辑组件):

        def 设置当前配置项对应展示组件的值(self, value=None):
            """此处无用"""
            pass

        def __init__(self, 文本):
            super().__init__(文本)
            # self.布局[子代][2][组件].setText(译.说明_结点角色枚举)

        def on_help(self):
            self.设置说明栏(译.说明_结点角色枚举)

        def on_test(self):
            # noinspection PyBroadException
            try:
                strings = self.布局[子代][0][组件].toPlainText()
                literal = literal_eval(strings)
                if type(literal) != list:
                    self.设置说明栏("type error:input must be a list")
                    return False
                elif [i for i in literal if type(i) != str]:
                    self.设置说明栏("type error:every element of the list must be string")
                    return False
                elif len(literal) != len(set(literal)):
                    self.设置说明栏("value error:every element must be unique")
                else:
                    self.设置说明栏("ok")
                    return True
            except Exception as err:
                self.设置说明栏("syntax error:" + err.__str__())
                return False

            #

            pass

        def on_ok(self):
            if self.on_test():
                self.ok = True
                self.合法字符串 = self.布局[子代][0][组件].toPlainText()
                self.close()

            pass

    def on_edit_btn_clicked(self):
        w = self.角色枚举编辑器(self.label.text())
        w.exec()
        if w.ok:
            self.ConfigModelItem.setValue(w.合法字符串)

        pass


class GviewConfigDeckChooser(ConfigItemLabelView):

    def on_edit_btn_clicked(self):

        w = 导入.selector_widgets.universal_deck_chooser()
        w.exec()
        self.ConfigModelItem.setValue(w.结果)
        pass

    def SetupData(self, raw_data):
        if raw_data != -1:
            self.label.setText(mw.col.decks.name(raw_data))
        else:
            self.label.setText("no default deck")
        pass


class GviewConfigTemplateChooser(ConfigItemLabelView):

    def on_edit_btn_clicked(self):
        w = imports.selector_widgets.universal_template_chooser()
        w.exec()
        self.ConfigModelItem.setValue(w.结果)
        pass
    def SetupData(self, raw_data):
        if raw_data != -1:
            self.label.setText(mw.col.models.get(raw_data)["name"])
        else:
            self.label.setText("no default template")
        pass

class GviewConfigViewConfigChooser(ConfigItemLabelView):
    """指的是创建视图型结点时,默认选择的视图配置"""
    def on_edit_btn_clicked(self):
        w = imports.selector_widgets.view_config_chooser()
        w.exec()
        self.ConfigModelItem.setValue(w.结果.ID)
        pass
    def SetupData(self, raw_data):
        if raw_data and G.safe.funcs.GviewConfigOperation.存在(raw_data):
            self.label.setText(G.safe.funcs.GviewConfigOperation.从数据库读(raw_data).name)
        else:
            self.label.setText("no default config")
        pass

class GlobalConfigDefaultViewChooser(ConfigItemLabelView):
    """默认视图用的他"""

    def on_edit_btn_clicked(self):

        w = 导入.selector_widgets.view_chooser()
        w.exec()
        self.SetupData(w.编号)
        self.ConfigModelItem.value = w.编号
        pass

    def SetupData(self, raw_data):
        if raw_data != -1:
            self.label.setText(G.safe.funcs.GviewOperation.load(raw_data).name)
        else:
            self.label.setText("no default view")
        pass
