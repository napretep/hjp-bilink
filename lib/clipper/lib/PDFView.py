from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView


class PDFView(QGraphicsView):
    """
    pdfviewport和rightsidebar共同构成了两大基础.
    """
    def __init__(self, scene, parent=None, *args, **kwargs):
        super().__init__(scene, parent=parent)
        self.parent = parent
        self._delta = 0.1
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
                            QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
        self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
        self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图

    def init_ratio(self):
        """保存最初建立的体系"""
        self.init_height = self.height()


if __name__ == "__main__":
    pass