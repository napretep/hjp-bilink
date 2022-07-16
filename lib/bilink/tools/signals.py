
from ..imports import common_tools
if common_tools.compatible_import.Anki.isQt6:
    from PyQt6.QtCore import pyqtSignal
else:
    from PyQt5.QtCore import pyqtSignal


class CustomSignals:
    instance = None

    on_data_refresh_all = pyqtSignal()  # 刷新browser和全部的webview

    on_data_refresh_browser = pyqtSignal()

    on_data_refresh_webview = pyqtSignal()

    on_bilink_link_operation_end = pyqtSignal()

    @classmethod
    def start(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        # print(cls.instance)
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance
