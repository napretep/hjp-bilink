import time
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QSizeF, QThread
from PyQt5.QtGui import QPixmap, QIcon, QPainterPath, QColor, QPen, QBrush, QKeySequence
from PyQt5.QtWidgets import QGraphicsItemGroup, QApplication, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, \
    QGraphicsItem, QGraphicsPixmapItem, QGraphicsWidget, QGraphicsLayout, QGraphicsGridLayout, QGraphicsLinearLayout, \
    QGraphicsLayoutItem, QWidget, QTextEdit, QGraphicsScene, QPushButton, QGraphicsProxyWidget, QLabel, QToolButton, \
    QGraphicsRectItem, QSizePolicy, QGraphicsDropShadowEffect, QShortcut, QGraphicsView
from PyQt5 import QtGui
from ..tools.funcs import pixmap_page_load
from ..tools.objs import CustomSignals
from ..tools.events import PageItemAddToSceneEvent, PageItemClickEvent
from ..tools import events, objs, funcs, ALL
from ..PageInfo import PageInfo
from . import PageItem_


class centerOn_job(QThread):
    def __init__(self, pageitem):
        super().__init__()
        self.pageitem = pageitem

    def run(self) -> None:
        time.sleep(0.01)
        e = events.PageItemResizeEvent
        type = e.fullscreenType
        if self.pageitem.isFullscreen:
            self.pageitem.isFullscreen = False
            type = e.resetType
        else:
            self.pageitem.isFullscreen = True
        ALL.signals.on_pageItem_resize_event.emit(
            e(pageItem=self.pageitem, eventType=type)
        )
        time.sleep(0.01)

class PageItem5(QGraphicsItem):
    """
    """

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar' = None, pageview_ratio=None):
        super().__init__(parent=parent)
        self.isFullscreen = False
        self.uuid = funcs.uuidmake()  # 仅需要内存级别的唯一性
        self.clipBoxList = []
        self._delta = None
        self.rightsidebar = rightsidebar  # 指向的是主窗口的rightsidebar
        self.pdfview = rightsidebar.clipper.pdfview
        self.belongto_pagelist_row = None
        self.pageinfo = pageinfo
        self.pageview = PageItem_.PageView(pageinfo, pageitem=self, ratio=pageview_ratio)
        self.toolsBar = PageItem_.ToolsBar2(pageinfo, pageitem=self)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.init_toolsbar_position()
        self.init_signals()

    def init_toolsbar_position(self):
        x = self.pageview.pixmap().width() - self.toolsBar.boundingRect().width()
        y = self.pageview.boundingRect().height()
        self.toolsBar.setPos(x, y)
        self.toolsBar.update()
        self.update()

    def init_signals(self):
        self.on_pageItem_clicked = ALL.signals.on_pageItem_clicked
        self.on_pageItem_resize_event = ALL.signals.on_pageItem_resize_event

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

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:

        modifiers = QApplication.keyboardModifiers()
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_E:
            e = events.PageItemResizeEvent
            if not self.isFullscreen:
                ALL.signals.on_pageItem_resize_event.emit(e(pageItem=self, eventType=e.fullscreenType))
                self.isFullscreen = True
            else:
                ALL.signals.on_pageItem_resize_event.emit(e(pageItem=self, eventType=e.resetType))
                self.isFullscreen = False

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.setCursor(Qt.ArrowCursor)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.pdfview.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier):
            if event.button() == Qt.LeftButton:
                self.setFlag(QGraphicsItem.ItemIsMovable, True)
                self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            if event.button() == Qt.RightButton:
                self.on_pageItem_clicked.emit(
                    PageItemClickEvent(pageitem=self, eventType=PageItemClickEvent.rightClickType))
                self.toolsBar.setPos(event.pos())
                self.toolsBar.show()
        else:
            if event.buttons() == Qt.MidButton:
                e = events.PageItemResizeEvent
                self.centerOn_job = centerOn_job(pageitem=self)
                self.centerOn_job.start()
            elif event.button() == Qt.RightButton:
                self.pdfview.curr_selected_item = self
                self.setCursor(Qt.CrossCursor)
                self.pdfview.setDragMode(QGraphicsView.RubberBandDrag)
                super().mousePressEvent(event)
            elif event.button() == Qt.LeftButton:
                self.on_pageItem_clicked.emit(
                    PageItemClickEvent(pageitem=self, eventType=PageItemClickEvent.leftClickType))
                self.toolsBar.hide()
                # if event.button() == Qt.RightButton:
                #     self.on_pageItem_clicked.emit(
                #         PageItemClickEvent(pageitem=self, eventType=PageItemClickEvent.rightClickType))
                #     self.toolsBar.setPos(event.pos())
                #     self.toolsBar.show()
                super().mousePressEvent(event)
        super().mousePressEvent(event)
    def toEvent(self):
        return PageItemAddToSceneEvent(pageItem=self, eventType=PageItemAddToSceneEvent.addPageType)
