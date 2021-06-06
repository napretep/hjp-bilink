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
from ...PageInfo import PageInfo
from . import ClipBox_


class ClipBox(QGraphicsItemGroup):
    """
    由三个部分构成:Frame,ToolsBar,EditLine
    """

    def __init__(self, pos: QPointF = None, pageitem: 'PageItem' = None, card_id: str = "0", QA: str = "Q"):
        super().__init__()
        self._pos=pos
        self.pageitem=pageitem
        self.card_id=card_id
        self.QA=QA

        self.frame = ClipBox_.Frame()
        self.addToGroup(self.frame)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        # self.setPos(self._pos)

    def boundingRect(self) -> QtCore.QRectF:
        return self.frame.boundingRect()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.pageitem.pageWidget.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.setPos(event.pos() - QPointF(self.frame.begindelta / 2, self.frame.begindelta / 2))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)


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

    def __init__(self, *args, parent_pos: QPointF = None, pageview: 'pageview' = None, card_id: str = "0",
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
            self.default_height * 6, self.default_height)
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
        self.toolsbar = ClipBox_.ToolsBar(model=self.pageview.pageitem.rightsidebar.cardlist.model, clipbox=self,
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
            self.toolsbar.lineEdit.resize(self.rect().width() - self.toolsbar.editQAButtonProxy.rect().width() - 1,
                                          self.toolsbar.lineEdit.height())

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
            self.toolsbar.cardCombox.resize(
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
        # boundingrect 在静止不动的时候可用，当移动 的时候无法表现他的位置。
        # print(f"clipbox.boundingRect={self.boundingRect()},pageview.boundingRect={self.pageitem.pageview.boundingRect()}")
        # 经过实验表明，pos和boundingRect的left,top不相等
        pos = QPointF(self.pageview.boundingRect().left(), self.pageview.boundingRect().top())
        # print(f"pos={self.birthPos.x()-self.pos().x()} boundingRect={self.boundingRect()}, rect={self.rect()}")
        # print(f"pos={self.birthPos + self.pos()} ") # 这是在pageview中,如果不拉伸框架下的坐标,需要升级到左上顶点坐标
        # print(f"{self.rect()},{self.pos()}")
        self.borderUpdate()
        # print(self.pos())
        # leftBorder = self.pageview.boundingRect().x()
        # rightBorder = leftBorder+ self.pageview.boundingRect().width()
        # topBorder = self.pageview.boundingRect().y()
        # bottomBorder =topBorder+ self.pageview.boundingRect().height()
        # print(f"onResize2,mouspos={mouseEvent.pos()},pos={self.pos()},rect={self.rect()}")

        # if leftBorder < self.left < rightBorder and topBorder<self.top<bottomBorder and \
        #     leftBorder < self.right < rightBorder and topBorder < self.bottom < bottomBorder:
        #     # self.setFlag(QGraphicsItem.ItemIsMovable, True)
        #     print("movable")
        # else:
        #
        #     # self.setFlag(QGraphicsItem.ItemIsMovable, False)
        #     print("not movable")

        if self.handleSelected is not None:
            self.onResize(mouseEvent.pos())
        else:
            # self.move_bordercheck()
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


class pageview(QGraphicsPixmapItem):
    """只需要pixmap就够了"""

    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem' = None):
        super().__init__(pageinfo.pagepixmap)
        self.clipBoxList: 'list[ClipBox2]' = []
        self.pageinfo = pageinfo
        self.pageitem = pageitem
        self.setParentItem(pageitem)
        self._delta = 0.1
        self.ratio = 1
        self.width = self.pixmap().width()

        # self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def add_round(self):
        round = QGraphicsRectItem(QRectF(self.pixmap().rect()), parent=self)
        round.setPen(ClipBox_.FramePen())
        round.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.add_clipbox(event.pos())
        print(f"pixmap_pos={event.pos()}")
        super().mousePressEvent(event)

    def add_clipbox(self, pos):
        """"""
        QA = self.pageitem.rightsidebar.get_QA()
        clipbox = ClipBox2(parent_pos=pos, pageview=self, QA=QA)
        self.clipBoxList.append(clipbox)

    def remove_clipbox(self, clipbox: 'ClipBox2'):
        if clipbox in self.clipBoxList:
            self.clipBoxList.remove(clipbox)
        self.pageitem.rightsidebar.clipper.scene.removeItem(clipbox)
        del clipbox
        print(self.childItems())

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
        self.ratio = self.ratio * (1 - self._delta)
        self.zoom(self.ratio)

    def zoom(self, factor):
        """缩放
        :param factor: 缩放的比例因子
        """
        if factor < 0.07 or factor > 100:
            # 防止过大过小
            return
        p = pixmap_page_load(self.pageinfo.doc, self.pageinfo.pagenum, factor)
        self.setPixmap(p)
        self.update()
        w, h = self.boundingRect().width(), self.boundingRect().height()
        for box in self.clipBoxList:
            r = box.rect()
            x, y = box.x(), box.y()
            r.setTop(box.ratioTop * h - y)
            r.setLeft(box.ratioLeft * w - x)
            r.setBottom(box.ratioBottom * h - y)
            r.setRight(box.ratioRight * w - x)  # 之所以减原来的x,y可行,是因为图片的放大并不是膨胀放大,每个点都是原来的点,只是增加了一些新的点而已.
            box.setRect(r)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.x(), self.y(), self.pixmap().width(), self.pixmap().height())

    pass


class ToolsBar2(QGraphicsWidget):
    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem' = None):
        super().__init__(parent=pageitem)
        self.pageinfo = pageinfo
        self.pageitem = pageitem
        self.setParentItem(pageitem)
        self.init_UI()
        # self.add_round()

    def add_round(self):
        round = QGraphicsRectItem(QRectF(self.pixmap().rect()), parent=self)
        round.setPen(ClipBox_.FramePen())
        round.update()

    def init_UI(self):
        L_layout = QGraphicsGridLayout()
        L_layout.setSpacing(0.0)
        L_layout.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        # L_layout = QGraphicsAnchorLayout()
        nameli = ["button_close", "button_prevpage", "button_nextpage", "button_zoomin", "button_zoomout", "label_desc"]
        self.widgetLi = nameli
        pngli = ["./resource/icon_close_button.png", "./resource/icon_prev_button.png",
                 "./resource/icon_next_button.png", "./resource/icon_zoom_in.png", "./resource/icon_zoom_out.png", ""]
        tipli = ["关闭/close", "上一页/previous page \n ctrl+click=新建上一页/create previous page to the view",
                 "下一页/next page \n ctrl+click=新建下一页/create next page to the view", "缩小/zoom out", "放大/zoom in",
                 f"""{self.pageinfo.doc.name}"""]
        label_dict = {}
        orderli = [5, 1, 2, 3, 4, 0]
        for i in range(6):
            label_dict[nameli[i]] = QToolButton()
            if pngli[i] != "":
                label_dict[nameli[i]].setIcon(QIcon(pngli[i]))
            else:
                label_dict[nameli[i]].setText(
                    str_shorten(os.path.basename(self.pageinfo.doc.name)) + ", page=" + str(self.pageinfo.pagenum))
            label_dict[nameli[i]].setToolTip(tipli[i])
            self.__dict__[nameli[i]] = QGraphicsProxyWidget()
            self.__dict__[nameli[i]].setContentsMargins(0.0, 0.0, 0.0, 0.0)
            self.__dict__[nameli[i]].setWidget(label_dict[nameli[i]])
        for i in range(6):
            L_layout.addItem(self.__dict__[nameli[i]], 0, orderli[i])
        self.label_desc.widget().setStyleSheet(f"height:{self.button_close.widget().height() - 6}px")
        self.setLayout(L_layout)

    def boundingRect(self) -> QtCore.QRectF:
        x, y = self.x(), self.y()
        w = 0
        for i in self.widgetLi:
            w += self.__dict__[i].rect().width()
        h = self.__dict__[self.widgetLi[-1]].rect().height()
        return QRectF(x, y, w, h)


from . import ToolsBar_


class ToolsBar(QGraphicsItemGroup):
    """一个pageitem要含有的item:
        item_of_tools:{
            closebutton,
            QAswitchbutton,
            cardswitchbutton,
            rect_point,
            nextpage_button,
            prevpage_button,
            input_field,
            zoomin,
            zoomout
        }"""

    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem' = None):
        super().__init__()
        self.setAcceptHoverEvents(True)
        self.pageitem = pageitem
        self.pageinfo = pageinfo
        self.init_UI()

    def init_item(self):
        self.button_close = ToolsBar_.PixmapItem(QPixmap("./resource/icon_close_button.png").scaled(25, 25))
        self.button_nextpage = ToolsBar_.PixmapItem(QPixmap("./resource/icon_next_button.png").scaled(25, 25))
        self.button_prevpage = ToolsBar_.PixmapItem(QPixmap("./resource/icon_prev_button.png").scaled(25, 25))
        self.button_zoomin = ToolsBar_.PixmapItem(QPixmap("./resource/icon_zoom_in.png").scaled(25, 25))
        self.button_zoomout = ToolsBar_.PixmapItem(QPixmap("./resource/icon_zoom_out.png").scaled(25, 25))
        self.label_desc = QGraphicsTextItem()

    def config_item(self):
        self.button_close.setToolTip("关闭/close")
        self.button_zoomin.setToolTip("放大/zoom in")
        self.button_zoomout.setToolTip("缩小/zoom out")
        self.button_prevpage.setToolTip("下一页/previous page \n ctrl+click=新建下一页/create previous page to the view")
        self.button_nextpage.setToolTip("下一页/next page \n ctrl+click=新建下一页/create next page to the view")
        self.label_desc.setToolTip(self.pageinfo.doc.name)

    def group_add_item(self):
        self.addToGroup(self.button_zoomin)
        self.addToGroup(self.button_zoomout)
        self.addToGroup(self.button_prevpage)
        self.addToGroup(self.button_nextpage)
        self.addToGroup(self.button_close)
        self.addToGroup(self.label_desc)

    def init_UI(self):
        self.init_item()
        self.config_item()
        self.group_add_item()

        p = self.pos()
        self.button_zoomin.setPos(p)
        p = p + QPointF(self.button_zoomin.boundingRect().width() + 10, 0)
        self.button_zoomout.setPos(p)
        p = p + QPointF(self.button_zoomout.boundingRect().width() + 10, 0)
        self.button_prevpage.setPos(p)
        p = p + QPointF(self.button_prevpage.boundingRect().width() + 10, 0)
        self.button_nextpage.setPos(p)
        p = p + QPointF(self.button_nextpage.boundingRect().width() + 10, 0)
        self.button_close.setPos(p)
        self.width = p.x() + self.button_close.boundingRect().width()
        self.height = self.button_zoomin.boundingRect().height()
        self.label_desc.setPos(QPointF(0, self.height))
        self.height += self.label_desc.boundingRect().height()
        PDFname = str_shorten(os.path.basename(self.pageinfo.doc.name), length=int(self.width))
        self.label_desc.setPlainText("""PDF:{PDF},Page:{pagenum}""".format(PDF=PDFname, pagenum=self.pageinfo.pagenum))
        self.frameBox = QGraphicsRectItem(self.boundingRect())
        self.addToGroup(self.frameBox)
        self.update()

    def boundingRect(self) -> QtCore.QRectF:
        # 不能用定值来代替坐标位置否则会出错.
        return QRectF(self.x(), self.y(), self.width, self.height)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print(self.button_close.boundingRect().__str__() + ", pos=" + event.pos().__str__())
        list(map(lambda x: x.mousePressEvent(event), self.childItems()))
        # clickedLi = list(map(lambda x:x.contains(event.pos()),self.childItems()))
        # clickedindex = clickedLi.index(True) if True in clickedLi else -1
        # print(clickedindex.__str__())
        # if clickedindex>0:
        #    print(self.childItems()[clickedindex].__str__())

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        needSetCusor = reduce(lambda x, y: x or y, map(lambda x: x.contains(event.pos()), self.childItems()))
        # print(needSetCusor.__str__())
        if needSetCusor:
            self.setCursor(Qt.CrossCursor)
        super().hoverMoveEvent(event)
