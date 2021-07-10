"""
clipbox->toolsbar
"""
import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QLineF, QPointF, Qt, QRectF, QSize
from PyQt5.QtGui import QPen, QBrush, QStandardItemModel, QIcon, QPainterPath
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, QGraphicsItem, QGraphicsEllipseItem, QGraphicsWidget, \
    QGraphicsGridLayout, QComboBox, QGraphicsProxyWidget, QToolButton, QLineEdit, QGraphicsLinearLayout, QWidget, \
    QGraphicsRectItem
# from .. import ClipBox2
from aqt.utils import showInfo
from .. import ALL, events, funcs, objs
from ....RightSideBar_ import CardList
from .ToolsBar_ import QAButton, CloseButton, EditQAbutton, LineEdit, CardCombox


class ToolsBar(QGraphicsWidget):
    """QAswitchButton,CardSwitchButton,closeButton,EditLine"""

    def __init__(self, cardlist: 'CardList' = None, clipbox: 'ClipBox2' = None, QA="Q"):
        super().__init__(parent=clipbox)
        self.__G_Layout = QGraphicsGridLayout()
        # self.G_Layout = QGraphicsLinearLayout()
        self.__G_Layout.setSpacing(0)
        self.cardlist = cardlist
        self.clipbox = clipbox
        self.__imgDir = self.cardlist.rightsidebar.clipper.objs.SrcAdmin.imgDir
        self.__QA_icon_dict = {
            "Q": QIcon(self.__imgDir.question),
            "A": QIcon(self.__imgDir.answer)
        }
        self.lineEditProxy: 'LineEdit' = LineEdit(toolsbar=self)
        self.cardComboxProxy: 'CardCombox' = CardCombox(toolsbar=self)
        self.QAButtonProxy: 'QAButton' = QAButton(toolsbar=self, QA=QA)
        self.editQAButtonProxy: 'EditQAbutton' = EditQAbutton(toolsbar=self)
        self.closeButtonProxy: 'CloseButton' = CloseButton(toolsbar=self)
        self.setParentItem(clipbox)

    def __cardcombox_update(self):
        for row in range(self.cardlist.model.rowCount()):
            item = self.cardlist.model.item(row, 0)
            t = item.text()
            self.cardCombox.addItem(t, userData=item)

    def __onCardComboxIndexChanged(self, index):
        print(f"you choosed {self.cardCombox.itemText(index)}")

    def boundingRect(self) -> QtCore.QRectF:
        try:  # anki所使用的pyqt版本在这块会出问题,需要加一个try 来避免问题.
            height = self.lineEditProxy.rect().height()
            width = self.lineEditProxy.rect().width() + self.cardComboxProxy.rect().width() + \
                    self.QAButtonProxy.rect().width() + self.closeButtonProxy.rect().width()
            return QtCore.QRectF(self.x(), self.y(), width, height)
        except:
            return QtCore.QRectF(0, 0, 200, 200)

    def size_pos_adjust(self):
        self.setPos(self.clipbox.rect().x() + 1, self.clipbox.rect().y() + 1)
        self.lineEditProxy.resize(self.clipbox.rect().width() - self.editQAButtonProxy.rect().width() - 1,
                                  self.lineEditProxy.rect().height())

        C = self.cardComboxProxy
        l = self.lineEditProxy
        c = self.closeButtonProxy
        Q = self.QAButtonProxy
        eQ = self.editQAButtonProxy
        r = self.clipbox.rect()
        self.cardComboxProxy.resize(
            self.clipbox.rect().width() - c.rect().width() - Q.rect().width() - 1,
            Q.rect().height() - 1
        )
        C.setPos(0, 0)
        c.setPos(r.width() - c.rect().width() - 1, 0)
        Q.setPos(r.width() - c.rect().width() - Q.rect().width() - 1, 0)
        l.setPos(0, C.rect().height())
        eQ.setPos(l.rect().right() - 1, C.rect().height() + 1)
        C.update()

    def return_data(self):
        data = {
            "QA": self.QAButtonProxy.return_data(),
            "text_": self.lineEditProxy.return_data(),
            "textQA": self.editQAButtonProxy.return_data(),
            # "card_id":self.cardlist.cardUuidDict[self.cardComboxProxy.return_data()][1].text()
        }
        return data
class FramePen(QPen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FramePenColor = kwargs.pop("FramePenColor", None)
        if FramePenColor is None:
            FramePenColor = Qt.red
        self.setColor(FramePenColor)
        self.setWidth(4)


class FrameLineItem(QGraphicsLineItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pencolor = kwargs.pop("pencolor", None)
        if pencolor is None:
            self.setPen(FramePen())
        else:
            self.setPen(FramePen(FramePenColor=pencolor))

        self.update()


class FrameCornerItem(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setBrush(QBrush(Qt.yellow))
        self.update()


class Frame(QGraphicsItemGroup):
    """
    Top,Bottom,Left,Right,TopLeft,TopRight,BottomLeft,BottomRight,
    """

    def __init__(self, pos: 'QPointF' = None, ):
        super().__init__()
        self.pos = pos
        self.begindelta = 50.0  # 开始时的矩形大小
        self.delta = 0.1
        self.dotRadius = 10.0
        self.direction = ["Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"]
        self.posTop, self.posBottom, self.posLeft, self.posRight, self.posTopLeft, self.posTopRight, self.posBottomLeft, self.posBottomRight = \
            "Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"
        self.border_lines = {
            self.posTop: FrameLineItem(QLineF(QPointF(0, 0), QPointF(self.begindelta, 0))),
            self.posBottom: FrameLineItem(QLineF(QPointF(0, self.begindelta),
                                                 QPointF(self.begindelta, self.begindelta))),
            self.posLeft: FrameLineItem(QLineF(QPointF(0, 0), QPointF(0, self.begindelta))),
            self.posRight: FrameLineItem(QLineF(QPointF(self.begindelta, 0),
                                                QPointF(self.begindelta, self.begindelta)))}
        self.corner_dots = {
            self.posTopLeft: FrameCornerItem(QRectF(
                - self.dotRadius / 2, - self.dotRadius / 2, self.dotRadius, self.dotRadius)),
            self.posTopRight: FrameCornerItem(QRectF(
                self.begindelta - self.dotRadius / 2, -self.dotRadius / 2, self.dotRadius, self.dotRadius
            )),
            self.posBottomLeft: FrameCornerItem(QRectF(
                - self.dotRadius / 2, self.begindelta - self.dotRadius / 2, self.dotRadius, self.dotRadius
            )),
            self.posBottomRight: FrameCornerItem(QRectF(
                self.begindelta - self.dotRadius / 2, self.begindelta - self.dotRadius / 2,
                self.dotRadius, self.dotRadius
            ))
        }
        list(map(lambda pair: self.addToGroup(pair[1]), self.border_lines.items()))
        list(map(lambda pair: self.addToGroup(pair[1]), self.corner_dots.items()))

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        count = -1
        for i in range(4):
            if self.dir_lines[i].contains(event.pos()):
                count = i
                # print(self.direction[i] + " has been clicked")
        if count > -1:
            pass
        else:
            super().mousePressEvent(event)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 100, 100)
