from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsScene, QWidget, QGraphicsPixmapItem, QToolButton, \
    QComboBox, QHBoxLayout, QLabel
from ..tools import events, funcs, objs, ALL


class Item(QGraphicsPixmapItem):
    mousecenter = 0
    viewcenter = 1

    def __init__(self, view: "View" = None):
        super().__init__()
        self.view = view
        path = funcs.pixmap_page_load(self.view.pdfname, self.view.pagenum, self.ratio_get())
        self.setPixmap(QPixmap(path))
        # self.ratio = 1

    def ratio_get(self):
        return self.view.previewer.pagepicker.ratio_value_get()

    def ratio_set(self, value):
        self.view.previewer.pagepicker.ratio_value_set(value)

    def view_center_pos_get(self):
        centerpos = QPointF(self.view.size().width() / 2, self.view.size().height() / 2)
        self.view_center_scene_p = self.view.mapToScene(centerpos.toPoint())
        p = self.mapFromScene(self.view_center_scene_p)
        self.view_center_item_p = [p.x() / self.boundingRect().width(), p.y() / self.boundingRect().height()]

    def mouse_center_pos_get(self, pos):
        self.mouse_center_item_p = [pos.x() / self.boundingRect().width(),
                                    pos.y() / self.boundingRect().height()]
        self.mouse_center_scene_p = self.mapToScene(pos)

    def wheelEvent(self, event):
        self.mouse_center_pos_get(event.pos())

        if event.delta() > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    def zoomIn(self):
        """放大"""
        ratio = self.ratio_get()
        ratio *= 1.1
        self.zoom(ratio)

    def zoomOut(self):
        """缩小"""
        ratio = self.ratio_get()
        ratio /= 1.1
        self.zoom(ratio)

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
        else:
            raise TypeError(f"无法处理数据:{center}")
        scrollY = self.view.verticalScrollBar()
        scrollX = self.view.horizontalScrollBar()
        # 如果你不打算采用根据图片放大缩小,可以用下面的注释的代码实现scrollbar的大小适应

        print(f"x={dx}, dy={dy}")
        self.view.setSceneRect(self.mapRectToScene(self.boundingRect()))
        scrollY.setValue(scrollY.value() + int(dy))
        scrollX.setValue(scrollX.value() + int(dx))

        self.view_center_scene_p = None
        self.view_center_item_p = None

        # p=  self.mapToScene(QPoint(1,1))
        # print(f"""scrolly={scrollY.value()},rect.height()={rect.height()}""")

    def zoom(self, factor, center=None):
        """缩放
        :param factor: 缩放的比例因子
        """
        if center is None:
            center = self.mousecenter
        _factor = self.transform().scale(
            factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
        if _factor < 0.07 or _factor > 100:
            # 防止过大过小
            return
        if center == self.viewcenter:
            self.view_center_pos_get()
        path = funcs.pixmap_page_load(self.view.pdfname, self.view.pagenum, factor)
        self.setPixmap(QPixmap(path))
        self.ratio_set(factor)
        self.center_zoom(center)

    pass


class Scene(QGraphicsScene):
    """Scene和Item一样大,需要限制"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.previewer = parent
    pass


class View(QGraphicsView):
    """打开drag功能"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.single_item: "Item" = None
        self.previewer = parent
        self.setScene(self.previewer.scene)
        self.setDragMode(self.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                            QPainter.SmoothPixmapTransform)
        self.__event = {
            ALL.signals.on_pagepicker_previewer_ratio_adjust: self.on_pagepicker_previewer_ratio_adjust_handle
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()

    def on_pagepicker_previewer_ratio_adjust_handle(self, event: "events.PagePickerPreviewerRatioAdjustEvent"):
        if self.single_item is not None:
            self.single_item.zoom(event.data, center=self.single_item.viewcenter)

    def init_data(self, pdfname=None, pagenum=None):
        self.pdfname = pdfname
        self.pagenum = pagenum

    # def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
    #     e = events.PagePickerPreviewerRatioAdjustEvent
    #     if event.angleDelta().y() < 0:
    #         type = e.ZoomInType
    #     else:
    #         type = e.ZoomOutType
    #     ALL.signals.on_pagepicker_previewer_ratio_adjust.emit(
    #         e(sender=self, eventType=type)
    #     )

    pass


class ToolsBar(QWidget):
    """上下页,放大缩小,切换"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.zoomin_button = QToolButton(self)
        self.zoomout_button = QToolButton(self)
        self.nextpage_button = QToolButton(self)
        self.prevpage_button = QToolButton(self)
        self.pagenum_label = QLabel(self)
        self.loadplace_switch = objs.GridHDescUnit(parent=self, labelname="切换到/switch to", widget=QComboBox())
        self.widgetli = [self.loadplace_switch, self.zoomin_button, self.zoomout_button, self.prevpage_button,
                         self.nextpage_button]
        self.imgLi = [None, objs.SrcAdmin.imgDir.zoomin, objs.SrcAdmin.imgDir.zoomout, objs.SrcAdmin.imgDir.prev,
                      objs.SrcAdmin.imgDir.next]
        self.sequenceli = [0, 1, 2, 3, 4]
        self.init_UI()

    def init_UI(self):
        H_layout = QHBoxLayout(self)
        for i in self.sequenceli:
            H_layout.addWidget(self.widgetli[i])
            if i != 0:
                w: "QToolButton" = self.widgetli[i]
                w.setIcon(QIcon(self.imgLi[i]))
                H_layout.setStretch(i, 1)
        self.setLayout(H_layout)

    # def init_events(self):
    #     self.nextpage_button.clicked.connect(self.on_nextpage_button_clicked_handle)

    # def on_nextpage_button_clicked_handle(self):
    #     pass

    pass
