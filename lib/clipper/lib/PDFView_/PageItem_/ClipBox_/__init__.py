from PyQt5.QtCore import QLineF, QPointF, Qt, QRectF
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsLineItem, QGraphicsItem


class ToolsBar(QGraphicsItemGroup):
    """QAswitchButton,CardSwitchButton,position(x,y,w,h),closeButton"""

    def __init__(self):
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
        self.setWidth(30)



class Frame(QGraphicsItemGroup):
    """
    Top,Bottom,Left,Right,TopLeft,TopRight,BottomLeft,BottomRight,
    """

    def __init__(self):
        super().__init__()
        self.direction = ["Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"]

        self.Top, self.Bottom, self.Left, self.Right, self.TopLeft, self.TopRight, self.BottomLeft, self.BottomRight = \
            "Top", "Bottom", "Left", "Right", "TopLeft", "TopRight", "BottomLeft", "BottomRight"
        self.border_lines = {self.Top:QLineF(QPointF(0,0),QPointF(100,0)), self.Bottom:QLineF(QPointF(0,100),QPointF(100,100)),
                       self.Left:QLineF(QPointF(0,0),QPointF(0,100)), self.Right:QLineF(QPointF(100,0),QPointF(100,100))}
        self.dir_lines = list(map(lambda x:QGraphicsLineItem(),self.direction[0:4]))
        list(map(lambda x: self.init_frame_lines(x),range(4)))
    def init_frame_lines(self,num):
        self.dir_lines[num].setPen(FramePen())
        self.dir_lines[num].setLine(self.border_lines[self.direction[num]])
        self.dir_lines[num].setFlag(QGraphicsItem.ItemIsMovable)
        self.addToGroup(self.dir_lines[num])

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.contains(event.pos()):
            print("frame")
        else:
            super().mousePressEvent(event)

    def boundingRect(self) -> QRectF:
        return QRectF(0,0,100,100)
