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


@dataclass
class ModelGraphConfig:
    uuid:str
    name:str
