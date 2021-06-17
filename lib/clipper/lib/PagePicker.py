from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QSizePolicy, QApplication, QMainWindow
from .tools import objs, funcs, events
from . import PagePicker_
from .fitz import fitz


class PagePicker(QDialog):
    """接受目录和页码两个参数
    目录和页码可更改,加载书签,预览,
    可选择替换当前page或新增page, 如果父类不是pageItem,那自然不能替换
    """

    def __init__(self, pdfDirectory=None, pageNum=None, frompageitem=None, ratio=None, clipper=None, parent=None):
        super().__init__()
        self.setUpdatesEnabled(True)
        self.doc = None
        self.pdfDir = pdfDirectory
        self.clipper = clipper
        self.frompageitem = frompageitem
        self.pageNum = pageNum
        self.bookmark_opened = False
        self.browser = PagePicker_.Browser(parent=self)
        self.rightpart = PagePicker_.Previewer(parent=self)
        self.bookmark = PagePicker_.BookMark(parent=self)
        self.toolsbar = PagePicker_.ToolsBar(parent=self, clipper=clipper,
                                             pdfDirectory=pdfDirectory, pageNum=pageNum, ratio=ratio,
                                             frompageitem=frompageitem)
        self.current_preview_pagenum = None
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.init_UI()
        self.init_events()
        self.setFixedSize(1300, 900)
        self.show()
        # self.bookmark.resize(100,500)
        # self.bookmark.move(self.pos().x()-self.bookmark.maximumWidth(),self.pos().y())
        # self.bookmark.show()

    def init_UI(self):
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.bag))
        self.setWindowTitle("PDF page picker")
        V_layout_TB = QVBoxLayout()
        H_layout_LR = QHBoxLayout()

        H_layout = QHBoxLayout(self)
        H_layout_LR.addWidget(self.browser)
        H_layout_LR.addWidget(self.rightpart)
        H_layout_LR.setStretch(0, 1)
        H_layout_LR.setStretch(1, 1)

        V_layout_TB.addLayout(H_layout_LR)
        V_layout_TB.addWidget(self.toolsbar)
        V_layout_TB.setStretch(0, 1)
        V_layout_TB.setStretch(1, 0)
        H_layout.addWidget(self.bookmark)

        H_layout.addLayout(V_layout_TB)
        H_layout.setStretch(0, 1)
        H_layout.setStretch(1, 0)
        # V_layout.addWidget(self.bookmark,0,0,2,1)
        self.setLayout(H_layout)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        print(self.size())
        self.origin_size = self.size()
        self.setMaximumWidth(QApplication.desktop().width())
        pass

    def start(self, beginpage):
        e = events.PDFOpenEvent
        objs.CustomSignals.start().on_pagepicker_PDFopen.emit(e(sender=self, beginpage=beginpage,
                                                                path=self.pdfDir, eventType=e.PDFReadType))

    def init_events(self):
        objs.CustomSignals.start().on_pagepicker_close.connect(self.on_pagepicker_close_handle)
        objs.CustomSignals.start().on_pagepicker_PDFopen.connect(self.on_pagepicker_PDFopen_handle)
        objs.CustomSignals.start().on_pagepicker_bookmark_open.connect(self.on_pagepicker_openBookmark_handle)

    def on_pagepicker_openBookmark_handle(self, event: 'events.OpenBookmarkEvent'):
        # self.setMaximumWidth(QApplication.desktop().width())
        self.bookmark_switch()
        self.setMaximumWidth(QApplication.desktop().width())

    def bookmark_switch(self):
        if self.bookmark_opened != True:
            self.bookmark.show()
            self.setFixedSize(self.size().width() + self.bookmark.width(), self.size().height())
            self.move(self.x() - self.bookmark.width() - 8, self.y())
            self.bookmark_opened = True
        else:
            self.bookmark.hide()
            self.setFixedSize(self.size().width() - self.bookmark.width(), self.size().height())
            self.move(self.x() + self.bookmark.width() + 8, self.y())
            self.bookmark_opened = False

    def on_pagepicker_close_handle(self, event: 'events.PagePickerCloseEvent'):
        self.close()

    def on_pagepicker_PDFopen_handle(self, event: "events.PDFOpenEvent"):
        if event.Type == event.PDFReadType and event.path != "" and event.path is not None:
            self.doc = fitz.open(event.path)
            e = events.PDFParseEvent
            objs.CustomSignals.start().on_pagepicker_PDFparse.emit(
                e(sender=self, eventType=e.PDFInitParseType, path=event.path, doc=self.doc, pagenum=event.beginpage))

    def ratio_value_get(self):
        return self.toolsbar.ratio_value
