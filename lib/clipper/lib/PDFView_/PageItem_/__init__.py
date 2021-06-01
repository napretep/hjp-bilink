import os

from PyQt5 import QtCore
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPixmapItem, QApplication, QGraphicsTextItem, QGraphicsItem
from ...tools.funcs import pixmap_page_load,str_shorten
from ...PageInfo import PageInfo
from . import ClipBox_


class ClipBox(QGraphicsItemGroup):
    """
    由三个部分构成:Frame,ToolsBar,EditLine
    """
    def __init__(self):
        super().__init__()
        self.frame = ClipBox_.Frame()
        self.addToGroup(self.frame)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def boundingRect(self) -> QtCore.QRectF:
        return self.frame.boundingRect()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print("come to here")
        if self.contains(event.pos()):
            print("yes")
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)

class Pixmap(QGraphicsPixmapItem):
    """只需要pixmap就够了"""
    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem' =None):
        super().__init__(pageinfo.pagepixmap)
        self.pageinfo = pageinfo
        self.pageitem = pageitem
        self._delta = 0.1
        self.ratio = 1
        self.width = self.pixmap().width()

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

    pass


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

    def __init__(self, pageinfo: 'PageInfo', pageitem: 'PageItem' =None):
        super().__init__()
        self.pageitem = pageitem
        self.pageinfo = pageinfo
        self.button_close = QGraphicsPixmapItem(QPixmap("./resource/icon_close_button.png").scaled(25, 25))
        self.button_nextpage = QGraphicsPixmapItem(QPixmap("./resource/icon_next_button.png").scaled(25, 25))
        self.button_prevpage = QGraphicsPixmapItem(QPixmap("./resource/icon_prev_button.png").scaled(25, 25))
        self.button_zoomin = QGraphicsPixmapItem(QPixmap("./resource/icon_zoom_in.png").scaled(25, 25))
        self.button_zoomout = QGraphicsPixmapItem(QPixmap("./resource/icon_zoom_out.png").scaled(25, 25))
        self.button_close.setToolTip("关闭/close")
        self.button_zoomin.setToolTip("放大/zoom in")
        self.button_zoomout.setToolTip("缩小/zoom out")
        self.button_prevpage.setToolTip("下一页/previous page \n ctrl+click=新建下一页/create previous page to the view")
        self.button_nextpage.setToolTip("下一页/next page \n ctrl+click=新建下一页/create next page to the view")
        self.label_desc = QGraphicsTextItem()
        self.label_desc.setToolTip(pageinfo.doc.name)
        self.addToGroup(self.button_zoomin)
        self.addToGroup(self.button_zoomout)
        self.addToGroup(self.button_prevpage)
        self.addToGroup(self.button_nextpage)
        self.addToGroup(self.button_close)
        self.addToGroup(self.label_desc)
        p = QPointF(0, 0)
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
        self.label_desc.setPos(QPointF(0,self.height))
        self.height+=self.label_desc.boundingRect().height()
        PDFname = str_shorten(os.path.basename(pageinfo.doc.name), length=int(self.width))
        self.label_desc.setPlainText("""PDF:{PDF},Page:{pagenum}""".format(PDF=PDFname, pagenum=pageinfo.pagenum))

    def boundingRect(self) -> QtCore.QRectF:
        return QRectF(0, 0, self.width, self.height)
