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

print, printer = funcs.logger(__name__)

class PageItem5(QGraphicsItem):
    """
    """

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar' = None, pageview_ratio=None):
        super().__init__(parent=parent)
        self.isFullscreen = False
        self.uuid = funcs.uuidmake()  # 仅需要内存级别的唯一性
        self.clipBoxList = []
        self._delta = None
        self.rightsidebar = rightsidebar  # 指向的是主窗口的rightsidebar 这个属性已经弃用
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
        width1 = self.toolsBar.boundingRect().width()

        width2 = self.pageview.boundingRect().width()
        height2 = self.pageview.boundingRect().height()
        self.toolsBar.setPos(width2 - width1, height2)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.setCursor(Qt.ArrowCursor)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier):
            if event.button() == Qt.LeftButton:
                self.setFlag(QGraphicsItem.ItemIsMovable, True)
                self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            if event.button() == Qt.RightButton:
                self.on_pageItem_clicked.emit(
                    PageItemClickEvent(pageitem=self, eventType=PageItemClickEvent.ctrl_rightClickType))
        else:
            # self.toolsBar.setPos(event.pos())

            if event.buttons() == Qt.MidButton:
                pass  # 本来这里有一个全屏功能,删掉了.
            elif event.button() == Qt.RightButton:  # 了解当前选中的是哪个pageitem,因为我之前已经取消了selectable功能,

                e = events.PageItemClickEvent
                ALL.signals.on_pageItem_clicked.emit(e(sender=self, pageitem=self, eventType=e.rightClickType))
                super().mousePressEvent(event)
            elif event.button() == Qt.LeftButton:
                self.on_pageItem_clicked.emit(
                    PageItemClickEvent(sender=self, pageitem=self, eventType=PageItemClickEvent.leftClickType))
                # self.toolsBar.hide()
                self.toolsBar.show()
                super().mousePressEvent(event)

        super().mousePressEvent(event)

    def toEvent(self):
        return PageItemAddToSceneEvent(pageItem=self, eventType=PageItemAddToSceneEvent.addPageType)
