from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QGraphicsItemGroup, QApplication, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, \
    QGraphicsItem, QGraphicsPixmapItem
from PyQt5 import QtGui

from ..PageInfo import PageInfo
from . import PageItem_

class PageItem(QGraphicsItemGroup):
    """
        page_itself+PageToolsBar
    """

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar'=None):
        super().__init__(parent=parent)
        self.setFiltersChildEvents(False)
        # test = QGraphicsPixmapItem()
        # test.setHandlesChildEvents(False)
        self.rightsidebar = rightsidebar #指向的是主窗口的rightsidebar
        self.belongto_pagelist_row=None
        self.pageinfo = pageinfo
        self.pageview = PageItem_.Pixmap(pageinfo)
        self.page_tools_bar = PageItem_.ToolsBar(pageinfo, pageitem=self)
        self.addToGroup(self.pageview)
        self.addToGroup(self.page_tools_bar)
        self.init_position()

    def init_position(self):
        x = self.pageview.boundingRect().width() / 2 - self.page_tools_bar.boundingRect().width() / 2
        y = self.pageview.boundingRect().height()
        self.page_tools_bar.setPos(x, y)
        self.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """对于事件冒泡, 底层父item 接管了子item, 但是可以反向传播回去, 因此从这里开始分发事件
        setHandlesChildEvents 这玩意儿在pyqt5上好像消失了
        """
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.setCursor(Qt.CrossCursor)
            clipbox = PageItem_.ClipBox(pos=event.pos(), pageitem=self)
            self.addToGroup(clipbox)
        # elif self.clipbox.contains(event.pos()):
        #     self.clipbox.mousePressEvent(event)
        elif self.page_tools_bar.contains(event.pos()):
            self.page_tools_bar.mousePressEvent(event)
        else:
            super().mousePressEvent(event)
        pass

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            print("")
        else:
            super().mouseMoveEvent(event)
        pass

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)
        pass

    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.setCursor(Qt.SizeFDiagCursor)
            self.pageview.wheelEvent(event)
            self.init_position()
        else:
            super().wheelEvent(event)
        pass

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Control:
            self.setCursor(Qt.ArrowCursor)

    def boundingRect(self) -> QtCore.QRectF:
        width = self.pageview.boundingRect().width() if self.pageview.boundingRect().width() > \
                                                        self.page_tools_bar.boundingRect().width() else \
            self.page_tools_bar.boundingRect().width()
        height = self.pageview.boundingRect().height()
        return QRectF(self.pageview.x(), self.pageview.y(), width, height)

