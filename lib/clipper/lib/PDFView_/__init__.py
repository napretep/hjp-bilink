import time
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QSizeF
from PyQt5.QtGui import QPixmap, QIcon, QPainterPath, QColor, QPen, QBrush, QKeySequence
from PyQt5.QtWidgets import QGraphicsItemGroup, QApplication, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, \
    QGraphicsItem, QGraphicsPixmapItem, QGraphicsWidget, QGraphicsLayout, QGraphicsGridLayout, QGraphicsLinearLayout, \
    QGraphicsLayoutItem, QWidget, QTextEdit, QGraphicsScene, QPushButton, QGraphicsProxyWidget, QLabel, QToolButton, \
    QGraphicsRectItem, QSizePolicy, QGraphicsDropShadowEffect, QShortcut
from PyQt5 import QtGui
from ..tools.funcs import pixmap_page_load
from ..tools.objs import CustomSignals
from ..tools.events import PageItemAddToSceneEvent, PageItemClickEvent
from ..tools import events, objs, funcs
from ..PageInfo import PageInfo
from . import PageItem_


class PageItem5(QGraphicsItem):
    """
    """

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar' = None):
        super().__init__(parent=parent)
        self.isFullscreen = False
        self.hash = hash(time.time())
        self.clipBoxList = []
        self._delta = None
        self.rightsidebar = rightsidebar  # 指向的是主窗口的rightsidebar
        self.belongto_pagelist_row = None
        self.pageinfo = pageinfo
        self.pageview = PageItem_.PageView(pageinfo, pageitem=self)
        self.toolsBar = PageItem_.ToolsBar2(pageinfo, pageitem=self)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
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
        self.on_pageItem_clicked = CustomSignals.start().on_pageItem_clicked
        self.on_pageItem_resize_event = CustomSignals.start().on_pageItem_resize_event

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
                CustomSignals.start().on_pageItem_resize_event.emit(e(pageItem=self, eventType=e.fullscreenType))
                self.isFullscreen = True
            else:
                CustomSignals.start().on_pageItem_resize_event.emit(e(pageItem=self, eventType=e.resetType))
                self.isFullscreen = False

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            print("here")
        else:
            if event.button() == Qt.LeftButton:
                self.on_pageItem_clicked.emit(
                    PageItemClickEvent(pageitem=self, eventType=PageItemClickEvent.leftClickType))
                self.toolsBar.hide()
            if event.button() == Qt.RightButton:
                self.on_pageItem_clicked.emit(
                    PageItemClickEvent(pageitem=self, eventType=PageItemClickEvent.rightClickType))
                self.toolsBar.setPos(event.pos())
                self.toolsBar.show()
            super().mousePressEvent(event)

    def toEvent(self):
        return PageItemAddToSceneEvent(pageItem=self, eventType=PageItemAddToSceneEvent.addPageType)
