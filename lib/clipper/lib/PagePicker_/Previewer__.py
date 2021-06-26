from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGraphicsView, QGraphicsItem, QGraphicsScene, QWidget, QGraphicsPixmapItem, QToolButton, \
    QComboBox, QHBoxLayout, QLabel
from ..tools import events, funcs, objs, ALL


class Item(QGraphicsItem):
    pass


class Scene(QGraphicsScene):
    """Scene和Item一样大,需要限制"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.previewer = parent

    pass


class View(QGraphicsView):
    """打开drag功能"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.previewer = parent
        self.setScene(self.previewer.scene)
        self.setDragMode(self.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        e = events.PagePickerPreviewerRatioAdjustEvent
        if event.angleDelta().y() < 0:
            type = e.ZoomInType
        else:
            type = e.ZoomOutType
        ALL.signals.on_pagepicker_previewer_ratio_adjust.emit(
            e(sender=self, eventType=type)
        )

    pass


class ToolsBar(QWidget):
    """上下页,放大缩小,切换"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.zoomin_button = QToolButton(self)
        self.zoomout_button = QToolButton(self)
        self.nextpage_button = QToolButton(self)
        self.prevpage_button = QToolButton(self)
        self.pagenum_label = QLabel(self)
        self.loadplace_switch = objs.GridHDescUnit(parent=self, labelname="切换到/switch to", widget=QComboBox())
        self.widgetli = [self.loadplace_switch, self.zoomin_button, self.zoomout_button, self.prevpage_button,
                         self.nextpage_button]
        self.imgLi = [None, objs.SrcAdmin.imgDir.zoomin, objs.SrcAdmin.imgDir.zoomout, objs.SrcAdmin.imgDir.prev,
                      objs.SrcAdmin.imgDir.next]
        self.sequenceli = [0, 1, 2, 3, 4]
        self.init_UI()

    def init_UI(self):
        H_layout = QHBoxLayout(self)
        for i in self.sequenceli:
            H_layout.addWidget(self.widgetli[i])
            if i != 0:
                w: "QToolButton" = self.widgetli[i]
                w.setIcon(QIcon(self.imgLi[i]))
                H_layout.setStretch(i, 1)
        self.setLayout(H_layout)

    def init_events(self):
        self.nextpage_button.clicked.connect(self.on_nextpage_button_clicked_handle)

    def on_nextpage_button_clicked_handle(self):
        pass

    pass
