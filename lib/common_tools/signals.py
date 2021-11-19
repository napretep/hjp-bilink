# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'signals.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/30 9:15'
"""
from PyQt5.QtCore import pyqtSignal, QObject


class CustomSignals(QObject):
    instance = None
    testsignal = pyqtSignal(object)

    on_data_refresh_all = pyqtSignal()  # 刷新browser和全部的webview

    on_data_refresh_browser = pyqtSignal()

    on_data_refresh_webview = pyqtSignal()

    on_bilink_link_operation_end = pyqtSignal()

    on_clipper_closed = pyqtSignal()

    on_progress_break = pyqtSignal()

    on_card_answerd = pyqtSignal(object)

    on_card_changed = pyqtSignal(object)

    on_auto_review_search_string_changed = pyqtSignal()

    @classmethod
    def start(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        # print(cls.instance)
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance
