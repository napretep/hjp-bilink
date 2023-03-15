# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'view_create_dialog_model.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/3/10 0:53'
这个东西用来操控创建视图的UI
"""
from typing import *

import abc
import datetime, time

from ..compatible_import import *
from .. import language, baseClass, funcs, funcs2, configsModel, widgets, hookers, G
from .basic_models import *
from dataclasses import dataclass, field
from typing import Dict, Any, NewType


# class 类型_自定义组件:


@dataclass
class 类型_数据源_视图创建参数:
    视图名: str = ""
    上级: "G.safe.linkdata_grapher.Grapher|G.safe.linkdata_grapher.GViewAdmin" = None
    # 状态: "dict" = field(default_factory=lambda: {枚举.视图.名称: "", 枚举.视图.配置: None})
    配置: Id_name = field(default_factory=lambda: Id_name())

    def 设置视图名(self, value):
        self.视图名 = value

    def 设置配置(self, value):
        self.配置 = value


@dataclass
class 类型_属性项_视图创建参数(基类_属性项):
    上级: "类型_模型_视图创建参数" = None

    @property
    def 值(self):
        if self._读取函数:
            return self.读取函数(self)
        else:
            raise NotImplementedError()
        pass

    def 设值(self, value):
        if self._保存值的函数:
            self.保存值的函数(self, value)
        else:
            raise NotImplementedError()
        pass

    def __eq__(self, other):
        return self.值 == other
        pass


@dataclass
class 类型_模型_视图创建参数(基类_模型):
    数据源: "None|类型_数据源_视图创建参数" = None
    视图名: 类型_属性项_视图创建参数 = field(default_factory=lambda: 类型_属性项_视图创建参数(
        字段名=枚举.视图.名称,
        展示名=译.视图名,
        从上级读数据=1,
        保存到上级=1,
        可展示=1,
        可展示中编辑=1,
        用户可访=1,
        组件类型=枚举.组件类型.text,
        _读取函数=lambda 项: 项.上级.数据源.视图名,
        _保存值的函数=lambda 项, 值: 项.上级.数据源.设置视图名(值),
    ))
    视图配置选择: 类型_属性项_视图创建参数 = field(default_factory=lambda: 类型_属性项_视图创建参数(
        字段名=枚举.视图.配置,
        展示名=译.视图配置选择,
        说明=译.说明_新建视图_配置选择,
        从上级读数据=1,
        保存到上级=1,
        可展示=1,
        可展示中编辑=1,
        用户可访=1,
        组件类型=枚举.组件类型.customize,
        自定义组件=lambda 组件生成器: 函数库_UI生成.自定义().属性项组件.视图配置选择(组件生成器),
        _读取函数=lambda 项: 项.上级.数据源.配置,
        _保存值的函数=lambda 项, 值: 项.上级.数据源.设置配置(值),
    ))

    def 创建UI(self, 父类组件: "QWidget" = None, 布局: "QLayout" = None):
        组件 = super().创建UI(父类组件, 布局)
        布局: QFormLayout = 组件.layout()

        def 关闭():
            self.完成选择 = True
            组件.close()

        确认按钮 = G.safe.funcs.组件定制.组件组合(
            {砖.布局: QHBoxLayout(), 砖.子代: [{砖.组件: G.safe.funcs.组件定制.按钮_确认(触发函数=关闭)}]})
        布局.addRow("", 确认按钮)
        return 组件

    def __post_init__(self):
        super().__post_init__()
        self.完成选择 = False

    # def __init__(self):
    #     self.视图名: 类型_属性项_视图创建参数 = 类型_属性项_视图创建参数()

    pass
