from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsScene, QWidget, QGraphicsPixmapItem


class Item(QGraphicsItem):
    pass


class Scene(QGraphicsPixmapItem):
    """Scene和Item一样大,需要限制"""
    pass


class View(QGraphicsView):
    """打开drag功能"""
    pass


class ToolsBar(QWidget):
    """上下页,放大缩小"""
    pass
