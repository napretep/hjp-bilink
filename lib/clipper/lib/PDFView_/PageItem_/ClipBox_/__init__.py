from PyQt5.QtCore import QLineF, QPointF, Qt, QRectF
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, QGraphicsItem, QGraphicsEllipseItem, QGraphicsWidget


class ToolsBar(QGraphicsWidget):
    """QAswitchButton,CardSwitchButton,closeButton,EditLine"""

    def __init__(self, model: 'QStandardItemModel' = None, clipbox: 'ClipBox' = None):
        super().__init__()

        pass


class EditLine(QGraphicsItemGroup):
    """专门用来设计input,还没想好怎么写"""

    def __init__(self):
        super().__init__()
        pass



class FramePen(QPen):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        FramePenColor = kwargs.pop("FramePenColor",None)
        if FramePenColor is None:
            FramePenColor=Qt.red
        self.setColor(FramePenColor)
        self.setWidth(4)
class FrameLineItem(QGraphicsLineItem):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        pencolor = kwargs.pop("pencolor",None)
        if pencolor is None:
            self.setPen(FramePen())
        else:
            self.setPen(FramePen(FramePenColor=pencolor))

        self.update()

class FrameCornerItem(QGraphicsEllipseItem):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setBrush(QBrush(Qt.yellow))
        self.update()





class Frame(QGraphicsItemGroup):
    """
    Top,Bottom,Left,Right,TopLeft,TopRight,BottomLeft,BottomRight,
    """

    def __init__(self,pos:'QPointF'=None,):
        super().__init__()
        self.pos=pos
        self.begindelta=50.0 #开始时的矩形大小
        self.delta=0.1
        self.dotRadius=10.0
        self.direction = ["Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"]
        self.posTop, self.posBottom, self.posLeft, self.posRight, self.posTopLeft, self.posTopRight, self.posBottomLeft, self.posBottomRight = \
            "Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"
        self.border_lines = {
            self.posTop:FrameLineItem(QLineF(QPointF(0,0),QPointF(self.begindelta,0))),
            self.posBottom:FrameLineItem(QLineF(QPointF(0,self.begindelta),
                                                QPointF(self.begindelta,self.begindelta))),
            self.posLeft:FrameLineItem(QLineF(QPointF(0,0),QPointF(0,self.begindelta))),
            self.posRight:FrameLineItem(QLineF(QPointF(self.begindelta, 0),
                                               QPointF(self.begindelta, self.begindelta)))}
        self.corner_dots = {
            self.posTopLeft:FrameCornerItem(QRectF(
                - self.dotRadius / 2,  - self.dotRadius / 2,self.dotRadius, self.dotRadius)),
            self.posTopRight:FrameCornerItem(QRectF(
                self.begindelta - self.dotRadius / 2,-self.dotRadius / 2,self.dotRadius, self.dotRadius
            )),
            self.posBottomLeft:FrameCornerItem(QRectF(
                - self.dotRadius / 2,self.begindelta - self.dotRadius / 2,self.dotRadius, self.dotRadius
            )),
            self.posBottomRight:FrameCornerItem(QRectF(
                self.begindelta - self.dotRadius / 2, self.begindelta - self.dotRadius / 2,
                self.dotRadius, self.dotRadius
            ))
        }
        list(map(lambda pair: self.addToGroup(pair[1]), self.border_lines.items()))
        list(map(lambda pair: self.addToGroup(pair[1]), self.corner_dots.items()))

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        count = -1
        for i in range(4):
            if self.dir_lines[i].contains(event.pos()):
                count = i
                print(self.direction[i]+" has been clicked")
        if count>-1:
            pass
        else:
            super().mousePressEvent(event)

    def boundingRect(self) -> QRectF:
        return QRectF(0,0,100,100)
