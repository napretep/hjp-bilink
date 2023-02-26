# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'funcs2.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 4:30'
"""
from typing import Callable


class 逻辑:
    @staticmethod
    def 缺省值(值,规则:"Callable",缺省值=None):
        try:
            结果 = 规则(值)
            if 结果:return 结果
            else:return 缺省值
        except:
            return 缺省值