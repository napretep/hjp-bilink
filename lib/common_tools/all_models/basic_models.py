# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'basic_models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 5:10'
当你要继承这些东西时，你需要继承以下的内容：
1 数据源
2 属性项
3 模型
"""
# from .basic_import import *
from typing import *

import abc
import datetime, time

from dataclasses import dataclass, field
from typing import Dict, Any, NewType

from ..compatible_import import *
from .. import language, baseClass, funcs, funcs2,configsModel,widgets,hookers,G


class 安全导入:
    @property
    def widgets(self):
        from .. import widgets
        return widgets

    @property
    def funcs(self):
        from .. import funcs
        return funcs

safe = 安全导入()

译 = language.Translate
枚举 = baseClass.枚举命名
砖 = 枚举.砖
类型_结点编号 = 类型_属性名 = str
类型_视图数据=configsModel.GViewData
类型_数据源_提取规则 = NewType("类型_数据源_提取规则",dict)


class 函数库_UI生成:
    """UI有不同的类型,每种类型都要定制地写一个函数, 最后把它们组合进一个字典, 到时候根据组件类型作为键访问字典的值并调用即可获得组件"""

    @staticmethod
    def 提示按钮(说明: "str"):
        return funcs.组件定制.按钮_提示(触发函数=lambda: funcs.Utils.大文本提示框(说明))

    @staticmethod
    def 做成行(左: "QWidget|QLayout", 右: "QPushButton|QWidget|QLayout"):
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

    @staticmethod
    def 自定义():
        from .. import widgets
        return widgets

    class 组件(QWidget):
        def __init__(self, 项: "基类_属性项"):
            super().__init__()
            self.给UI赋值:"None|Callable[[Any],None]" =None
            self.提示按钮 = 函数库_UI生成.提示按钮(项.说明)
            self.数据源: "基类_属性项" = 项
            self.核心组件: "Optional[QWidget]" = None
            self.当完成赋值 = hookers.当模型的属性项组件_完成赋值()
            self.setLayout(函数库_UI生成.做成行(*self.组件生成()))

        def 组件生成(self):
            左, 右 = QWidget(), self.提示按钮
            if self.数据源.组件类型 == 枚举.组件类型.slider:
                拖动条 = QSlider(Qt.Orientation.Horizontal)
                self.核心组件 = 拖动条
                数值显示 = QLabel(self.数据源.组件显示值)
                拖动条.setValue(self.数据源.值)
                if self.数据源.有限制:
                    拖动条.setRange(self.数据源.限制[0], self.数据源.限制[1])
                组件 = funcs.组件定制.组件组合(
                    {砖.布局: QHBoxLayout(), 砖.子代: [{砖.组件: 数值显示}, {砖.组件: 拖动条}]})

                def item_set_value(value):
                    self.数据源.设值(value)
                    数值显示.setText(self.数据源.组件显示值)
                    self.当完成赋值(组件, value)

                拖动条.valueChanged.connect(item_set_value)
                self.给UI赋值 = lambda value: 拖动条.setValue(value)
            elif self.数据源.组件类型 == 枚举.组件类型.label:
                组件 = funcs.组件定制.文本框(self.数据源.组件显示值, True)
                self.核心组件 = 组件
                self.给UI赋值 = lambda value: 组件.setText(value.__str__())
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.checkbox:
                组件 = QCheckBox()
                self.核心组件 = 组件
                组件.setChecked(self.数据源.值)

                def item_set_value(value):
                    self.数据源.设值(value)
                    self.当完成赋值(组件, value)

                组件.clicked.connect(lambda: item_set_value(组件.isChecked()))
                self.给UI赋值 = lambda value: 组件.setChecked(value)
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.text:
                组件 = QTextEdit()
                组件.setText(self.数据源.组件显示值)
                临时文本储存 = [""]
                self.核心组件 = 组件

                def when_need_update():
                    组件.blockSignals(False)
                    if 临时文本储存[0] != 组件.toPlainText():
                        临时文本储存[0] = 组件.toPlainText()
                        组件.blockSignals(True)
                        return QTimer.singleShot(100, when_need_update)
                    else:
                        self.数据源.设值(组件.toPlainText())
                        self.当完成赋值(组件, 组件.toPlainText())

                组件.textChanged.connect(when_need_update)
                self.给UI赋值 = lambda value: 组件.setText(value)
                pass
            elif self.数据源.组件类型 == 枚举.组件类型.customize:
                组件 = self.数据源.自定义组件(self)
                # 组件.当完成赋值+=self.当完成赋值
                组件.当完成赋值.append(lambda x, y: self.当完成赋值(x, y))
                self.核心组件 = 组件
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
                    self.当完成赋值(组件, value)

                self.给UI赋值 = lambda value: setValue(value)
                self.核心组件 = 组件
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
                        if self.数据源.有校验 and not self.数据源.校验函数(self.数据源, 结果[0]):
                            tooltip("illegal value")
                    pass

                def setValue(value):
                    组件.setText(value)
                    self.数据源.设值(value)
                    self.当完成赋值(组件, value)

                self.核心组件 = 组件
                按钮2.clicked.connect(on_edit)
                self.给UI赋值 = lambda value: setValue(value)
            elif self.数据源.组件类型 == 枚举.组件类型.spin:
                组件 = QSpinBox()
                self.核心组件 = 组件
                组件.setValue(self.数据源.值)

                def setValue(value):
                    self.数据源.设值(value)
                    self.当完成赋值(组件, value)

                组件.valueChanged.connect(lambda x: setValue(int(组件.value())))
                self.给UI赋值 = lambda value: setValue(value)
            else:
                raise NotImplementedError()
            左 = 组件
            return 左, 右

        # def 给UI赋值(self,value,赋值函数):
        #     赋值函数(value)
        #     self.当完成赋值(self,value)



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
    数据源: "Any" = None
    属性字典: "dict[str,基类_属性项]" = field(init=False)

    def 初始化(self, *args):
        # raise NotImplementedError()
        pass

    def 创建UI字典(self):
        字典 = {}
        for 属性名 in self.__dict__.keys():
            if isinstance(self.__dict__[属性名], 基类_属性项):
                项: 基类_属性项 = self.__dict__[属性名]
                if 项.可展示:
                    组件 = 函数库_UI生成.组件(项)
                    字典[项.字段名] = 组件
        return 字典

    def 创建UI(self, 父类组件: "QWidget" = None, 布局: "QLayout" = None):
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

    def 获取属性项有序列表_属性名(self):
        return sorted(self.属性字典.keys(), key=lambda x: self.属性字典[x].属性项排序位置)

    def 获取属性项有序列表_属性字典(self):
        return sorted(self.属性字典.values(), key=lambda x: self.属性字典[x.字段名].属性项排序位置)

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
        字典 = {}
        [字典.__setitem__(属性名, 属性.值) for 属性名, 属性 in self.属性字典.items()]

        return 字典.__str__()

    def __repr__(self):
        return self.__str__()


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
    组件传值方式: "Optional[Callable[[基类_属性项],Any]]" = None
    _读取函数: "Optional[Callable[[基类_属性项],Any]]" = None
    _保存值的函数: "Optional[Callable[[基类_属性项, Any], None]]" = None
    _保存后执行: "Optional[Callable[[基类_属性项],Any]]" = None
    校验函数: "Optional[Callable[[基类_属性项,Any],bool]]" = None
    自定义组件: "Optional[Callable[[函数库_UI生成.组件],safe.widgets.自定义.基类_项组件基础]]" = None
    上级: "Optional[基类_模型]" = None
    默认值: "Any|list|str|int|float" = None
    值类型: "str" = None
    值解释: "str" = None
    属性项排序位置: "int" = 0  # 用于对属性项顺序有要求的环境.
    可批量编辑: "int" = 0
    在视图中显示: "int" = 1
    版本:int = 1
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
        return self.值.__str__() if not self.组件传值方式 else self.组件传值方式(self)

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
