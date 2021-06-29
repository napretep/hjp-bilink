import time

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QPoint
from PyQt5.QtGui import QPainter, QIcon, QKeySequence
from PyQt5.QtWidgets import QGraphicsView, QToolButton, QGraphicsProxyWidget, QGraphicsGridLayout, QGraphicsItem, \
    QShortcut, QApplication

from .tools import events, objs, ALL


class PDFView(QGraphicsView):
    """
    pdfviewport和rightsidebar共同构成了两大基础.
    """

    def __init__(self, scene: 'QGraphicsScene', parent=None, clipper=None, *args, **kwargs):
        super().__init__(scene, parent=parent)
        self.parent = parent
        self.clipper = clipper
        self.begin_drag = False
        self.begin_drag_pos = None
        self.reset_ratio_value = 1
        self._delta = 0.1
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
                            QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
        self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
        self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图
        self.setDragMode(self.ScrollHandDrag)
        self.setCursor(Qt.ArrowCursor)
        # self.
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # print(f"viewrect={self.rect()},scenerect={self.sceneRect()},viewWidth={self}")
        self.init_events()
        self.init_shortcuts()

    def init_events(self):
        ALL.signals.on_pageItem_resize_event.connect(self.on_pageItem_resize_event_handle)
        ALL.signals.on_rightSideBar_buttonGroup_clicked.connect(
            self.on_rightSideBar_buttonGroup_clicked_handle)
        ALL.signals.on_pageItem_needCenterOn.connect(self.on_pageItem_needCenterOn_handle)
        ALL.signals.on_pageItem_centerOn_process.connect(self.on_pageItem_centerOn_process_handle)

    def on_pageItem_centerOn_process_handle(self, event: "events.PageItemCenterOnProcessEvent"):
        self.centerOn(event.centerpos)

    def on_rightSideBar_buttonGroup_clicked_handle(self, event: 'events.RightSideBarButtonGroupEvent'):
        if event.Type == event.resetViewRatioType:
            self.viewRatioReset()

    def on_pageItem_needCenterOn_handle_(self, event: "events.PageItemNeedCenterOnEvent"):
        if event.Type == event.centerOnType:
            origin_pos = self.mapToScene(self.pos())
            dest_pos = event.pageitem.mapToScene(event.pageitem.pos())
            delta_pos = dest_pos - origin_pos

            # hbar = self.horizontalScrollBar()
            # vbar = self.verticalScrollBar()
            # hbar.setValue(0)
            # vbar.setValue(0)
            # hbar.setValue(dest_pos.x())
            # vbar.setValue(dest_pos.y())
            self.update()

    def on_pageItem_needCenterOn_handle(self, event: "events.PageItemNeedCenterOnEvent"):

        if event.Type == event.centerOnType:
            # print(self.frameRect())
            origin_center = QPointF(
                self.pos().x() + self.frameRect().width() / 2,
                self.pos().y() + self.frameRect().height() / 2
            )
            item_center_pos = QPointF(
                event.pageitem.pos().x() + self.width() / 2,
                event.pageitem.pos().y() + self.height() / 2
            )
            count = 15
            deltapoint = item_center_pos - origin_center

            for i in range(count):
                QApplication.processEvents()
                centerpos = QPointF(
                    origin_center.x() + deltapoint.x() / count * i,
                    origin_center.y() + deltapoint.y() / count * i
                )
                e = events.PageItemCenterOnProcessEvent
                ALL.signals.on_pageItem_centerOn_process.emit(
                    e(centerpos=centerpos)
                )
                time.sleep(0.001)
            # QApplication.processEvents()
            # self.centerOn(item_center_pos)

    def on_pageItem_resize_event_handle(self, event: "events.PageItemResizeEvent"):
        """无论是全屏,还是恢复,都需要centerOn"""
        e = events.PageItemNeedCenterOnEvent
        ALL.signals.on_pageItem_needCenterOn.emit(
            e(eventType=e.centerOnType, pageitem=event.pageItem)
        )
        # item_center_pos = event.pageItem.pos()
        # item_center_pos = QPointF(
        #     (event.pageItem.pos().x() + self.width() / 2),
        #     event.pageItem.pos().y() + self.height() / 2
        # )
        # self.centerOn(item_center_pos)
        # # self.view_moveto_pos(item_center_pos)

        pass

    # def view_moveto_pos(self,pos:QPointF):
    #     newpos=-(pos-self.pos())
    #     print(newpos)
    #     self.centerOn(item_center_pos)

    def init_shortcuts(self):
        QShortcut(QKeySequence("ctrl+-"), self, activated=lambda: self.scale(1 / 1.1, 1 / 1.1))
        QShortcut(QKeySequence("ctrl+="), self, activated=lambda: self.scale(1.1, 1.1))

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if (event.modifiers() & Qt.ControlModifier) and (event.modifiers() & Qt.ShiftModifier):
            self.setInteractive(False)
            super().mousePressEvent(event)
        else:
            self.setInteractive(True)
            super().mousePressEvent(event)
        # self.scroll(10,10)
        # modifiers = QApplication.keyboardModifiers()
        # if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
        #     self.begin_drag = True
        #     self.begin_drag_pos = event.pos()
        #     self.setCursor(Qt.ClosedHandCursor)
        #     # print(f"鼠标点击----------------------\n位置{self.begin_drag_pos}")
        # else:
        #     # self.centerOn(event.pos())
        #     super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # modifiers = QApplication.keyboardModifiers()
        # if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier) and self.begin_drag:
        #     delta = self.begin_drag_pos - event.pos() + QPointF()
        #     self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y() / 10)
        #     self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x() / 10)
        #     # self.translate(delta.x()/10,delta.y()/10)
        #     self.update()
        # else:
        super().mouseMoveEvent(event)
        pass

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        # if self.begin_drag:
        #     self.begin_drag = False
        #     self.begin_drag_pos = None
        #     self.setCursor(Qt.ArrowCursor)

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            e = events.PDFViewResizeViewEvent
            if event.angleDelta().y() > 0:
                self.scale(1.1, 1.1)
                self.reset_ratio_value *= 1.1
                ALL.signals.on_PDFView_ResizeView.emit(
                    e(eventType=e.zoomInType, pdfview=self, ratio=self.reset_ratio_value))
            else:
                self.scale(1 / 1.1, 1 / 1.1)
                self.reset_ratio_value /= 1.1
                ALL.signals.on_PDFView_ResizeView.emit(
                    e(eventType=e.zoomOutType, pdfview=self, ratio=self.reset_ratio_value))
        else:
            super().wheelEvent(event)
        pass

    def viewRatioReset(self):
        self.scale(1 / self.reset_ratio_value, 1 / self.reset_ratio_value)
        e = events.PDFViewResizeViewEvent
        ALL.signals.on_PDFView_ResizeView.emit(
            e(eventType=e.RatioResetType, pdfview=self, ratio=1 / self.reset_ratio_value))
        self.reset_ratio_value = 1

if __name__ == "__main__":
    pass
