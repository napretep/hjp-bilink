from PyQt5 import QtGui
from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtWidgets import QGraphicsView, QToolButton, QGraphicsProxyWidget, QGraphicsGridLayout, QGraphicsItem


class PDFView(QGraphicsView):
    """
    pdfviewport和rightsidebar共同构成了两大基础.
    """

    def __init__(self, scene: 'QGraphicsScene', parent=None, *args, **kwargs):
        super().__init__(scene, parent=parent)
        self.parent = parent
        self._delta = 0.1
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
                            QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
        self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
        self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图


if __name__ == "__main__":
    pass