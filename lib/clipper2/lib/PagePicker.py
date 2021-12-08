import re
import time
from math import ceil
from typing import Union, Any

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF, QRect, QTimer, QThread
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QPixmap, QPainter, QColor, QBrush
from PyQt5.QtWidgets import QDialog, QGraphicsView, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication, \
    QGridLayout, QToolButton, QLineEdit, QDoubleSpinBox, QSpinBox, QGraphicsScene, QGraphicsPixmapItem, QProgressBar, \
    QTreeView, QFileDialog, QGraphicsTextItem, QGraphicsItem, QGraphicsSceneMouseEvent, QGraphicsRectItem, \
    QStyleOptionGraphicsItem
import os
from .fitz import fitz
from .Clipper import Clipper
from .Model import Entity
from .tools import objs, events, funcs, ALL, Worker
from dataclasses import dataclass, asdict


class Color:
    yellow = "yellow"
    red = "#DC143C"
    white = "white"


class PagePicker(QDialog):
    def __init__(self, parent=None, superior: "Clipper" = None, root: "Clipper" = None, entity: "Entity" = None):
        super().__init__(parent)
        self.superior = superior
        self.root = root
        self.E = entity if root is None else root.E
        self.E.pagepicker.browser.worker = FrameLoadWorker(self.E)
        self.E.pagepicker.browser.worker.start()
        self.signals = self.E.signals
        self.setUpdatesEnabled(True)
        self.setFixedWidth(1000)
        self.setFixedHeight(700)
        self.browser = self.Browser(parent=self, superior=self, root=self.root)
        self.previewer = self.Previewer(parent=self, superior=self, root=self.root)
        self.bookmark = self.BookMark(parent=self, superior=self, root=self.root)
        self.toolsbar = self.ToolsBar(parent=self, superior=self, root=self.root)
        self.init_UI()
        self.allevent = objs.AllEventAdmin([
            [self.E.signals.on_pagepicker_PDFopen, self.on_pagepicker_PDFopen_handle],
            [self.E.signals.on_pagepicker_PDFparse, self.on_pagepicker_PDFparse_handle],
            [self.toolsbar.widget_button_bookmark.clicked, self.on_widget_button_bookmark_clicked_handle],
            [self.toolsbar.widget_button_open.clicked, self.on_widget_button_open_clicked_handle],
            [self.toolsbar.widget_DBspinbox_ratio.valueChanged, self.on_widget_DBspinbox_ratio_valueChanged_handle],
            [self.toolsbar.widget_spinbox_pagejump.valueChanged, self.on_widget_spinbox_pagejump_valueChanged_handle],
            [self.toolsbar.widget_spinbox_pageoffset.valueChanged, self.on_widget_spinbox_pageoffset_valueChanged_handle],
            [self.toolsbar.widget_lineEdit_pagenum.textChanged, self.on_widget_lineEdit_pagenum_textChanged_handle],
            [self.toolsbar.widget_button_newPage.clicked, self.on_widget_button_newPage_clicked_handle],
            [self.E.signals.on_pagepicker_browser_loadframe, self.on_pagepicker_browser_loadframe_handle],
            [self.E.pagepicker.browser.worker.on_1_page_load, self.browser.on_1_page_load_handle],
            [self.E.signals.on_pagepicker_browser_select, self.on_pagepicker_browser_select_handle],
            [self.E.signals.on_pagepicker_preivewer_read_page, self.on_pagepicker_preivewer_read_page_handle],
            [self.bookmark.view.clicked, self.on_bookmark_view_clicked],
            [self.browser.view.verticalScrollBar().valueChanged, self.on_browser_view_verticalScrollBar_valueChanged_handle],
        ]).bind()

    def on_widget_button_newPage_clicked_handle(self):
        ratio = self.toolsbar.widget_DBspinbox_ratio.value()
        pdf_path = self.root.E.pagepicker.curr_pdf_path
        li = self.browser.scene.selected_item_pagenum()
        if len(li) == 0:
            li = list(self.E.pagepicker.toolsbar.collect_page_set)
        datali = [objs.PageInfo(pdf_path=pdf_path, ratio=ratio, pagenum=pagenum) for pagenum in li]
        e = events.PageItemAddToSceneEvent
        self.signals.on_pageItem_addToScene.emit(e(type=e.defaultType.addMultiPage, datali=datali))
        self.close()
        # print(datali)

    def on_widget_lineEdit_pagenum_textChanged_handle(self, string):
        t = self.E.pagepicker.toolsbar
        t.collect_page_isvalide = self.toolsbar.collect_page_validity(string)
        if t.collect_page_isvalide:
            self.toolsbar.collect_page_highlight(Color.white)
            self.toolsbar.collect_page_set_convert(string)
        else:
            self.toolsbar.collect_page_highlight(Color.red)
        self.toolsbar.newpage_validitycheck()
        # print(t.collect_page_set)

    def on_widget_DBspinbox_ratio_valueChanged_handle(self):
        if self.previewer.item is not None:
            ratio = self.toolsbar.widget_DBspinbox_ratio.value()
            self.previewer.item.zoom(ratio, center=self.previewer.item.viewcenter)

    def on_browser_view_verticalScrollBar_valueChanged_handle(self):
        self.browser.view.frame_idx_change_check(self.browser.view.noscroll)
        pass

    def on_bookmark_view_clicked(self, index):
        item: "PagePicker.BookMark.Item" = self.bookmark.model.itemFromIndex(index)
        e = events.PagePickerPreviewerReadPageEvent
        self.E.signals.on_pagepicker_preivewer_read_page.emit(
            e(sender=self, type=e.defaultType.fromBookmark, pagenum=item.pagenum))

    def on_pagepicker_preivewer_read_page_handle(self, event: "events.PagePickerPreviewerReadPageEvent"):
        print(event.pagenum)

        if event.type == event.defaultType.fromBrowser:  # 只加载,不跳转,不高亮
            self.toolsbar.widget_spinbox_pagejump.blockSignals(True)
            self.toolsbar.setBookPageFromPDFpage(event.pagenum)
            self.previewer.page_load()
            self.toolsbar.widget_spinbox_pagejump.blockSignals(False)
            pass
        elif event.type in [event.defaultType.fromSpinbox, event.defaultType.fromBookmark]:
            self.toolsbar.setBookPageFromPDFpage(event.pagenum)
            self.previewer.page_load()
            QTimer.singleShot(100, lambda: self.browser.high_light(event.pagenum))  # 有时候需要的变量还未加载完成,所以延迟执行
            QTimer.singleShot(100, lambda: self.browser.focus_on(self.browser.frameidx_pagenum_at(event.pagenum)))
            e = events.PagePickerBrowserLoadFrameEvent
            QTimer.singleShot(100, lambda: self.E.signals.on_pagepicker_browser_loadframe.emit(
                e(type=e.defaultType.continueLoad, pagenum=event.pagenum)))

    def on_pagepicker_browser_select_handle(self, event: "events.PagePickerBrowserSelectEvent"):
        """处理单选,多选,分批选,选框等问题"""
        if event.type == event.defaultType.singleSelect:
            self.E.pagepicker.browser.selectedItemList = [event.sender]
        elif event.type == event.defaultType.multiSelect:
            self.E.pagepicker.browser.selectedItemList.append(event.sender)
        elif event.type == event.defaultType.multiCancel:
            self.E.pagepicker.browser.selectedItemList = []

    def on_pagepicker_browser_loadframe_handle(self, event: "events.PagePickerBrowserLoadFrameEvent"):
        if event.type == event.defaultType.initParse:
            self.browser.init_parse_load_frame(event.pagenum)
        elif event.type == event.defaultType.continueLoad:
            self.browser.continue_load_frame(pagenum=event.pagenum, frame_idx=event.frame_idx)
        elif event.type == event.defaultType.Jump:
            if event.frame_idx is None:
                event.frame_idx = self.frameidx_pagenum_at(event.pagenum)
            self.frame_load_worker.on_frame_load_begin.emit(event.frame_idx)
            self.focus_on(event.frame_idx)
            self.high_light(event.pagenum)
            pass
        elif event.type == event.defaultType.Scroll:
            # self.page_load_handle(event.doc, frame_idx=event.frame_idx)
            # print(f"scroll type,frame_idx={event.frame_idx}")
            self.frame_load_worker.on_frame_load_begin.emit(event.frame_idx)
            pass
        # self.E.pagepicker.browser.worker=Worker.FrameLoadWorker()

    def on_widget_spinbox_pageoffset_valueChanged_handle(self):
        print("here")
        self.toolsbar.setBookPageFromPDFpage(self.E.pagepicker.curr_pagenum)
        # self.toolsbar.widget_spinbox_pagejump.valueChanged.emit(self.toolsbar.widget_spinbox_pagejump.value())

    def on_widget_spinbox_pagejump_valueChanged_handle(self):
        offset = self.toolsbar.widget_spinbox_pageoffset.value()
        self.E.pagepicker.curr_pagenum = self.toolsbar.widget_spinbox_pagejump.value() - 1 + offset
        e = events.PagePickerPreviewerReadPageEvent
        self.E.signals.on_pagepicker_preivewer_read_page.emit(
            e(sender=self, type=e.defaultType.fromSpinbox, pagenum=self.E.pagepicker.curr_pagenum))

    def on_widget_button_bookmark_clicked_handle(self):
        if self.bookmark.isVisible():
            self.bookmark.hide()
        else:
            self.bookmark.show()

    def on_widget_button_open_clicked_handle(self):
        path = self.toolsbar.unit_li[self.toolsbar.widget_button_open].label.toolTip()
        if os.path.exists(path):
            path = os.path.dirname(path)
        elif self.E.pagepicker.curr_pdf_path is not None and os.path.exists(self.E.pagepicker.curr_pdf_path):
            path = os.path.dirname(self.E.pagepicker.curr_pdf_path)
        else:
            path = self.E.config.pagepicker.bottombar_default_path
        e = events.PagePickerPDFOpenEvent
        self.E.signals.on_pagepicker_PDFopen.emit(e())

    def on_pagepicker_PDFopen_handle(self, event: "events.PagePickerPDFOpenEvent"):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self, "选取文件", event.pdf_path, "(*.pdf)")
        if fileName_choose:  # 如果存在则进一步解析PDF的目录,缩略图,以及元信息显示
            e = events.PagePickerPDFParseEvent
            if os.path.exists(self.E.pagepicker.curr_pdf_path) and os.path.isfile(self.E.pagepicker.curr_pdf_path):
                self.save_pdf_info()
            self.E.pagepicker.curr_pdf_path = fileName_choose.replace("\\", "/")
            pagenum = self.E.config.pagepicker.bottombar_page_num if event.pagenum is None else event.pagenum
            self.E.signals.on_pagepicker_PDFparse.emit(
                e(type=e.defaultType.PDFRead, path=fileName_choose, pagenum=pagenum))
            pass
        # else:  # 如果不存在则保持空白
        # self.E.pagepicker.curr_pdf_path = None
        # self.toolsbar.unit_li[self.toolsbar.widget_button_open].setDescText("")
        # self.toolsbar.unit_li[self.toolsbar.widget_button_open].setDescTooltip("")

    def on_pagepicker_PDFparse_handle(self, event: "events.PagePickerPDFParseEvent"):
        assert (event.pagenum is not None and event.path is not None)
        pdfname = funcs.str_shorten(os.path.basename(event.path))
        self.toolsbar.unit_li[self.toolsbar.widget_button_open].setDescText(pdfname)
        self.toolsbar.unit_li[self.toolsbar.widget_button_open].setDescTooltip(event.path)
        self.E.pagepicker.curr_doc = fitz.Document(event.path)
        self.E.pagepicker.curr_pdf_path = event.path
        self.E.pagepicker.curr_pagenum = event.pagenum

        self.bookmark.load_bookmark()
        self.toolsbar.widget_lineEdit_pagenum.setText(str(event.pagenum))
        pdfuuid = funcs.uuid_hash_make(event.path)
        DB = objs.SrcAdmin.DB.go(objs.SrcAdmin.DB.table_pdfinfo)
        if not DB.exists(DB.EQ(uuid=pdfuuid)):
            ratio = self.E.config.pagepicker.bottombar_page_ratio
            record = objs.PDFinfoRecord(uuid=pdfuuid, pdf_path=event.path, ratio=ratio, offset=0)
            DB.insert(**(asdict(record))).commit()
        result = objs.PDFinfoRecord(**DB.select(uuid=pdfuuid).return_all().zip_up()[0])
        QTimer.singleShot(100, lambda: self.toolsbar.widget_spinbox_pageoffset.setValue(result.offset))
        self.toolsbar.widget_DBspinbox_ratio.blockSignals(True)
        self.toolsbar.widget_DBspinbox_ratio.setValue(result.ratio)
        self.toolsbar.widget_DBspinbox_ratio.blockSignals(False)
        count = len(self.E.pagepicker.curr_doc) - 1
        self.toolsbar.widget_spinbox_pagejump.setRange(-count, count)
        self.toolsbar.setBookPageFromPDFpage(event.pagenum)
        self.previewer.page_load()
        e = events.PagePickerBrowserLoadFrameEvent
        self.root.E.signals.on_pagepicker_browser_loadframe.emit(e(type=e.defaultType.initParse, pagenum=event.pagenum))
        # self.on_widget_DBspinbox_ratio_valueChanged_handle()

    def show(self) -> None:
        QTimer.singleShot(100, self.if_no_pdf_path_open_filepicker)
        super().show()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.E.pagepicker.curr_pdf_path is not None \
                and os.path.exists(self.E.pagepicker.curr_pdf_path) \
                and os.path.isfile(self.E.pagepicker.curr_pdf_path):
            self.save_pdf_info()
        self.E.pagepicker.browser.worker.terminate()
        self.allevent.unbind()
        self.E.pagepicker = Entity.PagePicker()

    def reject(self) -> None:
        self.close()

    def if_no_pdf_path_open_filepicker(self):
        if self.E.pagepicker.curr_pdf_path:
            # 如果有当前路径的pdf,则加载之.
            pass
        elif self.E.pagepicker.frompageItem:
            e = events.PagePickerPDFParseEvent
            from .Clipper import Clipper
            pageitem: "Clipper.PageItem" = self.E.pagepicker.frompageItem
            pdf_path = pageitem.pageinfo.pdf_path
            pagenum = pageitem.pageinfo.pagenum
            self.E.signals.on_pagepicker_PDFparse.emit(
                e(type=e.defaultType.PDFInitParse, path=pdf_path, pagenum=pagenum))
        else:
            if os.path.exists(self.E.config.pagepicker.bottombar_default_path):
                self.E.pagepicker.curr_pdf_path = self.E.config.pagepicker.bottombar_default_path.replace("\\", "/")
            else:
                self.E.pagepicker.curr_pdf_path = objs.SrcAdmin.get.user_files_dir().replace("\\", "/")

            e = events.PagePickerPDFOpenEvent
            self.E.signals.on_pagepicker_PDFopen.emit(e(pdf_path=self.E.pagepicker.curr_pdf_path))

    def save_pdf_info(self):

        ratio = self.toolsbar.widget_DBspinbox_ratio.value()
        offset = self.toolsbar.widget_spinbox_pageoffset.value()
        uuid = funcs.uuid_hash_make(self.root.E.pagepicker.curr_pdf_path)
        print(f"当前pdfpath={self.E.pagepicker.curr_pdf_path}")
        DB = objs.SrcAdmin.DB
        DB.go(DB.table_pdfinfo)
        DB.replace(uuid=uuid, ratio=ratio, offset=offset, pdf_path=self.E.pagepicker.curr_pdf_path).commit(print)
        # if DB.exists(DB.EQ(uuid=uuid)):
        #     DB.update(values=DB.VALUEEQ(ratio=ratio, offset=offset), where=DB.EQ(uuid=uuid)).commit(print)
        # else:
        #     DB.insert(uuid=uuid, ratio=ratio, offset=offset, pdf_path=self.E.pagepicker.curr_pdf_path).commit(print)

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
        self.setMaximumWidth(QApplication.desktop().width())
        self.setMaximumHeight(QApplication.desktop().height())
        pass

    class Browser(QWidget):
        def __init__(self, parent=None, superior: "PagePicker" = None, root: "Clipper" = None):
            super().__init__(parent)
            self.superior = superior
            self.root = root
            self.scene = self.Scene(parent=self, superior=self, root=self.root)
            self.view = self.View(parent=self, superior=self, root=self.root)
            self.bottomBar = self.BottomBar(parent=self, superior=self, root=self.root)

            self.init_UI()

        def on_1_page_load_handle(self, data: "Entity.OnePageLoadData"):
            """

            Args:
                item_dict: {"frame_idx":int,"frame_item_idx":int,"pagenum":int,"posx":,"posy":,"show":True/False}

            Returns:

            """
            b = self.root.E.pagepicker.browser
            pixmap = QPixmap(funcs.pixmap_page_load(self.root.E.pagepicker.curr_pdf_path, data.pagenum, browser=True))

            item = PagePicker.Browser.Item(pixmap=pixmap, pagenum=data.pagenum, unit_size=b.unit_size, superior=self,
                                           root=self.root)
            item.setPos(data.x, data.y)

            b.frame_list[data.frame_idx][data.frame_item_idx] = item
            self.scene.addItem(item)

            b.workerstate.bussy = False
            if b.frame_list[data.frame_idx].blocks_full():
                b.workerstate.do = False
            self.bottomBar.progressbar.setValue(ceil(data.percent * 100))
            if b.wait_for_page_select is not None and b.wait_for_page_select == data.pagenum:
                self.high_light(data.pagenum)
                b.wait_for_page_select = None

        def high_light(self, page_num):
            b = self.root.E.pagepicker.browser
            self.scene.clearSelection()
            at_frame_idx = int(page_num / (b.row_per_frame * b.col_per_row))
            at_item_idx = page_num % (b.row_per_frame * b.col_per_row)
            page_item = b.frame_list[at_frame_idx][at_item_idx]
            if page_item is not None:
                page_item.setSelected(True)
            else:
                self.root.E.PagePicker.browser.wait_for_page_select = page_num

            pass

        def init_UI(self):
            # self.setFixedSize(600, self.pagepicker.size().height()-100)
            self.setFixedWidth(600)
            V_layout = QVBoxLayout(self)
            V_layout.addWidget(self.view)
            V_layout.addWidget(self.bottomBar)
            V_layout.setStretch(0, 1)
            V_layout.setStretch(1, 0)
            V_layout.setSpacing(0)
            self.setLayout(V_layout)

        def init_parse_load_frame(self, pagenum):
            p = self.root.E.pagepicker
            b = self.root.E.pagepicker.browser
            c = self.root.E.config.pagepicker
            if b.col_per_row is None:
                b.col_per_row = c.browser_layout_col_per_row
            self.init_basedata(pagenum)
            self.init_framelist()
            self.init_scene_size()
            self.scene.clear()
            frame_idx = self.frameidx_pagenum_at(pagenum)
            b.worker.init_data(frame_list=b.frame_list, doc=p.curr_doc, unit_size=b.unit_size,
                               col_per_row=b.col_per_row, row_per_frame=b.row_per_frame)
            b.worker.on_frame_load_begin.emit(frame_idx)
            self.focus_on(frame_idx)

        def continue_load_frame(self, pagenum=None, frame_idx=None):
            p = self.root.E.pagepicker
            b = self.root.E.pagepicker.browser
            b.workerstate.do = False
            if frame_idx is None:
                frame_idx = self.frameidx_pagenum_at(pagenum)
            b.worker.init_data(frame_list=b.frame_list, doc=p.curr_doc, unit_size=b.unit_size,
                               col_per_row=b.col_per_row, row_per_frame=b.row_per_frame)
            b.worker.on_frame_load_begin_handle(frame_idx)

        def focus_on(self, frame_idx):
            b = self.root.E.pagepicker.browser
            frame_center_y = (frame_idx + 0.5) * b.row_per_frame * b.unit_size
            frame_center_x = self.size().width() / 2
            view_center_x = int(self.view.size().width() / 2)
            view_center_y = int(self.view.size().height() / 2)
            scene_center_p = self.view.mapToScene(view_center_x, view_center_y)
            dx = frame_center_x - scene_center_p.x()
            dy = frame_center_y - scene_center_p.y()
            v_scroll = self.view.verticalScrollBar()
            v_scroll.setRange(0, self.scene.sceneRect().height())
            # print(v_scroll.value())
            v_scroll.setValue(v_scroll.value() + dy)

            # self.view.centerOn(frame_center_x, frame_center_y)

        def init_scene_size(self):
            b = self.root.E.pagepicker.browser
            height = b.row_per_frame * len(b.frame_list) * b.unit_size
            width = self.size().width() - b.scene_shift_width
            self.scene.setSceneRect(QRectF(0, 0, width, height))

        def init_basedata(self, pagenum):
            """初始化数据"""
            b = self.root.E.pagepicker.browser
            view_size = self.size()
            shift_width = b.scene_shift_width
            b.unit_size = int((view_size.width() - shift_width) / b.col_per_row)
            b.row_per_frame = int(view_size.height() / b.unit_size)
            # print(f"view_size height={view_size.height()},shift_widt={self.scene_shift_width},unit_size={unit_size},row_per_frame={row_per_frame}")
            b.curr_frame_idx = self.frameidx_pagenum_at(pagenum)

        def frameidx_pagenum_at(self, pagenum):
            b = self.root.E.pagepicker.browser
            # print(f"colperrow={self.col_per_row},rowperframe={self.row_per_frame}")
            frame_idx = int(pagenum / (b.col_per_row * b.row_per_frame))
            # print(frame_idx)
            return frame_idx

        def init_framelist(self):
            """算出有多少个frame即可"""
            p = self.root.E.pagepicker
            totalpage = len(p.curr_doc)
            units_per_frame = p.browser.col_per_row * p.browser.row_per_frame
            total_frame_count = int(ceil(totalpage / units_per_frame))
            frame_list = [None] * total_frame_count
            last_frame_count = totalpage % units_per_frame
            for i in range(total_frame_count):
                if i < total_frame_count - 1:
                    frame_list[i] = self.FrameItem(frame_list=frame_list, frame_unit_count=units_per_frame)
                else:
                    frame_list[i] = self.FrameItem(frame_list=frame_list, frame_unit_count=last_frame_count)
            p.browser.frame_list = frame_list

        class FrameItem(object):
            state_free = 0
            state_bussy = 1
            state_done = 2
            state_doing = 3

            def __init__(self, parent=None, frame_list=None, frame_unit_count: "int" = None):
                self.frame_unit_count = frame_unit_count
                self.parent = parent
                self.frame_list = frame_list
                self.blocks = [None] * frame_unit_count  # 将来要赋值
                self.state = self.state_free

            def reset_blocks(self, frame_unit_count):
                """用法: 当你给frame_unit_count赋值时, 会调用这个方法, 重新设定blocks"""
                for i in self.blocks:
                    del i
                self.blocks = [None] * frame_unit_count
                self.state = self.state_free

            def effective_len(self):
                return len(list(filter(lambda x: x is not None, self.blocks)))

            def blocks_full(self):
                return len(self) == self.effective_len()

            def __setattr__(self, key, value):
                if key == "frame_unit_count" and "blocks" in self.__dict__:
                    self.reset_blocks(value)
                self.__dict__[key] = value

            def __len__(self):
                """返回实际长度?"""
                return len(self.blocks)

            def __getitem__(self, key):
                return self.blocks[key]

            def __setitem__(self, key, value):
                self.blocks[key] = value
                self.state = self.state_doing

            def __del__(self):
                self.__delattr__("parent")
                self.__delattr__("frame_list")
                for i in self.blocks:
                    del i
                self.__delattr__("blocks")

        class Scene(QGraphicsScene):
            def __init__(self, parent=None, superior: "PagePicker.Browser" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.signals = self.root.E.signals

            def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                e = events.PagePickerBrowserSelectSendEvent
                self.root.E.signals.on_pagepicker_browser_select_send.emit(e(pagenumlist=self.selected_item_pagenum()))

            def selected_item_pagenum(self):
                return sorted([page.pagenum for page in self.selectedItems()])

        class View(QGraphicsView):
            scrollUp = 0
            scrollDown = 1
            noscroll = 2

            def __init__(self, parent=None, superior: "PagePicker.Browser" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.signals = self.root.E.signals
                self.setScene(self.superior.scene)
                self.setDragMode(QGraphicsView.NoDrag)
                self.init_UI()

            def init_UI(self):
                self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.verticalScrollBar().setStyleSheet("width:5px;")
                self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
                if self.itemAt(event.pos()) is None:
                    e = events.PagePickerBrowserSelectEvent
                    self.signals.on_pagepicker_browser_select.emit(e(type=e.defaultType.multiCancel))
                if event.buttons() == Qt.RightButton:
                    self.setDragMode(QGraphicsView.RubberBandDrag)
                super().mousePressEvent(event)

            def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
                """下拉上拉触发子线程加载"""
                b = self.root.E.pagepicker.browser
                if event.modifiers() == Qt.ControlModifier:
                    col_per_row = b.col_per_row

                    if event.angleDelta().y() > 0 and col_per_row > 1:
                        b.col_per_row -= 1
                    if event.angleDelta().y() < 0:
                        b.col_per_row += 1
                    e = events.PagePickerBrowserLoadFrameEvent
                    # if frame_item_first is not None:
                    height_per_frame = b.row_per_frame * b.unit_size
                    count_per_frame = b.row_per_frame * b.col_per_row
                    frame_item_first = int(self.mapToScene(self.pos()).y() / height_per_frame) * count_per_frame
                    self.root.E.signals.on_pagepicker_browser_loadframe.emit(
                        e(sender=self, type=e.defaultType.initParse,  # 改变了每行列数,等于重新加载.
                          pagenum=frame_item_first)
                    )
                else:
                    if event.angleDelta().y() > 0:  # 千万别再错了
                        self.frame_idx_change_check(self.scrollUp)
                    elif event.angleDelta().y() < 0:
                        self.frame_idx_change_check(self.scrollDown)
                    super().wheelEvent(event)

            def frame_idx_change_check(self, scrollDir):
                """当发生变化,需要检查是否应该载入frame"""
                b = self.root.E.pagepicker.browser
                if b.frame_list is None or b.row_per_frame is None:
                    return
                height_per_frame = b.row_per_frame * b.unit_size
                at_frame_idx = int(self.mapToScene(self.pos()).y() / height_per_frame)  # 向上滚很容易解释
                if scrollDir == self.scrollDown:
                    at_frame_idx = int(self.mapToScene(self.pos()).y() / height_per_frame)
                    curr_frame_height_y = (at_frame_idx + 0.3) * height_per_frame
                    if curr_frame_height_y < self.mapToScene(self.pos()).y():
                        at_frame_idx += 1
                # print(f"at_frame_idx={at_frame_idx},curr_frame_idx={b.curr_frame_idx}")
                if len(b.frame_list) > at_frame_idx >= 0 and at_frame_idx != b.curr_frame_idx:
                    e = events.PagePickerBrowserLoadFrameEvent
                    self.root.E.signals.on_pagepicker_browser_loadframe.emit(
                        e(type=e.defaultType.continueLoad, frame_idx=at_frame_idx, sender=self))
                    b.curr_frame_idx = at_frame_idx

        class BottomBar(QWidget):
            def __init__(self, parent=None, superior: "PagePicker.Browser" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.progressbar = QProgressBar(self)
                H = QHBoxLayout(self)
                H.addWidget(self.progressbar)
                self.setLayout(H)

        class Item(QGraphicsPixmapItem):
            def __init__(self, parent=None, pixmap: "QPixmap" = None, pagenum=None, unit_size=None,
                         superior: "PagePicker.Browser" = None, root: "Clipper" = None):
                super().__init__(parent=parent)
                self.signals = objs.CustomSignals.start()
                self.superior = superior
                self.root = root
                self.uuid = funcs.uuid_random_make()  # 仅需要内存级别的唯一性
                self._pixmap = pixmap
                self.is_selected = False
                self.multi_select = False
                self.unit_size = unit_size
                self.setPixmap(pixmap.scaled(self.unit_size, self.unit_size, Qt.KeepAspectRatio))

                self.pagenum = pagenum
                self.pagenumtext = QGraphicsTextItem(parent=self)
                self.pagenumtext.setHtml(
                    f"<div style='background-color:green;color:white;padding:2px;font-size:20px;align:center;'>{self.pagenum}</div>")
                self.pagenumtext.setPos(0, 0)
                self.setFlag(QGraphicsItem.ItemIsSelectable, True)
                self.setFlag(QGraphicsItem.ItemIsFocusable, True)
                self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
                self.events = [
                    [self.signals.on_pagepicker_browser_select,self.on_pagepicker_browser_select_handle]

                ]
                self.all_event = objs.AllEventAdmin(self.events)
                self.all_event.bind()

            def __lt__(self, other: "PagePicker.Browser.Item"):
                return self.pagenum < other.pagenum

            def __eq__(self, other: "PagePicker.Browser.Item"):
                return self.pagenum == other.pagenum

            def set_pixmap_scale(self, size=None):
                if self.boundingRect().width() != size:
                    self.setPixmap(self._pixmap.scaled(size, size, Qt.KeepAspectRatio))
                    self.unit_size = size
                    self.update()

            def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                # self.show_selected_rect(self.isSelected())
                e = events.PagePickerBrowserSelectEvent
                if event.modifiers() == Qt.ControlModifier:  # 启动多选
                    self.multi_select = True
                    self.signals.on_pagepicker_browser_select.emit(
                        e(sender=self, item=self, type=e.defaultType.multiSelect))
                else:
                    self.multi_select = False
                    self.signals.on_pagepicker_browser_select.emit(
                        e(sender=self, item=self, type=e.defaultType.multiCancel))
                    self.signals.on_pagepicker_browser_select.emit(
                        e(sender=self, type=e.defaultType.singleSelect, item=self))

                e = events.PagePickerPreviewerReadPageEvent
                self.signals.on_pagepicker_preivewer_read_page.emit(
                    e(sender=self, type=e.defaultType.fromBrowser, pagenum=self.pagenum))
                super().mousePressEvent(event)

            def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                e = events.PageItemAddToSceneEvent
                PDFpath = self.root.E.pagepicker.curr_pdf_path
                pagenum = self.pagenum
                ratio = self.superior.superior.toolsbar.widget_DBspinbox_ratio.value()

                data = objs.PageInfo(pdf_path=PDFpath, pagenum=pagenum, ratio=ratio)
                if self.root.E.pagepicker.frompageItem is None:
                    self.signals.on_pageItem_addToScene.emit(e(sender=self, type=e.defaultType.addPage, data=data))
                else:
                    pageitem: "Clipper.PageItem" = self.root.E.pagepicker.frompageItem
                    if self.root.E.config.pagepicker.changepage_ratio_choose == self.root.E.schema.changepage_ratio_choose.old:
                        data.ratio = pageitem.pageinfo.ratio
                    self.signals.on_pageItem_addToScene.emit(e(sender=self.root.E.pagepicker.frompageItem,
                                                               type=e.defaultType.changePage, data=data))
                self.superior.superior.close()

            #
            def on_pagepicker_browser_select_handle(self, event: "events.PagePickerBrowserSelectEvent"):
                if event.type == event.defaultType.singleSelect:
                    if self == event.item:
                        self.setSelected(True)
                    else:
                        self.setSelected(False)
                elif event.type == event.defaultType.multiSelect:
                    if self == event.item:
                        self.multi_select = True
                        self.setSelected(True)
                elif event.type == event.defaultType.multiCancel:
                    self.multi_select = False
                    self.setSelected(False)
                elif event.type == event.defaultType.rubberband:
                    rect = event.rubberBandRect
                    pos = self.mapToScene(self.pos())
                    itemrect = QRect(pos.x(), pos.y(), int(self.boundingRect().width()),
                                     int(self.boundingRect().height()))

                    if rect.intersects(itemrect):
                        self.multi_select = True
                    else:
                        self.multi_select = False
                # print(f"select pagenum:{self.pagenum},{self.is_selected or self.multi_select}")
                self.show_selected_rect(self.is_selected or self.multi_select)

            def show_selected_rect(self, need: "bool"):
                if "selected_rect" not in self.__dict__:
                    rect = None
                    if self.unit_size is not None:
                        unit_size = self.unit_size
                        rect = QtCore.QRectF(0, 0, unit_size, unit_size)
                    else:
                        rect = QtCore.QRectF(0, 0, self.pixmap().width(),
                                             self.pixmap().height() + self.pagenumtext.boundingRect().height())
                    self.selected_rect = PagePicker.Browser.SelectedRect(self, rect)
                if need:
                    self.selected_rect.show()
                else:
                    self.selected_rect.hide()

            def boundingRect(self) -> QtCore.QRectF:

                if self.unit_size is not None:
                    unit_size = self.unit_size
                    return QtCore.QRectF(0, 0, unit_size, unit_size)
                else:
                    return QtCore.QRectF(0, 0, self.pixmap().width(), self.pixmap().height())

            # def previewer_select_show(self):
            #     if self.scene() is not None and len(self.scene().selectedItems()) > 0 \
            #             and self.scene().selectedItems()[-1].pagenum == self.pagenum \
            #             and self.scene().browser.pagepicker.current_preview_pagenum != self.pagenum:
            #         self.signals.on_pagepicker_preivewer_read_page.emit(self.pagenum)

            #

            def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: QWidget) -> None:
                # self.prepareGeometryChange()
                super().paint(painter, option, widget)
                self.show_selected_rect(self.isSelected() or self.multi_select)

        class SelectedRect(QGraphicsRectItem):
            def __init__(self, target: 'QGraphicsItem' = None, rect=None):
                super().__init__(parent=target)
                self.setBrush(QBrush(QColor(81, 168, 220, 100)))
                self.setRect(target.boundingRect())

    class Previewer(QWidget):
        def __init__(self, parent=None, superior: "PagePicker" = None, root: "Clipper" = None):
            super().__init__(parent)
            self.superior = superior
            self.root = root
            self.setFixedWidth(600)
            self.scene = self.Scene(parent=self, superior=self, root=root)
            self.view = self.View(parent=self, superior=self, root=root)
            # self.item = self.Item(superior=self,root=self.root)
            self.view.setScene(self.scene)
            self.item: "PagePicker.Previewer.Item" = None
            self.init_UI()

        def init_UI(self):
            V_layout = QVBoxLayout(self)
            V_layout.addWidget(self.view)
            V_layout.setStretch(0, 1)
            self.setLayout(V_layout)

        def page_load(self):
            self.scene.clear()
            self.item = self.Item(superior=self, root=self.root)
            self.scene.addItem(self.item)
            self.scene.setSceneRect(self.item.boundingRect())

        class Scene(QGraphicsScene):
            def __init__(self, parent=None, superior: "PagePicker.Previewer" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root

        class View(QGraphicsView):
            def __init__(self, parent=None, superior: "PagePicker.Previewer" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.setDragMode(self.ScrollHandDrag)
                self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                                    QPainter.SmoothPixmapTransform)

        class Item(QGraphicsPixmapItem):
            mousecenter = 0
            viewcenter = 1

            def __init__(self, superior: "PagePicker.Previewer" = None, root: "Clipper" = None):
                super().__init__()
                self.superior = superior
                self.root = root
                pdf_path, pagenum, ratio = self.path_page_ratio_get()
                path = funcs.pixmap_page_load(pdf_path, pagenum, ratio)
                self.setPixmap(QPixmap(path))
                # self.ratio = 1

            def path_page_ratio_get(self):
                # bookpagenum = self.root.E.pagepicker.curr_pagenum
                # pageoffset = self.superior.superior.toolsbar.widget_spinbox_pageoffset.value()
                count = len(self.root.E.pagepicker.curr_doc)
                pagenum = self.root.E.pagepicker.curr_pagenum  # pdfpage = bookpage-1 + pageoffset
                ratio = self.ratio_get()
                pdf_path = self.root.E.pagepicker.curr_pdf_path
                return pdf_path, pagenum, ratio

            def ratio_get(self):
                return self.superior.superior.toolsbar.widget_DBspinbox_ratio.value()

            def ratio_set(self, value):
                self.superior.superior.toolsbar.widget_DBspinbox_ratio.setValue(value)

            def view_center_pos_get(self):
                centerpos = QPointF(self.superior.view.size().width() / 2, self.superior.view.size().height() / 2)
                self.view_center_scene_p = self.superior.view.mapToScene(centerpos.toPoint())
                p = self.mapFromScene(self.view_center_scene_p)
                if not (self.boundingRect().width() > 0 and self.boundingRect().height() > 0):
                    raise ValueError("self.boundingRect().width()=0 or self.boundingRect().height()=0")
                self.view_center_item_p = [p.x() / self.boundingRect().width(), p.y() / self.boundingRect().height()]

            def mouse_center_pos_get(self, pos):
                self.mouse_center_item_p = [pos.x() / self.boundingRect().width(),
                                            pos.y() / self.boundingRect().height()]
                self.mouse_center_scene_p = self.mapToScene(pos)

            def wheelEvent(self, event):
                self.mouse_center_pos_get(event.pos())

                if event.delta() > 0:
                    self.zoomIn()
                else:
                    self.zoomOut()

            # def boundingRect(self) -> QtCore.QRectF:
            #     return QRectF(0,0,self.pixmap().rect().width(),self.pixmap().rect().height())

            def zoomIn(self):
                """放大"""
                ratio = self.ratio_get()
                ratio *= 1.1
                self.zoom(ratio)

            def zoomOut(self):
                """缩小"""
                ratio = self.ratio_get()
                ratio /= 1.1
                self.zoom(ratio)

            def center_zoom(self, center=0):
                if center == self.mousecenter:
                    X = self.mouse_center_item_p[0] * self.boundingRect().width()
                    Y = self.mouse_center_item_p[1] * self.boundingRect().height()
                    new_scene_p = self.mapToScene(X, Y)
                    dx = new_scene_p.x() - self.mouse_center_scene_p.x()
                    dy = new_scene_p.y() - self.mouse_center_scene_p.y()
                elif center == self.viewcenter:
                    X = self.view_center_item_p[0] * self.boundingRect().width()
                    Y = self.view_center_item_p[1] * self.boundingRect().height()
                    new_scene_p = self.mapToScene(X, Y)
                    dx = new_scene_p.x() - self.view_center_scene_p.x()
                    dy = new_scene_p.y() - self.view_center_scene_p.y()
                else:
                    raise TypeError(f"无法处理数据:{center}")
                scrollY = self.superior.view.verticalScrollBar()
                scrollX = self.superior.view.horizontalScrollBar()
                # 如果你不打算采用根据图片放大缩小,可以用下面的注释的代码实现scrollbar的大小适应

                print(f"x={dx}, dy={dy}")
                self.superior.view.setSceneRect(self.mapRectToScene(self.boundingRect()))
                scrollY.setValue(scrollY.value() + int(dy))
                scrollX.setValue(scrollX.value() + int(dx))

                self.view_center_scene_p = None
                self.view_center_item_p = None

                # p=  self.mapToScene(QPoint(1,1))
                # print(f"""scrolly={scrollY.value()},rect.height()={rect.height()}""")

            def zoom(self, factor, center=None):
                """缩放
                :param factor: 缩放的比例因子
                """
                if center is None:
                    center = self.mousecenter
                _factor = self.transform().scale(
                    factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
                if _factor < 0.07 or _factor > 100:
                    # 防止过大过小
                    return
                if center == self.viewcenter:
                    self.view_center_pos_get()
                pdf_path, pagenum, _ = self.path_page_ratio_get()

                path = funcs.pixmap_page_load(pdf_path, pagenum, factor)
                self.setPixmap(QPixmap(path))
                self.ratio_set(factor)
                self.center_zoom(center)

    class BookMark(QWidget):
        def __init__(self, parent=None, superior: "PagePicker" = None, root: "Clipper" = None):
            super().__init__(parent)
            self.superior = superior
            self.root = root
            self.view = QTreeView(self)
            self.model = QStandardItemModel(self)
            self.superior.E.pagepicker.bookmark.model = self.model
            self.hide()
            self.init_UI()
            self.init_model()

        def init_UI(self):
            H = QHBoxLayout(self)
            H.addWidget(self.view)
            self.setLayout(H)
            self.view.setMinimumWidth(150)
            self.view.setIndentation(10)
            pass

        def init_model(self):
            self.view.setModel(self.model)
            self.model_root = self.model.invisibleRootItem()
            self.model_root.level = 0
            self.model.setHorizontalHeaderItem(0, QStandardItem("toc"))

        def load_bookmark(self):
            doc = self.root.E.pagepicker.curr_doc
            doc_shift = -1 if doc.xref_xml_metadata() != 0 else 0
            toc = doc.get_toc()
            self.setup_toc(toc, doc_shift)

        def setup_toc(self, toc: 'list[list[int,str,int]]', doc_shift):
            parentNode = []
            self.model.clear()
            self.model.setHorizontalHeaderItem(0, QStandardItem("toc"))
            last = self.Item(name="virtual item")
            lastparent = self.root
            for i in toc:
                level, name, pagenum = i[0], i[1], i[2] + doc_shift
                item = self.Item(name=name, level=level, pagenum=pagenum)
                if self.model.rowCount() == 0:  # 为空时添加第一个元素
                    self.model.appendRow(item)
                else:
                    if level > 1:  # 层级大于1才在这里
                        if last.level == level:  # 同级就可以加到父辈
                            lastparent.appendRow(item)
                        elif last.level > level:  # 前面的等级高,后面的等级低说明开了一个新上级,需要找到与他相同级的父级插入.
                            templast = last
                            while templast.level >= level and templast.parent() is not None:  # 找到比他小的那一级
                                templast = templast.parent()
                            templast.appendRow(item)
                        elif last.level < level:
                            last.appendRow(item)

                    else:  #
                        self.model.appendRow(item)
                last = item
                lastparent = item.parent() if item.parent() is not None else self.root

        class Item(QStandardItem):
            def __init__(self, name=None, pagenum=None, level=1):
                super().__init__(name)
                self.pagenum = pagenum
                self.level = level
                self.setToolTip(name)
                self.setFlags(self.flags() & ~Qt.ItemIsEditable)

    class ToolsBar(QWidget):
        def __init__(self, parent=None, superior: "PagePicker" = None, root: "Clipper" = None):
            super().__init__(parent)
            self.superior = superior
            self.root = root
            self.g_layout = QGridLayout(self)
            self.widget_button_open = QToolButton()
            self.widget_lineEdit_pagenum = QLineEdit()
            self.widget_DBspinbox_ratio = QDoubleSpinBox()
            self.widget_spinbox_pageoffset = QSpinBox()
            self.widget_spinbox_pagejump = QSpinBox()
            self.widget_button_newPage = QToolButton()
            self.widget_button_bookmark = QToolButton()
            imgDir = objs.SrcAdmin.imgDir
            self.widget_li = [self.Data(*data) for data in
                              [(self.widget_spinbox_pagejump, True, "book page jump:", "book page=pdf_page +1 + offset",
                                None, 0, 5),
                               (self.widget_button_open, True, "", "", imgDir.item_open, 0, 1),
                               (self.widget_button_bookmark, False, None, None, imgDir.bookmark, 0, 0),
                               (self.widget_button_newPage, False, None, None, imgDir.download, 0, 6),
                               (self.widget_DBspinbox_ratio, True, "image ratio:", "", None, 0, 3),
                               (self.widget_lineEdit_pagenum, True, "collected pages:", "", None, 0, 2),
                               (self.widget_spinbox_pageoffset, True, "offset:", "", None, 0, 4)]]

            self.unit_li: "dict[Union[QToolButton,QLineEdit,QDoubleSpinBox,QSpinBox],objs.GridHDescUnit]" = {}
            for data in self.widget_li:
                if data.needunit:
                    self.unit_li[data.widget] = objs.GridHDescUnit(parent=self, widget=data.widget,
                                                                   labelname=data.unittext, tooltip=data.tooltip)
                    self.g_layout.addWidget(self.unit_li[data.widget], data.x, data.y)
                    if data.imgDir: data.widget.setIcon(QIcon(data.imgDir))
                else:
                    if data.unittext: data.widget.setText(data.unittext)
                    if data.tooltip: data.widget.setToolTip(data.tooltip)
                    if data.imgDir: data.widget.setIcon(QIcon(data.imgDir))
                    self.g_layout.addWidget(data.widget, data.x, data.y)
            self.widget_spinbox_pagejump.setRange(-20000, 20000)
            self.widget_spinbox_pageoffset.setRange(-20000, 20000)
            self.widget_DBspinbox_ratio.setSingleStep(0.1)

            self.setLayout(self.g_layout)

        def newpage_validitycheck(self):
            """先检查是否选中,再检查collect page是否有值"""
            pass

        def setBookPageFromPDFpage(self, pdfpagenum):
            if type(pdfpagenum) == int:
                count = len(self.root.E.pagepicker.curr_doc)
                self.root.E.pagepicker.curr_pagenum = pdfpagenum % count
                self.widget_spinbox_pagejump.setValue(pdfpagenum - self.widget_spinbox_pageoffset.value() + 1)

        def collect_page_validity(self, string):

            return re.search(r"^(:?\d+,|\d+-\d+,)*(:?\d+-\d+|\d+)$", string)
            pass

        def collect_page_highlight(self, color, delay=None):
            if delay is None:
                self.widget_lineEdit_pagenum.setStyleSheet(f"background-color:{color};")
            else:
                QTimer.singleShot(delay, lambda: self.collect_page_highlight(color))

        def collect_page_set_convert(self, string):
            t = self.root.E.pagepicker.toolsbar
            t.collect_page_set = set()
            li = string.split(",")
            for num in li:
                if "-" in num:
                    LR = num.split("-")
                    for i in range(int(LR[0]), int(LR[1]) + 1):
                        t.collect_page_set.add(i)
                else:
                    t.collect_page_set.add(int(num))

        @dataclass
        class Data:
            widget: "Union[QToolButton,QLineEdit,QDoubleSpinBox,QSpinBox]" = None
            needunit: "bool" = None
            unittext: "str" = None
            tooltip: "str" = None  # 如果有unit,就写到unit,没有就写自身上
            imgDir: "str" = None
            x: "int" = None
            y: "int" = None

    pass


class FrameLoadWorker(QThread):
    """专供使用"""
    on_frame_load_begin = pyqtSignal(object)  # {"frame_id","frame_list"}
    on_stop_load = pyqtSignal(object)  #
    on_1_page_load = pyqtSignal(object)  # {"frame_id","percent"}
    on_1_page_loaded = pyqtSignal(object)
    on_all_page_loaded = pyqtSignal()  #
    frame_id_default = None

    def __init__(self, E: "Entity" = None):
        super().__init__()
        self.E = E
        self.daemon = True
        self.ws = self.E.pagepicker.browser.workerstate
        self.w = self.E.pagepicker.browser.worker
        self.b = self.E.pagepicker.browser
        self.p = self.E.pagepicker
        self.all_event = objs.AllEventAdmin([
            [self.on_frame_load_begin, self.on_frame_load_begin_handle],
            [self.on_stop_load, self.on_stop_load_handle],
            [self.on_all_page_loaded, self.on_all_page_loaded_handle],
            [self.on_1_page_loaded, self.on_1_page_loaded_handle],
        ]).bind()

    def on_1_page_loaded_handle(self, _):
        self.ws.bussy = False
        # print("1 page loaded self.bussy = False")

    def on_all_page_loaded_handle(self):
        self.ws.killself = True

    def on_stop_load_handle(self, _):
        self.ws.do = False
        # self.frame_id = self.frame_id_default

    def on_frame_load_begin_handle(self, frame_id):
        self.ws.do = True
        self.b.frame_id = frame_id
        self.ws.frame_id = frame_id
        print(f"frame_id at worker= {frame_id}")

    def init_data(self, E: "Entity" = None, frame_list=None, doc=None, unit_size=None, col_per_row=None,
                  row_per_frame=None):
        # self.E=E
        self.ws.bussy = False

    def sleepgap(self):
        gap = 1
        # return 1
        if self.b.frame_list is not None:
            return gap / (self.b.row_per_frame * self.b.col_per_row) * 0.1
        else:
            return gap / 5

    def run(self):
        while 1:
            if self.ws.killself:
                break
            # 从原有变量中提取出来, 因为很有可能在运行中变化.
            # print(f"self.do={self.ws.do},not bussy={not self.ws.bussy},self.doc={self.p.curr_doc},frame_id={self.ws.frame_id},")
            if self.ws.do and not self.ws.bussy and self.p.curr_doc is not None:
                # print("begin")

                doc = self.p.curr_doc
                frame_id = self.ws.frame_id
                frame = self.b.frame_list[frame_id]
                unit_size = self.b.unit_size
                col_per_row = self.b.col_per_row
                row_per_frame = self.b.row_per_frame

                # print(f"frame.effective_len={frame.effective_len()},frame.blocks_full()={frame.blocks_full()}")
                if not frame.blocks_full():
                    print(f"not blocks_full, frame_at={frame_id}")
                    self.ws.bussy = True
                    self.browser_pageinfo_make(doc, frame, frame_id, col_per_row, row_per_frame, unit_size)
            time.sleep(self.sleepgap())

    def browser_pageinfo_make(self, doc, frame, frame_id, col_per_row, row_per_frame, unit_size):

        total = len(frame)
        frame_item_idx = frame.effective_len()  # 直接就下一个
        pagenum = frame_id * row_per_frame * col_per_row + frame_item_idx
        d = {"frame_idx": frame_id, "frame_item_idx": frame_item_idx, "pagenum": pagenum}
        X = (frame_item_idx % col_per_row) * unit_size
        Y = (frame_id * row_per_frame + int(frame_item_idx / col_per_row)) * unit_size
        d["x"] = X
        d["y"] = Y
        d["percent"] = (frame_item_idx + 1) / total
        d["pixmapdir"] = funcs.pixmap_page_load(doc, pagenum)
        data = self.E.OnePageLoadData(**d)
        self.on_1_page_load.emit(data)
