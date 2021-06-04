from PyQt5 import QtCore
from PyQt5.QtWidgets import QGraphicsPixmapItem


class PixmapItem(QGraphicsPixmapItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.setCursor(QtCore.Qt.CrossCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        self.setCursor(QtCore.Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(self.x(), self.y(), self.pixmap().width(), self.pixmap().height())

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        print(self.boundingRect().__str__() + ",eventpos=" + event.pos().__str__())
        if self.contains(event.pos()):
            print("get!")
        else:
            print("no")
        super().mouseMoveEvent(event)
