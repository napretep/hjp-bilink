import os.path
import sys
import time
from dataclasses import dataclass, field
from collections import namedtuple
from typing import Union

import typing
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPointF, QPoint, QRectF, QPersistentModelIndex, QModelIndex
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QPixmap, QPen, QColor
from PyQt5.QtWidgets import QDialog, QWidget, QGraphicsScene, QGraphicsView, QToolButton, QHBoxLayout, QApplication, \
    QVBoxLayout, QGridLayout, QTreeView, QLabel, QHeaderView, QAbstractItemView, QGraphicsItem, QGraphicsRectItem, \
    QGraphicsWidget, QGraphicsPixmapItem, QGraphicsSceneMouseEvent, QGraphicsGridLayout, QGraphicsProxyWidget, \
    QGraphicsSceneWheelEvent, QStyleOptionGraphicsItem, QGraphicsSceneHoverEvent
from .tools import objs, events, ALL, funcs
from .Model import Entity
from .fitz import fitz

print, printer = funcs.logger(__name__)


class Clipper(QDialog):
    """空打开一定会加载,如果不空请手工加载."""

    def __init__(self, entity: "Entity"):
        super().__init__()
        self.E = entity
        # self.E.pagepicker.browser.worker=FrameLoadWorker(self.E)
        self.imgDir = objs.SrcAdmin.call().imgDir
        self.signals = self.E.signals
        self.container0 = QWidget(self)
        self.scene = QGraphicsScene(self)
        self.pdfview = self.PDFView(self.scene, parent=self, superior=self)
        self.rightsidebar = self.RightSideBar(superior=self)
        self.widget_button_show_rightsidebar = QToolButton(self)
        self.init_UI()
        self.api = self.API(self)
        self.allevent = objs.AllEventAdmin({
            self.E.signals.on_pagepicker_open: self.on_pagepicker_open_handle,
            self.signals.on_pageItem_addToScene: self.on_pageItem_addToScene_handle,
            self.pdfview.verticalScrollBar().valueChanged: self.on_pdfview_verticalScrollBar_valueChanged_handle,
            self.pdfview.horizontalScrollBar().valueChanged: self.on_pdfview_horizontalScrollBar_valueChanged_handle,
            self.signals.on_pageitem_close: self.on_pageitem_close_handle,
            self.rightsidebar.pagelist.addButton.clicked: self.on_righsidebar_pagelist_addButton_clicked_handle,
            self.rightsidebar.pagelist.view.clicked: self.on_rightsidebar_pagelist_view_clicked_handle,
            self.rightsidebar.pagelist.view.doubleClicked: self.on_rightsidebar_pagelist_view_doubleClicked_handle
        }).bind()

    def on_rightsidebar_pagelist_view_doubleClicked_handle(self, index: "QModelIndex"):
        item: "Clipper.RightSideBar.PageList.PDFItem" = self.rightsidebar.pagelist.model.item(index.row(), 0)
        e = events.PagePickerOpenEvent
        self.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromPage, fromPageItem=item.pageitem))

    def on_rightsidebar_pagelist_view_clicked_handle(self, index: "QModelIndex"):
        item: "Clipper.RightSideBar.PageList.PDFItem" = self.rightsidebar.pagelist.model.item(index.row(), 0)
        self.pdfview.centerOn(item=item.pageitem)

    def on_pagepicker_open_handle(self, event: "events.PagePickerOpenEvent"):
        from .PagePicker import PagePicker
        if event.type == event.defaultType.fromMainWin:
            pass
        elif event.type == event.defaultType.fromPage:
            self.E.pagepicker.frompageItem = event.fromPageItem
        elif event.type == event.defaultType.fromAddButton:
            pass
        # self.E.pagepicker.browser.worker.start()
        self.E.pagepicker.ins = PagePicker(parent=self, superior=self, root=self)
        self.E.pagepicker.ins.show()

    def on_righsidebar_pagelist_addButton_clicked_handle(self):
        self.rightsidebar.pagelist.on_addButton_clicked_handle()

    def on_pageitem_close_handle(self, event: "events.PageItemCloseEvent"):
        self.delpage(event.pageitem)

    def on_pdfview_horizontalScrollBar_valueChanged_handle(self, value):
        rect = self.pdfview.sceneRect()
        if value == self.pdfview.horizontalScrollBar().maximum():
            rect.setRight(rect.right() + 50)
        elif value == self.pdfview.horizontalScrollBar().minimum():
            rect.setLeft(rect.left() - 50)
        self.pdfview.setSceneRect(rect)

    def on_pdfview_verticalScrollBar_valueChanged_handle(self, value):
        rect = self.pdfview.sceneRect()
        if value == self.pdfview.verticalScrollBar().maximum():
            rect.setBottom(rect.bottom() + 50)
            # self.pdfview.setSceneRect(rect.x(), rect.y(), rect.width(), rect.height() + 10)
        elif value <= self.pdfview.verticalScrollBar().minimum() + 1:
            rect.setTop(rect.top() - 50)
            # self.pdfview.verticalScrollBar().setMinimum(self.pdfview.verticalScrollBar().value()-50)
        self.pdfview.setSceneRect(rect)

        # self.pdfview.setSceneRect(rect.x(), rect.y() - 10, rect.width(), rect.height())

    def on_ScenePageLoader_1_page_load_handle(self, data: "pageloaddata"):
        print(f"on_ScenePageLoader_1_page_load_handle,{data}")
        # TODO 1 pageitem, 2 pdfview addpage, 3 rightsidebar addpage
        pageitem = Clipper.PageItem(data.pixdir, data.pageinfo, superior=self.pdfview, root=self)
        self.addpage(pageitem)
        self.E.pdfview.progresser.valtxt_set(data.progress)
        if data.progress >= 100:
            self.E.pdfview.progresser.close()

        pass

    def on_pageItem_addToScene_handle(self, event: "events.PageItemAddToSceneEvent"):
        """#分别控制两个地方"""
        if event.type == event.defaultType.addPage:
            data: "objs.PageInfo" = event.data
            png_path = funcs.pixmap_page_load(data.pdf_path, data.pagenum, data.ratio)
            pageitem = self.PageItem(png_path, data, superior=self.pdfview, root=self)
            self.addpage(pageitem)
            pass
        elif event.type == event.defaultType.addMultiPage:
            self.E.pdfview.scenepageload_worker = ScenePageLoader(event.datali)
            self.E.pdfview.scenepageload_worker.on_1_page_load.connect(self.on_ScenePageLoader_1_page_load_handle)
            self.E.pdfview.progresser = objs.UniversalProgresser(parent=self)
            self.E.pdfview.progresser.show()
            self.E.pdfview.scenepageload_worker.start()
            pass
        elif event.type == event.defaultType.changePage:
            pageitem: "Clipper.PageItem" = event.sender
            data: "objs.PageInfo" = event.data
            self.changepage(pageitem, data)
            QTimer.singleShot(100, lambda: self.pdfview.centerOn(item=pageitem))
            pass

    def addpage(self, pageitem: "Clipper.PageItem"):
        self.pdfview.addpage(self, pageitem)
        self.rightsidebar.addpage(self, pageitem)

    def delpage(self, pageitem: "Clipper.PageItem"):
        self.pdfview.delpage(self, pageitem)
        self.rightsidebar.delpage(self, pageitem)

    def changepage(self, pageitem: "Clipper.PageItem", data: "objs.PageInfo"):
        assert isinstance(pageitem, Clipper.PageItem) and isinstance(data, objs.PageInfo)
        pageitem.changepage(self, data)
        self.rightsidebar.changepage(self, pageitem)

    def init_UI(self):
        self.setWindowIcon(QIcon(self.imgDir.clipper))
        self.setWindowTitle("PDF clipper")
        self.setModal(False)
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.pdfview)
        self.h_layout.addWidget(self.rightsidebar)
        self.h_layout.setStretch(0, 1)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))
        self.container0.resize(self.width(), self.height())
        self.container0.setLayout(self.h_layout)
        self.widget_button_show_rightsidebar.setIcon(QIcon(objs.SrcAdmin.imgDir.left_direction))
        self.widget_button_show_rightsidebar.move(self.geometry().width() - 20, self.geometry().height() / 2)
        self.widget_button_show_rightsidebar.hide()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        print(self.pdfview.horizontalScrollBar().maximum())
        print(self.pdfview.horizontalScrollBar().minimum())
        super().mousePressEvent(event)

    def resizeEvent(self, *args):
        self.container0.resize(self.width(), self.height())
        self.widget_button_show_rightsidebar.move(self.geometry().width() - 20, self.geometry().height() / 2)

        pass

    def start(self, pairs_li: "list[objs.Pair]" = None):
        """用于clipper启动时添加一些特别条件"""
        if pairs_li:
            # 批量添加到cardlist
            # for pair in pairs_li:
            #     self.rightsidebar.card_list_add(desc=pair["desc"], card_id=pair["card_id"], newcard=False)
            # pdfinfo_dict = self.pdf_info_card_id_li_load(pairs_li)
            # pdf_page_ratio = []
            #
            # for k, v in pdfinfo_dict.items():
            #     PDF_JSON = objs.SrcAdmin.PDF_JSON
            #     if PDF_JSON.exists(k) and "ratio" in PDF_JSON[k]:
            #         ratio = PDF_JSON.read(k)["ratio"]
            #     else:
            #         ratio = 1
            #     for pagenum in v["pagenum"]:
            #         pdf_page_ratio.append((v["pdfname"], pagenum, ratio))
            #
            # if len(pdf_page_ratio) > 0:
            #     self.start_mainpage_loader(pdf_page_ratio)
            pass
        else:
            QTimer.singleShot(50, self.if_empty_start_pagepicker)

    def if_empty_start_pagepicker(self):
        if len(self.scene.items()) == 0:
            e = events.PagePickerOpenEvent
            self.E.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromMainWin))


    @dataclass
    class API:
        """API只能用在初始化之后的函数中,否则会出错容易"""

        def __init__(self, superior: "Clipper"):
            self.superior = superior

        pass

    class PDFView(QGraphicsView):
        def __init__(self, scene, parent=None, superior: "Clipper" = None):
            super().__init__(parent)
            self.setScene(scene)
            self.superior = superior
            self.root = superior
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            # self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
            #                     QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
            #                     QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
            self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
            self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图
            self.setDragMode(self.ScrollHandDrag)
            self.setCursor(Qt.ArrowCursor)
            self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        def addpage(self, caller: "Clipper", pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.addpage, caller, Clipper)
            self.root.E.pdfview.pageitem_container.append_data(self, pageitem)
            self.pageitem_layout_arrange()  # 先布局后插入
            self.scene().addItem(pageitem)
            self.centerOn(item=pageitem)

        def delpage(self, caller: "Clipper", pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.delpage, caller, Clipper)
            self.root.E.pdfview.pageitem_container.remove_data(self, pageitem)
            self.scene().removeItem(pageitem)

        def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().keyReleaseEvent(event)

        def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
            if event.buttons() == Qt.RightButton:
                self.setDragMode(QGraphicsView.RubberBandDrag)
                # funcs.show_clipbox_state()
            super().mousePressEvent(event)

        def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
            # print(self.scene().selectedItems())
            super().mouseMoveEvent(event)
            pass

        def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
            # if self.curr_selected_item is not None and self.curr_rubberBand_rect is not None:
            #     r = self.curr_rubberBand_rect
            #     pos = self.mapToScene(r.x(), r.y())
            #     x, y, w, h = pos.x(), pos.y(), r.width(), r.height()
            #     e = events.PageItemRubberBandRectSendEvent
            #     ALL.signals.on_pageItem_rubberBandRect_send.emit(
            #         e(sender=self.curr_selected_item, eventType=e.oneType, rubberBandRect=QRectF(x, y, w, h)))
            #     self.curr_selected_item = None
            #     self.curr_rubberBand_rect = None
            #     e = events.ClipboxCreateEvent
            #     ALL.signals.on_clipbox_create.emit(e(sender=self, eventType=e.rubbedType))

            super().mouseReleaseEvent(event)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            # e = events.ClipboxStateSwitchEvent
            #
            # ALL.signals.on_clipboxstate_switch.emit(
            #     e(sender=self, eventType=e.hideType)
            # )

        def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
            modifiers = QApplication.keyboardModifiers()

            if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
                # e = events.PDFViewResizeViewEvent
                # if event.angleDelta().y() > 0:
                #     self.scale(1.1, 1.1)
                #     self.reset_ratio_value *= 1.1
                #     ALL.signals.on_PDFView_ResizeView.emit(
                #         e(eventType=e.zoomInType, pdfview=self, ratio=self.reset_ratio_value))
                # else:
                #     self.scale(1 / 1.1, 1 / 1.1)
                #     self.reset_ratio_value /= 1.1
                #     ALL.signals.on_PDFView_ResizeView.emit(
                #         e(eventType=e.zoomOutType, pdfview=self, ratio=self.reset_ratio_value))
                pass
            else:
                super().wheelEvent(event)
            pass

        def pageitem_moveto_oldpage_bottom(self, old_item: 'Clipper.PageItem', new_item: 'Clipper.PageItem'):
            new_pos = QPointF(old_item.x(), old_item.y() + old_item.boundingRect().height())
            # print(new_pos)
            new_item.setPos(new_pos)

        def pageitem_moveto_oldpage_left(self, old_item: 'Clipper.PageItem', new_item: 'Clipper.PageItem'):
            new_pos = QPointF(old_item.x() + old_item.boundingRect().width(), old_item.y())
            # print(new_pos)
            new_item.setPos(new_pos)

        def pageitem_layout_arrange(self):
            config = self.root.E.config.mainview
            viewlayoutmode = config.layout_mode
            pdfview = self.root.E.pdfview
            pageItemList = list(pdfview.pageitem_container.uuidBased_data.values())
            newitem: 'Clipper.PageItem' = pageItemList[-1]
            old_count = len(pageItemList) - 1
            if old_count == 0:  # 由于每次进来必然加载了一个所以这里可能用不太到
                newitem.setPos(0, 0)
                return
            if viewlayoutmode == pdfview.layoutmode.Horizontal:
                row = config.layout_row_per_col
                rem = old_count % row  #
                if rem != 0:
                    olditem = pageItemList[-2]
                    self.pageitem_moveto_oldpage_bottom(olditem, newitem)
                else:
                    olditem = pageItemList[-row - 1]
                    self.pageitem_moveto_oldpage_left(olditem, newitem)
                pass

            elif viewlayoutmode == pdfview.layoutmode.Vertical:
                col = config.layout_col_per_row
                rem = old_count % col
                if rem != 0:
                    olditem = pageItemList[-2]
                    self.pageitem_moveto_oldpage_left(olditem, newitem)
                else:
                    olditem = pageItemList[-col - 1]
                    self.pageitem_moveto_oldpage_bottom(olditem, newitem)

        def centerOn(self, pos: "Union[QPoint]" = None, item: "QGraphicsItem" = None):
            """居中显示"""
            assert pos is not None or item is not None
            if pos is None:
                x, y, r, b = item.boundingRect().left(), item.boundingRect().top(), item.boundingRect().right(), item.boundingRect().bottom()

                pos = item.mapToScene(int((x + r) / 2), int((y + b) / 2)).toPoint()
            curr_view_center = self.mapToScene(int(self.viewport().width() / 2),
                                               int(self.viewport().height() / 2)).toPoint()
            dp = pos - curr_view_center
            self.safeScroll(dp.x(), dp.y())

        def safeScroll(self, x, y):
            """遇到边界会扩大scene"""
            x_scroll = self.horizontalScrollBar()
            y_scroll = self.verticalScrollBar()
            rect = self.sceneRect()
            if x_scroll.value() + x > x_scroll.maximum():
                rect.setRight(rect.right() + x)
                # self.setSceneRect(rect.x(),rect.y(),rect.width()+x,rect.height())
            if x_scroll.value() + x < x_scroll.minimum():
                rect.setLeft(rect.left() + x)
                # self.setSceneRect(rect.x()+x, rect.y(), rect.width() + x, rect.height())
            if y_scroll.value() + y > y_scroll.maximum():
                # self.setSceneRect(rect.x(),rect.y(),rect.width(),rect.height()+y)
                rect.setBottom(rect.bottom() + y)
            if y_scroll.value() + y < y_scroll.minimum():
                rect.setTop(rect.top() + y)
                # self.setSceneRect(rect.x(),rect.y()+y,rect.width(),rect.height())
            self.setSceneRect(rect)
            x_scroll.setValue(x_scroll.value() + x)
            y_scroll.setValue(y_scroll.value() + y)

        # pass
        # def smoothScroll(self,x,y,times=5,gap=0.1):
        #     x_scroll = self.horizontalScrollBar()
        #     y_scroll = self.verticalScrollBar()
        #     x,y=int(x/times),int(y/times)
        #     for i in range(times):
        #         x_scroll.setValue(x_scroll.value() + x)
        #         y_scroll.setValue(y_scroll.value() + y)
        #         time.sleep(0.1/times)

    class RightSideBar(QWidget):
        def __init__(self, parent=None, superior: "Clipper" = None):
            super().__init__(parent)
            self.superior = superior
            self.root = superior

            self.pagelist = self.PageList(parent=self, superior=self, root=self.root)
            self.cardlist = self.CardList(parent=self, superior=self, root=self.root)
            self.buttonPanel = self.ButtonPanel(parent=self, superior=self, root=self.root)
            self.init_UI()

        def addpage(self, caller, pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.addpage, caller, Clipper)
            pdfname = funcs.str_shorten(os.path.basename(pageitem.pageinfo.pdf_path))
            # pagenum = str(pageitem.pageinfo.pagenum)
            item_pdf = self.PageList.PDFItem(pdfname, pageitem)
            item_page = self.PageList.PageNumItem(pageitem)
            self.pagelist.model.appendRow([item_pdf, item_page])
            pageitem.pagelist_index = QPersistentModelIndex(item_pdf.index())

        def delpage(self, caller, pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.delpage, caller, Clipper)
            self.pagelist.model.removeRow(pageitem.pagelist_index.row())

        def changepage(self, caller, pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.changepage, caller, Clipper)
            row, col = pageitem.pagelist_index.row(), pageitem.pagelist_index.column()
            item_pdf: "Clipper.RightSideBar.PageList.PDFItem" = self.pagelist.model.item(row, col)
            item_page: "Clipper.RightSideBar.PageList.PageNumItem" = self.pagelist.model.item(row, col + 1)
            item_pdf.update_data(self, pageitem)
            item_page.update_data(self, pageitem)

        def init_UI(self):
            self.V_layout = QVBoxLayout()
            self.V_layout.addWidget(self.pagelist)
            self.V_layout.addWidget(self.cardlist)
            self.V_layout.addWidget(self.buttonPanel)
            self.V_layout.setStretch(0, 1)
            self.V_layout.setStretch(1, 1)
            self.setLayout(self.V_layout)

        class PageList(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.view = QTreeView(self)
                self.model = QStandardItemModel(self)
                self.root.E.rightsidebar.pagelist.model = self.model
                self.V_layout = QVBoxLayout(self)
                self.addButton = QToolButton(self)
                self.delButton = QToolButton(self)
                self.init_UI()
                self.init_model()
                self.allevent = objs.AllEventAdmin({
                    self.addButton.clicked: self.on_addButton_clicked_handle
                }).bind()

            def on_addButton_clicked_handle(self):
                e = events.PagePickerOpenEvent
                self.root.E.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromAddButton))

            def init_UI(self):
                H_layout = QHBoxLayout()
                V_layout2 = QVBoxLayout()
                self.label = QLabel("page list")
                self.addButton.setText("+")
                self.delButton.setText("-")
                self.V_layout.addLayout(H_layout)
                self.V_layout.addLayout(V_layout2)
                self.V_layout.setStretch(1, 1)
                self.view.setIndentation(0)
                H_layout.addWidget(self.label)
                H_layout.addWidget(self.addButton)
                H_layout.addWidget(self.delButton)
                V_layout2.addWidget(self.view)

            pass

            def init_model(self):
                pdfname = QStandardItem("PDFname")  # 存文件路径
                pagenum = QStandardItem("pagenum")  # 存页码和graphics_page对象
                self.model.setHorizontalHeaderItem(0, pdfname)
                self.model.setHorizontalHeaderItem(1, pagenum)
                self.pagepicker = None
                self.pageItemDict = {}
                self.view.setModel(self.model)
                self.view.header().setDefaultSectionSize(180)
                self.view.header().setSectionsMovable(False)
                self.view.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                self.view.header().setSectionResizeMode(0, QHeaderView.Interactive)
                self.view.header().setSectionResizeMode(1, QHeaderView.Stretch)
                self.view.setColumnWidth(1, 10)

            class PDFItem(QStandardItem):
                def __init__(self, PDFName, selfData: "Clipper.PageItem"):
                    super().__init__(PDFName)
                    self.setFlags(self.flags() & ~ Qt.ItemIsEditable & ~ Qt.ItemIsDragEnabled)
                    self.pageitem: "Clipper.PageItem" = selfData
                    self.setData(selfData, Qt.UserRole)
                    self.setToolTip(selfData.pageinfo.pdf_path)

                def update_data(self, caller, pageitem: "Clipper.PageItem"):
                    funcs.caller_check(Clipper.RightSideBar.changepage, caller, Clipper.RightSideBar)
                    PDFName = funcs.str_shorten(os.path.basename(pageitem.pageinfo.pdf_path))
                    self.setText(PDFName)
                    self.setToolTip(pageitem.pageinfo.pdf_path)

            class PageNumItem(QStandardItem):
                def __init__(self, selfData: "Clipper.PageItem"):
                    super().__init__(str(selfData.pageinfo.pagenum))
                    self.setFlags(self.flags() & ~ Qt.ItemIsEditable & ~ Qt.ItemIsDragEnabled)
                    self.pageitem: "Clipper.PageItem" = selfData
                    self.setData(selfData, Qt.UserRole)

                def update_data(self, caller, pageitem: "Clipper.PageItem"):
                    funcs.caller_check(Clipper.RightSideBar.changepage, caller, Clipper.RightSideBar)
                    self.setText(str(pageitem.pageinfo.pagenum))

        class CardList(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.model = QStandardItemModel(self)
                self.root.E.rightsidebar.cardlist.model = self.model
                self.label = QLabel(self)
                self.view = QTreeView(self)
                self.addButton = QToolButton(self)
                self.delButton = QToolButton(self)
                self.init_UI()

            def init_UI(self):
                H_layout = QHBoxLayout()
                V_layout2 = QVBoxLayout()
                self.label.setText("card list")
                self.V_layout = QVBoxLayout(self)
                self.addButton.setText("+")
                self.delButton.setText("-")
                self.view.setIndentation(0)
                self.view.header().setSectionResizeMode(QHeaderView.Stretch)

                H_layout.addWidget(self.label)
                H_layout.addWidget(self.addButton)
                H_layout.addWidget(self.delButton)
                V_layout2.addWidget(self.view)
                self.view.setDragEnabled(True)
                self.view.setDragDropMode(QAbstractItemView.InternalMove)
                self.view.setDefaultDropAction(Qt.MoveAction)
                self.view.setAcceptDrops(True)
                self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.view.dropEvent = self.dropEvent
                self.V_layout.addLayout(H_layout)
                self.V_layout.addLayout(V_layout2)
                self.V_layout.setStretch(1, 1)

            def init_model(self):
                self.newcardcount = 0
                self.ClipboxState = None
                # self.model=QStandardItemModel(self)
                # self.listView=QTreeView(self)
                self.model_rootNode = self.model.invisibleRootItem()
                self.model_rootNode.character = "root"
                self.model_rootNode.level = -1
                self.model_rootNode.primData = None
                label_id = self.CardItem("card_id", parent=self, superior=self, root=self.root)
                label_desc = self.DescItem("desc", parent=self, superior=self, root=self.root)
                self.model.setHorizontalHeaderItem(1, label_id)
                self.model.setHorizontalHeaderItem(0, label_desc)
                self.listView.setModel(self.model)
                self.listView.header().setDefaultSectionSize(150)
                self.listView.header().setSectionsMovable(False)
                self.listView.setColumnWidth(1, 10)

            class CardItem:
                def __init__(self, *agrs, parent=None, superior: "Clipper.RightSideBar.CardList" = None,
                             root: "Clipper" = None):
                    super().__init__(*agrs, parent=parent)
                    self.superior = superior
                    self.root = root

                pass

            class DescItem:
                def __init__(self, *agrs, parent=None, superior: "Clipper.RightSideBar.CardList" = None,
                             root: "Clipper" = None):
                    super().__init__(*agrs, parent=parent)
                    self.superior = superior
                    self.root = root

                pass

        class ButtonPanel(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.g_layout = QGridLayout(self)
                self.widget_button_QA = QToolButton(self)
                self.widget_button_hide = QToolButton(self)
                self.widget_button_confirm = QToolButton(self)
                self.widget_button_relayout = QToolButton(self)
                self.widget_button_config = QToolButton(self)
                self.widget_button_resetRatio = QToolButton(self)
                self.widget_button_clearView = QToolButton(self)
                e = events.RightSideBarButtonGroupEvent

                imgDir = objs.SrcAdmin.imgDir
                buttoninfoli = [(self.widget_button_hide, 0, imgDir.right_direction, e.hideRighsidebarType,
                                 "隐藏侧边栏\nhide rightsidebar"),
                                (self.widget_button_clearView, 1, imgDir.clear, e.clearViewType,
                                 "清空视图中的项目\nclear view items"),
                                (self.widget_button_resetRatio, 2, imgDir.reset, e.resetViewRatioType,
                                 "恢复视图为正常比例\nreset view size"),
                                (self.widget_button_QA, 3, imgDir.question, e.QAswitchType, "切换插入点为Q或A\nswitch Q or A"),
                                (self.widget_button_relayout, 4, imgDir.refresh, e.reLayoutType,
                                 "视图布局重置\nview relayout"),
                                (self.widget_button_config, 5, imgDir.config, e.configType, "配置选项\nset configuration"),
                                (self.widget_button_confirm, 6, imgDir.correct, e.correctType,
                                 "开始插入clipbox的任务\nBegin the task of inserting Clipbox"),
                                ]
                self.buttondatali = [self.ButtonData(*data) for data in buttoninfoli]
                self.init_UI()

            def init_UI(self):
                e = events.RightSideBarButtonGroupEvent
                for data in self.buttondatali:
                    data.button.setIcon(QIcon(data.icondir))
                    self.g_layout.addWidget(data.button, 0, data.layoutpos)
                    data.button.clicked.connect(
                        lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(e(eventType=data.eventType)))
                    data.button.setToolTip(data.tooltip)

            @dataclass
            class ButtonData:
                button: "QToolButton"
                layoutpos: "int"
                icondir: "str"
                eventType: "int"
                tooltip: "str"

            pass

    class PageItem(QGraphicsItem):
        def __init__(self, png_path: "str", data: "objs.PageInfo", superior: "Clipper.PDFView", root: "Clipper", *args,
                     **kwargs):
            super().__init__(*args, **kwargs)
            self.superior = superior
            self.root = root
            self.ratio = 1  # 这个ratio是需要通过1:1恢复的方式去掉的., 所以必须有,不能直接修改pageinfo里的ratio

            self.signals = self.root.signals
            self.uuid = hash(self).__str__()  # 这个uuid不用做存储,仅在内存中标记唯一性
            self.png_path = png_path
            self.pageinfo = data
            self.pageview = self.PageView(superior=self, root=self.root)
            self.toolsbar = self.ToolsBar(superior=self, root=self.root)
            self.pagelist_index: "QPersistentModelIndex" = None
            self.setAcceptHoverEvents(True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            self.events = objs.AllEventAdmin({
                self.toolsbar.widget_button_close.clicked: self.on_widget_button_close_clicked_handle,
                self.toolsbar.widget_button_pageinfo.clicked: self.on_widget_button_pageinfo_clicked_handle,
                self.toolsbar.widget_button_prev.clicked: self.on_widget_button_prev_clicked_handle,
                self.toolsbar.widget_button_next.clicked: self.on_widget_button_next_clicked_handle,
                self.toolsbar.widget_button_fullscreen.clicked: self.on_widget_button_fullscreen_clicked_handle,
                self.toolsbar.widget_button_recover.clicked: self.on_widget_button_recover_clicked_handle,
                self.signals.on_pageItem_resize_event: self.on_pageItem_resize_event_handle,
            }).bind()

        def on_pageItem_resize_event_handle(self, event: "events.PageItemResizeEvent"):
            v_size_width = self.superior.size().width()
            v_size_height = self.superior.size().height()
            v_viewport_width = self.superior.viewport().width()
            v_viewport_height = self.superior.viewport().height()
            v_framerect_width = self.superior.frameRect().width()
            v_framerect_height = self.superior.frameRect().height()
            if event.type == event.defaultType.fullscreen:
                ratio = v_viewport_width / self.pageview.boundingRect().width()
                self.pageview.zoom(ratio, center=event.center)
            elif event.type == event.defaultType.fitheight:
                ratio = v_viewport_height / self.pageview.boundingRect().height()
                self.pageview.zoom(ratio, center=event.center)
            elif event.type == event.defaultType.recover:
                ratio = 1
                self.pageview.zoom(ratio, center=event.center)

        def on_widget_button_recover_clicked_handle(self):
            e = events.PageItemResizeEvent
            self.signals.on_pageItem_resize_event.emit(e(type=e.defaultType.recover, center=e.centertype.viewcenter))
            pass

        def on_widget_button_fullscreen_clicked_handle(self):
            pass

        def on_widget_button_prev_clicked_handle(self):
            e = events.PageItemAddToSceneEvent
            if self.pageinfo.pagenum > 0:
                modifiers = QApplication.keyboardModifiers()
                if modifiers & Qt.ControlModifier:
                    self.widget_button_next_prev_clicked(-1, e.defaultType.changePage)
                else:
                    self.widget_button_next_prev_clicked(-1, e.defaultType.addPage)

        def on_widget_button_next_clicked_handle(self):
            e = events.PageItemAddToSceneEvent
            if self.pageinfo.pagenum < len(fitz.Document(self.pageinfo.pdf_path)):
                modifiers = QApplication.keyboardModifiers()
                if modifiers & Qt.ControlModifier:
                    self.widget_button_next_prev_clicked(1, e.defaultType.changePage)
                else:
                    self.widget_button_next_prev_clicked(1, e.defaultType.addPage)

        def widget_button_next_prev_clicked(self, inc, addtype):
            pageinfo = objs.PageInfo(self.pageinfo.pdf_path, self.pageinfo.pagenum + inc, self.pageinfo.ratio)
            e = events.PageItemAddToSceneEvent
            self.signals.on_pageItem_addToScene.emit(e(type=addtype, data=pageinfo, sender=self))

        def on_widget_button_pageinfo_clicked_handle(self):
            # print("on_widget_button_pageinfo_clicked_handle")
            e = events.PagePickerOpenEvent
            self.root.on_pagepicker_open_handle(e(type=e.defaultType.fromPage, fromPageItem=self))
            # self.root.signals.on_pagepicker_PDFopen.emit(e(type=e.defaultType.fromPage,fromPageItem=self))

        def on_widget_button_close_clicked_handle(self):
            e = events.PageItemCloseEvent()
            e.pageitem = self
            self.signals.on_pageitem_close.emit(e)

        def boundingRect(self) -> QtCore.QRectF:
            w = self.pageview.boundingRect().width()
            h = self.pageview.boundingRect().height()
            rect = QRectF(0, 0, w, h)

            return rect

        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            self.prepareGeometryChange()  # 这个 非常重要. https://www.cnblogs.com/ybqjymy/p/13862382.html
            painter.setPen(QPen(QColor(127, 127, 127), 2.0, Qt.DashLine))
            painter.drawRect(self.boundingRect())
            width1 = self.toolsbar.boundingRect().width()

            width2 = self.pageview.boundingRect().width()
            height2 = self.pageview.boundingRect().height()
            self.toolsbar.setPos(width2 - width1, height2)
            # super().paint(painter,option,widget)

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            modifiers = QApplication.keyboardModifiers()
            if (modifiers & Qt.ControlModifier):
                if event.button() == Qt.LeftButton:
                    self.setFlag(QGraphicsItem.ItemIsMovable, True)
                    self.setFlag(QGraphicsItem.ItemIsSelectable, True)
                # if event.button() == Qt.RightButton:
                #     self.on_pageItem_clicked.emit(
                #         PageItemClickEvent(pageitem=self, eventType=PageItemClickEvent.ctrl_rightClickType))
            else:
                # self.toolsBar.setPos(event.pos())

                if event.buttons() == Qt.MidButton:
                    pass  # 本来这里有一个全屏功能,删掉了.
                elif event.button() == Qt.RightButton:  # 了解当前选中的是哪个pageitem,因为我之前已经取消了selectable功能,

                    e = events.PageItemClickEvent
                    # ALL.signals.on_pageItem_clicked.emit(e(sender=self, pageitem=self, eventType=e.rightClickType))
                    super().mousePressEvent(event)
                elif event.button() == Qt.LeftButton:
                    # self.on_pageItem_clicked.emit(
                    #     PageItemClickEvent(sender=self, pageitem=self, eventType=PageItemClickEvent.leftClickType))
                    # self.toolsBar.hide()
                    self.toolsbar.show()
                    super().mousePressEvent(event)

            super().mousePressEvent(event)

        def changepage(self, caller, data: "objs.PageInfo"):
            """事先加载好pixdir"""
            assert type(data) == objs.PageInfo
            funcs.caller_check(Clipper.changepage, caller, Clipper)
            self.png_path = funcs.pixmap_page_load(data.pdf_path, data.pagenum, data.ratio)
            self.pageview.setPixmap(QPixmap(self.png_path))
            self.pageinfo = data
            self.toolsbar.update_from_pageinfo(self)

        class PageView(QGraphicsPixmapItem):
            mousecenter = 0
            viewcenter = 1
            itemcenter = 2
            nocenter = 3

            def __init__(self, superior: "Clipper.PageItem" = None, root: "Clipper" = None, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.superior = superior
                self.root = root
                self.setPixmap(QPixmap(self.superior.png_path))
                self.setParentItem(self.superior)
                self.is_fullscreen = False
                self.setAcceptHoverEvents(True)
                self.mousecenter_pos = None
                self.mouse_item_percent_p: "objs.Position" = None  # 鼠标在图元中的比例位置
                self.mouse_item_old_abs_p: "QPointF" = None
                self.item_center_percent_p: "objs.Position" = None
                self.item_center_old_abs_p: "QPointF" = None
                self.view_center_scene_p: "QPoint" = None
                self.viewcenter_pos = None
                self.itemcenter_pos = None

            # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            #     print(f"event.pos={event.pos()},self.mapToScene(event.pos())={self.mapToScene(event.pos())}")
            #     super().mousePressEvent(event)

            def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                e = events.PageItemResizeEvent
                if not self.is_fullscreen:
                    self.is_fullscreen = True
                    self.superior.signals.on_pageItem_resize_event.emit(
                        e(type=e.defaultType.fullscreen, center=e.centertype.viewcenter))
                else:
                    self.is_fullscreen = False
                    self.superior.signals.on_pageItem_resize_event.emit(e(type=e.defaultType.recover))

            def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                self.mouse_center_pos_get(event.pos())
                super().hoverEnterEvent(event)

            def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                self.mouse_center_pos_get(event.pos())
                super().hoverMoveEvent(event)

            def wheelEvent(self, event):
                modifiers = QApplication.keyboardModifiers()  # 判断ctrl键是否按下
                if modifiers == QtCore.Qt.ControlModifier:
                    self.mouse_center_pos_get(event.pos())
                    # print(event.delta().__str__())
                    if event.delta() > 0:
                        self.zoomIn()
                    else:
                        self.zoomOut()
                else:
                    super().wheelEvent(event)

            def zoomIn(self):
                """放大"""
                self.zoom(self.superior.ratio * 1.1)

            def zoomOut(self):
                """缩小"""
                self.zoom(self.superior.ratio / 1.1)

            def mouse_center_pos_get(self, pos: QPointF):
                """
                1 指针所在图元的比例位置
                2 指针所在图元的绝对位置
                """
                self.mouse_item_percent_p = objs.Position(pos.x() / self.boundingRect().width(),
                                                          pos.y() / self.boundingRect().height())
                self.mouse_item_old_abs_p = pos

            def item_center_pos_get(self):
                self.item_center_percent_p = objs.Position(0.5, 0.5)
                self.item_center_old_abs_p = self.mapToScene(0.5 * self.boundingRect().width(),
                                                             0.5 * self.boundingRect().height())

            def view_center_pos_get(self):
                """
                获取视口中心对应的相对坐标的比例值
                Returns:

                """
                view = self.superior.superior
                view_center = QPoint(int(view.viewport().width() / 2), int(view.viewport().height() / 2))
                self.view_center_scene_p = view.mapToScene(view_center)

            def center_zoom(self, center=0):
                if center == self.mousecenter:
                    new_x = self.mouse_item_percent_p.x * self.boundingRect().width()
                    new_y = self.mouse_item_percent_p.y * self.boundingRect().height()
                    new_p = self.mapToScene(new_x, new_y)
                    dx = new_p.x() - self.mouse_item_old_abs_p.x()
                    dy = new_p.y() - self.mouse_item_old_abs_p.y()
                elif center == self.viewcenter:
                    # 获取放大后的中心坐标
                    new_x = self.item_center_percent_p.x * self.boundingRect().width()
                    new_y = self.item_center_percent_p.y * self.boundingRect().height()
                    # 转为场景坐标
                    new_p = self.mapToScene(new_x, new_y)
                    # 当前场景加上dx,dy就能移动到放大后的中心坐标
                    dx = new_p.x() - self.view_center_scene_p.x()
                    dy = new_p.y() - self.view_center_scene_p.y()
                self.superior.superior.safeScroll(dx, dy)
                pass

            def zoom(self, factor, center=None, needbase=True):
                if center is None:  # 默认是指针为中心放大
                    center = self.mousecenter
                if center == self.viewcenter:  # 视口中心放大,需要获取视口中心坐标
                    self.view_center_pos_get()
                    self.item_center_pos_get()
                if center == self.itemcenter:  # 图元中心放大,需要获取图元的中心
                    self.item_center_pos_get()
                """缩放
                :param factor: 缩放的比例因子
                """
                self.prepareGeometryChange()
                if factor < 0.07 or factor > 100:
                    # 防止过大过小
                    return
                pdf_path, pagenum, baseratio = self.path_page_ratio_get()
                factor2 = factor * baseratio if needbase else factor
                p = funcs.pixmap_page_load(pdf_path, pagenum, ratio=factor * baseratio)
                self.setPixmap(QPixmap(p))
                if center != self.nocenter:  # 只要不是 nocenter, 都要执行 center_zoom
                    self.center_zoom(center)

                # self.width = self.pixmap().width()
                # self.height = self.pixmap().height()
                # self.keep_clipbox_in_postion()

                self.superior.ratio = factor

            def boundingRect(self) -> QtCore.QRectF:
                return QtCore.QRectF(0, 0, self.pixmap().width(), self.pixmap().height())

            def path_page_ratio_get(self):
                pageinfo = self.superior.pageinfo
                return pageinfo.pdf_path, pageinfo.pagenum, pageinfo.ratio

            pass

        class ToolsBar(QGraphicsWidget):
            def __init__(self, superior: "Clipper.PageItem" = None, root: "Clipper" = None, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.superior = superior
                self.root = root
                self.imgdir = objs.SrcAdmin.imgDir
                self.setParentItem(self.superior)
                self.widget_button_close = QToolButton()
                self.widget_button_prev = QToolButton()
                self.widget_button_next = QToolButton()
                self.widget_button_recover = QToolButton()
                self.widget_button_fullscreen = QToolButton()
                self.widget_button_pageinfo = QToolButton()

                self.widgetdata_li = [self.widgetdata(*data) for data in [
                    (self.widget_button_close, self.imgdir.close, 0, 5, "关闭/close"),
                    (self.widget_button_next, self.imgdir.next, 0, 1,
                     "新建下一页/create next page to the view \n ctrl+click=改变当前页到下一页/Change the current page to the next"),
                    (self.widget_button_prev, self.imgdir.prev, 0, 0,
                     "新建上一页/create previous page to the view \n ctrl+click=改变当前页到上一页/Change the current page to the previous"),
                    (self.widget_button_recover, self.imgdir.reset, 0, 2, "重设大小/reset size"),
                    (self.widget_button_fullscreen, self.imgdir.expand, 0, 3, "全屏/fullscreen"),
                    (self.widget_button_pageinfo, None, 0, 4, "")
                ]]
                g = QGraphicsGridLayout(self)
                g.setSpacing(0.0)
                g.setContentsMargins(0.0, 0.0, 0.0, 0.0)
                self.widget_proxy_dict: "dict[QToolButton,QGraphicsProxyWidget]" = {}
                for data in self.widgetdata_li:
                    if data.imgdir:
                        data.widget.setIcon(QIcon(data.imgdir))
                    if data.tooltip != "":
                        data.widget.setToolTip(data.tooltip)
                    else:
                        data.widget.setStyleSheet(f"height:{self.widget_button_close.height() - 6}px")
                        self.update_from_pageinfo(self, needCheck=False)

                    self.widget_proxy_dict[data.widget] = QGraphicsProxyWidget(self)
                    self.widget_proxy_dict[data.widget].setContentsMargins(0.0, 0.0, 0.0, 0.0)
                    self.widget_proxy_dict[data.widget].setWidget(data.widget)
                    g.addItem(self.widget_proxy_dict[data.widget], data.x, data.y)
                self.setLayout(g)

            def update_from_pageinfo(self, caller, needCheck=True):
                if needCheck:
                    funcs.caller_check(Clipper.PageItem.changepage, caller, Clipper.PageItem)
                pdfname = funcs.str_shorten(os.path.basename(self.superior.pageinfo.pdf_path[:-4]))
                pdfpage = self.superior.pageinfo.pagenum
                DB = objs.SrcAdmin.DB.go(objs.SrcAdmin.DB.table_pdfinfo)
                pdfuuid = funcs.uuid_hash_make(self.superior.pageinfo.pdf_path)
                if DB.exists(uuid=pdfuuid):
                    offset = DB.select(uuid=pdfuuid).return_all().zip_up()[0]["offset"]
                else:
                    offset = 0
                bookpage = pdfpage + 1 - offset
                self.widget_button_pageinfo.setText(f"{pdfname} pdfpage={pdfpage},bookpage={bookpage}")
                self.widget_button_pageinfo.setToolTip(self.superior.pageinfo.pdf_path)

            def boundingRect(self) -> QtCore.QRectF:
                x, y = self.x(), self.y()
                w = 0
                for k, v in self.widget_proxy_dict.items():
                    w += v.boundingRect().width()
                h = self.widget_proxy_dict[self.widget_button_pageinfo].boundingRect().height()
                return QRectF(x, y, w, h)

            @dataclass
            class widgetdata:
                widget: "QToolButton"
                imgdir: "str"
                x: "int"
                y: "int"
                tooltip: "str"

            pass


        pass

    class ClipBox(QGraphicsRectItem):
        pass


class ScenePageLoader(QThread):
    on_1_page_load = pyqtSignal(object)

    def __init__(self, datali: "list[objs.PageInfo]"):
        super().__init__()
        self.datali = datali

    def run(self) -> None:
        total = len(self.datali)
        count = 0
        for data in self.datali:
            count += 1
            pixdir = funcs.pixmap_page_load(data.pdf_path, data.pagenum, data.ratio)
            self.on_1_page_load.emit(pageloaddata(pixdir, data, int(count / total * 100)))
            time.sleep(0.1)


pageloaddata = namedtuple("pageloaddata", "pixdir pageinfo progress")
