import time
from math import ceil
from typing import Union

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QIcon
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QWidget, QVBoxLayout, QLabel, \
    QCheckBox, QHBoxLayout, QGraphicsSceneMouseEvent, QGraphicsItem, QRubberBand, QStyleOptionGraphicsItem, \
    QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem, QApplication, QProgressBar, QToolButton
from PyQt5.QtCore import Qt, QRect, QSize, QRectF, QThread, pyqtSignal, QPointF, QPoint, QSizeF
from ..tools import objs, events, funcs, ALL


def frame_partition(cols_per_row, view_size: "QSize", shift_width, total_unit_num=1, _total_list=None) -> object:
    """

    Args:
        cols_per_row:
        view_size:
        total_unit_num:
        _total_list:

    Returns: unit_size, rows_per_frame, frame_list

    """
    total_list = _total_list if _total_list is not None else [None] * total_unit_num
    unit_size = int((view_size.width() - shift_width) / cols_per_row)
    rows_per_frame = int(view_size.height() / unit_size)
    units_per_frame = cols_per_row * rows_per_frame
    total_frame_count = ceil(len(total_list) / units_per_frame)
    frame_list = []
    for i in range(total_frame_count):
        frame_list.append(total_list[i * units_per_frame:min((i + 1) * units_per_frame, len(total_list))])
    return unit_size, rows_per_frame, frame_list

    pass


def setup_item(item_idx, row_per_frame=None, col_per_row=None, unit_size=None, frame_num=None,
               doc: "fitz.Document" = None,
               frame_list=None, need_positioning=True):
    pagenum = frame_num * row_per_frame * col_per_row + item_idx
    pixmap = funcs.pixmap_page_load(doc, pagenum)
    item = Item2(pixmap=pixmap, pagenum=pagenum, unit_size=unit_size)
    # 调整位置, 需要 x,y坐标
    X = (item_idx % col_per_row) * unit_size
    Y = (frame_num * row_per_frame + int(item_idx / col_per_row)) * unit_size

    item.setPos(X, Y)
    frame_list[frame_num][item_idx] = item
    return frame_list


def browser_pageinfo_make(frame_idx, frame_item_idx, row_per_frame, col_per_row, unit_size, show, focus):
    pagenum = frame_idx * row_per_frame * col_per_row + frame_item_idx
    d = {"frame_idx": frame_idx, "frame_item_idx": frame_item_idx,
         "pagenum": pagenum}
    X = (frame_item_idx % col_per_row) * unit_size
    Y = (frame_idx * row_per_frame + int(frame_item_idx / col_per_row)) * unit_size
    d["posx"] = X
    d["posy"] = Y
    d["show"] = show
    d["focus"] = focus
    return d


class ReLayoutJob(QThread):
    """用来布局与重新布局,每次只布局一个屏幕,也可以布局多个, 这个看参数里的pageitem数量决定"""
    on_job_begin = pyqtSignal()
    on_job_end = pyqtSignal()
    on_progress = pyqtSignal(int)
    on_1_job_done = pyqtSignal(object)
    on_framelist_done = pyqtSignal(object)
    on_1_frame_job_done = pyqtSignal(object)
    on_all_job_done = pyqtSignal()
    Top = 0
    Down = 1

    def __init__(self, select_list: "list[Item2]" = None, view_size: "Union[QSize,QSizeF]" = None,
                 unit_size: "int" = 100,
                 frame_list: "list[list[Item2]]" = None, total_list: "list[Item2]" = None,
                 frame_num_li: 'list[int]' = None,
                 col_per_row: "int" = 1,
                 start_pos=None, direction=None):
        super().__init__()
        self.select_list = select_list if select_list is not None else total_list
        self.total_list = total_list
        self.view_size = view_size
        self.frame_list = frame_list
        self.unit_size = unit_size
        self.col_per_row = col_per_row
        self.row_per_frame = None
        self.frame_num_li = frame_num_li
        self.start_pos = start_pos if start_pos is not None else QPoint()
        self.direction = direction if direction is not None else self.Down

    def run(self):
        self.on_job_begin.emit()
        if self.framelist is None:
            self.unit_size, self.row_per_frame, self.frame_list = frame_partition(
                self.col_per_row, self.view_size, _total_list=self.total_list
            )
            self.on_framelist_done.emit([self.col_per_row, self.row_per_frame, self.frame_list])
        self.selectlist[0].set_pixmap_scale(self.unit_size)
        for frame_idx in self.frame_num_li:
            for item_idx in range(len(self.frame_list[frame_idx])):
                self.layout_setup(item_idx, frame_idx)
                # self.on_progress.emit(int(item_idx / len(self.frame_list[frame_idx]) * 100))
            # self.on_progress.emit(100)
            self.on_1_frame_job_done.emit(self.frame_list[frame_idx])
        self.on_job_end.emit()

    def frame_partition(self):
        unit_w = self.unit_size
        unit_h = self.unit_size
        cols_per_row = int(self.view_size.width() / unit_w)
        rows_per_frame = int(self.view_size.height() / unit_h)
        units_per_frame = cols_per_row * rows_per_frame
        total_frame_count = ceil(len(self.total_list) / units_per_frame)
        frame_list = []
        for i in range(total_frame_count):
            frame_list.append(self.total_list[i * units_per_frame:min((i + 1) * units_per_frame, len(self.total_list))])
        return cols_per_row, rows_per_frame, frame_list

        pass

    def layout_setup(self, item_idx, frame_idx):
        item: "Item2" = self.frame_list[frame_idx][item_idx]
        item.set_pixmap_scale(self.unit_size)
        X = (item_idx % self.col_per_row) * self.unit_size
        Y = (frame_idx * self.row_per_frame + int(item_idx / self.col_per_row)) * self.unit_size
        item.setPos(X, Y)

        pass

    pass


class PageContinueLoadJob(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        pass


class PageInitLoadJob(QThread):
    """从 pdf 读取 页面转化为pageitem, 只在第一次读取pdf时启动"""
    on_job_begin = pyqtSignal()
    on_job_end = pyqtSignal()
    on_job_progress = pyqtSignal(int)
    on_1_page_loaded = pyqtSignal(object)
    on_1_frame_loaded = pyqtSignal(object)
    on_all_page_loaded = pyqtSignal(object)
    on_frame_partition_done = pyqtSignal(object)

    def __init__(self, doc=None,
                 browser: 'QWidget' = None, frame_idx=None, parent=None, select=True,
                 begin_page=0, focus=True):

        super().__init__(parent=parent)
        self.browser = browser
        self.doc = doc
        self.total_list: "list" = []
        self.unit_size: "int" = self.browser.unit_size
        self.view_size: "QSize" = self.browser.size()
        self.col_per_row: "int" = self.browser.col_per_row
        self.row_per_frame = self.browser.row_per_frame
        self.begin_page: "int" = begin_page if begin_page is not None else 0
        self.pageItemList = []
        self.shift_width = self.browser.scene_shift_width
        self.progress_count = 0
        self.subjob_queue = []
        self.frame_list = self.browser.frame_list
        self.focus = focus
        self.frame_idx = frame_idx
        self.select = select
        self.exc_time = 0.005
        pass

    def run(self) -> None:
        self.on_job_begin.emit()
        if self.frame_list is None:  # 如果为空则重建
            self.unit_size, self.row_per_frame, self.frame_list = frame_partition(
                self.col_per_row, self.view_size, self.shift_width, total_unit_num=len(self.doc))
            self.on_frame_partition_done.emit(
                [self.unit_size, self.row_per_frame, self.frame_list])

        main_frame_num = self.frame_idx if self.frame_idx is not None \
            else int(self.begin_page / (self.row_per_frame * self.col_per_row))
        if self.frame_list[main_frame_num][0] is None:  # 如果一帧的开头为空,说明还未初始化,需要初始化
            for frame_item_idx in range(len(self.frame_list[main_frame_num])):
                d = browser_pageinfo_make(main_frame_num, frame_item_idx, self.row_per_frame, self.col_per_row,
                                          self.unit_size, True, True)
                self.on_1_page_loaded.emit(d)
                self.on_job_progress.emit(int(frame_item_idx / len(self.frame_list[main_frame_num]) * 100))
                time.sleep(self.exc_time)
            self.on_job_progress.emit(100)
        # 无论做了什么, 都需要最终都要返回这个, 是否有选择啊,是否要聚焦啊,这里解决
        self.on_all_page_loaded.emit({"frame": self.frame_list[main_frame_num],
                                      "focus": self.focus, "select": self.select, "pagenum": self.begin_page})

        self.on_job_end.emit()
        pass

    def pageinfo_make(self, frame_idx, frame_item_idx, show, focus):
        pagenum = frame_idx * self.row_per_frame * self.col_per_row + frame_item_idx
        d = {"frame_idx": frame_idx, "frame_item_idx": frame_item_idx,
             "pagenum": pagenum}
        X = (frame_item_idx % self.col_per_row) * self.unit_size
        Y = (frame_idx * self.row_per_frame + int(frame_item_idx / self.col_per_row)) * self.unit_size
        d["posx"] = X
        d["posy"] = Y
        d["show"] = show
        d["focus"] = focus
        self.on_1_page_loaded.emit(d)
        self.progress_move_1()
        time.sleep(self.exc_time)

    def progress_move_1(self):
        self.progress_count += 1
        self.on_job_progress.emit(int(self.progress_count / len(self.doc) * 100 + 1))

    pass


class SelectedRect(QGraphicsRectItem):
    def __init__(self, target: 'QGraphicsItem' = None, rect=None):
        super().__init__(parent=target)
        self.setBrush(QBrush(QColor(81, 168, 220, 100)))
        self.setRect(target.boundingRect())


class Item2(QGraphicsPixmapItem):
    def __init__(self, parent=None, pixmap: "QPixmap" = None, pagenum=None, unit_size=None):
        super().__init__(parent=parent)
        self.hash = funcs.base64(int(time.time() * 100000000))
        self._pixmap = pixmap
        self.is_selected = False
        self.multi_select = False
        self.unit_size = unit_size
        self.setPixmap(pixmap.scaled(self.unit_size, self.unit_size, Qt.KeepAspectRatio))
        self.pagenum = pagenum
        self.pagenumtext = QGraphicsTextItem(parent=self)
        self.pagenumtext.setHtml(f"<div style='background-color:green;color:white;padding:2px;'>{self.pagenum}</div>")
        self.pagenumtext.setPos(0, 0)
        # self.pixmap = QGraphicsPixmapItem(pixmap)
        # self.setScale(unit_size/(max(self.pixmap().width(),self.pixmap().height())))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.init_events()

    def __lt__(self, other: "Item2"):
        return self.pagenum < other.pagenum

    def __eq__(self, other):
        return self.pagenum == other.pagenum

    def init_events(self):
        ALL.signals.on_pagepicker_browser_select.connect(
            self.on_pagepicker_browser_select_handle
        )
        pass

    def set_pixmap_scale(self, size=None):
        if self.boundingRect().width() != size:
            self.setPixmap(self._pixmap.scaled(size, size, Qt.KeepAspectRatio))
            self.unit_size = size
            self.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # self.show_selected_rect(self.isSelected())
        e = events.PagePickerBrowserSelectEvent
        if event.modifiers() == Qt.ControlModifier:
            self.multi_select = True
            ALL.signals.on_pagepicker_browser_select.emit(
                e(sender=self, item=self, eventType=e.multiSelectType))
        else:
            self.multi_select = False
            # 因为非多选,所以取消掉多选
            ALL.signals.on_pagepicker_browser_select.emit(e(sender=self, item=self))
            ALL.signals.on_pagepicker_browser_select.emit(
                e(sender=self, eventType=e.singleSelectType, item=self))
        e = events.PagePickerPreviewerReadPageEvent
        ALL.signals.on_pagepicker_preivewer_read_page.emit(
            e(sender=self, eventType=e.loadType, pagenum=self.pagenum))
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        e = events.PagePickerBrowserSelectSendEvent
        ALL.signals.on_pagepicker_browser_select_send.emit(
            e(sender=self, eventType=e.overWriteType, pagenumlist=[self.pagenum])
        )

    #
    def on_pagepicker_browser_select_handle(self, event: "events.PagePickerBrowserSelectEvent"):
        if event.Type == event.singleSelectType:
            if self == event.item:
                self.setSelected(True)
            else:
                self.setSelected(False)
        elif event.Type == event.multiSelectType:
            if self == event.item:
                self.multi_select = True
        elif event.Type == event.multiCancelType:
            self.multi_select = False
        elif event.Type == event.rubberbandType:
            rect = event.rubberBandRect
            pos = self.mapToScene(self.pos())
            itemrect = QRect(pos.x(), pos.y(), int(self.boundingRect().width()), int(self.boundingRect().height()))

            if rect.intersects(itemrect):
                self.multi_select = True
            else:
                self.multi_select = False

        self.show_selected_rect(self.is_selected or self.multi_select)

    #
    #
    def show_selected_rect(self, need: "bool"):
        if "selected_rect" not in self.__dict__:
            rect = None
            if self.unit_size is not None:
                unit_size = self.unit_size
                rect = QtCore.QRectF(0, 0, unit_size, unit_size)
            else:
                rect = QtCore.QRectF(0, 0, self.pixmap().width(),
                                     self.pixmap().height() + self.pagenumtext.boundingRect().height())
            self.selected_rect = SelectedRect(self, rect)
        if need:
            self.selected_rect.show()
        else:
            self.selected_rect.hide()

    def boundingRect(self) -> QtCore.QRectF:

        if self.unit_size is not None:
            unit_size = self.unit_size
            return QtCore.QRectF(0, 0, unit_size, unit_size)
        else:
            return QtCore.QRectF(0, 0, self.pixmap().width(),
                                 self.pixmap().height() + self.pagenumtext.boundingRect().height())

    def previewer_select_show(self):
        if self.scene() is not None and len(self.scene().selectedItems()) > 0 \
                and self.scene().selectedItems()[-1].pagenum == self.pagenum \
                and self.scene().browser.pagepicker.current_preview_pagenum != self.pagenum:
            ALL.signals.on_pagepicker_preivewer_read_page.emit(self.pagenum)

    #

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: QWidget) -> None:
        # self.prepareGeometryChange()
        super().paint(painter, option, widget)
        self.show_selected_rect(self.isSelected())

        #


class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.browser = parent
        self.init_events()

    def init_events(self):
        ALL.signals.on_pagepicker_browser_sceneClear.connect(
            self.on_pagepicker_browser_sceneClear_handle)
        ALL.signals.on_pagepicker_browser_select.connect(self.on_pagepicker_browser_select_handle)

    def on_pagepicker_browser_select_handle(self, event: "events.PagePickerBrowserSelectEvent"):
        if event.collectType == event.Type:
            pagenumlist = [page.pagenum for page in self.selectedItems()]
            pagenumlist.sort()
            print(pagenumlist)
            e = events.PagePickerBrowserSelectSendEvent
            ALL.signals.on_pagepicker_browser_select_send.emit(
                e(sender=self, eventType=e.appendType, pagenumlist=pagenumlist)
            )

    def on_pagepicker_browser_sceneClear_handle(self, event: "events.PagePickerBrowserSceneClear"):
        if event.Type == event.clearType:
            self.clear()

    #
    # def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     print(self.selectedItems())
    #     super().mouseMoveEvent(event)


class View(QGraphicsView):
    def __init__(self, parent=None, scene=None, browser=None):
        super().__init__(parent=parent)
        # self.setFixedWidth(580)
        self.browser = browser
        self.begin_dragband = False
        self.origin_pos = None
        self.wheel_event_last_item = 0
        self.paint_event_last_time = 0
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.mousePressed = False
        if scene is not None:
            self.setScene(scene)
        self.init_UI()
        self.init_events()

    def init_events(self):
        ALL.signals.on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)
        # self.rubberBandChanged.connect(self.on_rubberBandChanged_handle)

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        # self.centerOn(0,0)
        pass

    def init_UI(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.verticalScrollBar().setFixedWidth(10)
        self.verticalScrollBar().setStyleSheet("width:5px;")
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        # self.translate(-11,0)
        # print(f"view rect={self.rect()}")

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        now_time = time.time()
        if self.paint_event_last_time == 0:
            self.paint_event_last_time = now_time
        if now_time - self.paint_event_last_time >= 0.5 and not self.browser.PageLoadJob_isBussy:

            if event.rect().y() == 0:  # 向上
                self.frame_idx_update(0)
            else:  # 向下
                # print("向下")
                self.frame_idx_update(1)
            self.paint_event_last_time = now_time
        super().paintEvent(event)


    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """下拉上拉触发子线程加载"""
        if event.modifiers() == Qt.ControlModifier:
            if not self.browser.PageLoadJob_isBussy:
                if event.angleDelta().y() > 0 and self.browser.col_per_row > 1:
                    self.browser.col_per_row -= 1
                if event.angleDelta().y() < 0:
                    self.browser.col_per_row += 1
                e = events.PDFParseEvent
                # if frame_item_first is not None:
                height_per_frame = self.browser.row_per_frame * self.browser.unit_size
                count_per_frame = self.browser.row_per_frame * self.browser.col_per_row
                frame_item_first = int(self.mapToScene(self.pos()).y() / height_per_frame) * count_per_frame
                ALL.signals.on_pagepicker_PDFparse.emit(
                    e(sender=self, eventType=e.PDFInitParseType,
                      doc=self.browser.pagepicker.doc, pagenum=frame_item_first)
                )
        else:
            # print(f"view pos = {self.mapToScene(self.pos())}")
            if not self.browser.PageLoadJob_isBussy:
                if event.angleDelta().y() > 0:
                    self.frame_idx_update(0)
                if event.angleDelta().y() < 0:
                    self.frame_idx_update(1)
            super().wheelEvent(event)

    def frame_idx_update(self, goType=0):
        if self.browser.frame_list is None or self.browser.row_per_frame is None:
            return
        height_per_frame = self.browser.row_per_frame * self.browser.unit_size
        goUp = 0
        goDown = 1
        at_frame_idx = -1
        if goType == goUp:
            at_frame_idx = int(self.mapToScene(self.pos()).y() / height_per_frame)
        if goType == goDown:
            at_frame_idx = int(self.mapToScene(self.pos()).y() / height_per_frame)
            curr_frame_height_y = (at_frame_idx + 0.3) * height_per_frame
            # print(f"curr_frame_height_y={curr_frame_height_y},self.mapToScene(self.pos()).y()="
            #       f"{self.mapToScene(self.pos()).y()}")
            if curr_frame_height_y < self.mapToScene(self.pos()).y():
                at_frame_idx += 1
        if -1 < at_frame_idx < len(self.browser.pagepicker.doc) and self.browser.frame_list[at_frame_idx][0] is None:
            e = events.PDFParseEvent
            ALL.signals.on_pagepicker_PDFparse.emit(
                e(eventType=e.ScrollType, doc=self.browser.pagepicker.doc, frame_idx=at_frame_idx)
            )


class BottomBar(QWidget):
    """一个进度条，一个页面收集按钮"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.browser = parent
        self.progressBar = objs.GridHDescUnit(labelname="加载进度/loading", widget=QProgressBar())
        self.pick_page_button = QToolButton(self)
        self.init_UI()
        self.init_events()

    def init_UI(self):
        self.pick_page_button.setIcon(QIcon(objs.SrcAdmin.imgDir.download))
        self.pick_page_button.setToolTip("将选中的页码插入页码收集器\npick the selected pagenum and add to the page collector")
        H_layout = QHBoxLayout(self)
        H_layout.addWidget(self.progressBar)
        H_layout.addWidget(self.pick_page_button)
        H_layout.setStretch(0, 1)
        H_layout.setStretch(1, 0)
        self.setLayout(H_layout)

    def init_events(self):
        self.pick_page_button.clicked.connect(self.pick_page_button_clicked_handle)
        ALL.signals.on_pagepicker_browser_progress.connect(self.on_pagepicker_browser_progress_handle)

    def on_pagepicker_browser_progress_handle(self, value):
        self.progressBar.widget.setValue(value)

    def pick_page_button_clicked_handle(self):
        e = events.PagePickerBrowserSelectEvent
        ALL.signals.on_pagepicker_browser_select.emit(
            e(sender=self, eventType=e.collectType)
        )
        pass
