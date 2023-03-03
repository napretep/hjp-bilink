# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'funcs2.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2023/2/27 4:30'
"""
from typing import Callable
from .compatible_import import *

class 逻辑:
    @staticmethod
    def 缺省值(值,规则:"Callable",缺省值=None):
        try:
            结果 = 规则(值)
            if 结果:return 结果
            else:return 缺省值
        except:
            return 缺省值


class 通用:

    class 窗口:
        @staticmethod
        def 半开(组件:"QWidget",左右="左"):
            桌面尺寸 = QApplication.instance().screens()[0].availableGeometry()  # https://blog.csdn.net/dgxl22/article/details/121725550
            桌面宽度 = 桌面尺寸.width()
            桌面高度 = 桌面尺寸.height()
            组件.resize(int(桌面宽度 / 2), 桌面高度)
            组件.move(int(桌面尺寸.x()+桌面尺寸.width() / 2) if 左右=="右" else 桌面尺寸.x(), 桌面尺寸.y())