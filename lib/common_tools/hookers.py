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

Card_id = str
Ease = int


class 钩子之母(list):

    def __call__(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)

    @abc.abstractmethod
    def append(self, *args, **kwargs) -> None:
        super().append( *args, **kwargs)


class 当ReviewButtonForCardPreviewer完成复习(钩子之母):

    def append(self, fun: "Callable[[Card_id,Ease],None]") -> None:
        super().append(fun)
