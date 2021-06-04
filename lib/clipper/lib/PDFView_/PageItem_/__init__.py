import os
import typing
from functools import reduce

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF, QRectF, Qt, QSizeF
from PyQt5.QtGui import QPixmap, QBrush, QColor, QPen, QPainter, QIcon
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
    handleCursors = {
        TopLeft: Qt.SizeFDiagCursor,
        TopMiddle: Qt.SizeVerCursor,
        TopRight: Qt.SizeBDiagCursor,
        MiddleLeft: Qt.SizeHorCursor,
        MiddleRight: Qt.SizeHorCursor,
        BottomLeft: Qt.SizeBDiagCursor,
        BottomMiddle: Qt.SizeVerCursor,
        BottomRight: Qt.SizeFDiagCursor,
    }

    def __init__(self, *args, parent_pos: QPointF = None, pageitem: 'PageItem' = None, card_id: str = "0",
                 QA: str = "Q"):
        super().__init__(*args)
        # 规定自身
        self.last_delta = None
        self.now_delta = None
        # self.setPos(pos)
        self.pageitem = pageitem
        self.setRect(parent_pos.x() - self.default_height / 2, parent_pos.y() - self.default_height / 2,
                     self.default_height, self.default_height)
        self.setParentItem(pageitem)
        self.handlers = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.init_toolsbar()

    # "./resource/icon_close_button.png"
    def init_toolsbar(self):
        """卡片选择,QA切换,输入栏,关闭"""
        self.toolsbar = ClipBox_.ToolsBar(model=self.pageitem.rightsidebar.cardlist.model_rootNode, clipbox=self)

    def init_handlers(self):
        """八个方向都要有一个方块"""

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...) -> None:
        self.prepareGeometryChange()  # 这个 非常重要. https://www.cnblogs.com/ybqjymy/p/13862382.html
        painter.setBrush(QBrush(QColor(255, 0, 0, 0)))
        painter.setPen(QPen(QColor(127, 127, 127), 2.0, Qt.DashLine))
        painter.drawRect(self.rect())

        if self.isSelected():
            self.toolsbar.show()
        else:
            self.toolsbar.hide()

    # def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
    #     if Qt.LeftButton and  self.last_delta:
    #         self.now_delta = event.pos() - self.last_delta
    #         self.last_delta = event.pos()
    #         self.setPos(self.pos() + self.now_delta)
    #
    #
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.isSelected():
            print(self.__str__() + "selected")
        if self.contains(event.pos()):
            # print(self.__str__()+"activated move")
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
        super().mousePressEvent(event)


class Pixmap(QGraphicsPixmapItem):
    """只需要pixmap就够了"""

    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem' = None):
        super().__init__(pageinfo.pagepixmap)
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
