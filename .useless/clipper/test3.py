# test3 目标: 在scene中添加PDF页面,实现PDF页面可随滚轮放缩,而且精度保持变化,
# 实现在mainwindow里布局两个不同的东西
import sys, os

from PyQt5 import QtGui, QtCore, Qt
from PyQt5.QtCore import QRectF, QPoint, QPointF
from PyQt5.QtGui import QImage, QPixmap, QPainter
from fitz import fitz
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget, QGraphicsScene, QGraphicsView, \
    QGraphicsItem, QGraphicsPixmapItem, QMainWindow, QHBoxLayout, QListWidget, QPushButton, QToolButton, \
    QGraphicsItemGroup, QGraphicsTextItem, QGraphicsSceneMouseEvent, QGraphicsSceneWheelEvent, QGraphicsRectItem


class PageList(QWidget):
    """
    左边竖排添加删除按钮,右边一个QListWidget
    """
    def __init__(self,parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.init_UI()
    def init_UI(self):
        H_layout = QHBoxLayout()
        V_layout2= QVBoxLayout()
        self.label = QLabel()
        self.label.setText("page list")
        self.V_layout = QVBoxLayout(self)
        self.addButton=QToolButton(self)
        self.addButton.setText("+")
        self.delButton=QToolButton(self)
        self.delButton.setText("-")
        self.list = QListWidget(self)
        H_layout.addWidget(self.label)
        H_layout.addWidget(self.addButton)
        H_layout.addWidget(self.delButton)
        V_layout2.addWidget(self.list)
        self.V_layout.addLayout(H_layout)
        self.V_layout.addLayout(V_layout2)
        self.V_layout.setStretch(1, 1)

class CardList(QWidget):
    def __init__(self,parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.init_UI()
    def init_UI(self):
        H_layout = QHBoxLayout()
        V_layout2 = QVBoxLayout()
        self.label = QLabel()
        self.label.setText("card list")
        self.V_layout = QVBoxLayout(self)
        self.addButton = QToolButton(self)
        self.addButton.setText("+")
        self.delButton = QToolButton(self)
        self.delButton.setText("-")
        self.list = QListWidget(self)
        H_layout.addWidget(self.label)
        H_layout.addWidget(self.addButton)
        H_layout.addWidget(self.delButton)
        V_layout2.addWidget(self.list)
        self.V_layout.addLayout(H_layout)
        self.V_layout.addLayout(V_layout2)
        self.V_layout.setStretch(1, 1)

class QAConfirm_group(QWidget):
    def __init__(self,parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.init_UI()
    def init_UI(self):
        self.h_layout = QHBoxLayout(self)
        self.Qbutton = QToolButton(self)
        self.Abutton = QToolButton(self)
        self.Confirm = QToolButton(self)
        self.Qbutton.setText("Q")
        self.Abutton.setText("A")
        self.Confirm.setText("√")
        for w in [self.Qbutton,self.Abutton,self.Confirm]:
            self.h_layout.addWidget(w)
        for i in range(3):
            self.h_layout.setStretch(i,1)
        self.setLayout(self.h_layout)

class RightSideBar(QWidget):
    def __init__(self,parent=None,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        self.init_UI()
    def init_UI(self):
        self.V_layout = QVBoxLayout()
        w_li= [PageList,CardList,QAConfirm_group]
        for i in range(len(w_li)):
            self.__dict__[w_li[i].__name__]=w_li[i]()
            self.V_layout.addWidget(self.__dict__[w_li[i].__name__])
            if i<2:
                self.V_layout.setStretch(i,1)
        self.setLayout(self.V_layout)

class PageToolsBar(QGraphicsItemGroup):
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
    def __init__(self,doc,pagenum,pageview):
        super().__init__()
        self.doc=doc
        self.pagenum = pagenum
        self.pageview=pageview

        self.button_close = QGraphicsPixmapItem(QPixmap("./resource/icon_close_button.png").scaled(25,25))
        self.button_nextpage = QGraphicsPixmapItem(QPixmap("./resource/icon_next_button.png").scaled(25,25))
        self.button_prevpage = QGraphicsPixmapItem(QPixmap("./resource/icon_prev_button.png").scaled(25,25))
        self.button_input_field = QGraphicsTextItem()
        self.button_zoomin = QGraphicsPixmapItem(QPixmap("./resource/icon_zoom_in.png").scaled(25,25))
        self.button_zoomout = QGraphicsPixmapItem(QPixmap("./resource/icon_zoom_out.png").scaled(25,25))
        self.button_close.setToolTip("关闭/close")
        self.button_zoomin.setToolTip("放大/zoom in")
        self.button_zoomout.setToolTip("缩小/zoom out")
        self.button_prevpage.setToolTip("下一页/previous page \n ctrl+click=新建下一页/create previous page to the view")
        self.button_nextpage.setToolTip("下一页/next page \n ctrl+click=新建下一页/create next page to the view")
        self.addToGroup(self.button_zoomin)
        self.addToGroup(self.button_zoomout)
        self.addToGroup(self.button_prevpage)
        self.addToGroup(self.button_nextpage)
        self.addToGroup(self.button_close)
        p = QPointF(0,0)
        self.button_zoomin.setPos(p)
        p = p+QPointF(self.button_zoomin.boundingRect().width()+10,0)
        self.button_zoomout.setPos(p)
        p = p + QPointF(self.button_zoomout.boundingRect().width()+10, 0)
        self.button_prevpage.setPos(p)
        p = p + QPointF(self.button_prevpage.boundingRect().width()+10, 0)
        self.button_nextpage.setPos(p)
        p = p + QPointF(self.button_nextpage.boundingRect().width()+10, 0)
        self.button_close.setPos(p)
        self.width = p.x()+self.button_close.boundingRect().width()
        self.height = self.button_zoomin.boundingRect().height()

    def boundingRect(self) -> QtCore.QRectF:

        return QRectF(0,0,self.width,self.height)

class PageItemGroup(QGraphicsItemGroup):
    """
        page_itself+PageToolsBar
    """
    def __init__(self, doc, pagenum,  pixmap :'QPixmap' , parent=None,root=None):
        super().__init__(parent=parent)
        self.root=root
        self.mouse_last_posi=None
        self.doc=doc
        self.pagenum = pagenum
        self.pageview = ClipperPixmapItem(doc, pagenum,pixmap)
        self.page_tools_bar=PageToolsBar(doc,pagenum,self.pageview)
        self.addToGroup(self.pageview)
        self.addToGroup(self.page_tools_bar)
        self.init_position()

    def init_position(self):
        x=self.pageview.boundingRect().width()/2-self.page_tools_bar.boundingRect().width()/2
        y=self.pageview.boundingRect().height()
        self.page_tools_bar.setPos(x,y)
        self.update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier:
            self.setCursor(Qt.Qt.CrossCursor)
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
            print("")
        else:
            super().mouseReleaseEvent(event)
        pass
    def wheelEvent(self, event: 'QGraphicsSceneWheelEvent') -> None:
        modifiers = QApplication.keyboardModifiers()
        if self.pageview.contains(event.pos()) and modifiers == QtCore.Qt.ControlModifier :
            self.setCursor(Qt.Qt.SizeFDiagCursor)
            self.pageview.wheelEvent(event)
            self.init_position()
        else:
            super().wheelEvent(event)
        pass
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        super().keyPressEvent(event)
    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key()==Qt.Qt.Key_Control:
            self.setCursor(Qt.Qt.ArrowCursor)
    def boundingRect(self) -> QtCore.QRectF:
        width =self.pageview.boundingRect().width() if self.pageview.boundingRect().width() > \
                                                       self.page_tools_bar.boundingRect().width() else \
                                                        self.page_tools_bar.boundingRect().width()
        height= self.pageview.boundingRect().height()
        return QRectF(self.pageview.x(),self.pageview.y(),width,height)


class ClipperPixmapItem(QGraphicsPixmapItem):
    def __init__(self,doc,pagenum,pixmap):
        super().__init__(pixmap)
        self._delta=0.1
        self.ratio = 1
        self.doc=doc
        self.pagenum=pagenum
        self.width = self.pixmap().width()
    def wheelEvent(self, event):
        modifiers = QApplication.keyboardModifiers() #判断ctrl键是否按下

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
        self.ratio=self.ratio*(1+self._delta)
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
        p = pixmap_page_load(self.doc,self.pagenum,factor)
        self.setPixmap(p)
        self.update()
    pass

class PDFViewPort(QGraphicsView):
    def __init__(self,scene,parent=None,*args,**kwargs):
        super().__init__(scene,parent=parent)
        self.parent= parent
        self._delta = 0.1
        self.setRenderHints(QPainter.Antialiasing | #抗锯齿
                            QPainter.HighQualityAntialiasing | #高精度抗锯齿
                            QPainter.SmoothPixmapTransform) # 平滑过渡 渲染设定
        self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
        self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图

    def init_ratio(self):
        """保存最初建立的体系"""
        self.init_height = self.height()


def pixmap_page_load(doc, pagenum, ratio=1):
    """从self.doc读取page,再转换为pixmap"""
    page = doc.load_page(pagenum)  # 加载的是页面
    print(ratio.__str__())
    pix = page.getPixmap(matrix=fitz.Matrix(ratio,ratio))  # 将页面渲染为图片
    fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888  # 渲染的格式
    pageImage = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
    pixmap = QPixmap()
    pixmap.convertFromImage(pageImage)  # 转为pixmap
    return QPixmap(pixmap)


class PDFReader(QMainWindow):
    def __init__(self, PDFpath):
        super().__init__()
        self.doc = fitz.open(PDFpath)  # 加载的是文档
        self.init_UI()
        self.init_events()
        self.init_view()
        # self.showMaximized()
        self.show()

    def init_view(self):
        page = pixmap_page_load(self.doc,0)
        self.scene_pixmap_add(page)

    def init_events(self):
        self.resizeEvent = self.OnResize

    def init_UI(self):
        # 经验：QGraphicsView 必须放置在 QWidget 中， 才能和其他QWidget 保持正常的大小关系
        self.container0 = QWidget(self) #不能删
        self.scene = QGraphicsScene()
        self.pdfview = PDFViewPort(self.scene,parent=self)
        self.rightsidebar = RightSideBar()
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.pdfview)
        self.h_layout.addWidget(self.rightsidebar)
        self.h_layout.setStretch(0,1)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))
        self.container0.resize(self.width(),self.height())
        self.container0.setLayout(self.h_layout)

    def OnResize(self, *args):
        self.container0.resize(self.width(),self.height())
        pass

    def scene_pixmap_add(self, pixmap):
        self.item_page = PageItemGroup(self.doc,0,pixmap,root=self)
        self.scene.addItem(self.item_page)
        self.item_page.setFlag(QGraphicsItem.ItemIsMovable)
        self.item_page.setFlag(QGraphicsPixmapItem.ItemIsFocusable)
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    reader = PDFReader("./resource/徐森林_数学分析_第8章.pdf")
    sys.exit(app.exec_())
