import math

from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt5.QtGui import QColor, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QPointF


class Edge:

    def __init__(self, scene, start_item, end_item):
        super().__init__()
        self.scene = scene
        self.start_item = start_item
        self.end_item = end_item

        self.gr_edge = GraphicEdge(self)
        # add edge on graphic scene
        self.scene.add_edge(self.gr_edge)

        if self.start_item is not None:
            self.update_positions()

    def store(self):
        self.scene.add_edge(self.gr_edge)

    def update_positions(self):
        patch = self.start_item.width / 2
        src_pos = self.start_item.pos()
        self.gr_edge.set_src(src_pos.x()+patch, src_pos.y()+patch)
        if self.end_item is not None:
            end_pos = self.end_item.pos()
            self.gr_edge.set_dst(end_pos.x()+patch, end_pos.y()+patch)
        else:
            self.gr_edge.set_dst(src_pos.x()+patch, src_pos.y()+patch)
        self.gr_edge.update()

    def remove_from_current_items(self):
        self.end_item = None
        self.start_item = None

    def remove(self):
        self.remove_from_current_items()
        self.scene.remove_edge(self.gr_edge)
        self.gr_edge = None


class GraphicEdge(QGraphicsPathItem):

    def __init__(self, edge_wrap, parent=None):
        super().__init__(parent)
        self.edge_wrap = edge_wrap
        self.width = 3.0
        self.pos_src = [0, 0]
        self.pos_dst = [0, 0]

        self._pen = QPen(QColor("#000"))
        self._pen.setWidthF(self.width)

        self._pen_dragging = QPen(QColor("#000"))
        self._pen_dragging.setStyle(Qt.DashDotLine)
        self._pen_dragging.setWidthF(self.width)

        self._mark_pen = QPen(Qt.green)
        self._mark_pen.setWidthF(self.width)
        self._mark_brush = QBrush()
        self._mark_brush.setColor(Qt.green)
        self._mark_brush.setStyle(Qt.SolidPattern)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def set_src(self, x, y):
        self.pos_src = [x, y]

    def set_dst(self, x, y):
        self.pos_dst = [x, y]

    def calc_path(self):
        path = QPainterPath(QPointF(self.pos_src[0], self.pos_src[1]))
        path.lineTo(self.pos_dst[0], self.pos_dst[1])
        return path

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calc_path()

    def paint(self, painter, graphics_item, widget=None):
        self.setPath(self.calc_path())
        path = self.path()
        if self.edge_wrap.end_item is None:
            painter.setPen(self._pen_dragging)
            painter.drawPath(path)
        else:
            x1, y1 = self.pos_src
            x2, y2 = self.pos_dst
            radius = 5    # marker radius
            length = 70   # marker length
            k = math.atan2(y2 - y1, x2 - x1)
            new_x = x2 - length * math.cos(k) - self.width
            new_y = y2 - length * math.sin(k) - self.width

            painter.setPen(self._pen)
            painter.drawPath(path)

            painter.setPen(self._mark_pen)
            painter.setBrush(self._mark_brush)
            painter.drawEllipse(new_x, new_y, radius, radius)
