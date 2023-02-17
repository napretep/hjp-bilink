# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/10/26 3:21'
TODO: 把所有的models移动到这里来
"""
from dataclasses import dataclass, field
from typing import Any

from .compatible_import import *
from . import funcs, baseClass, language, widgets

译 = language.Translate
枚举 = baseClass.枚举命名
砖 = 枚举.砖
类型_结点编号 = 类型_属性名 = str
类型_视图数据 = funcs.GViewData

class 函数库_UI展示:
    """UI有不同的类型,每种类型都要定制地写一个函数, 最后把它们组合进一个字典, 到时候根据组件类型作为键访问字典的值并调用即可获得组件"""

    @staticmethod
    def 提示按钮(消息):
        # QStyle().SP_MessageBoxQuestion
        btn = QPushButton()
        btn.setIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        btn.clicked.connect((lambda msg: lambda: showInfo(msg))(消息))
        return btn

    @staticmethod
    def 做成行(左: "QWidget|QLayout", 右: "QPushButton"):
        布局 = QHBoxLayout()
        if isinstance(左, QWidget):
            布局.addWidget(左, stretch=1)
        else:
            布局.addLayout(左, stretch=0)
        布局.addWidget(右)
        布局.setContentsMargins(0, 0, 0, 0)
        return 布局

    @staticmethod
    def checkbox(项: "类型_视图结点属性项"):
        self = 函数库_UI展示
        按钮 = self.提示按钮(项.说明)
        组件 = QCheckBox()
        组件.setChecked(项.组件传值方式(项.值) if 项.组件传值方式 else 项.值)
        item_set_value = lambda value: 项.设值(value)
        组件.clicked.connect(lambda: item_set_value(组件.isChecked()))
        return self.做成行(组件, 按钮)

    @staticmethod
    def label(项: "类型_视图结点属性项"):
        self = 函数库_UI展示
        按钮 = self.提示按钮(项.说明)
        组件 = QLabel(项.组件传值方式(项.值) if 项.组件传值方式 else 项.值.__str__())
        return self.做成行(组件, 按钮)
        pass

    @staticmethod
    def text(项: "类型_视图结点属性项"):
        self = 函数库_UI展示
        按钮 = self.提示按钮(项.说明)
        组件 = QTextEdit()
        组件.setText(项.值)
        临时文本储存 = [""]

        def when_need_update():
            组件.blockSignals(False)
            if 临时文本储存[0] != 组件.toPlainText():
                临时文本储存[0] = 组件.toPlainText()
                组件.blockSignals(True)
                return QTimer.singleShot(100, when_need_update)
            else:
                项.设值(组件.toPlainText())

        组件.textChanged.connect(when_need_update)
        return self.做成行(组件, 按钮)

    @staticmethod
    def customize(项: "类型_视图结点属性项"):
        self = 函数库_UI展示
        按钮 = self.提示按钮(项.说明)
        组件 = 项.自定义组件(项)
        return self.做成行(组件, 按钮)
        pass

    @staticmethod
    def slider(项: "类型_视图结点属性项"):
        self = 函数库_UI展示
        按钮 = self.提示按钮(项.说明)
        拖动条 = QSlider(Qt.Orientation.Horizontal)

        数值显示 = QLabel()
        if 项.有限制:
            拖动条.setRange(项.限制[0], 项.限制[1])
        组件 = funcs.组件定制.组件组合({砖.布局: QHBoxLayout(), 砖.子代: [{砖.组件: 数值显示}, {砖.组件: 拖动条}]})

        def item_set_value(value):
            项.设值(value)
            数值显示.setText(value.__str__())

        拖动条.valueChanged.connect(item_set_value)
        拖动条.setValue(项.值)
        return self.做成行(组件, 按钮)

    @staticmethod
    def 开始(项: "类型_视图结点属性项"):
        函数字典 = {
                枚举.组件类型.slider   : 函数库_UI展示.slider,
                枚举.组件类型.label    : 函数库_UI展示.label,
                枚举.组件类型.checkbox : 函数库_UI展示.checkbox,
                枚举.组件类型.text     : 函数库_UI展示.text,
                枚举.组件类型.customize: 函数库_UI展示.customize
        }
        return 函数字典[项.组件类型](项)

    pass


# 布局, 组件, 子代 = 0, 1, 2
@dataclass
class 基类_模型:
    元数据: "None|Any" = None

    def 初始化(self,*args):
        raise NotImplementedError()

    def 创建结点UI(self):
        对话框 = QDialog()
        表单布局 = QFormLayout()

        for 属性名 in self.__dict__.keys():
            if isinstance(self.__dict__[属性名], 基类_属性项):
                项: 类型_视图结点属性项 = self.__dict__[属性名]
                if 项.可展示:
                    组件 = 函数库_UI展示.开始(项)
                    表单布局.addRow(项.展示名, 组件)
        对话框.setLayout(表单布局)
        return 对话框

    def 获取可访变量(self):
        raise NotImplementedError()

    def 获取可访字面量(self):
        raise NotImplementedError()

    def __getitem__(self, item):
        return self.__dict__[item]


@dataclass
class 基类_属性项:
    字段名: "str"
    展示名: "str"
    # 值:"Any"
    说明: "str" = ""
    可展示: "int" = 0  # 需要对应的展示组件,
    可展示中编辑: "int" = 0  # 需要对应的可展示中编辑组件, 与可展示联合判断
    推算得到: "int" = 0  # 需要提供推算方法
    用户可访: "int" = 0
    推算函数: "None|Callable[[类型_视图数据,类型_结点编号],Any]" = None
    组件类型: "int" = None
    组件传值方式: "None|Callable[[值],Any]" = None
    保存值的函数: "None|Callable[[类型_视图数据,类型_结点编号,Any],Any]" = None
    有限制: "int" = 0
    限制: "list" = field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT])
    自定义组件: "None|Callable[[类型_视图结点属性项],QWidget]" = None
    上级 = None

    @property
    def 值(self):
        raise NotImplementedError()

    def 设值(self, value):
        raise NotImplementedError()

    def __str__(self):
        return self.值.__str__()

    def __eq__(self, other):
        return self.值 == other


@dataclass
class 类型_视图结点属性项(基类_属性项):
    """描述了每一项的特点"""
    可保存到视图数据: "int" = 0
    上级: "类型_视图结点模型" = None

    @property
    def 值(self):
        编号 = self.上级.元数据.结点编号
        数据 = self.上级.元数据.视图数据
        if self.可保存到视图数据:
            return 数据.nodes[编号][self.字段名]
        elif self.推算得到:
            return self.推算函数(数据, 编号)
        else:
            raise ValueError("未知的读取方式")

    def 设值(self, value):
        编号 = self.上级.元数据.结点编号
        数据 = self.上级.元数据.视图数据
        if self.可保存到视图数据:
            数据.nodes[编号][self.字段名] = value
            funcs.GviewOperation.save(数据)
        elif self.保存值的函数:
            self.保存值的函数(数据, 编号, value)
        else:
            raise ValueError("未知的保存方式,或者不该保存")


@dataclass
class 类型_视图本身属性项(基类_属性项):
    上级: "类型_视图数据" = None

    @property
    def 值(self):
        return self.上级.meta[self.字段名]

    def 设值(self, value):
        self.上级.meta[self.字段名] = value
        funcs.GviewOperation.save(self.上级)




@dataclass
class 类型_视图结点元数据:
    视图数据: "类型_视图数据"
    结点编号: "类型_结点编号"

@dataclass
class 类型_视图结点模型(基类_模型):
    """
    这是针对一个结点而言的,比gviewdata的层级更低
    提供:
        将非推算项保存到视图结点数据库的方法 -> 保存结点信息()
        将可展示与可展示中编辑项以UI形式呈现 -> 创建结点信息UI()
        将用户可访的变量提供给对应的接口. -> 可访变量, 可访字面量
    """

    # def __init__(self,视图数据:"funcs.GViewData",视图结点编号:"str"):
    #     self.元数据 = self.元数据类(视图数据,视图结点编号)
    完成初始化 = 0

    元数据: "None|类型_视图结点元数据" = None
    # 不可修改->数值/bool/日期/文本
    位置: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.位置,
            展示名=译.结点位置,
            可保存到视图数据=1,
            可展示=1,  # 需要对应的展示组件,
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            用户可访=0,  # 指的是用户自定义python语句是否可访问
            组件类型=枚举.组件类型.label,
    ))

    出度: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.出度,
            展示名=译.结点出度,
            说明=译.从结点出发的边的数量,
            可保存到视图数据=0,
            可展示=1,  # 需要对应的展示组件,
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=1,  # 需要提供推算方法
            用户可访=1,
            推算函数=lambda 视图数据, 结点数据: funcs.GviewOperation.获取结点出度(视图数据, 结点数据),
            组件类型=枚举.组件类型.label,
    ))
    入度: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.入度,
            展示名=译.结点入度,
            说明=译.从结点出发的边的数量,
            可保存到视图数据=0,
            可展示=1,  # 需要对应的展示组件,
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=1,  # 需要提供推算方法
            用户可访=1,
            推算函数=lambda 视图数据, 结点编号: funcs.GviewOperation.获取结点入度(视图数据, 结点编号),
            组件类型=枚举.组件类型.label,
    ))

    访问次数: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.访问次数,
            展示名=译.访问数,
            说明=译.说明_访问数,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.label,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))

    已到期: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.已到期,
            展示名=译.到期卡片,
            说明=译.说明_到期结点,
            可保存到视图数据=0,
            可展示=1,  # 需要对应的展示组件,
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=1,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            推算函数=lambda 视图数据, 结点编号: funcs.GviewOperation.判断结点已到期(视图数据, 结点编号),
            组件类型=枚举.组件类型.label,  # 展示用的组件
            # 组件传值方式=None,
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))

    上次复习: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.上次复习,
            展示名=译.上次复习,
            说明=译.说明_上次复习,
            可保存到视图数据=0,
            可展示=1,  # 需要对应的展示组件,
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=1,  # 需要提供推算方法
            用户可访=1,
            推算函数=lambda 视图数据, 结点编号: funcs.GviewOperation.结点上次复习时间(视图数据, 结点编号),
            组件类型=枚举.组件类型.label,  # 展示用的组件
            组件传值方式=lambda 值: 值.__str__(),
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))
    上次编辑: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.上次编辑,
            展示名=译.上次编辑时间,
            说明=译.说明_上次编辑,
            可保存到视图数据=1,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.label,  # 展示用的组件
            组件传值方式=lambda 值: funcs.Utils.时间戳转日期(值).__str__(),
            # 保存值的函数=None,
            有限制=0,
            限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))
    上次访问: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.上次访问,
            展示名=译.上次访问,
            说明=译.说明_上次访问,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.label,  # 展示用的组件
            组件传值方式=lambda 值: funcs.Utils.时间戳转日期(值).__str__(),
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))
    创建时间: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.创建时间,
            展示名=译.创建时间,
            说明=译.说明_创建时间,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.label,  # 展示用的组件
            组件传值方式=lambda 值: funcs.Utils.时间戳转日期(值).__str__(),
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))
    数据类型: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.数据类型,
            展示名=译.结点数据类型,
            说明=译.说明_结点数据类型,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            推算函数=None,
            组件类型=枚举.组件类型.label,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))
    # 可修改: 数值/bool/文本
    优先级: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.优先级,
            展示名=译.结点优先级,
            说明=译.说明_结点优先级,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.slider,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            有限制=1,
            限制=[-100, 100],
            # 自定义组件=lambda 项:widgets.自定义组件.视图结点属性.优先级(项),
    ))

    描述: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.描述,
            展示名=译.结点描述,
            说明=译.说明_结点描述,
            可保存到视图数据=0,
            可展示=1,  # 需要对应的展示组件,
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=1,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            推算函数=lambda 视图数据, 结点编号: funcs.GviewOperation.获取视图结点描述(视图数据, 结点编号),
            组件类型=枚举.组件类型.text,  # 展示用的组件
            保存值的函数=lambda 视图数据, 结点编号, 设定内容: funcs.GviewOperation.设定视图结点描述(视图数据, 结点编号, 设定内容)
            # 组件传值方式=None,
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))

    角色: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.角色,
            展示名=译.结点角色,
            说明=译.说明_结点角色,
            可保存到视图数据=1,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.customize,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None,
            #    有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            自定义组件=lambda 项: widgets.自定义组件.视图结点属性.角色多选(项),
    ))

    主要结点: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.主要结点,
            展示名=译.主要结点,
            说明=译.说明_主要结点,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.checkbox,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))

    需要复习: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.需要复习,
            展示名=译.需要复习,
            说明=译.说明_需要复习,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.checkbox,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))

    必须复习: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.必须复习,
            展示名=译.必须复习,
            说明=译.说明_必须复习,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.checkbox,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))

    漫游起点: 类型_视图结点属性项 = field(default_factory=lambda: 类型_视图结点属性项(
            字段名=枚举.结点.漫游起点,
            展示名=译.漫游起点,
            说明=译.说明_漫游起点,
            可保存到视图数据=1,  # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            推算得到=0,  # 需要提供推算方法
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            # 推算函数=None,
            组件类型=枚举.组件类型.checkbox,  # 展示用的组件
            # 组件传值方式=None,
            # 保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
            # 有限制=0,
            # 限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
            # 自定义组件=None,
    ))

    # 样板:视图结点属性项 = field(default_factory=lambda :视图结点属性项(
    #     字段名 = 枚举.结点.位置,
    #     展示名 = 译.结点位置,
    #     说明=译,
    #     可保存到视图数据=0, # 可保存到视图数据的意思是可保存到视图数据到视图数据中,
    #     可展示=0,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
    #     可展示中编辑=0,  # 需要对应的可展示中编辑组件, 与可展示联合判断
    #     推算得到=0,  # 需要提供推算方法
    #     用户可访=0, # 用户可以用自定义的python语句访问到这个变量的值
    #     推算函数=None,
    #     组件类型=枚举.组件类型, #展示用的组件
    #     组件传值方式=None,
    #     保存值的函数=None, # 当不能直接保存到视图中时, 采用这个函数保存
    #     有限制=0,
    #     限制=field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT]),
    #     自定义组件=None,
    # ))
    def 初始化(self, 视图数据, 结点编号):
        self.元数据 = 类型_视图结点元数据(视图数据, 结点编号)
        self.完成初始化 = 1
        for key in self.__dict__.keys():
            if isinstance(self.__dict__[key], 类型_视图结点属性项):
                项: 类型_视图结点属性项 = self.__dict__[key]
                项.上级 = self
        return self

    # def 保存结点信息(self):
    #     raise NotImplementedError()

    # def 属性(self,key)->类型_视图结点属性项:
    #     """返回键值对,键是结点的属性名, 值是属性项"""
    #     return self.__dict__[key]


@dataclass
class 类型_视图本身模型(基类_模型):
    元数据: "类型_视图数据" = None

    def 初始化(self, 上级):
        self.元数据 = 上级



    pass
