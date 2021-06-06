import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QLineF, QPointF, Qt, QRectF, QSize
from PyQt5.QtGui import QPen, QBrush, QStandardItemModel, QIcon, QPainterPath
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, QGraphicsItem, QGraphicsEllipseItem, QGraphicsWidget, \
    QGraphicsGridLayout, QComboBox, QGraphicsProxyWidget, QToolButton, QLineEdit, QGraphicsLinearLayout, QWidget, \
    QGraphicsRectItem
# from .. import ClipBox2
from ....tools.objs import CustomSignals


class ToolsBar(QGraphicsWidget):
    """QAswitchButton,CardSwitchButton,closeButton,EditLine"""
    QAdict = {
        "Q": QIcon("./resource/icon_question.png"),
        "A": QIcon("./resource/icon_answer.png")
    }

    on_cardlist_dataChanged = CustomSignals.start().on_cardlist_dataChanged

    def __init__(self, model: 'QStandardItemModel' = None, clipbox: 'ClipBox2' = None, QA="Q"):
        super().__init__()
        self.G_Layout = QGraphicsGridLayout()
        # self.G_Layout = QGraphicsLinearLayout()
        self.G_Layout.setSpacing(0)
        self.layout()
        self.CardDataModel = model
        self.clipbox = clipbox
        self.QAButtonProxy = QGraphicsProxyWidget(self)
        self.lineEditProxy = QGraphicsProxyWidget(self)
        self.editQAButtonProxy = QGraphicsProxyWidget(self)
        self.closeButtonProxy = QGraphicsProxyWidget(self)
        self.cardComboxProxy = QGraphicsProxyWidget(self)
        self.proxyli = [self.lineEditProxy, self.cardComboxProxy, self.QAButtonProxy, self.closeButtonProxy,
                        self.editQAButtonProxy]
        self.init_UI()
        # for p in range(len(self.proxyli)):
        #     self.G_Layout.addItem(self.proxyli[p],0,p)
        # self.G_Layout.addItem(self.proxyli[p])
        # self.setLayout(self.G_Layout)
        self.setParentItem(clipbox)
        # 下面这个用来计算lineEdit的长度时去掉需要去掉的量.因为需要用
        self.lineEdit_delta = self.cardComboxProxy.rect().width() + self.QAButtonProxy.rect().width() + self.closeButtonProxy.rect().width()
        self.init_events()

    def init_UI(self):
        self.init_editLine()
        self.init_closeButton()
        self.init_cardcombox()
        self.init_QAButton()
        self.init_editQAbutton()

    def init_editLine(self):

        self.lineEdit = QLineEdit()
        self.lineEdit.setToolTip("在此处编辑可给选框增加文字描述\nedit here to add a description to the clipbox")
        self.lineEdit.setPlaceholderText("edit here to add a description to the clipbox")
        self.lineEditProxy.setWidget(self.lineEdit)

    def init_editQAbutton(self):

        self.editQAButton = QToolButton()
        self.editQAButton.setText(self.QA)
        self.editQAButton.setIcon(self.QAdict[self.QA])
        self.editQAButton.clicked.connect(self.onEditQAButtonClicked)
        self.editQAButton.setStyleSheet(
            f"margin-right:-1px;margin-left:-1px;margin-top: -1px;height:{self.lineEdit.size().height() - 3}px;")
        self.editQAButton.setToolTip("将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card")
        self.editQAButtonProxy.setWidget(self.editQAButton)

    def init_closeButton(self):

        self.closeButton = QToolButton()
        self.closeButton.setIcon(QIcon("./resource/icon_close_button.png"))
        self.closeButton.clicked.connect(self.onCloseButtonClicked)
        self.closeButton.setStyleSheet(
            f"margin-left:-1px;margin-top: -1px;height:{self.lineEdit.size().height() - 3}px;")
        self.closeButton.setToolTip("关闭/close")
        self.closeButtonProxy.setWidget(self.closeButton)

    def init_events(self):
        self.on_cardlist_dataChanged.connect(self.on_cardlist_dataChanged_handle)

    def init_QAButton(self):
        self.QAButton = QToolButton()
        self.QAButton.setText("Q")
        self.QAButton.setIcon(QIcon("./resource/icon_question.png"))
        self.QAButton.clicked.connect(self.onQAButtonClicked)
        self.QAButton.setStyleSheet(
            f"margin-right:-1px;margin-left:-1px;margin-top: -1px;height:{self.lineEdit.size().height() - 3}px;")
        self.QAButton.setToolTip("将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card")
        self.QAButtonProxy.setWidget(self.QAButton)
        # self.QAButton.resize(self.closeButton.size().width(), self.closeButton.size().height())
        # self.QAButton.setStyleSheet(f"margin: 0px;height:{self.closeButton.size().height()}px")

    def init_cardcombox(self):
        self.cardCombox = QComboBox()
        self.update_cardcombox()
        self.cardCombox.setToolTip("选择一张卡片用来保存当前选框\nSelect a card to store the current clip box")
        self.cardCombox.currentIndexChanged.connect(self.onCardComboxIndexChanged)
        self.cardComboxProxy.setWidget(self.cardCombox)
        # self.cardCombox.resize(self.cardCombox.size().width(),self.closeButton.size().height())
        # self.cardCombox.setStyleSheet(f"margin: 0px;height:{self.closeButton.size().height()}px")

    def on_cardlist_dataChanged_handle(self, li):
        """当添加的时候比较简单,更新新加的内容就好了"""
        model = li[0]
        self.cardCombox.clear()
        self.update_cardcombox()
        self.cardComboxProxy.update()

    def update_cardcombox(self):
        for row in range(self.CardDataModel.rowCount()):
            item = self.CardDataModel.item(row, 0)
            t = item.text()
            self.cardCombox.addItem(t, userData=item)

    def onCardComboxIndexChanged(self, index):
        print(f"you choosed {self.cardCombox.itemText(index)}")

    def onQAButtonClicked(self):
        if self.QAButton.text() == "Q":
            self.QAButton.setText("A")
            self.QAButton.setIcon(self.QAdict["A"])
            self.QAButton.setToolTip("将选框保存到卡片答案字段\nrestore the clipbox to the answer field of the card")

        else:
            self.QAButton.setText("Q")
            self.QAButton.setIcon(self.QAdict["Q"])
            self.QAButton.setToolTip("将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card")
        self.QAButtonProxy.setWidget(self.QAButton)
        for i in self.proxyli:
            print(i.pos())
            print(i.widget().size().width())

    def onEditQAButtonClicked(self):
        if self.editQAButton.text() == "Q":
            self.editQAButton.setText("A")
            self.editQAButton.setIcon(QIcon("./resource/icon_answer.png"))
            self.editQAButton.setToolTip("将选框保存到卡片答案字段\nrestore the clipbox to the answer field of the card")

        else:
            self.editQAButton.setText("Q")
            self.editQAButton.setIcon(QIcon("./resource/icon_question.png"))
            self.editQAButton.setToolTip("将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card")
        self.editQAButtonProxy.setWidget(self.editQAButton)

    def onCloseButtonClicked(self):
        print("close button clicked")
        # for i in self.proxyli:
        #     print(i.pos())
        #     print(i.widget().size().width())
        self.clipbox.pageview.remove_clipbox(self.clipbox)
        #
        # clipper.scene.removeItem(self.clipbox)
        del self.clipbox

    def boundingRect(self) -> QtCore.QRectF:
        height = self.lineEditProxy.rect().height()
        width = self.lineEditProxy.rect().width() + self.cardComboxProxy.rect().width() + \
                self.QAButtonProxy.rect().width() + self.closeButtonProxy.rect().width()
        return QtCore.QRectF(self.x(), self.y(), width, height)
        pass


class FramePen(QPen):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        FramePenColor = kwargs.pop("FramePenColor",None)
        if FramePenColor is None:
            FramePenColor=Qt.red
        self.setColor(FramePenColor)
        self.setWidth(4)


class FrameLineItem(QGraphicsLineItem):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        pencolor = kwargs.pop("pencolor",None)
        if pencolor is None:
            self.setPen(FramePen())
        else:
            self.setPen(FramePen(FramePenColor=pencolor))

        self.update()

class FrameCornerItem(QGraphicsEllipseItem):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setBrush(QBrush(Qt.yellow))
        self.update()


class Frame(QGraphicsItemGroup):
    """
    Top,Bottom,Left,Right,TopLeft,TopRight,BottomLeft,BottomRight,
    """

    def __init__(self,pos:'QPointF'=None,):
        super().__init__()
        self.pos=pos
        self.begindelta=50.0 #开始时的矩形大小
        self.delta=0.1
        self.dotRadius=10.0
        self.direction = ["Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"]
        self.posTop, self.posBottom, self.posLeft, self.posRight, self.posTopLeft, self.posTopRight, self.posBottomLeft, self.posBottomRight = \
            "Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"
        self.border_lines = {
            self.posTop:FrameLineItem(QLineF(QPointF(0,0),QPointF(self.begindelta,0))),
            self.posBottom:FrameLineItem(QLineF(QPointF(0,self.begindelta),
                                                QPointF(self.begindelta,self.begindelta))),
            self.posLeft:FrameLineItem(QLineF(QPointF(0,0),QPointF(0,self.begindelta))),
            self.posRight:FrameLineItem(QLineF(QPointF(self.begindelta, 0),
                                               QPointF(self.begindelta, self.begindelta)))}
        self.corner_dots = {
            self.posTopLeft:FrameCornerItem(QRectF(
                - self.dotRadius / 2,  - self.dotRadius / 2,self.dotRadius, self.dotRadius)),
            self.posTopRight:FrameCornerItem(QRectF(
                self.begindelta - self.dotRadius / 2,-self.dotRadius / 2,self.dotRadius, self.dotRadius
            )),
            self.posBottomLeft:FrameCornerItem(QRectF(
                - self.dotRadius / 2,self.begindelta - self.dotRadius / 2,self.dotRadius, self.dotRadius
            )),
            self.posBottomRight:FrameCornerItem(QRectF(
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
                print(self.direction[i]+" has been clicked")
        if count>-1:
            pass
        else:
            super().mousePressEvent(event)

    def boundingRect(self) -> QRectF:
        return QRectF(0,0,100,100)
