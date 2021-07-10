import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QSizePolicy, QApplication, QMainWindow
from .tools import objs, funcs, events, ALL
from . import PagePicker_
from .fitz import fitz
print, debugger = funcs.logger(logname=__name__)

class PagePicker(QDialog):
    """接受目录和页码两个参数
    目录和页码可更改,加载书签,预览,
    可选择替换当前page或新增page, 如果父类不是pageItem,那自然不能替换
    """

    def __init__(self, pdfpath=None, pageNum=None, frompageitem=None,
                 ratio=None, clipper=None, parent=None):

        super().__init__(parent)
        self.bookmark_openning = False
        self.setUpdatesEnabled(True)
        self.doc = None
        self.pdfDir = pdfpath
        self.clipper = clipper
        self.config_dict = objs.SrcAdmin.get_config("clipper")
        self.frompageitem = frompageitem
        self.pageNum = pageNum
        self.bookmark_opened = False
        # self.setFixedSize(1300, 600)
        self.setFixedWidth(1300)
        self.setFixedHeight(700)
        self.browser = PagePicker_.Browser(parent=self)
        self.previewer = PagePicker_.Previewer(parent=self)
        self.bookmark = PagePicker_.BookMark(parent=self)
        self.toolsbar = PagePicker_.ToolsBar(parent=self, clipper=clipper,
                                             pdfpath=pdfpath, pageNum=pageNum, ratio=ratio,
                                             frompageitem=frompageitem)
        self.current_preview_pagenum = None
        # self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.init_UI()
        self.event_dict = {
            ALL.signals.on_pagepicker_close: (self.on_pagepicker_close_handle),
            ALL.signals.on_pagepicker_PDFopen: (self.on_pagepicker_PDFopen_handle),
            ALL.signals.on_pagepicker_bookmark_open: (self.on_pagepicker_openBookmark_handle)

        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
        self.show()

    def init_UI(self):
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.bag))
        self.setWindowTitle("PDF page picker")

        V_layout_TB = QVBoxLayout()
        H_layout_LR = QHBoxLayout()

        H_layout = QHBoxLayout(self)
        H_layout_LR.addWidget(self.browser)
        H_layout_LR.addWidget(self.previewer)
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
        self.origin_size = self.size()
        self.setMaximumWidth(QApplication.desktop().width())
        self.setMaximumHeight(QApplication.desktop().height())
        pass

    def start(self, beginpage):
        e = events.PDFOpenEvent
        ALL.signals.on_pagepicker_PDFopen.emit(e(sender=self, beginpage=beginpage,
                                                 path=self.pdfDir, eventType=e.PDFReadType))

    def init_data(self, pagenum=None, PDFpath=None, frompageitem=None):
        self.pdfDir = PDFpath
        self.frompageitem = frompageitem
        self.pageNum = pagenum
        self.config_reload()

    def config_reload(self):
        self.config_dict = objs.SrcAdmin.get_config("clipper")
        self.bookmark.config_reload()
        self.browser.config_reload()
        self.previewer.config_reload()
        self.toolsbar.config_reload()

    def on_pagepicker_openBookmark_handle(self, event: 'events.OpenBookmarkEvent'):
        # self.setMaximumWidth(QApplication.desktop().width())
        self.bookmark_openning = True
        self.bookmark_switch()
        self.setMaximumWidth(QApplication.desktop().width())
        self.setMaximumHeight(QApplication.desktop().height())
        self.bookmark_openning = False

    def bookmark_switch(self):
        if self.bookmark_opened != True:
            self.bookmark.show()
            # self.setFixedSize(self.size().width() + self.bookmark.width(), self.size().height())
            self.setFixedWidth(self.size().width() + self.bookmark.width())
            self.move(self.x() - self.bookmark.width() - 8, self.y())

            self.bookmark_opened = True
        else:
            self.bookmark.hide()
            # self.setFixedSize(self.size().width() - self.bookmark.width(), self.size().height())
            self.setFixedWidth(self.size().width() - self.bookmark.width())
            self.move(self.x() + self.bookmark.width() + 8, self.y())
            self.bookmark_opened = False

    def on_pagepicker_close_handle(self, event: 'events.PagePickerCloseEvent'):
        print("get close order")

    def on_pagepicker_PDFopen_handle(self, event: "events.PDFOpenEvent"):
        if event.Type == event.PDFReadType and event.path is not None and os.path.exists(
                event.path) and event.beginpage is not None:
            self.doc: "fitz.Document" = fitz.open(event.path)
            e = events.PDFParseEvent
            ALL.signals.on_pagepicker_PDFparse.emit(
                e(sender=self, eventType=e.PDFInitParseType, path=event.path, doc=self.doc, pagenum=event.beginpage))
        else:
            self.browser.scene.clear()
            self.previewer.scene.clear()
            self.bookmark.model.clear()
            self.toolsbar.open.label.setText("")
            self.toolsbar.open.label.setToolTip("")
            QTimer.singleShot(100, self.toolsbar.on_open_button_clicked_handle)

    def ratio_value_get(self):
        """这些接口太深了,所以提出来一点"""
        return self.toolsbar.ratio_value

    def pageshift_value_get(self):
        return self.toolsbar.pageoffset_spinbox.value()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self.browser.curr_frame_idx is not None and self.browser.row_per_frame is not None and not self.bookmark_openning:
            e = events.PDFParseEvent
            curr_frame_first_page = self.browser.curr_frame_idx * self.browser.col_per_row * self.browser.row_per_frame
            ALL.signals.on_pagepicker_PDFparse.emit(
                e(sender=self, eventType=e.PDFInitParseType, doc=self.doc, pagenum=curr_frame_first_page)
            )
    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     self.all_event.unbind(self.__class__.__name__)
    # def browser_progressbar_value_set(self,value):
    #     self.browser.bottomBar.progressBar.setValue(value)

    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     # self.browser.all_event.unbind()
    #     self.all_event.unbind(self.__class__.__name__)
    #     super().closeEvent(a0)
