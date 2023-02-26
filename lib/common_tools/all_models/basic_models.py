# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'basic_models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 5:10'
"""
# from .basic_import import *
from .imports import *

# from . import *
class 函数库_UI生成:
    """UI有不同的类型,每种类型都要定制地写一个函数, 最后把它们组合进一个字典, 到时候根据组件类型作为键访问字典的值并调用即可获得组件"""
    @staticmethod
    def 提示按钮(说明:"str"):
        return funcs.组件定制.按钮_提示(触发函数=lambda :funcs.Utils.大文本提示框(说明))

    @staticmethod
    def 做成行(左: "QWidget|QLayout", 右: "QPushButton|Widget|QLayout"):
        布局 = QHBoxLayout()
        if isinstance(左, QWidget):
            布局.addWidget(左, stretch=1)
        else:
            布局.addLayout(左, stretch=1)

        if isinstance(右, QWidget):
            布局.addWidget(右, stretch=0)
        else:
            布局.addLayout(右, stretch=0)
        布局.setContentsMargins(0, 0, 0, 0)
        return 布局

    class 组件(QWidget):
        def __init__(self, 项: "基类_属性项"):
            super().__init__()
            self.提示按钮 = 函数库_UI生成.提示按钮(项.说明)
            self.数据源: "基类_属性项" = 项
            self.setLayout(函数库_UI生成.做成行(*self.组件生成()))

        def 组件生成(self):
            左,右 = QWidget(),self.提示按钮
            if self.数据源.组件类型 == 枚举.组件类型.slider:
                拖动条 = QSlider(Qt.Orientation.Horizontal)

                数值显示 = QLabel(self.数据源.组件显示值.__str__())
                拖动条.setValue(self.数据源.组件显示值)
                if self.数据源.有限制:
                    拖动条.setRange(self.数据源.限制[0], self.数据源.限制[1])
                组件 = funcs.组件定制.组件组合({砖.布局: QHBoxLayout(), 砖.子代: [{砖.组件: 数值显示}, {砖.组件: 拖动条}]})

                def item_set_value(value):
                    self.数据源.设值(value)
                    数值显示.setText(value.__str__())

                拖动条.valueChanged.connect(item_set_value)
                self.给UI赋值 = lambda value: 拖动条.setValue(value)
            elif self.数据源.组件类型 == 枚举.组件类型.label:
                组件 = QLabel(self.数据源.组件显示值)
                组件.setWordWrap(True)
                self.给UI赋值 = lambda value: 组件.setText(value.__str__())
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.checkbox:
                组件 = QCheckBox()
                组件.setChecked(self.数据源.组件显示值)
                item_set_value = lambda value: self.数据源.设值(value)
                组件.clicked.connect(lambda: item_set_value(组件.isChecked()))
                self.给UI赋值 = lambda value: 组件.setChecked(value)
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.text:
                组件 = QTextEdit()
                组件.setText(self.数据源.组件显示值)
                临时文本储存 = [""]

                def when_need_update():
                    组件.blockSignals(False)
                    if 临时文本储存[0] != 组件.toPlainText():
                        临时文本储存[0] = 组件.toPlainText()
                        组件.blockSignals(True)
                        return QTimer.singleShot(100, when_need_update)
                    else:
                        self.数据源.设值(组件.toPlainText())

                组件.textChanged.connect(when_need_update)
                self.给UI赋值 = lambda value: 组件.setText(value)
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.customize:
                组件 = self.数据源.自定义组件(self)
                self.给UI赋值 = lambda value: 组件.setValue(value)
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.time:
                if isinstance(self.数据源.值, datetime.datetime):
                    组件 = QLabel(self.数据源.值.__str__())
                elif type(self.数据源.值) in [int, float]:
                    组件 = QLabel(funcs.Utils.时间戳转日期(self.数据源.值).__str__())
                else:
                    raise NotImplementedError(self.数据源.值)

                def setValue(value):
                    self.数据源.设值(value)
                    组件.setText(funcs.Utils.时间戳转日期(value).__str__())

                self.给UI赋值 = lambda value: setValue(value)
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.editable_label:

                按钮2 = funcs.组件定制.按钮_修改()
                右 = QVBoxLayout()
                组件 = funcs.组件定制.文本框(self.数据源.组件显示值)
                组件.setWordWrap(True)
                [右.addWidget(i) for i in [self.提示按钮, 按钮2]]

                def on_edit():
                    结果 = funcs.组件定制.长文本获取(组件.text())
                    if len(结果) > 0:
                        组件.setText(结果[0])
                        self.数据源.设值(结果[0])
                        if self.数据源.有校验 and not self.数据源.校验函数(self.数据源,结果[0]):
                            tooltip("illegal value")
                    pass

                def setValue(value):
                    组件.setText(value)
                    self.数据源.设值(value)

                按钮2.clicked.connect(on_edit)
                self.给UI赋值 = lambda value: setValue(value)
            elif self.数据源.组件类型 == 枚举.组件类型.spin:
                组件 = QSpinBox()
                组件.setValue(self.数据源.值)
                组件.valueChanged.connect(lambda x:self.数据源.设值(int(组件.value())))
                self.给UI赋值 = lambda value: 组件.setValue(value)
            左 = 组件
            return (左,右)


    pass



# """集->模型->属性, 集是模型的集合, 属性是模型的属性"""
@dataclass
class 基类_集模型:
    data: dict = None

    def keys(self):
        return self.data.keys()

    def copy(self):
        return self.data.copy()

    def items(self):
        return self.data.items()

    @abc.abstractmethod
    def __getitem__(self, node_id):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __str__(self):
        return self.data.__str__()

    def __repr__(self):
        return self.__str__()
    # 成员: "基类_模型" = None
    #
    # @abc.abstractmethod
    # def __getitem__(self, item):
    #     raise NotImplementedError()
    #
    #
    # @abc.abstractmethod
    # def keys(self):
    #     raise NotImplementedError()


# 布局, 组件, 子代 = 0, 1, 2
@dataclass
class 基类_模型:

    UI创建完成 = 0
    数据源: "None|Any" = None
    属性字典: "dict[str,基类_属性项]" = field(init=False)

    def 初始化(self, *args):
        raise NotImplementedError()

    def 创建UI字典(self):
        字典 = {}
        for 属性名 in self.__dict__.keys():
            if isinstance(self.__dict__[属性名], 基类_属性项):
                项: 基类_属性项 = self.__dict__[属性名]
                if 项.可展示:
                    组件 = 函数库_UI生成.组件(项)
                    字典[项.字段名] = 组件
        return 字典

    def 创建UI(self, 父类组件: "QWidget" = None):
        对话框 = 父类组件 if 父类组件 else QDialog()
        表单布局 = QFormLayout()
        表单布局.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        for 属性名 in self.__dict__.keys():
            if isinstance(self.__dict__[属性名], 基类_属性项):
                项: 基类_属性项 = self.__dict__[属性名]
                if 项.可展示:
                    组件 = 函数库_UI生成.组件(项)
                    表单布局.addRow(项.展示名, 组件)

        对话框.setLayout(表单布局)
        self.UI创建完成 = 1
        对话框.closeEvent = lambda x: self.__dict__.__setitem__("UI创建完成", 0)
        return 对话框

    def 获取可访变量(self, 指定变量类型=None) -> "Dict":
        """如果指定了变量类型, 则根据类型返回值"""
        变量字典 = {}
        for 变量名 in self.__dict__:

            if isinstance(self.__dict__[变量名], 基类_属性项):
                项: 基类_属性项 = self.__dict__[变量名]
                if 项.用户可访:
                    if 指定变量类型:
                        if type(项.值) in 指定变量类型:
                            变量字典[项.字段名] = 项.值
                    else:
                        变量字典[项.字段名] = 项.值

        return 变量字典

    def 获取可访字面量(self, 指定变量类型=None) -> "Dict":
        字面量字典 = {}

        for 变量名 in self.__dict__:
            if isinstance(self.__dict__[变量名], 基类_属性项):
                值 = self.__dict__[变量名].值
                字段名 = self.__dict__[变量名].字段名
                if 指定变量类型:
                    if type(值) in 指定变量类型:
                        字面量字典[字段名] = 字段名
                else:
                    字面量字典[字段名] = 字段名

        return 字面量字典

    def 获取属性项有序列表(self):
        return sorted(self.属性字典.keys(),key=lambda x:self.属性字典[x].属性项排序位置)

    # def 获取属性项(self):#获取的可能是无序列表
    #     属性字典 = {}
    #
    #     pass
    def __setitem__(self, key, value):
        self.属性字典[key].设值(value)

    def __getitem__(self, item) -> "基类_属性项":
        return self.属性字典[item]
        # return self.__dict__[item]

    def __post_init__(self):
        self.属性字典 = {}
        for 可能项 in self.__dict__:
            if isinstance(self.__dict__[可能项], 基类_属性项):
                项: 基类_属性项 = self.__dict__[可能项]
                self.属性字典[项.字段名] = 项
                项.上级 = self

    def __str__(self):
        return self.属性字典.__str__()

    def __repr__(self):
        return self.属性字典.__str__()


@dataclass
class 基类_属性项:
    """
    """

    字段名: "str"
    展示名: "str"
    从上级读数据: "int"
    保存到上级: "int"
    说明: "str" = 译.该项解释工作未完成
    可展示: "int" = 0  # 需要对应的展示组件,
    可展示中编辑: "int" = 0  # 需要对应的可展示中编辑组件, 与可展示联合判断
    用户可访: "int" = 0
    组件类型: "int" = None
    有校验: "int" = 0
    有限制: "int" = 0
    限制: "list" = field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT])
    组件传值方式: "None|Callable[[基类_属性项],Any]" = None
    _读取函数: "None|Callable[[基类_属性项],Any]" = None
    _保存值的函数: "Optional[Callable[[基类_属性项, Any], None]]" = None
    _保存后执行: "None|Callable[[基类_属性项],Any]" = None
    校验函数: "None|Callable[[基类_属性项,Any],bool]" = None
    自定义组件: "None|Callable[[函数库_UI生成.组件],QWidget]" = None
    上级:"None|基类_模型" = None
    默认值: "Any|None|list|str|int|float" = None
    值类型: "str" = None
    值解释: "str" = None
    属性项排序位置:"int" = 0 #用于对属性项顺序有要求的环境.

    @property
    def 值(self):
        raise NotImplementedError()

    def 设值(self, value):
        raise NotImplementedError()

    @staticmethod
    def 保存值的函数(self, value):
        self._保存值的函数(self, value)

    @staticmethod
    def 保存后执行(self):
        self._保存后执行(self)

    @staticmethod
    def 读取函数(self):
        return self._读取函数(self)

    @property
    def 组件显示值(self):
        if self.组件类型 in [枚举.组件类型.label, 枚举.组件类型.text, 枚举.组件类型.editable_label,枚举.组件类型.spin]:
            return self.值.__str__() if not self.组件传值方式 else self.组件传值方式(self)
        else:
            return self.值 if not self.组件传值方式 else self.组件传值方式(self)

    def 变量使用的解释(self):
        return f"mean:{self.展示名},type:{self.值类型},example:{self.值解释}"

    def __str__(self):
        return self.值.__str__()

    def __repr__(self):
        return self.值.__str__()

    def __eq__(self, other):
        raise NotImplementedError()

    # def __iadd__(self, other):
    #     self.设值(self.值+other)
    #     return self

