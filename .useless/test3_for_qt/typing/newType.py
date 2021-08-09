# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'newType.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/3 19:52'
"""
from typing import NewType

CardId = NewType("CardId", int)

a = CardId(1)

if __name__ == "__main__":
    print(a)
