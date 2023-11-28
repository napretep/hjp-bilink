# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'hookers.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/24 20:45'
"""
import abc
from typing import Callable
from .compatible_import import *

类型_卡片编号 = str
类型_难度 = 类型_选的值 = int
类型_平台 = object

class 钩子之母(list):

    def __call__(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)

    @abc.abstractmethod
    def append(self, *args, **kwargs) -> None:
        super().append( *args, **kwargs)

    # def remove(self,func):
    #     self.remove(func)

class 当_ReviewButtonForCardPreviewer_完成复习(钩子之母):

    def append(self, fun: "Callable[[类型_卡片编号,类型_难度,类型_平台],None]") -> None:
        super().append(fun)


class 当全局配置_描述提取规则_模板选择器完成选择(钩子之母):
    def append(self,fun:"Callable[[类型_平台,类型_选的值],None]"):
        super().append(fun)

class 当模型的属性项组件_完成赋值(钩子之母):
    def append(self,fun:"Callable[[类型_平台,类型_选的值],None]"):
        super().append(fun)