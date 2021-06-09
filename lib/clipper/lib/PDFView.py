from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt5.QtGui import QPainter, QIcon, QKeySequence
from PyQt5.QtWidgets import QGraphicsView, QToolButton, QGraphicsProxyWidget, QGraphicsGridLayout, QGraphicsItem, \
    QShortcut, QApplication


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
        self.scale_times = 0
        self._delta = 0.1
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
                            QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
        self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
        self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图
        # self.
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # print(f"viewrect={self.rect()},scenerect={self.sceneRect()},viewWidth={self}")
        self.init_shortcuts()

    def init_shortcuts(self):
        QShortcut(QKeySequence("ctrl+-"), self, activated=lambda: self.scale(1 / 1.1, 1 / 1.1))
        QShortcut(QKeySequence("ctrl+="), self, activated=lambda: self.scale(1.1, 1.1))

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        # self.scroll(10,10)
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            self.begin_drag = True
            self.begin_drag_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            # print(f"鼠标点击----------------------\n位置{self.begin_drag_pos}")
        else:
            # self.centerOn(event.pos())
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier) and self.begin_drag:
            delta = self.begin_drag_pos - event.pos() + QPointF()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + delta.y() / 10)
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta.x() / 10)
            # self.translate(delta.x()/10,delta.y()/10)
            self.update()


        else:
            super().mouseMoveEvent(event)
        pass

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.begin_drag:
            self.begin_drag = False
            self.begin_drag_pos = None
            self.setCursor(Qt.ArrowCursor)

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            self.scale_times += event.angleDelta().y() / 120
            if event.angleDelta().y() > 0:
                self.scale(1.1, 1.1)
            else:
                self.scale(1 / 1.1, 1 / 1.1)
            pass
        else:
            super().wheelEvent(event)
        pass

if __name__ == "__main__":
    pass