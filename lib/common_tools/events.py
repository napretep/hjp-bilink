# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'events.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:15'
"""
from aqt.utils import tooltip

from . import funcs

def on_profile_will_close_handle():
    funcs.LinkPoolOperation.clear()
    funcs.LOG.file_clear()
    
