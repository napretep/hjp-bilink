# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'imports.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 6:14'
"""
import abc
import datetime, time

from dataclasses import dataclass, field
from typing import Dict, Any, NewType

from ..compatible_import import *
from .. import language, baseClass, funcs, funcs2,configsModel,widgets,hookers


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