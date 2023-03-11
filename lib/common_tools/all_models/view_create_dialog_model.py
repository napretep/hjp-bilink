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
from .. import language, baseClass, funcs, funcs2,configsModel,widgets,hookers,G
from .basic_models import *
from dataclasses import dataclass, field
from typing import Dict, Any, NewType

# class 类型_自定义组件:




@dataclass
class 类型_数据源_视图创建参数:
    上级: "G.safe.linkdata_grapher.Grapher|G.safe.linkdata_grapher.GViewAdmin" = None
    状态: "dict" = field(default_factory=lambda: {枚举.视图.名称: "", 枚举.视图.配置: None})


@dataclass
class 类型_属性项_视图创建参数(基类_属性项):
    上级: "类型_模型_视图创建参数" = None

    @property
    def 值(self):
        return self.上级.数据源.状态[self.字段名]
        pass

    def 设值(self, value):
        self.上级.数据源.状态[self.字段名] = value
        pass

    def __eq__(self, other):
        return self.值 == other
        pass


@dataclass
class 类型_模型_视图创建参数(基类_模型):
    数据源: "None|类型_数据源_视图创建参数" = None

    视图名:类型_属性项_视图创建参数=field(default_factory=lambda:类型_属性项_视图创建参数(
        字段名=枚举.视图.名称,
        展示名=译.视图名,
        从上级读数据=1,
        保存到上级=1,
        可展示=1,
        可展示中编辑=1,
        用户可访=1,
        组件类型=枚举.组件类型.text,
    ))
    视图配置选择:类型_属性项_视图创建参数=field(default_factory=lambda:类型_属性项_视图创建参数(
        字段名=枚举.视图.配置,
        展示名=译.视图配置选择,
        说明=译.说明_新建视图_配置选择,
        从上级读数据=1,
        保存到上级=1,
        可展示=1,
        可展示中编辑=1,
        用户可访=1,
        组件类型=枚举.组件类型.customize,
        自定义组件=lambda 组件生成器:函数库_UI生成.自定义().属性项组件,
    ))

    # def __init__(self):
    #     self.视图名: 类型_属性项_视图创建参数 = 类型_属性项_视图创建参数()

    pass
