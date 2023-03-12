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


# class 逻辑:
#     @staticmethod
#     def 缺省值(值, 规则: "Callable", 缺省值=None):
#         try:
#             结果 = 规则(值)
#             if 结果:
#                 return 结果
#             else:
#                 return 缺省值
#         except:
#             return 缺省值
#
#
# class 通用:
#     class 窗口:
#         @staticmethod
#         def 半开(组件: "QWidget", 左右="左",中心化=True,长比例=0.4,宽比例=0.8):
#             桌面尺寸 = QApplication.instance().screens()[
#                 0].availableGeometry()  # https://blog.csdn.net/dgxl22/article/details/121725550
#             桌面宽度 = 桌面尺寸.width()
#             桌面高度 = 桌面尺寸.height()
#             桌面横坐标 = 桌面尺寸.x()
#             桌面纵坐标 = 桌面尺寸.y()
#             桌面中心 = [int((桌面横坐标 + 桌面宽度) / 2), int((桌面纵坐标 + 桌面高度) / 2)]
#             组件长宽 = [int(桌面尺寸.width() * 0.4), int(桌面尺寸.height() * 0.8)]
#
#             组件坐标 = [桌面中心[0] if 左右 == "右" else int(桌面宽度 * 0.1), int(桌面高度 * 0.1)]
#
#             组件.resize(*组件长宽)
#             组件.move(*组件坐标)
