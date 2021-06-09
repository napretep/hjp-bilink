import os
import typing
from functools import reduce

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF, QRectF, Qt, QSizeF, QLineF
from PyQt5.QtGui import QPixmap, QBrush, QColor, QPen, QPainter, QIcon, QPainterPath
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QApplication, QGraphicsTextItem, QGraphicsItem, \
    QGraphicsRectItem, QWidget, QGraphicsWidget, QGraphicsLinearLayout, QLabel, QLineEdit, QGraphicsProxyWidget, \
    QGraphicsGridLayout, QToolButton, QGraphicsAnchorLayout, QComboBox

from ...tools.funcs import pixmap_page_load, str_shorten
from ...tools.objs import CustomSignals, PagePicker
from ...tools.events import PageItemDeleteEvent, PagePickerEvent, PageItemChangeEvent, PageItemResizeEvent
from ...PageInfo import PageInfo
from . import ClipBox_


class PageItem_ClipBox_Event:
    def __init__(self, clipbox=None, cardhash=None):
        self.clipbox = clipbox
        self.cardhash = cardhash


class ClipBox2(QGraphicsRectItem):
    """
    一个矩形,拖拽按钮,

    """
    default_height = 50.0
    TopLeft = 1
    TopMiddle = 2
    TopRight = 3
    MiddleLeft = 4
    MiddleRight = 5
    BottomLeft = 6
    BottomMiddle = 7
    BottomRight = 8
    handlerCursors = {
        TopLeft: Qt.SizeFDiagCursor,
        TopMiddle: Qt.SizeVerCursor,
        TopRight: Qt.SizeBDiagCursor,
        MiddleLeft: Qt.SizeHorCursor,
        MiddleRight: Qt.SizeHorCursor,
        BottomLeft: Qt.SizeBDiagCursor,
        BottomMiddle: Qt.SizeVerCursor,
        BottomRight: Qt.SizeFDiagCursor,
    }
    handlerSize = 15

    def __init__(self, *args, parent_pos: QPointF = None, pageview: 'PageView' = None, card_id: str = "0",
                 QA: str = "Q"):
        super().__init__(*args)
        # 规定自身
        self.QA = QA
        self.last_delta = None
        self.now_delta = None
        # self.setPos(0,0) #默认赋值为0,因此不必设置
        self.pageview = pageview
        self.setRect(
            # 0,0,
            parent_pos.x() - self.default_height / 2, parent_pos.y() - self.default_height / 2,
            self.default_height * 6, self.default_height * 2)
        self.birthPos = QPointF(self.rect().x(), self.rect().y())
        self.birthRect = QRectF(self.rect())
        self.setParentItem(pageview)
        self.handlers = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.ratioTop = None
        self.ratioLeft = None
        self.ratioBottom = None
        self.ratioRight = None
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        # self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges,True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.init_toolsbar()
        self.init_handlers()

    # "./resource/icon_close_button.png"
    def init_toolsbar(self):
        """卡片选择,QA切换,输入栏,关闭"""
        self.toolsbar = ClipBox_.ToolsBar(cardlist=self.pageview.pageitem.rightsidebar.cardlist, clipbox=self,
                                          QA=self.QA)

    def init_handlers(self):
        """八个方向都要有一个方块"""
        s = self.handlerSize
        b = self.rect()
        # 这些都是拖拽块
        self.handlers[self.TopLeft] = QRectF(b.left() - s + 1, b.top() - s + 1, s, s)
        self.handlers[self.TopMiddle] = QRectF(b.center().x() - s / 2, b.top() - s + 1, s, s)
        self.handlers[self.TopRight] = QRectF(b.right(), b.top() - s + 1, s, s)
        self.handlers[self.MiddleLeft] = QRectF(b.left() - s + 1, b.center().y() - s / 2, s, s)
        self.handlers[self.MiddleRight] = QRectF(b.right() - 1, b.center().y() - s / 2, s, s)
        self.handlers[self.BottomLeft] = QRectF(b.left() - s + 1, b.bottom(), s, s)
        self.handlers[self.BottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom(), s, s)
        self.handlers[self.BottomRight] = QRectF(b.right(), b.bottom(), s, s)

    def handlerAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handlers.items():
            if v.contains(point):
                print(f"{str(k)} clicked")
                return k
        return None

    def boundingRect(self) -> QtCore.QRectF:
        s = self.handlerSize
        return self.rect().adjusted(-s, -s, s, s)

    def init_toolsbar_size(self):
        if self.isSelected():
            self.toolsbar.setPos(self.rect().x() + 1, self.rect().y() + 1)
            self.toolsbar.lineEditProxy.resize(self.rect().width() - self.toolsbar.editQAButtonProxy.rect().width() - 1,
                                               self.toolsbar.lineEditProxy.rect().height())

            l = self.toolsbar.lineEditProxy
            eQ = self.toolsbar.editQAButtonProxy
            c = self.toolsbar.closeButtonProxy
            Q = self.toolsbar.QAButtonProxy
            C = self.toolsbar.cardComboxProxy
            r = self.rect()
            l.setPos(0, r.height() - l.rect().height())
            eQ.setPos(l.rect().right() - 1, r.height() - l.rect().height())
            c.setPos(r.width() - c.rect().width() - 1, 0)
            Q.setPos(r.width() - c.rect().width() - Q.rect().width() - 1, 0)
            C.setPos(0, 0)
            self.toolsbar.cardComboxProxy.resize(
                self.rect().width() - c.rect().width() - Q.rect().width() - 1,
                Q.rect().height() - 1
            )
            C.update()

            self.toolsbar.show()
        else:
            self.toolsbar.hide()

    def shape(self):
        """
        shape在boundingRect里面
        """
        path = QPainterPath()
        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handlers.values():
                path.addRect(shape)
        return path

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        # self.prepareGeometryChange()  # 这个 非常重要. https://www.cnblogs.com/ybqjymy/p/13862382.html
        self.calc_ratio()
        painter.setBrush(QBrush(QColor(255, 0, 0, 0)))
        painter.setPen(QPen(QColor(127, 127, 127), 2.0, Qt.DashLine))
        painter.drawRect(self.rect())
        self.init_toolsbar_size()

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(81, 168, 220, 200)))
        painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        if self.isSelected():
            self.init_handlers()
            for handle, rect in self.handlers.items():
                painter.drawRect(rect)
        self.move_bordercheck()
        self.prepareGeometryChange()

        # def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

    def resize_bordercheck(self, toX=None, toY=None):
        """根据是否越界进行一个边界的修正，超出边界就用边界的值代替"""
        X, Y = None, None
        if toX is not None:
            X = toX if self.leftBorder < toX + self.pos().x() < self.rightBorder \
                else self.rightBorder - self.pos().x() if toX + self.pos().x() >= self.rightBorder \
                else self.leftBorder - self.pos().x()
        if toY is not None:
            Y = toY if self.topBorder < toY + self.pos().y() < self.bottomBorder \
                else self.bottomBorder - self.pos().y() if toY + self.pos().y() >= self.bottomBorder \
                else self.topBorder - self.pos().y()
        return X, Y

    def move_bordercheck(self):
        """根据是否越界进行一个边界的修正，超出边界就用边界的值代替,同样必须用父类来检测边界"""
        rect = self.rect()
        x, y = self.pos().x(), self.pos().y()
        view_left = 0
        view_top = 0
        view_right = self.pageview.boundingRect().width()
        view_bottom = self.pageview.boundingRect().height()
        top = rect.top() + y
        bottom = rect.bottom() + y
        left = rect.left() + x
        right = rect.right() + x
        if top < view_top:
            print("over top")
            rect.translate(0, view_top - top)
        if left < view_left:
            print("over left")
            rect.translate(view_left - left, 0)
        if view_bottom < bottom:
            print("over bottom")
            rect.translate(0, view_bottom - bottom)
        if view_right < right:
            print("over right")
            rect.translate(view_right - right, 0)
        self.setRect(rect)

    def onResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        pageview: 'pageview' = self.pageview
        MAXRect = pageview.boundingRect()  # 外边界

        offset = self.handlerSize
        boundingRect = self.boundingRect()
        rect = self.rect()
        diff = QPointF(0, 0)

        self.prepareGeometryChange()

        if self.handleSelected == self.TopLeft:
            # 左上角的范围
            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            # 全部换算成pageview中的坐标,公式 :pageviewpos = selfpos+rectpos
            self.rightBorder = rect.x() + self.pos().x() + rect.width() - 2 * offset
            self.leftBorder = MAXRect.x() - offset
            self.topBorder = MAXRect.y() - offset
            self.bottomBorder = rect.y() + self.pos().y() + rect.height() - 2 * offset
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()

            finalX, finalY = self.resize_bordercheck(toX=toX, toY=toY)

            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(finalX)
            boundingRect.setTop(finalY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.TopMiddle:

            fromY = self.mousePressRect.top()
            toY = fromY + mousePos.y() - self.mousePressPos.y()

            self.topBorder = MAXRect.y() - offset
            self.bottomBorder = rect.y() + self.pos().y() + rect.height() - 2 * offset
            finalX, finalY = self.resize_bordercheck(toY=toY)

            diff.setY(toY - fromY)
            boundingRect.setTop(finalY)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.TopRight:

            self.rightBorder = MAXRect.x() + MAXRect.width() + offset
            self.leftBorder = rect.x() + self.pos().x() + 2 * offset
            self.topBorder = MAXRect.y() - offset
            self.bottomBorder = rect.y() + self.pos().y() + rect.height() - 2 * offset

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            finalX, finalY = self.resize_bordercheck(toX=toX, toY=toY)

            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(finalX)
            boundingRect.setTop(finalY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.MiddleLeft:
            self.leftBorder = MAXRect.left() - offset
            self.rightBorder = rect.right() + self.pos().x() - 2 * offset
            fromX = self.mousePressRect.left()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            finalX, finalY = self.resize_bordercheck(toX=toX)
            diff.setX(toX - fromX)
            boundingRect.setLeft(finalX)
            rect.setLeft(boundingRect.left() + offset)
            self.setRect(rect)

        elif self.handleSelected == self.MiddleRight:
            self.leftBorder = rect.left() + self.pos().x() + 2 * offset
            self.rightBorder = MAXRect.right() + offset
            fromX = self.mousePressRect.right()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            finalX, finalY = self.resize_bordercheck(toX=toX)
            diff.setX(toX - fromX)
            boundingRect.setRight(finalX)
            rect.setRight(boundingRect.right() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.BottomLeft:
            self.leftBorder = MAXRect.left() - offset
            self.rightBorder = rect.right() + self.pos().x() - 2 * offset
            self.topBorder = rect.top() + self.pos().y() + 2 * offset
            self.bottomBorder = MAXRect.bottom() + offset

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            finalX, finalY = self.resize_bordercheck(toX=toX, toY=toY)
            boundingRect.setLeft(finalX)
            boundingRect.setBottom(finalY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.BottomMiddle:
            self.topBorder = rect.top() + self.pos().y() + 2 * offset
            self.bottomBorder = MAXRect.bottom() + offset
            fromY = self.mousePressRect.bottom()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            finalX, finalY = self.resize_bordercheck(toY=toY)

            boundingRect.setBottom(finalY)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        elif self.handleSelected == self.BottomRight:
            self.leftBorder = rect.left() + self.pos().x() + 2 * offset
            self.rightBorder = MAXRect.right() + offset
            self.topBorder = rect.top() + self.pos().y() + 2 * offset
            self.bottomBorder = MAXRect.bottom() + offset
            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            finalX, finalY = self.resize_bordercheck(toX=toX, toY=toY)
            boundingRect.setRight(finalX)
            boundingRect.setBottom(finalY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.setRect(rect)

        self.init_handlers()

    def calc_ratio(self):
        """记录上下左右所处的坐标系的比例，方便放大缩小跟随"""
        max_X, max_Y = self.pageview.boundingRect().right(), self.pageview.boundingRect().bottom()
        fix_x, fix_y = self.pos().x(), self.pos().y()
        top, left, right, bottom = self.rect().top(), self.rect().left(), self.rect().right(), self.rect().bottom()
        self.ratioTop = (top + fix_y) / max_Y
        self.ratioLeft = (left + fix_x) / max_X
        self.ratioBottom = (bottom + fix_y) / max_Y
        self.ratioRight = (right + fix_x) / max_X

    def borderUpdate(self):
        """边界取自父类pageview的边界,是坐标"""
        self.leftBorder = 0
        self.topBorder = 0
        self.rightBorder = self.leftBorder + self.pageview.pixmap().width()
        self.bottomBorder = self.topBorder + self.pageview.pixmap().height()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.handleSelected = self.handlerAt(event.pos())
        self.mousePressRect = self.rect()
        self.mousePressSelfPos = self.pos()
        if self.handleSelected:
            self.mousePressPos = event.pos()
            event.accept()
        # super().mousePressEvent(event)
        # print(f"clipboxpos={event.pos()}")

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """

        self.borderUpdate()

        if self.handleSelected is not None:
            self.onResize(mouseEvent.pos())
        else:
            super().mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        super().mouseReleaseEvent(mouseEvent)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.update()


class PageView(QGraphicsPixmapItem):
    """只需要pixmap就够了"""

    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem5' = None):
        super().__init__(pageinfo.pagepixmap)
        self.clipBoxList: 'list[ClipBox2]' = []
        self.pageinfo = pageinfo
        self.pageitem = pageitem
        self.setParentItem(pageitem)
        self.init_signals()
        self.init_events()
        self._delta = 0.1
        self.ratio = 1
        self.width = self.pixmap().width()

        # self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def init_signals(self):
        self.on_clipbox_closed = CustomSignals.start().on_clipbox_closed
        self.on_pageItem_clipbox_added = CustomSignals.start().on_pageItem_clipbox_added
        self.on_pageItem_changePage = CustomSignals.start().on_pageItem_changePage
        self.on_pageItem_resize_event = CustomSignals.start().on_pageItem_resize_event

    def init_events(self):
        self.on_clipbox_closed.connect(self.pageview_clipbox_remove)
        self.on_pageItem_changePage.connect(self.on_pageItem_changePage_handle)
        self.on_pageItem_resize_event.connect(self.on_pageItem_resize_event_handle)

    def on_pageItem_resize_event_handle(self, event: "PageItemResizeEvent"):
        print("here")
        if event.pageItem.hash == self.pageitem.hash:
            if event.eventType == PageItemResizeEvent.fullscreenType:
                self.zoom(self.view_divde_page_ratio())
            if event.eventType == PageItemResizeEvent.resetType:
                self.zoom(1)
            # self.setX(self.pageitem.rightsidebar.clipper.pdfview.viewport())

    def view_divde_page_ratio(self):
        view_Width = self.pageitem.rightsidebar.clipper.pdfview.geometry().width()
        pixwidth = self.pageinfo.pagepixmap.width()
        ratio = view_Width / pixwidth
        return ratio

    def on_pageItem_changePage_handle(self, event: 'PageItemChangeEvent'):
        if event.eventType == event.updateType and event.pageItem.hash == self.pageitem.hash:
            self.pageinfo_read(event.pageInfo)
            self.update()
            self.pageitem.update()

    def pageinfo_read(self, pageinfo):
        self.pageinfo = pageinfo
        self.setPixmap(pageinfo.pagepixmap)

    def add_round(self):
        round = QGraphicsRectItem(QRectF(self.pixmap().rect()), parent=self)
        round.setPen(ClipBox_.FramePen())
        round.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.pageview_clipbox_add(event.pos())

        # print(f"pixmap_pos={event.pos()}")
        print(self.pageitem.zValue())
        super().mousePressEvent(event)

    def pageview_clipbox_add(self, pos):
        """顺带解决"""
        QA = self.pageitem.rightsidebar.get_QA()
        clipbox = ClipBox2(parent_pos=pos, pageview=self, QA=QA)
        _hash = clipbox.toolsbar.cardComboxProxy.currentData
        self.clipBoxList.append(clipbox)  # 创建后必须添加到clipboxlist
        self.on_pageItem_clipbox_added.emit(PageItem_ClipBox_Event(clipbox=clipbox, cardhash=_hash))

    def pageview_clipbox_remove(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        """这里要做的事情就是从clipBoxList中移除"""
        clipbox = event.clipBox
        if clipbox in self.clipBoxList:  # 有可能来自其他page的信号
            self.clipBoxList.remove(clipbox)

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
        self.ratio = self.ratio * (1 + self._delta)
        self.zoom(self.ratio)

    def zoomOut(self):
        """缩小"""
        self.ratio = self.ratio / (1 + self._delta)
        self.zoom(self.ratio)

    def zoom(self, factor):
        """缩放
        :param factor: 缩放的比例因子
        """
        if factor < 0.07 or factor > 100:
            # 防止过大过小
            return
        p = pixmap_page_load(self.pageinfo.doc, self.pageinfo.pagenum, ratio=factor * self.pageinfo.ratio)
        self.setPixmap(p)
        w, h = self.boundingRect().width(), self.boundingRect().height()
        for box in self.clipBoxList:
            r = box.rect()
            x, y = box.x(), box.y()
            r.setTop(box.ratioTop * h - y)
            r.setLeft(box.ratioLeft * w - x)
            r.setBottom(box.ratioBottom * h - y)
            r.setRight(box.ratioRight * w - x)  # 之所以减原来的x,y可行,是因为图片的放大并不是膨胀放大,每个点都是原来的点,只是增加了一些新的点而已.
            box.setRect(r)
        self.update()

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.x(), self.y(), self.pixmap().width(), self.pixmap().height())

    pass


class ToolsBar2(QGraphicsWidget):
    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem' = None):
        super().__init__(parent=pageitem)
        self.pageinfo = pageinfo
        self.pageitem = pageitem
        self.Control_pressed = False
        self.setParentItem(pageitem)
        self.init_UI()
        self.init_signals()
        self.init_events()

    def add_round(self):
        round = QGraphicsRectItem(QRectF(self.pixmap().rect()), parent=self)
        round.setPen(ClipBox_.FramePen())
        round.update()

    def init_UI(self):
        L_layout = QGraphicsGridLayout()
        L_layout.setSpacing(0.0)
        L_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        # L_layout = QGraphicsAnchorLayout()
        nameli = ["button_close", "button_prevpage", "button_nextpage", "button_reset", "button_fullscreen",
                  "button_pageinfo"]
        self.widgetLi = nameli
        pngli = ["./resource/icon_close_button.png", "./resource/icon_prev_button.png",
                 "./resource/icon_next_button.png", "./resource/icon_reset.png", "./resource/icon_fullscreen.png", ""]
        tipli = ["关闭/close", "上一页/previous page \n ctrl+click=新建上一页/create previous page to the view",
                 "下一页/next page \n ctrl+click=新建下一页/create next page to the view", "重设大小/reset size", "全屏/fullscreen",
                 f"""{self.pageinfo.doc.name}"""]
        handleli = [self.on_button_close_clicked_handle, self.on_button_prevpage_clicked_handle,
                    self.on_button_nextpage_clicked_handle, self.on_button_reset_clicked_handle,
                    self.on_button_fullscreen_clicked_handle, self.on_button_pageinfo_clicked_handle]

        buttons_dict = {}
        orderli = [5, 1, 2, 3, 4, 0]
        for i in range(6):
            buttons_dict[nameli[i]] = QToolButton()
            if pngli[i] != "":
                buttons_dict[nameli[i]].setIcon(QIcon(pngli[i]))
            else:
                buttons_dict[nameli[i]].setText(
                    str_shorten(os.path.basename(self.pageinfo.doc.name)) + ", page=" + str(self.pageinfo.pagenum))
            buttons_dict[nameli[i]].clicked.connect(handleli[i])
            buttons_dict[nameli[i]].setToolTip(tipli[i])
            self.__dict__[nameli[i]] = QGraphicsProxyWidget()
            self.__dict__[nameli[i]].setContentsMargins(0.0, 0.0, 0.0, 0.0)
            self.__dict__[nameli[i]].setWidget(buttons_dict[nameli[i]])
        for i in range(6):
            L_layout.addItem(self.__dict__[nameli[i]], 0, orderli[i])
        self.button_pageinfo.widget().setStyleSheet(f"height:{self.button_close.widget().height() - 6}px")
        self.setLayout(L_layout)

    def update_from_pageinfo(self, pageinfo):
        self.pageinfo = pageinfo
        p: 'QGraphicsProxyWidget' = self.__dict__["button_pageinfo"]
        q: 'QToolButton' = p.widget()
        q.setToolTip(self.pageinfo.doc.name)
        q.setText(str_shorten(os.path.basename(self.pageinfo.doc.name)) + ", page=" + str(self.pageinfo.pagenum))
        p.update()

    def init_signals(self):
        self.on_pageItem_removeFromScene = CustomSignals.start().on_pageItem_removeFromScene
        self.on_pageItem_addToScene = CustomSignals.start().on_pageItem_addToScene
        self.on_pageItem_changePage = CustomSignals.start().on_pageItem_changePage
        self.on_pageItem_resize_event = CustomSignals.start().on_pageItem_resize_event

    def init_events(self):
        self.on_pageItem_changePage.connect(self.on_pageItem_changePage_handle)
        self.on_pageItem_resize_event.connect(self.on_pageItem_resize_event_handle)

    def on_button_fullscreen_clicked_handle(self):
        self.on_pageItem_resize_event.emit(
            PageItemResizeEvent(pageItem=self.pageitem, eventType=PageItemResizeEvent.fullscreenType)
        )

    def on_pageItem_resize_event_handle(self, event):
        self.update()

    def on_pageItem_changePage_handle(self, event: 'PageItemChangeEvent'):
        if event.pageItem.hash == self.pageitem.hash:
            self.update_from_pageinfo(event.pageInfo)

    def on_button_reset_clicked_handle(self):
        self.on_pageItem_resize_event.emit(
            PageItemResizeEvent(pageItem=self.pageitem, eventType=PageItemResizeEvent.resetType)
        )
        pass

    def on_button_nextpage_clicked_handle(self):
        print("next clicked")

        if self.pageinfo.pagenum + 1 == len(self.pageinfo.doc):
            return
        modifiers = QApplication.keyboardModifiers()
        self._on_button_prev_next_page_handle(modifiers, self.pageinfo.doc.name, self.pageinfo.pagenum + 1)

    def on_button_prevpage_clicked_handle(self):
        print("prev clicked")
        if self.pageinfo.pagenum - 1 == -1:
            return
        modifiers = QApplication.keyboardModifiers()
        self._on_button_prev_next_page_handle(modifiers, self.pageinfo.doc.name, self.pageinfo.pagenum - 1)
        pass

    def _on_button_prev_next_page_handle(self, modifiers, docname, pagenum):
        if modifiers == QtCore.Qt.ControlModifier:
            from .. import PageItem5
            pageitem = PageItem5(PageInfo(docname, pagenum=pagenum),
                                 rightsidebar=self.pageitem.rightsidebar)
            self.on_pageItem_addToScene.emit(PagePickerEvent(pageItem=pageitem, eventType=PagePickerEvent.addPageType))
        else:
            pageinfo = PageInfo(docname, pagenum=pagenum)
            self.on_pageItem_changePage.emit(
                PageItemChangeEvent(pageInfo=pageinfo, pageItem=self.pageitem,
                                    eventType=PageItemChangeEvent.updateType))

    def on_button_close_clicked_handle(self):
        self.on_pageItem_removeFromScene.emit(
            PageItemDeleteEvent(pageItem=self.pageitem, eventType=PageItemDeleteEvent.deleteType))

    def on_button_pageinfo_clicked_handle(self):
        p = PagePicker(pdfDirectory=self.pageinfo.doc.name, frompageitem=self.pageitem,
                       pageNum=self.pageinfo.pagenum, clipper=self.pageitem.rightsidebar.clipper)
        p.exec()
        pass

    def boundingRect(self) -> QtCore.QRectF:
        x, y = self.x(), self.y()
        w = 0
        for i in self.widgetLi:
            w += self.__dict__[i].rect().width()
        h = self.__dict__[self.widgetLi[-1]].rect().height()
        return QRectF(x, y, w, h)
