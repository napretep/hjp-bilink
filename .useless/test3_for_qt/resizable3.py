from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QGraphicsObject, QGraphicsItem


class BoxItem(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.mousePressPos = None
        self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        # self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.rect = QRect(0, 0, 100, 100)

        self.moving = False
        self.origin = QPoint()

        # # Resizer actions
        # self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
        # self.resizer.resizeSignal.connect(self.resize)

    def corner_rect(self) -> QRect:
        """ Return corner rect geometry """
        return QRect(self.rect.right() - 10, self.rect.bottom() - 10, 10, 10)

    def boundingRect(self) -> QRectF:
        """ Override boundingRect """
        return self.rect.adjusted(-10, -10, 10, 10)

    def paint(self, painter, option, widget=None):
        """ OVerride paint  """

        brush = QBrush(QColor(255, 100, 100, 200))
        brush.setStyle(Qt.Dense7Pattern)
        painter.setBrush(brush)
        painter.drawRect(self.rect)

        if self.isSelected():
            painter.setBrush(QBrush(QColor(Qt.red)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.corner_rect())

            # Draw selection
            pen = QPen(QColor(Qt.green))
            pen.setStyle(Qt.DotLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.rect)

        self.update()

    def hoverMoveEvent(self, event: QMouseEvent):
        """ Override hover move Event : Display cursor """

        if self.isSelected() & self.corner_rect().contains(event.pos().toPoint()):
            self.setCursor(Qt.SizeFDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        super().hoverMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """ override mouse Press Event """
        if self.isSelected() & self.corner_rect().contains(
                QPoint(event.pos().toPoint())
        ):
            self.moving = True
            self.origin = self.rect.topLeft()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ Override mouse release event """
        self.moving = False
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """ Override mouse move event """
        if self.moving:
            # If moving is set from mousePressEvent , change geometry
            self.prepareGeometryChange()

            pos = event.pos().toPoint()

            if pos.x() >= self.origin.x():
                self.rect.setRight(pos.x())
            else:
                self.rect.setLeft(pos.x())

            if pos.y() >= self.origin.y():
                self.rect.setBottom(pos.y())
            else:
                self.rect.setTop(pos.y())
            self.rect = self.rect.normalized()
            self.update()
            return
        else:
            super().mouseMoveEvent(event)
