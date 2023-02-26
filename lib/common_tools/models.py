# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'models.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2022/10/26 3:21'
"""
import abc
import datetime
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Dict, NewType

from .compatible_import import *
from . import funcs, baseClass, language, widgets,funcs2
from .all_models import *

译 = language.Translate
枚举 = baseClass.枚举命名
砖 = 枚举.砖
类型_结点编号 = 类型_属性名 = str
类型_视图数据 = funcs.GViewData

