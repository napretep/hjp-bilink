# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/10/26 3:21'
TODO: 把所有的models移动到这里来
"""
from dataclasses import dataclass,field
from typing import Any

from compatible_import import *
from . import funcs

class 组件类型:
    pass

@dataclass
class 视图结点模型的项:

    名:"str"
    值:"Any"
    说明:"str"=""
    可保存:"bool"=False
    可展示:"bool"=False # 需要对应的展示组件,
    可编辑:"bool"=False # 需要对应的可编辑组件, 与可展示联合判断
    是推算:"bool"=False
    组件类型:"int"=None
    有限制:"bool"=False
    限制:"list" = field(default_factory=lambda: [0, funcs.G.src_admin.MAXINT])
    自定义组件:"QWidget"=None