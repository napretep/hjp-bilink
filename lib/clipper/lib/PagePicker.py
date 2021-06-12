from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout
from .tools import objs, funcs, events
from . import PagePicker_


class PagePicker(QDialog):
    """接受目录和页码两个参数
    目录和页码可更改,加载书签,预览,
    可选择替换当前page或新增page, 如果父类不是pageItem,那自然不能替换
    """

    def __init__(self, pdfDirectory=None, pageNum=None, frompageitem=None, ratio=None, clipper=None, parent=None):
        super().__init__(parent=parent)
        self.pdfDir = pdfDirectory
        self.clipper = clipper
        self.frompageitem = frompageitem
        self.pageNum = pageNum
        self.toolsbar = PagePicker_.ToolsBar(
            pdfDirectory=pdfDirectory, pageNum=pageNum, ratio=ratio, frompageitem=frompageitem, clipper=clipper)

        self.leftpart = PagePicker_.LeftPart(parent=self)
        self.rightpart = PagePicker_.RightPart(parent=self)
        self.bookmark = PagePicker_.BookMark(parent=self)
        self.init_UI()
        self.init_events()
        self.resize(800, 500)
        self.show()

    def init_UI(self):
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.bag))
        self.setWindowTitle("PDF page picker")
        V_layout = QGridLayout(self)
        # V_layout.addWidget(self.leftpart)
        # V_layout.addWidget(self.rightpart)
        # V_layout.addWidget(self.toolsbar)
        V_layout.addWidget(self.leftpart, 0, 1)
        V_layout.addWidget(self.rightpart, 0, 2)
        V_layout.addWidget(self.toolsbar, 1, 1, 1, 2)
        self.setLayout(V_layout)
        pass

    def init_events(self):
        objs.CustomSignals.start().on_pagepicker_close.connect(self.on_pagepicker_close_handle)

    def on_pagepicker_close_handle(self, event: 'events.PagePickerCloseEvent'):
        self.close()
