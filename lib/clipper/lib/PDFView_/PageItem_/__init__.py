import json
import os
import time
import typing

from functools import reduce

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF, QRectF, Qt, QSizeF, QLineF, QRect
from PyQt5.QtGui import QPixmap, QBrush, QColor, QPen, QPainter, QIcon, QPainterPath, QPainterPathStroker
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QApplication, QGraphicsTextItem, QGraphicsItem, \
    QGraphicsRectItem, QWidget, QGraphicsWidget, QGraphicsLinearLayout, QLabel, QLineEdit, QGraphicsProxyWidget, \
    QGraphicsGridLayout, QToolButton, QGraphicsAnchorLayout, QComboBox, QGraphicsSceneMouseEvent, \
    QGraphicsSceneHoverEvent, QGraphicsView

from ...tools.funcs import pixmap_page_load, str_shorten
from ...tools.objs import SrcAdmin
from ...tools.events import PageItemDeleteEvent, PageItemAddToSceneEvent, PageItemChangeEvent, PageItemResizeEvent
from ...tools import events, objs, funcs, ALL, dialogs
from ...PageInfo import PageInfo
from . import ClipBox_
from ...PagePicker import PagePicker

print, printer = funcs.logger(__name__)

class PageItem_ClipBox_Event:
    def __init__(self, clipbox=None, cardUuid=None):
        self.clipbox = clipbox
        self.cardUuid = cardUuid


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
    handlerSize = 14

    def __init__(self, *args, parent_pos: QPointF = None,
                 pageview: 'PageView' = None, card_id: str = "0", rect=None,
                 QA: str = "Q"):
        super().__init__(*args)
        # 规定自身
        self.uuid = self.init_UUID()  # TODO 需要进行数据库碰撞检查
        self.QA = QA
        self.text = ""
        self.textQA = "Q"
        self.ratio = pageview.ratio * pageview.pageinfo.ratio
        self.docname = pageview.pageinfo.doc.name
        self.pagenum = pageview.pageinfo.pagenum
        self.last_delta = None
        self.now_delta = None
        self.pageview = pageview
        self.pageitem = pageview.pageitem
        self.pageinfo = pageview.pageinfo
        self.isHovered = False
        if parent_pos is not None:
            self.setRect(
                parent_pos.x() - self.default_height / 2, parent_pos.y() - self.default_height / 2,
                self.default_height * 6, self.default_height * 2)
        else:
            self.setRect(rect)
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
        self.card_id = None
        self.version = 0
        self.toolsbar = ClipBox_.ToolsBar(cardlist=ALL.clipper.rightsidebar.cardlist, clipbox=self,
                                          QA=self.QA)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.init_handlers()

        self.event_dict = {
            ALL.signals.on_clipbox_closed: self.on_clipbox_closed_handle,
            ALL.signals.on_pageItem_update: self.on_pageItem_update_handle,
            ALL.signals.on_clipbox_toolsbar_update: self.on_clipbox_toolsbar_update_handle,
            ALL.signals.on_cardlist_dataChanged: self.on_cardlist_dataChanged_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def on_clipbox_closed_handle(self):
        self.all_event.unbind(self.__class__.__name__)

    def on_clipbox_create_handle(self, event: "events.ClipboxCreateEvent"):
        # print("on_clipbox_create_handle")
        if event.Type == event.rubbingType:
            self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        if event.Type == event.rubbedType:
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def on_cardlist_dataChanged_handle(self, event: "events.CardListDataChangedEvent"):
        # print("on_cardlist_dataChanged_handle")
        if event.Type == event.CardIdChangeType and event.sender.uuid == self.toolsbar.cardComboxProxy.return_data():
            # print("event.data= "+str(event.data))
            self.card_id = event.data
            e = events.AnkiCardCreatedEvent
            ALL.signals.on_anki_card_created.emit(e(eventType=e.infoUpdateType))

    def on_clipbox_toolsbar_update_handle(self, event: "events.ClipBoxToolsbarUpdateEvent"):

        if self.uuid == event.sender:
            self.__dict__[event.Type] = event.data

    def on_pageItem_update_handle(self, event: "events.PageItemUpdateEvent"):
        if self.pageitem.uuid == event.sender:
            self.__dict__[event.Type] = event.data
        pass

    def init_UUID(self):
        import uuid
        myid = str(uuid.uuid4())[0:8]
        while objs.SrcAdmin.DB.go().exists_check(myid).return_all()[0][0] > 0:
            myid = str(uuid.uuid4())[0:8]
        return myid

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
                # print(f"{str(k)} clicked")
                return k
        return None

    def boundingRect(self) -> QtCore.QRectF:
        s = self.handlerSize
        return self.rect().adjusted(-s, -s, s, s)

    def init_toolsbar_size(self):
        """工具条的位置和大小的设定"""
        if self.isSelected():
            self.toolsbar.size_pos_adjust()
            self.toolsbar.show()
        else:
            self.toolsbar.hide()

    def shape(self):
        """
        shape在boundingRect里面
        """
        strokepath = QPainterPathStroker()
        # print(self.rect())
        path = QPainterPath()

        path.addRect(self.rect())
        if self.isSelected():
            for shape in self.handlers.values():
                path.addRect(shape)
            return path
        else:
            strokepath.setWidth(2 * self.handlerSize)
            newpath = strokepath.createStroke(path)
            return newpath


    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        # self.prepareGeometryChange()  # 这个 非常重要. https://www.cnblogs.com/ybqjymy/p/13862382.html
        self.calc_ratio()  # 计算所占page的比例

        pen = QPen(QColor(127, 127, 127), 2.0, Qt.DashLine)
        if self.isHovered or self.isSelected():
            pen.setWidth(5)
        if self.isSelected():
            painter.setBrush(QBrush(QColor(0, 255, 0, 30)))

        painter.setPen(pen)
        painter.drawRect(self.rect())

        if "toolsbar" in self.__dict__:
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
        if ALL.pdfview.dragMode() == ALL.pdfview.RubberBandDrag:
            self.setFlag(self.ItemIsSelectable, False)
        else:
            self.setFlag(self.ItemIsSelectable, True)
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
        if rect.width() > view_right:
            rect.setWidth(view_right)
        if rect.height() > view_bottom:
            rect.setHeight(view_bottom)

        top = rect.top() + y
        bottom = rect.bottom() + y
        left = rect.left() + x
        right = rect.right() + x
        if top < view_top:
            # print("over top")
            rect.translate(0, view_top - top)
        if left < view_left:
            # print("over left")
            rect.translate(view_left - left, 0)
        if view_bottom < bottom:
            # print("over bottom")
            rect.translate(0, view_bottom - bottom)
        if view_right < right:
            # print("over right")
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
        # print(self.self_info_get())
        self.handleSelected = self.handlerAt(event.pos())
        self.mousePressRect = self.rect()
        self.mousePressSelfPos = self.pos()
        if self.handleSelected:
            self.mousePressPos = event.pos()
            event.accept()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        p = dialogs.ClipboxInfo(info=self.self_info_get(), callback=
        [lambda value: self.toolsbar.QAButtonProxy.set_data(str(value)),
         lambda value: self.toolsbar.editQAButtonProxy.set_data(str(value)),
         lambda value: self.toolsbar.lineEditProxy.set_data(value)])

        p.exec()
        pass

    def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        # print('hoverMoveEvent')
        self.isHovered = True
        super().hoverMoveEvent(event)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        # print('hoverEnterEvent')
        self.isHovered = True
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        # print('hoverLeaveEvent')
        self.isHovered = False
        super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        # if self.shape().contains(self.pos()):
        #     print ("shape")
        self.borderUpdate()
        # print('hoverMoveEvent')
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

    def self_info_get(self) -> dict:
        """

        Returns:
            {
            x,y,w,h
            QA,text,textQA,ratio
            card_id,docname,pagenum
            }
        """
        QA_dict = {
            "Q": ALL.CONFIG.clipbox.Q_map_Field,
            "A": ALL.CONFIG.clipbox.A_map_Field
        }
        textQA_dict = {
            "Q": ALL.CONFIG.clipbox.textQ_map_Field,
            "A": ALL.CONFIG.clipbox.textA_map_Field
        }
        x, y = self.pos().x() + self.rect().left(), self.pos().y() + self.rect().top()

        info = {
            "uuid": self.uuid,
            "card_id": self.card_id,
            "pdfname": os.path.abspath(self.docname).replace("\\", "/"),
            "pagenum": self.pagenum,
            "ratio": self.ratio,
            "x": x / self.pageview.boundingRect().width(),
            "y": y / self.pageview.boundingRect().height(),
            "w": self.rect().width() / self.pageview.boundingRect().width(),
            "h": self.rect().height() / self.pageview.boundingRect().height(),
        }
        info.update(self.toolsbar.return_data().copy())

        if type(info["QA"]) != int:
            if info["QA"] in ["Q", "A"]:
                info["QA"] = QA_dict[info["QA"]]
            else:
                info["QA"] = int(info["QA"])
        if type(info["textQA"]) != int:
            if info["textQA"] in ["Q", "A"]:
                info["textQA"] = textQA_dict[info["textQA"]]
            else:
                info["textQA"] = int(info["textQA"])
        return info


    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.all_event.unbind(self.__class__.__name__)

class PageView(QGraphicsPixmapItem):
    """只需要pixmap就够了"""
    mousecenter = 0
    viewcenter = 1
    itemcenter = 2
    nocenter = 3

    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem5' = None, ratio=None):
        super().__init__(pageinfo.pagepixmap)
        self.clipBoxList: 'list[ClipBox2]' = []
        self.pageinfo = pageinfo
        self.pageitem = pageitem
        self.setParentItem(pageitem)
        self.isFullscreen = False
        self.view = ALL.clipper.pdfview
        # self.init_signals()
        # self.init_events()
        self._delta = 0.1
        self.ratio = 1 if ratio is None else ratio
        self.viewratio = 1
        self.width = self.pixmap().width()
        self.height = self.pixmap().height()
        self.start_width = self.width
        self.start_height = self.height
        if self.ratio != 1:
            self.zoom(self.ratio)
        self.event_dict = {
            ALL.signals.on_clipbox_closed: self.pageview_clipbox_remove,
            ALL.signals.on_pageItem_changePage: self.on_pageItem_changePage_handle,
            ALL.signals.on_pageItem_resize_event: self.on_pageItem_resize_event_handle,
            ALL.signals.on_pageItem_rubberBandRect_send: self.on_pageItem_rubberBandRect_send_handle
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()


    def on_pageItem_rubberBandRect_send_handle(self, event: "events.PageItemRubberBandRectSendEvent"):
        if event.sender.uuid == self.pageitem.uuid:
            r: "QRectF" = self.mapRectFromScene(event.rubberBandRect)
            self.pageview_clipbox_add(rect=r)
            # print(f"event.rubberBandRect={(r)}")

    def on_pageItem_resize_event_handle(self, event: "PageItemResizeEvent"):
        if event.pageItem.uuid == self.pageitem.uuid:
            if event.Type == PageItemResizeEvent.fullscreenType:
                self.zoom(self.view_divde_page_ratio(), self.itemcenter)
            if event.Type == PageItemResizeEvent.resetType:
                self.zoom(1, self.itemcenter)


    def view_divde_page_ratio(self):
        view_Width = self.view.geometry().width()
        pixwidth = self.pageinfo.pagepixmap.width()
        ratio = view_Width / pixwidth
        return ratio

    def on_pageItem_changePage_handle(self, event: 'PageItemChangeEvent'):
        if event.Type == event.updateType and event.pageItem.uuid == self.pageitem.uuid:
            self.pageinfo_read(event.pageInfo)
            e = events.PageItemUpdateEvent
            self.update_sginal_emit(where=e.pageNumType)
            self.update_sginal_emit(where=e.docNameType)
            self.update()
            self.pageitem.update()

    def pageinfo_read(self, pageinfo):
        self.pageinfo = pageinfo
        self.zoom(self.ratio, center=self.nocenter)

    def add_round(self):
        round = QGraphicsRectItem(QRectF(self.pixmap().rect()), parent=self)
        round.setPen(ClipBox_.FramePen())
        round.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:

        modifiers = QApplication.keyboardModifiers()

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        e = events.PageItemResizeEvent
        if self.isFullscreen:
            self.isFullscreen = False
            objs.signals.on_pageItem_resize_event.emit(e(pageItem=self.pageitem, eventType=e.resetType))
        else:
            self.isFullscreen = True
            objs.signals.on_pageItem_resize_event.emit(e(pageItem=self.pageitem, eventType=e.fullscreenType))

    def pageview_clipbox_add(self, pos=None, rect=None):
        """顺带解决"""
        QA = ALL.QA
        if pos:
            clipbox = ClipBox2(parent_pos=pos, pageview=self, QA=QA)
        else:
            clipbox = ClipBox2(rect=rect, pageview=self, QA=QA)
        uuid = clipbox.toolsbar.cardComboxProxy.desc_item_uuid
        self.clipBoxList.append(clipbox)  # 创建后必须添加到clipboxlist
        ALL.signals.on_pageItem_clipbox_added.emit(PageItem_ClipBox_Event(clipbox=clipbox, cardUuid=uuid))

    def pageview_clipbox_remove(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        """这里要做的事情就是从clipBoxList中移除"""
        clipbox = event.clipBox
        if clipbox in self.clipBoxList:  # 有可能来自其他page的信号
            self.clipBoxList.remove(clipbox)

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
        self.zoom(self.ratio * (1 + self._delta))

    def zoomOut(self):
        """缩小"""
        self.zoom(self.ratio / (1 + self._delta))

    def center_zoom(self, center=0):
        if center == self.mousecenter:
            X = self.mouse_center_item_p[0] * self.boundingRect().width()
            Y = self.mouse_center_item_p[1] * self.boundingRect().height()
            new_scene_p = self.mapToScene(X, Y)
            dx = new_scene_p.x() - self.mouse_center_scene_p.x()
            dy = new_scene_p.y() - self.mouse_center_scene_p.y()
        elif center == self.viewcenter:
            X = self.view_center_item_p[0] * self.boundingRect().width()
            Y = self.view_center_item_p[1] * self.boundingRect().height()
            new_scene_p = self.mapToScene(X, Y)
            dx = new_scene_p.x() - self.view_center_scene_p.x()
            dy = new_scene_p.y() - self.view_center_scene_p.y()
        elif center == self.itemcenter:
            X = self.item_center_item_size[0] * self.boundingRect().width()
            Y = self.item_center_item_size[1] * self.boundingRect().height()
            new_scene_p = self.mapToScene(X, Y)
            dx = new_scene_p.x() - self.view_center_scene_p.x()
            dy = new_scene_p.y() - self.view_center_scene_p.y()
        else:
            raise TypeError(f"无法处理数据:{center}")
        scrollY = self.view.verticalScrollBar()
        scrollX = self.view.horizontalScrollBar()

        print(f"x={dx}, dy={dy}")
        rect = self.view.sceneRect()
        if scrollY.value() - dy < 0:
            self.view.setSceneRect(rect.x(), rect.y() - dy, rect.width(), rect.height())
        if scrollX.value() - dx < 0:
            self.view.setSceneRect(rect.x() - dx, rect.y(), rect.width(), rect.height())
        if scrollY.value() == scrollY.maximum():
            self.view.setSceneRect(rect.x(), rect.y(), rect.width(), rect.height() + dy)
        if scrollX.value() == scrollX.maximum():
            self.view.setSceneRect(rect.x(), rect.y(), rect.width() + dx, rect.height())
        # self.view.setSceneRect(self.mapRectToScene(self.boundingRect()))

        scrollY.setValue(scrollY.value() + int(dy))
        scrollX.setValue(scrollX.value() + int(dx))

        self.view_center_scene_p = None
        self.view_center_item_p = None

    def item_center_pos_get(self):
        self.item_center_item_size = [0.5, 0.5]
        self.view_center_pos_get()

    def mouse_center_pos_get(self, pos):
        self.mouse_center_item_p = [pos.x() / self.boundingRect().width(),
                                    pos.y() / self.boundingRect().height()]
        self.mouse_center_scene_p = self.mapToScene(pos)

    def view_center_pos_get(self):
        centerpos = QPointF(self.view.size().width() / 2, self.view.size().height() / 2)
        self.view_center_scene_p = self.view.mapToScene(centerpos.toPoint())
        p = self.mapFromScene(self.view_center_scene_p)
        self.view_center_item_p = [p.x() / self.boundingRect().width(), p.y() / self.boundingRect().height()]

    def zoom(self, factor, center=None):
        if center is None:
            center = self.mousecenter
        if center == self.viewcenter:
            self.view_center_pos_get()
        elif center == self.itemcenter:
            self.item_center_pos_get()
        """缩放
        :param factor: 缩放的比例因子
        """
        self.prepareGeometryChange()
        if factor < 0.07 or factor > 100:
            # 防止过大过小
            return
        p = pixmap_page_load(self.pageinfo.doc, self.pageinfo.pagenum, ratio=factor * self.pageinfo.ratio)
        self.setPixmap(QPixmap(p))
        if center != self.nocenter:
            self.center_zoom(center)

        self.width = self.pixmap().width()
        self.height = self.pixmap().height()
        self.keep_clipbox_in_postion()

        self.ratio = factor

        e = events.PageItemUpdateEvent
        self.update_sginal_emit(where=e.ratioType)
        self.update()

    def update_sginal_emit(self, where="ratio"):
        e = events.PageItemUpdateEvent
        data = None
        if where == e.ratioType:
            data = self.ratio * self.pageinfo.ratio
        elif where == e.pageNumType:
            data = self.pageinfo.pagenum
        elif where == e.docNameType:
            data = self.pageinfo.doc.name
        ALL.signals.on_pageItem_update.emit(
            e(sender=self.pageitem.uuid, eventType=where, data=data)
        )

    def keep_clipbox_in_postion(self):
        w, h = self.boundingRect().width(), self.boundingRect().height()
        for box in self.clipBoxList:
            r = box.rect()
            x, y = box.x(), box.y()
            r.setTop(box.ratioTop * self.viewratio * h - y)
            r.setLeft(box.ratioLeft * self.viewratio * w - x)
            r.setBottom(box.ratioBottom * self.viewratio * h - y)
            r.setRight(box.ratioRight * self.viewratio * w - x)  # 之所以减原来的x,y可行,是因为图片的放大并不是膨胀放大,每个点都是原来的点,只是增加了一些新的点而已.
            box.setRect(r)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self.pixmap().width(), self.pixmap().height())

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
        self.__event = {
            self.on_pageItem_changePage: self.on_pageItem_changePage_handle,
            self.on_pageItem_resize_event: self.on_pageItem_resize_event_handle,
            objs.signals.on_PDFView_clicked: self.on_PDFView_clicked_handle,
            objs.signals.on_pageItem_clicked: self.on_pageItem_clicked_handle,
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()

    def on_PDFView_clicked_handle(self, event):
        self.hide()

    def on_pageItem_clicked_handle(self, event: "events.PageItemClickEvent"):
        if event.sender.uuid != self.pageitem.uuid:
            self.hide()

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
        imgDir = SrcAdmin.call().imgDir
        iconli = [imgDir.close, imgDir.prev, imgDir.next, imgDir.reset, imgDir.expand, ""]
        tipli = ["关闭/close", "上一页/previous page \n ctrl+click=新建上一页/create previous page to the view",
                 "下一页/next page \n ctrl+click=新建下一页/create next page to the view", "重设大小/reset size", "全屏/fullscreen",
                 f"""{self.pageinfo.doc.name}"""]
        handleli = [self.on_button_close_clicked_handle, self.on_button_prevpage_clicked_handle,
                    self.on_button_nextpage_clicked_handle, self.on_button_reset_clicked_handle,
                    self.on_button_fullscreen_clicked_handle, self.on_button_pageinfo_clicked_handle]

        buttons_dict = {}
        gridpos = [(0, 5), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
        for i in range(6):
            buttons_dict[nameli[i]] = QToolButton()
            if iconli[i] != "":
                buttons_dict[nameli[i]].setIcon(QIcon(iconli[i]))
            else:
                buttons_dict[nameli[i]].setText(
                    str_shorten(os.path.basename(self.pageinfo.doc.name)) + ", page=" + str(self.pageinfo.pagenum))
            buttons_dict[nameli[i]].clicked.connect(handleli[i])
            buttons_dict[nameli[i]].setToolTip(tipli[i])
            self.__dict__[nameli[i]] = QGraphicsProxyWidget(self)
            self.__dict__[nameli[i]].setContentsMargins(0.0, 0.0, 0.0, 0.0)
            self.__dict__[nameli[i]].setWidget(buttons_dict[nameli[i]])
        for i in range(5):
            L_layout.addItem(self.__dict__[nameli[i]], gridpos[i][0], gridpos[i][1])
        self.button_pageinfo.widget().setStyleSheet(f"height:{self.button_close.widget().height() - 6}px")
        # self.button_pageinfo.setPos(0,self.button_fullscreen.pos().y()+self.button_prevpage.boundingRect().height())
        L_layout.addItem(self.__dict__[nameli[-1]], gridpos[-1][0], gridpos[-1][1], 1, 4)

        self.setLayout(L_layout)

    def update_from_pageinfo(self, pageinfo):
        self.pageinfo = pageinfo
        p: 'QGraphicsProxyWidget' = self.__dict__["button_pageinfo"]
        q: 'QToolButton' = p.widget()
        q.setToolTip(self.pageinfo.doc.name)
        q.setText(str_shorten(os.path.basename(self.pageinfo.doc.name)) + ", page=" + str(self.pageinfo.pagenum))
        p.update()

    def init_signals(self):
        self.on_pageItem_removeFromScene = ALL.signals.on_pageItem_removeFromScene
        self.on_pageItem_addToScene = ALL.signals.on_pageItem_addToScene
        self.on_pageItem_changePage = ALL.signals.on_pageItem_changePage
        self.on_pageItem_resize_event = ALL.signals.on_pageItem_resize_event

    # def init_events(self):
    #     self.on_pageItem_changePage.connect(self.on_pageItem_changePage_handle)
    #     self.on_pageItem_resize_event.connect(self.on_pageItem_resize_event_handle)

    def on_button_fullscreen_clicked_handle(self):
        self.on_pageItem_resize_event.emit(
            PageItemResizeEvent(pageItem=self.pageitem, eventType=PageItemResizeEvent.fullscreenType)
        )

    def on_pageItem_resize_event_handle(self, event):
        self.update()

    def on_pageItem_changePage_handle(self, event: 'PageItemChangeEvent'):
        if event.pageItem.uuid == self.pageitem.uuid:
            self.update_from_pageinfo(event.pageInfo)

    def on_button_reset_clicked_handle(self):
        self.on_pageItem_resize_event.emit(
            PageItemResizeEvent(pageItem=self.pageitem, eventType=PageItemResizeEvent.resetType)
        )
        pass

    def on_button_nextpage_clicked_handle(self):
        if self.pageinfo.pagenum + 1 == len(self.pageinfo.doc):
            return
        modifiers = QApplication.keyboardModifiers()
        self._on_button_prev_next_page_handle(modifiers, self.pageinfo, 1)

    def on_button_prevpage_clicked_handle(self):
        if self.pageinfo.pagenum - 1 == -1:
            return
        modifiers = QApplication.keyboardModifiers()
        self._on_button_prev_next_page_handle(modifiers, self.pageinfo, - 1)
        pass

    def _on_button_prev_next_page_handle(self, modifiers, pageinfo: "PageInfo", pagenum_delta):
        pageinfo = PageInfo(pageinfo.doc.name, pageinfo.pagenum + pagenum_delta, pageinfo.ratio)
        pageview_ratio = self.pageitem.pageview.ratio
        if modifiers == QtCore.Qt.ControlModifier:
            self.on_pageItem_changePage.emit(
                PageItemChangeEvent(pageInfo=pageinfo, pageItem=self.pageitem,
                                    eventType=PageItemChangeEvent.updateType))
        else:
            from .. import PageItem5
            pageitem = PageItem5(pageinfo, pageview_ratio=pageview_ratio)

            self.on_pageItem_addToScene.emit(
                PageItemAddToSceneEvent(pageItem=pageitem, eventType=PageItemAddToSceneEvent.addPageType))


    def on_button_close_clicked_handle(self):
        self.on_pageItem_removeFromScene.emit(
            PageItemDeleteEvent(pageItem=self.pageitem, eventType=PageItemDeleteEvent.deleteType))

    def on_button_pageinfo_clicked_handle(self):
        e = events.PagePickerOpenEvent
        ALL.signals.on_pagepicker_open.emit(
            e(sender=self, eventType=e.fromPageType
              , pdfpath=self.pageinfo.doc.name, fromPageItem=self.pageitem, pagenum=self.pageinfo.pagenum, )
        )

        pass

    def boundingRect(self) -> QtCore.QRectF:
        x, y = self.x(), self.y()
        w = 0
        for i in self.widgetLi:
            w += self.__dict__[i].rect().width()
        h = self.__dict__[self.widgetLi[-1]].rect().height()
        return QRectF(x, y, w, h)
