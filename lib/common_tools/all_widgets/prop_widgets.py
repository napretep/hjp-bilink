from .basic_widgets import *

枚举 = G.safe.baseClass.枚举命名
基 = G.objs.Bricks
布局, 组件, 子代, 占据 = 基.四元组

# class 新建视图(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.视图的名字 = ""
#         self.选中的配置 = None
#         self.确认建立 = False
#
#         # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
class 属性项组件:
    class 基类_项组件基础(QWidget):
        def __init__(self, 上级):
            super().__init__()
            self.上级: G.safe.models.函数库_UI生成.组件 = 上级
            self.当完成赋值 = G.safe.hookers.当模型的属性项组件_完成赋值()

        @abstractmethod
        def 设值到源(self, value):
            raise NotImplementedError()

    class 基本选择类(基类_项组件基础):
        def __init__(self, 上级):
            super().__init__(上级)
            self.ui组件 = G.safe.funcs.组件定制.文本框(开启自动换行=True)
            self.修改按钮 = G.safe.funcs.组件定制.按钮_修改行()
            self.修改按钮.clicked.connect(lambda: self.当修改按钮_被点击())  # 槽函数不支持中文
            G.safe.funcs.组件定制.组件组合({框: QHBoxLayout(), 子: [
                    {件: self.ui组件, 占: 1}, {件: self.修改按钮, 占: 0}]},
                                   self)
            self.ui组件.setText(self.get_name(self.上级.数据源.值))
            self.不选信息 = 译.不选等于全选

        def 当修改按钮_被点击(self):
            选择器实例 = self.选择器构造()
            选择器实例.exec()
            if 选择器实例.结果 is None or (type(选择器实例.结果) in [int, float] and 选择器实例.结果 < 0) or \
                    (type(选择器实例.结果) == list and len(选择器实例.结果) == 0):
                showInfo(self.不选信息)

            self.设值到源(选择器实例.结果)

        def 设值到源(self, 值):
            self.ui组件.setText(self.get_name(值))
            新值 = 值 if type(值) in [int, float, bool, str, complex] else 值.copy() if "copy" in 值.__dir__() else 值
            self.上级.数据源.设值(新值)
            self.当完成赋值(self, 新值)
            # funcs.Utils.print(self,new_value)
            pass

        def 选择器构造(self) -> "QDialog":
            raise NotImplementedError()  # """打开某一种选择器"""

        def get_name(self, value): raise NotImplementedError()

    class 角色多选(基本选择类):
        """卡片角色多选"""

        def __init__(self, 上级):
            super().__init__(上级)
            self.属性项: "G.safe.models.类型_视图结点属性项" = self.上级.数据源
            self.配置模型 = self.属性项.上级.数据源.模型.上级.config_model
            self.角色表 = eval(self.配置模型.data.node_role_list.value)
            self.值修正()
            self.不选信息 = 译.不选角色等于不选
            self.ui组件.setText(self.get_name(self.上级.数据源.值))

        def 值修正(self):
            角色选中表: 'list[str]' = self.属性项.值
            新表 = [角色 for 角色 in 角色选中表 if 角色 in range(len(self.角色表))]
            self.属性项.设值(新表)

        def 选择器构造(self):
            """需要获取到config,所以需要获取到view uuid"""
            return 导入.selector_widgets.role_chooser_for_node(self.属性项.值, self.角色表)
            pass

        def get_name(self, value):
            return G.safe.funcs.逻辑.缺省值(value, lambda x: [self.角色表[idx] for idx in x if
                                                         idx in range(len(self.角色表))],
                                       f"<img src='{G.src.ImgDir.cancel}' width=10 height=10> no role").__str__()

    class 牌组选择(基本选择类):

        def 选择器构造(self): return 导入.selector_widgets.universal_deck_chooser()

        def get_name(self, value): return mw.col.decks.name_if_exists(value) if value > 0 else "ALL DECKS"

        # def __init__(self, 上级):
        #     super().__init__(上级)
        #     self.ui组件.setText(self.get_name(self.上级.数据源.值))

    class 模板选择(基本选择类):

        def get_name(self, value): return mw.col.models.get(value)["name"] if value > 0 else "ALL TEMPLATES"

        def 选择器构造(self): return 导入.selector_widgets.universal_template_chooser()

        # def __init__(self, 上级):
        #     super().__init__(上级)
        #     self.ui组件.setText(self.get_name(self.上级.数据源.值))

    class 字段选择(基本选择类):
        def __init__(self, 上级, 模板编号):
            self.模板编号 = -1
            super().__init__(上级)
            self.检查模板编号合法性(模板编号)

        def 检查模板编号合法性(self, value):
            self.模板编号 = value
            if self.模板编号 < 0:
                self.修改按钮.setEnabled(False)
            else:
                self.修改按钮.setEnabled(True)
            self.ui组件.setText(self.get_name(self.上级.数据源.值))

        def 选择器构造(self):
            return 导入.selector_widgets.universal_field_chooser(self.模板编号)

        def get_name(self, value):
            return G.safe.funcs.卡片字段操作.获取字段名(self.模板编号, value, "ALL FIELDS")

    class 标签选择(基本选择类):
        def 选择器构造(self):
            return 导入.selector_widgets.universal_tag_chooser(self.上级.数据源.值)
            pass

        def get_name(self, value):
            return G.safe.funcs.逻辑.缺省值(value, lambda x: x, "ALL TAGS").__str__()
            # if len(value)==0:
            #     return "ALL TAGS"
            # return value.__str__()
            # pass

    class 视图配置选择(基本选择类):
        def 选择器构造(self) -> "QDialog":
            return 导入.selector_widgets.view_config_chooser()

        def get_name(self, value):
            value: G.safe.baseClass.IdName = value
            return G.safe.funcs.逻辑.缺省值(value, lambda x: x.name if x else None,
                                       f"<img src='{G.src.ImgDir.config}' width=16 height=16> new config").__str__()

        def __init__(self, 上级):
            super().__init__(上级)
            self.不选信息 = 译.不选等于新建

    # 表格类
    class 基本表格类(基类_项组件基础):
        """
        1 表格组件 2 附带按钮 + - / 3 基本列名 4 上级 5 新行,修改,删除
        """

        def __init__(self, 上级):
            super().__init__(上级)
            self.整体布局 = QVBoxLayout(上级)
            self.表格组件 = imports.funcs.组件定制.表格(单行选中=True,不可修改=True)
            self.表格模型 = imports.funcs.组件定制.模型(self.表格列名)
            self.按钮_添加行 = QPushButton("+")
            self.按钮_删除行 = QPushButton("-")
            self.按钮_修改行 = QPushButton(QIcon(G.src.ImgDir.edit), "")
            self.按钮_其他: "None|list[QPushButton]" =None
            self.初始化_组件界面()
            self.初始化_表格数据()
            self.初始化_事件()


        # 初始化
        def 初始化_事件(self):
            self.按钮_删除行.clicked.connect(lambda:self.行操作_删除())
            self.按钮_修改行.clicked.connect(lambda:self.行操作_修改())
            self.按钮_添加行.clicked.connect(lambda:self.行操作_添加())
            self.表格组件.doubleClicked.connect(lambda:self.行操作_修改())
            pass

        def 初始化_表格数据(self):
            """
            要考虑1 仅列表, 2 选中生效
            """
            self.表格组件.setModel(self.表格模型)
            self.表格模型.clear()
            self.表格模型.setHorizontalHeaderLabels(self.表格列名)
            if self.上级.数据源.值类型 == 枚举.值类型.表格:
                for 行 in self.上级.数据源.值:
                    行数据 = []
                    for 列名 in self.表格列名:
                        项 = 视图模型_表格_项(self.表格组件,展示值=行[列名].__str__(),列名=列名,实际值=行[列名])
                        行数据.append(项)

                    self.表格模型.appendRow(行数据)

            elif self.上级.数据源.值类型 == 枚举.值类型.列表:
                列名 = self.表格列名[0]
                for 行 in self.上级.数据源.值:
                    项 = 视图模型_表格_项(self.表格组件,展示值=行.__str__(),实际值=行,列名=列名)
                    self.表格模型.appendRow(项)
            else:
                raise ValueError("必须是列表或表格类型!")

        def 初始化_组件界面(self):
            布局字典 = {
                    布局: QVBoxLayout(),
                    子代: [
                            {组件: self.表格组件,占据:1,},
                            {布局: QHBoxLayout(),
                             占据: 0,
                             子代: [
                                     {组件: self.按钮_添加行},
                                     {组件: self.按钮_删除行},
                                     {组件: self.按钮_修改行},
                             ]
                             }
                    ]
            }
            if self.按钮_其他 is not None:
                [布局字典[子代][1][子代].append({组件: 按钮}) for 按钮 in self.按钮_其他]

            G.safe.funcs.组件定制.组件组合(布局字典, self.上级)
            # self.表格组件.verticalHeader().setHidden(True)
            # self.表格组件.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            # self.表格组件.horizontalHeader().setStretchLastSection(True)
            # self.表格组件.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            # self.表格组件.setSelectionMode(QAbstractItemViewSelectMode.SingleSelection)
            # self.表格组件.setSelectionBehavior(QAbstractItemViewSelectionBehavior.SelectRows)

        #抽象区

        @abstractmethod
        @property
        def 表格列名(self)->"list[str]":
            raise NotImplementedError()

        @abstractmethod
        @property
        def 单行模型(self) -> "G.safe.models.基类_模型":
            raise NotImplementedError()

        pass
        # 行操作

        def 行操作_添加(self):
            新行数据 = self.生成_行编辑器()
            if 新行数据:
                新行 = []
                for 列名 in self.表格列名:
                    项 = 视图模型_表格_项(self.表格组件, 展示值=新行数据[列名]["展示值"],
                                  列名=列名,
                                  实际值=新行数据[列名]["实际值"])
                    新行.append(项)
                self.表格模型.appendRow(新行)
            新数据 = self.数据_从表格生成()
            self.设值到源(新数据)

        def 行操作_删除(self):
            索引 = self.表格组件.selectedIndexes()
            if len(索引) == 0:
                tooltip("no selected row")
                return
            self.表格模型.removeRow(索引[0].row(), 索引[0].parent())
            新数据 = self.数据_从表格生成()
            self.设值到源(新数据)

        def 行操作_修改(self):
            if not self.表格组件.selectedIndexes():
                tooltip("no selected row")
                return
            选中行号 = self.表格组件.selectedIndexes()[0].row()
            修改项 = [self.表格模型.item(选中行号,列号) for 列号 in range(len(self.表格列名))]
            待修改行数据 = {}
            for 项 in 修改项:
                列数据 = 项.data(role=Qt.ItemDataRole.UserRole)
                待修改行数据[列数据["列名"]]=列数据
            #
            新行数据 = self.生成_行编辑器(待修改行数据)

            if 新行数据:
                for 项 in 修改项:
                    列数据 = 项.data(role=Qt.ItemDataRole.UserRole)
                    当前列名 = 列数据["列名"]
                    项.setText(新行数据[当前列名]["展示值"])
                    项.setData(新行数据[当前列名],role=Qt.ItemDataRole.UserRole)
            新数据 = self.数据_从表格生成()
            self.设值到源(新数据)

        def 数据_从表格生成(self):

            表格 = []
            表格列名 = self.表格列名
            if self.上级.数据源.值类型 == 枚举.值类型.表格:
                for 行号 in range(self.表格模型.rowCount()):
                    行数据 = {}
                    for 列号 in range(self.表格模型.columnCount()):
                        列名 = 表格列名[列号]
                        列项 = self.表格模型.item(行号,列号)
                        行数据[列名] = 列项.data(role=Qt.ItemDataRole.UserRole)["实际值"]
                    表格.append(行数据)
            elif self.上级.数据源.值类型 == 枚举.值类型.列表:
                for 行号 in range(self.表格模型.rowCount()):
                    for 列号 in range(self.表格模型.columnCount()):
                        列项 = self.表格模型.item(行号, 列号)
                        实际值 = 列项.data(role=Qt.ItemDataRole.UserRole)["实际值"]
                        表格.append(实际值)
            return 表格

        def 设值到源(self, value):
            self.上级.数据源.设值(value)
            pass



        def 生成_行编辑器(self, 预加载数据=None)->"None|dict":
            """
            预加载数据: {列名:{列名:str.展示值:str,实际值:str}
            """
            单行模型 = self.单行模型
            if 预加载数据:
                for 属性 in 单行模型.属性字典.values():
                    属性.设值(预加载数据[属性.展示名]["实际值"])
                pass

            单行表单 = 单行模型.创建UI(QWidget())
            单行组件 = imports.funcs.组件定制.表格_单行行编辑组件(单行表单)
            单行组件.窗口.exec()
            if 单行组件.确认按钮被点击:
                新数据 = {}
                for 属性 in 单行模型.属性字典.values():
                    新数据[属性.展示名] = {
                            "列名" : 属性.展示名,
                            "展示值": 属性.组件显示值,
                            "实际值": 属性.值
                    }
                return 新数据
            else:
                return None

    class 表格_提取规则(基本表格类):

        @property
        def 单行模型(self):
            return G.safe.models.类型_模型_描述提取规则()
        @property
        def 表格列名(self):
            属性项列表:"list[G.safe.models.类型_属性项_描述提取规则]" = list(self.单行.属性字典.values())
            属性项列表.sort(key=lambda x:x.属性项排序位置)
            列名= [属性项.展示名 for 属性项 in 属性项列表]
            return 列名







