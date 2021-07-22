import time
import traceback
from math import ceil
from typing import Union

from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QIcon
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsProxyWidget, QWidget, QVBoxLayout, QLabel, \
    QCheckBox, QHBoxLayout, QGraphicsSceneMouseEvent, QGraphicsItem, QRubberBand, QStyleOptionGraphicsItem, \
    QGraphicsPixmapItem, QGraphicsTextItem, QGraphicsRectItem, QApplication, QProgressBar, QToolButton
from PyQt5.QtCore import Qt, QRect, QSize, QRectF, QThread, pyqtSignal, QPointF, QPoint, QSizeF
from ..tools import objs, events, funcs, ALL

print, debugger = funcs.logger(logname=__name__)
from ..PDFView_ import PageItem5
from ..PageInfo import PageInfo


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


#
# def setup_item(item_idx, row_per_frame=None, col_per_row=None, unit_size=None, frame_num=None,
#                doc: "fitz.Document" = None,
#                frame_list=None, need_positioning=True):
#     pagenum = frame_num * row_per_frame * col_per_row + item_idx
#     pixmap = funcs.pixmap_page_load(doc, pagenum)
#     item = Item2(pixmap=pixmap, pagenum=pagenum, unit_size=unit_size)
#     # 调整位置, 需要 x,y坐标
#     X = (item_idx % col_per_row) * unit_size
#     Y = (frame_num * row_per_frame + int(item_idx / col_per_row)) * unit_size
#
#     item.setPos(X, Y)
#     frame_list[frame_num][item_idx] = item
#     return frame_list


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
        if self.frame_list is None:
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


# class PageInitLoadJob(QThread):
#     """从 pdf 读取 页面转化为pageitem, 只在第一次读取pdf时启动"""
#     on_job_begin = pyqtSignal()
#     on_job_end = pyqtSignal()
#     on_job_progress = pyqtSignal(int)
#     on_1_page_loaded = pyqtSignal(object)
#     on_1_frame_loaded = pyqtSignal(object)
#     on_all_page_loaded = pyqtSignal(object)
#     on_frame_partition_done = pyqtSignal(object)
#
#     def __init__(self, doc=None,
#                  browser: 'QWidget' = None, frame_idx=None, parent=None, select=True,
#                  begin_page=0, focus=True):
#
#         super().__init__(parent=parent)
#         self.browser = browser
#         self.doc = doc
#         self.total_list: "list" = []
#         self.unit_size: "int" = self.browser.unit_size
#         self.view_size: "QSize" = self.browser.size()
#         self.col_per_row: "int" = self.browser.col_per_row
#         self.row_per_frame = self.browser.row_per_frame
#         self.begin_page: "int" = begin_page if begin_page is not None else 0
#         self.pageItemList = []
#         self.shift_width = self.browser.scene_shift_width
#         self.progress_count = 0
#         self.subjob_queue = []
#         self.frame_list = self.browser.frame_list
#         self.focus = focus
#         self.frame_idx = frame_idx
#         self.select = select
#         self.exc_time = 0.005
#         pass
#
#     def run(self) -> None:
#         try:
#             self.on_job_begin.emit()
#             if self.frame_list is None:  # 如果为空则重建
#                 self.unit_size, self.row_per_frame, self.frame_list = frame_partition(
#                     self.col_per_row, self.view_size, self.shift_width, total_unit_num=len(self.doc))
#                 self.on_frame_partition_done.emit(
#                     [self.unit_size, self.row_per_frame, self.frame_list])
#
#             main_frame_num = self.frame_idx if self.frame_idx is not None \
#                 else int(self.begin_page / (self.row_per_frame * self.col_per_row))
#             if self.frame_list[main_frame_num][0] is None:  # 如果一帧的开头为空,说明还未初始化,需要初始化
#                 for frame_item_idx in range(len(self.frame_list[main_frame_num])):
#                     d = browser_pageinfo_make(main_frame_num, frame_item_idx, self.row_per_frame, self.col_per_row,
#                                               self.unit_size, True, True)
#                     self.on_1_page_loaded.emit(d)
#                     self.on_job_progress.emit(int(frame_item_idx / len(self.frame_list[main_frame_num]) * 100))
#                     time.sleep(self.exc_time)
#                 self.on_job_progress.emit(100)
#             # 无论做了什么, 都需要最终都要返回这个, 是否有选择啊,是否要聚焦啊,这里解决
#             self.on_all_page_loaded.emit({"frame": self.frame_list[main_frame_num],
#                                           "focus": self.focus, "select": self.select, "pagenum": self.begin_page})
#
#             self.on_job_end.emit()
#         except Exception as e:
#             print(traceback.format_exc()+"\n"+e.__str__())
#         pass
#
#     def pageinfo_make(self, frame_idx, frame_item_idx, show, focus):
#         pagenum = frame_idx * self.row_per_frame * self.col_per_row + frame_item_idx
#         d = {"frame_idx": frame_idx, "frame_item_idx": frame_item_idx,
#              "pagenum": pagenum}
#         X = (frame_item_idx % self.col_per_row) * self.unit_size
#         Y = (frame_idx * self.row_per_frame + int(frame_item_idx / self.col_per_row)) * self.unit_size
#         d["posx"] = X
#         d["posy"] = Y
#         d["show"] = show
#         d["focus"] = focus
#         self.on_1_page_loaded.emit(d)
#         self.progress_move_1()
#         time.sleep(self.exc_time)
#
#     def progress_move_1(self):
#         self.progress_count += 1
#         self.on_job_progress.emit(int(self.progress_count / len(self.doc) * 100 + 1))
#
#     pass


class SelectedRect(QGraphicsRectItem):
    def __init__(self, target: 'QGraphicsItem' = None, rect=None):
        super().__init__(parent=target)
        self.setBrush(QBrush(QColor(81, 168, 220, 100)))
        self.setRect(target.boundingRect())


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


class Item2(QGraphicsPixmapItem):
    def __init__(self, parent=None, pixmap: "QPixmap" = None, pagenum=None, unit_size=None, browser=None):
        super().__init__(parent=parent)
        self.browser = browser
        self.uuid = funcs.uuidmake()  # 仅需要内存级别的唯一性
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
        # self.pixmap = QGraphicsPixmapItem(pixmap)
        # self.setScale(unit_size/(max(self.pixmap().width(),self.pixmap().height())))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.__event = {
            ALL.signals.on_pagepicker_browser_select: self.on_pagepicker_browser_select_handle

        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()

    def __lt__(self, other: "Item2"):
        return self.pagenum < other.pagenum

    def __eq__(self, other):
        return self.pagenum == other.pagenum

    # def init_events(self):
    #     ALL.signals.on_pagepicker_browser_select.connect(
    #         self.on_pagepicker_browser_select_handle
    #     )
    #     pass

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
            ALL.signals.on_pagepicker_browser_select.emit(e(sender=self, item=self, eventType=e.multiSelectType))

        else:
            self.multi_select = False
            # 因为非多选,所以取消掉多选
            ALL.signals.on_pagepicker_browser_select.emit(e(sender=self, item=self))
            ALL.signals.on_pagepicker_browser_select.emit(e(sender=self, eventType=e.singleSelectType, item=self))

        e = events.PagePickerPreviewerReadPageEvent
        ALL.signals.on_pagepicker_preivewer_read_page.emit(e(sender=self, eventType=e.loadType, pagenum=self.pagenum))

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        # e = events.PagePickerBrowserSelectSendEvent
        # ALL.signals.on_pagepicker_browser_select_send.emit(
        #     e(sender=self, eventType=e.overWriteType, pagenumlist=[self.pagenum])
        # )
        e = events.PageItemAddToSceneEvent
        PDFpath = self.browser.doc.name
        pagenum = self.pagenum
        ratio = self.browser.pagepicker.ratio_value_get()
        item = PageInfo(PDFpath, pagenum, ratio=ratio)
        if self.browser.pagepicker.frompageitem is not None:
            ALL.signals.on_pageItem_changePage.emit(
                events.PageItemChangeEvent(pageInfo=item, pageItem=self.browser.pagepicker.frompageitem,
                                           eventType=events.PageItemChangeEvent.updateType)
            )
            pass
        else:
            pageitem = PageItem5(item)
            ALL.signals.on_pageItem_addToScene.emit(
                e(sender=self, eventType=e.addMultiPageType, pageItemList=[pageitem]))
        self.browser.pagepicker.close()
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



class Scene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.browser = parent
        self.__event = {
            ALL.signals.on_pagepicker_browser_sceneClear: self.on_pagepicker_browser_sceneClear_handle,
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()
        self.itemlist = []

    # def init_events(self):
    #     ALL.signals.on_pagepicker_browser_sceneClear.connect(
    #         self.on_pagepicker_browser_sceneClear_handle)
    #     ALL.signals.on_pagepicker_browser_select.connect(self.on_pagepicker_browser_select_handle)

    # def on_pagepicker_browser_select_handle(self, event: "events.PagePickerBrowserSelectEvent"):
    #     if event.collectType == event.Type:
    #         pagenumlist = [page.pagenum for page in self.selectedItems()]
    #         pagenumlist.sort()
    #         e = events.PagePickerBrowserSelectSendEvent
    #         ALL.signals.on_pagepicker_browser_select_send.emit(
    #             e(sender=self, eventType=e.appendType, pagenumlist=pagenumlist)
    #         )
    #         print(pagenumlist)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        e = events.PagePickerBrowserSelectSendEvent
        ALL.signals.on_pagepicker_browser_select_send.emit(e(pagenumlist=self.selected_item_pagenum()))

    def on_pagepicker_browser_sceneClear_handle(self, event: "events.PagePickerBrowserSceneClear"):
        if event.Type == event.clearType:
            self.clear()

    def addItem(self, item):
        self.itemlist.append(item)
        super().addItem(item)

    def clear(self):
        # list(map(lambda item:ALL.signals.on_pagepicker_browser_select.disconnect(item.on_pagepicker_browser_select_handle),
        #          self.itemlist))
        super().clear()

    def selected_item_pagenum(self):
        return sorted([page.pagenum for page in self.selectedItems()])

    #
    # def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     print(self.selectedItems())
    #     super().mouseMoveEvent(event)


class View(QGraphicsView):
    scrollUp = 0
    scrollDown = 1

    def __init__(self, parent=None, scene=None):
        super().__init__(parent=parent)
        # self.setFixedWidth(580)
        self.browser = parent
        self.begin_dragband = False
        self.origin_pos = None
        self.wheel_event_last_item = 0
        self.paint_event_last_time = 0
        self.setDragMode(QGraphicsView.RubberBandDrag)  # rubberband自带选中item的功能,所以没有任何调整.
        self.mousePressed = False
        if scene is not None:
            self.setScene(scene)
        self.init_UI()
        self.event_dict = {
            ALL.signals.on_pagepicker_PDFparse: self.on_pagepicker_PDFparse_handle
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()


    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        # self.centerOn(0,0)
        pass

    def init_UI(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setStyleSheet("width:5px;")
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        # self.translate(-11,0)
        # print(f"view rect={self.rect()}")

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        now_time = time.time()
        if self.paint_event_last_time == 0:
            self.paint_event_last_time = now_time
        if now_time - self.paint_event_last_time >= 0.1:
            self.frame_idx_change_check(self.scrollUp)
            self.paint_event_last_time = now_time
        super().paintEvent(event)


    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """下拉上拉触发子线程加载"""
        if event.modifiers() == Qt.ControlModifier:
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
                if event.angleDelta().y() > 0:  # 千万别再错了
                    self.frame_idx_change_check(self.scrollUp)
                if event.angleDelta().y() < 0:
                    self.frame_idx_change_check(self.scrollDown)
            super().wheelEvent(event)

    def frame_idx_change_check(self, scrollDir):
        if self.browser.frame_list is None or self.browser.row_per_frame is None:
            return
        height_per_frame = self.browser.row_per_frame * self.browser.unit_size
        at_frame_idx = int(self.mapToScene(self.pos()).y() / height_per_frame)  # 向上滚很容易解释
        if scrollDir == self.scrollDown:
            at_frame_idx = int(self.mapToScene(self.pos()).y() / height_per_frame)
            curr_frame_height_y = (at_frame_idx + 0.3) * height_per_frame
            # print(f"curr_frame_height_y={curr_frame_height_y},self.mapToScene(self.pos()).y()="
            #       f"{self.mapToScene(self.pos()).y()}")
            if curr_frame_height_y < self.mapToScene(self.pos()).y():
                at_frame_idx += 1
        # print(f"at_frame_idx={at_frame_idx},curr_frame_idx={self.browser.curr_frame_idx}")
        if len(self.browser.frame_list) > at_frame_idx > -1 and at_frame_idx != self.browser.curr_frame_idx:
            # e= events.PagePickerBrowserFrameChangedEvent
            # ALL.signals.on_pagepicker_browser_frame_changed.emit(
            #     e(sender=self,eventType=e.FrameChangedType,frame_idx=at_frame_idx)
            # )
            e = events.PDFParseEvent
            ALL.signals.on_pagepicker_PDFparse.emit(e(eventType=e.ScrollType, frame_idx=at_frame_idx, sender=self))
            self.browser.curr_frame_idx = at_frame_idx


class BottomBar(QWidget):
    """一个进度条，一个页面收集按钮"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.browser = parent
        self.progressBar = objs.ProgressBarBlackFont(
            self)  # objs.GridHDescUnit(labelname="加载进度/loading", widget=QProgressBar())
        # self.pick_page_button = QToolButton(self)
        self.init_UI()
        self.event_dict = {
            # self.pick_page_button.clicked:(self.pick_page_button_clicked_handle),
            # ALL.signals.on_pagepicker_browser_progress:(self.on_pagepicker_browser_progress_handle)
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def init_UI(self):
        # self.pick_page_button.setIcon(QIcon(objs.SrcAdmin.imgDir.download))
        # self.pick_page_button.setToolTip("将选中的页码插入页码收集器\npick the selected pagenum and add to the page collector")
        self.progressBar.setFormat("任务完成/task complete %p%")
        H_layout = QHBoxLayout(self)

        H_layout.addWidget(self.progressBar)
        # H_layout.addWidget(self.pick_page_button)
        H_layout.setStretch(0, 1)
        H_layout.setStretch(1, 0)
        self.setLayout(H_layout)

    def on_pagepicker_browser_progress_handle(self, value):
        self.progressBar.widget.setValue(value)

    #
    # def pick_page_button_clicked_handle(self):
    #     e = events.PagePickerBrowserSelectEvent
    #     ALL.signals.on_pagepicker_browser_select.emit(
    #         e(sender=self, eventType=e.collectType)
    #     )
    #     pass

    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     self.all_event.unbind(self.__class__.__str__())
