import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QSizeF
from PyQt5.QtGui import QPixmap, QIcon, QPainterPath, QColor, QPen, QBrush
from PyQt5.QtWidgets import QGraphicsItemGroup, QApplication, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, \
    QGraphicsItem, QGraphicsPixmapItem, QGraphicsWidget, QGraphicsLayout, QGraphicsGridLayout, QGraphicsLinearLayout, \
    QGraphicsLayoutItem, QWidget, QTextEdit, QGraphicsScene, QPushButton, QGraphicsProxyWidget, QLabel, QToolButton, \
    QGraphicsRectItem, QSizePolicy
from PyQt5 import QtGui
from ..tools.funcs import pixmap_page_load
from ..PageInfo import PageInfo
from . import PageItem_


class PageItem(QGraphicsItemGroup):
    """
        page_itself+PageToolsBar
    """
    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar'=None):
        super().__init__(parent=parent)
        QGraphicsWidget()
        # test = QGraphicsPixmapItem()
        # test.setHandlesChildEvents(False)
        self.rightsidebar = rightsidebar  # 指向的是主窗口的rightsidebar
        self.belongto_pagelist_row = None
        self.pageinfo = pageinfo
        self.pageview = PageItem_.Pixmap(pageinfo)
        self.page_tools_bar = PageItem_.ToolsBar2(pageinfo, pageitem=self)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setAcceptHoverEvents(True)
        self.addToGroup(self.pageview)
        self.addToGroup(self.page_tools_bar)
        self.init_position()

    def init_position(self):
        x = self.pageview.boundingRect().width() - self.page_tools_bar.boundingRect().width()
        y = self.pageview.boundingRect().height()
        self.page_tools_bar.setPos(x, y)
        self.page_tools_bar.update()
        self.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        """对于事件冒泡, 底层父item 接管了子item, 但是可以反向传播回去, 因此从这里开始分发事件
        setHandlesChildEvents 这玩意儿在pyqt5上好像消失了
        """
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.setCursor(Qt.CrossCursor)
            pos = self.scenePos()
            clipbox = PageItem_.ClipBox(pos=QPointF(event.pos().x() + pos.x(), event.pos().y() + pos.y()),
                                        pageitem=self)
            self.addToGroup(clipbox)
            clipbox.mousePressEvent(event)  # 必须把鼠标事件传递到子类，才能获取到在父类中的坐标
        # elif self.page_tools_bar.contains(event.pos()):
        #     print("clicked tools bar")
        #     self.page_tools_bar.mousePressEvent(event)
        else:
            super().mousePressEvent(event)
        pass

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()

        if self.pageview.contains(
                event.pos()) and modifiers == QtCore.Qt.ControlModifier and event.buttons() == Qt.LeftButton:
            # 此时在pageview上，而且按下ctrl，和左键
            print("ctrl+click+mouseMoveEvent")
        # elif self.page_tools_bar.contains(event.pos()):
        #     self.page_tools_bar.mouseMoveEvent(event)
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

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:

        if self.page_tools_bar.contains(event.pos()):
            self.page_tools_bar.hoverMoveEvent(event)
        super().hoverMoveEvent(event)


class PageItem5(QGraphicsItem):
    """
    """

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar' = None):
        super().__init__(parent=parent)
        QGraphicsWidget()
        self.clipBoxList = []
        self._delta = None
        self.rightsidebar = rightsidebar  # 指向的是主窗口的rightsidebar
        self.belongto_pagelist_row = None
        self.pageinfo = pageinfo
        self.pageview = PageItem_.Pixmap(pageinfo, pageitem=self)
        self.toolsBar = PageItem_.ToolsBar2(pageinfo, pageitem=self)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.init_toolsbar_position()

    def init_toolsbar_position(self):
        x = self.pageview.pixmap().width() - self.toolsBar.boundingRect().width()
        y = self.pageview.boundingRect().height()
        self.toolsBar.setPos(x, y)
        self.toolsBar.update()
        self.update()

    def boundingRect(self) -> QtCore.QRectF:
        w = self.pageview.pixmap().width()
        h = self.pageview.pixmap().height() + self.toolsBar.boundingRect().height()
        rect = QRectF(0, 0, w, h)
        return rect

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        self.prepareGeometryChange()  # 这个 非常重要. https://www.cnblogs.com/ybqjymy/p/13862382.html
        if self.isSelected():
            self.init_toolsbar_position()
            self.toolsBar.show()
        else:
            self.toolsBar.hide()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            clipbox = PageItem_.ClipBox2(parent_pos=event.pos(), pageitem=self)
            self.clipBoxList.append(clipbox)

    # #
    # def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #
    #     super().mouseMoveEvent(event)
    #
    # 不可以使用这个功能，
    # def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     super().mouseMoveEvent(event)


class PageItem4(QGraphicsRectItem):
    """clipbox,pagePixmap,toolsbar"""

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar' = None):
        super().__init__(parent=parent)
        self.rightsidebar = rightsidebar  # 指向的是主窗口的rightsidebar
        self.belongto_pagelist_row = None
        self.pageinfo = pageinfo
        self.Pixmap = PageItem_.Pixmap(pageinfo, pageitem=self)
        self.ToolsBar = PageItem_.ToolsBar2(pageinfo, pageitem=self)
        self.ToolsBar.setPos(self.Pixmap.pixmap().width() / 2 - self.ToolsBar.boundingRect().width() / 2,
                             self.Pixmap.pixmap().height())
        # item = QGraphicsRectItem(self.rect())
        # item.setParentItem(self)
        # self.rightsidebar.clipper.scene.addItem(item)

    def boundingRect(self) -> QtCore.QRectF:
        width = self.Pixmap.boundingRect().width()
        height = self.Pixmap.boundingRect().height() + self.ToolsBar.boundingRect().height()
        return QRectF(self.pos().x(), self.pos().y(), width, height)

    def shape(self) -> QtGui.QPainterPath:
        # print("reshape")
        path = QPainterPath()
        path.addRect(QRectF(self.Pixmap.pixmap().rect()))
        path.addRect(self.ToolsBar.boundingRect())
        return path

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:

        if self.isSelected():
            self.ToolsBar.setPos(self.Pixmap.pixmap().width() - self.ToolsBar.boundingRect().width(),
                                 self.Pixmap.pixmap().height())
            self.ToolsBar.show()
        else:
            self.ToolsBar.hide()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print("PDFitem mousePressEvent")
        print(event.pos())
        if self.contains(event.pos()):
            print(self.ItemIsMovable)
        super().mousePressEvent(event)


class PageItem3(QGraphicsRectItem):
    """clipbox,pagePixmap,toolsbar"""

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar' = None):
        super().__init__(parent=parent)
        self.rightsidebar = rightsidebar  # 指向的是主窗口的rightsidebar
        self.belongto_pagelist_row = None
        self.pageinfo = pageinfo
        self.Pixmap = PageItem_.Pixmap(pageinfo, pageitem=self)
        self.ToolsBar = PageItem_.ToolsBar2(pageinfo, pageitem=self)
        self.ToolsBar.setPos(self.Pixmap.pixmap().width() / 2 - self.ToolsBar.boundingRect().width() / 2,
                             self.Pixmap.pixmap().height())
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def boundingRect(self) -> QtCore.QRectF:
        width = self.Pixmap.boundingRect().width()
        height = self.Pixmap.boundingRect().height() + self.ToolsBar.boundingRect().height()
        return QRectF(self.pos().x(), self.pos().y(), width, height)

    def shape(self) -> QtGui.QPainterPath:
        # print("reshape")
        path = QPainterPath()
        path.addRect(QRectF(self.Pixmap.pixmap().rect()))
        path.addRect(self.ToolsBar.boundingRect())
        return path

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:

        if self.isSelected():
            self.ToolsBar.setPos(self.Pixmap.pixmap().width() - self.ToolsBar.boundingRect().width(),
                                 self.Pixmap.pixmap().height())
            self.ToolsBar.show()
        else:
            self.ToolsBar.hide()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print("PDFitem mousePressEvent")
        print(event.pos())
        if self.contains(event.pos()):
            print(self.ItemIsMovable)
        super().mousePressEvent(event)


class PageItem2(QGraphicsWidget):
    _delta = 0.1

    def __init__(self, pageinfo: 'PageInfo', parent=None, rightsidebar: 'RightSideBar' = None):
        super().__init__(parent=parent)
        self.pixmapRatio = 1
        self.clipBoxList = []
        self.pageinfo = pageinfo
        self.rightsidebar = rightsidebar
        self.pixmap = QLabel()
        self.pixmap.setPixmap(pageinfo.pagepixmap)
        self.pixmap.resize(self.pixmap.pixmap().width(), self.pixmap.pixmap().height())
        self.pageWidget = QGraphicsProxyWidget(self)
        self.pageWidget.setWidget(self.pixmap)
        self.toolsBar = PageItem_.ToolsBar2(pageinfo, pageitem=self)
        self.init_position()
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.init_layout()
        # self.draw_frame()

    def init_position(self):
        self.toolsBar.setPos(0, self.pageWidget.widget().height())

    def draw_frame(self):
        round = QGraphicsRectItem(QRectF(self.pageWidget.boundingRect()), parent=self)
        round.setPen(PageItem_.ClipBox_.FramePen())
        round.update()

    def init_layout(self):
        layout0 = QGraphicsGridLayout()
        layout0.setSpacing(0)
        layout0.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        layout0.addItem(self.pageWidget, 0, 0)
        layout0.addItem(self.toolsBar, 1, 0)
        self.setLayout(layout0)
        pass

    # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     """对于事件冒泡, 底层父item 接管了子item, 但是可以反向传播回去, 因此从这里开始分发事件
    #     setHandlesChildEvents 这玩意儿在pyqt5上好像消失了
    #     """
    #     modifiers = QApplication.keyboardModifiers()
    #     # ratioPoint = QPointF(event.pos().x()/self.rect().width(),event.pos().y()/self.rect().height())
    #
    #     if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
    #         self.setCursor(Qt.CrossCursor)
    #         pos = self.scenePos()
    #         clipbox = PageItem_.ClipBox2(pos=event.pos(), pageitem=self)
    #         self.clipBoxList.append(clipbox)
    #         # clipbox.setParentItem(self)
    #         # clipbox.mousePressEvent(event)
    #
    #     for i in self.clipBoxList:# 需要关闭子项的移动功能
    #         if not i.contains(event.pos()-i.pos()):
    #             # print(i.__str__()+"disabled move")
    #             i.setFlag(QGraphicsItem.ItemIsMovable, False)
    # def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
    #     self.pixmap.resize(self.pixmap.pixmap().size())
    #     self.pageWidget.resize(QSizeF(self.pixmap.size()))

    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers()  # 判断ctrl键是否按下

        if modifiers == QtCore.Qt.ControlModifier:
            # print(event.delta().__str__())
            if event.delta() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
        else:
            super().wheelEvent(event)

    def zoomIn(self):
        """放大"""
        self.pixmapRatio = self.pixmapRatio * (1 + self._delta)
        self.zoom(self.pixmapRatio)

    def zoomOut(self):
        """缩小"""
        self.pixmapRatio = self.pixmapRatio * (1 - self._delta)
        self.zoom(self.pixmapRatio)

    def zoom(self, factor):
        """缩放
        :param factor: 缩放的比例因子
        """
        if factor < 0.07 or factor > 100:
            # 防止过大过小
            return
        p = pixmap_page_load(self.pageinfo.doc, self.pageinfo.pagenum, factor)
        self.pixmap.setPixmap(p)
        self.pixmap.resize(self.pixmap.pixmap().size())
        self.pageWidget.resize(QSizeF(self.pixmap.size()))
        self.init_position()
        self.layout()
        self.update()

    # def boundingRect(self) -> QtCore.QRectF:
    #     w = self.pageWidget.rect().width()
    #     h = self.pageWidget.rect().height() + self.toolsBar.rect().height()
    #     return QtCore.QRectF(self.x(),self.y(),w,h)
