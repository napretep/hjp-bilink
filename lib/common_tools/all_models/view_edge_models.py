# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'view_edge_models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 6:01'
"""
from .basic_models import *


@dataclass
class 类型_视图边数据源:
    边集模型: "类型_视图边集模型" = None
    边: str = ""


@dataclass
class 类型_视图边属性项(基类_属性项):
    上级: "类型_视图边模型" = None

    @property
    def 值(self):
        if self.上级 and self.上级.数据源:
            if self.从上级读数据:
                return self.上级.数据源.边集模型.data[self.上级.数据源.边][self.字段名]
            elif self._读取函数:
                return self.读取函数(self)
            else:
                raise NotImplementedError()
        else:
            return self.默认值

    def 设值(self, value):
        if self.上级 and self.上级.数据源:
            边名 = self.上级.数据源.边
            if self.保存到上级:
                self.上级.数据源.边集模型.data[边名][self.字段名] = value
            elif self._保存值的函数:
                self.保存值的函数(self, value)
            else:
                raise NotImplementedError()
            if self._保存后执行:
                self.保存后执行(self)
            funcs.GviewOperation.save(self.上级.数据源.边集模型.上级)

    def __eq__(self, other):
        return self.值 == other


@dataclass
class 类型_视图边模型(基类_模型):
    数据源: "类型_视图边数据源" = field(default_factory=类型_视图边数据源)

    # def __post_init__(self):
    #     for key in self.__dict__.keys():
    #         if isinstance(self.__dict__[key], 类型_视图边属性项):
    #             项: 类型_视图边属性项 = self.__dict__[key]
    #             项.上级 = self

    # def 初始化(self, 视图数据: "类型_视图数据", 边: "str"):
    #     self.数据源 = 类型_视图边数据源(视图数据=视图数据, 边=边)
    #
    #     return self

    边名: 类型_视图边属性项 = field(default_factory=lambda: 类型_视图边属性项(
            字段名=枚举.边.名称,
            展示名=译.边名,
            保存到上级=1,
            从上级读数据=1,  # 从上级读数据的意思是从上级读数据到视图数据中,
            可展示=1,  # 需要对应的展示组件, 这里的展示是指展示在卡片详情中
            可展示中编辑=1,  # 需要对应的可展示中编辑组件, 与可展示联合判断
            用户可访=1,  # 用户可以用自定义的python语句访问到这个变量的值
            组件类型=枚举.组件类型.editable_label,  # 展示用的组件
    ))

@dataclass
class 类型_视图边集模型(基类_集模型):

    def __init__(self, 上级: "类型_视图数据", data: "dict"):
        self.data: "dict" = data
        self.上级: "类型_视图数据" = 上级

    def __getitem__(self, node_id):
        return 类型_视图边模型(数据源=类型_视图边数据源(self, node_id))

    # def keys(self):
    #     return self.成员.数据源.视图数据.edges.keys()
    #
    # def __init__(self, 视图数据):
    #     self.成员 = 类型_视图边模型()
    #     self.成员.数据源.视图数据=视图数据
    #
    # def __getitem__(self, item):
    #     self.成员.数据源.边 = item
    #     return self.成员
    #
    # 成员: 类型_视图边模型 = field(default_factory=类型_视图边模型)

