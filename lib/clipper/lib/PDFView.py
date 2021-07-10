import time

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF, QPointF, QLineF, QPoint, QRect
from PyQt5.QtGui import QPainter, QIcon, QKeySequence
from PyQt5.QtWidgets import QGraphicsView, QToolButton, QGraphicsProxyWidget, QGraphicsGridLayout, QGraphicsItem, \
    QShortcut, QApplication

from .tools import events, objs, ALL, funcs


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
        self.curr_rubberBand_rect = None
        self.on_clipbox_create_sended = False
        self.reset_ratio_value = 1
        self._delta = 0.1
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                            QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
                            QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
        self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
        self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图
        self.setDragMode(self.ScrollHandDrag)
        self.setCursor(Qt.ArrowCursor)
        self.curr_selected_item = None
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.event_dict = {
            ALL.signals.on_pageItem_resize_event: self.on_pageItem_resize_event_handle,
            ALL.signals.on_rightSideBar_buttonGroup_clicked: self.on_rightSideBar_buttonGroup_clicked_handle,
            ALL.signals.on_pageItem_needCenterOn: self.on_pageItem_needCenterOn_handle,
            ALL.signals.on_pageItem_centerOn_process: self.on_pageItem_centerOn_process_handle,
            self.rubberBandChanged: self.on_rubberBandChanged_handle,
            ALL.signals.on_pageItem_clicked: self.on_pageItem_clicked_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
        self.init_shortcuts()

    def on_pageItem_clicked_handle(self, event: "events.PageItemClickEvent"):
        if event.Type == event.rightClickType:
            self.curr_selected_item = event.pageitem
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.CrossCursor)

    def on_pageItem_centerOn_process_handle(self, event: "events.PageItemCenterOnProcessEvent"):
        self.centerOn(event.centerpos)

    def on_rightSideBar_buttonGroup_clicked_handle(self, event: 'events.RightSideBarButtonGroupEvent'):
        if event.Type == event.resetViewRatioType:
            self.viewRatioReset()

    def on_pageItem_needCenterOn_handle_(self, event: "events.PageItemNeedCenterOnEvent"):
        if event.Type == event.centerOnType:
            origin_pos = self.mapToScene(self.pos())
            dest_pos = event.pageitem.mapToScene(event.pageitem.pos())
            delta_pos = dest_pos - origin_pos

            self.update()

    def on_rubberBandChanged_handle(self, viewportRect, fromScenePoint, toScenePoint):
        self.scene().clearSelection()
        if self.curr_rubberBand_rect is not None and not self.on_clipbox_create_sended:
            e = events.ClipboxCreateEvent
            ALL.signals.on_clipbox_create.emit(e(eventType=e.rubbingType, sender=self))
            self.on_clipbox_create_sended = True
        if viewportRect:  # 空的rect不要
            self.curr_rubberBand_rect = viewportRect
            # print(f"viewportRect={viewportRect},fromScenePoint={fromScenePoint},toScenePoint={toScenePoint}")
            pass

    def on_pageItem_needCenterOn_handle(self, event: "events.PageItemNeedCenterOnEvent"):

        if event.Type == event.centerOnType:
            # print(self.frameRect())
            origin_center = QPointF(
                self.pos().x() + self.frameRect().width() / 2,
                self.pos().y() + self.frameRect().height() / 2
            )
            item_center_pos = QPointF(
                event.pageitem.pos().x() + self.width() / 2,
                event.pageitem.pos().y() + self.height() / 2
            )
            count = 15
            deltapoint = item_center_pos - origin_center

            for i in range(count):
                QApplication.processEvents()
                centerpos = QPointF(
                    origin_center.x() + deltapoint.x() / count * i,
                    origin_center.y() + deltapoint.y() / count * i
                )
                e = events.PageItemCenterOnProcessEvent
                ALL.signals.on_pageItem_centerOn_process.emit(
                    e(centerpos=centerpos)
                )
                time.sleep(0.001)
            # QApplication.processEvents()
            # self.centerOn(item_center_pos)

    def on_pageItem_resize_event_handle(self, event: "events.PageItemResizeEvent"):
        """无论是全屏,还是恢复,都需要centerOn"""
        e = events.PageItemNeedCenterOnEvent
        ALL.signals.on_pageItem_needCenterOn.emit(
            e(eventType=e.centerOnType, pageitem=event.pageItem)
        )
        pass

    def init_shortcuts(self):
        QShortcut(QKeySequence("ctrl+-"), self, activated=lambda: self.scale(1 / 1.1, 1 / 1.1))
        QShortcut(QKeySequence("ctrl+="), self, activated=lambda: self.scale(1.1, 1.1))

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() == Qt.RightButton:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            funcs.show_clipbox_state()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # print(self.scene().selectedItems())
        super().mouseMoveEvent(event)
        pass

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.curr_selected_item is not None and self.curr_rubberBand_rect is not None:
            r = self.curr_rubberBand_rect
            pos = self.mapToScene(r.x(), r.y())
            x, y, w, h = pos.x(), pos.y(), r.width(), r.height()
            e = events.PageItemRubberBandRectSendEvent
            ALL.signals.on_pageItem_rubberBandRect_send.emit(
                e(sender=self.curr_selected_item, eventType=e.oneType, rubberBandRect=QRectF(x, y, w, h)))
            self.curr_selected_item = None
            self.curr_rubberBand_rect = None
            e = events.ClipboxCreateEvent
            ALL.signals.on_clipbox_create.emit(e(sender=self, eventType=e.rubbedType))

        super().mouseReleaseEvent(event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        e = events.ClipboxStateSwitchEvent

        ALL.signals.on_clipboxstate_switch.emit(
            e(sender=self, eventType=e.hideType)
        )

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        modifiers = QApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            e = events.PDFViewResizeViewEvent
            if event.angleDelta().y() > 0:
                self.scale(1.1, 1.1)
                self.reset_ratio_value *= 1.1
                ALL.signals.on_PDFView_ResizeView.emit(
                    e(eventType=e.zoomInType, pdfview=self, ratio=self.reset_ratio_value))
            else:
                self.scale(1 / 1.1, 1 / 1.1)
                self.reset_ratio_value /= 1.1
                ALL.signals.on_PDFView_ResizeView.emit(
                    e(eventType=e.zoomOutType, pdfview=self, ratio=self.reset_ratio_value))
        else:
            super().wheelEvent(event)
        pass

    def viewRatioReset(self):
        self.scale(1 / self.reset_ratio_value, 1 / self.reset_ratio_value)
        e = events.PDFViewResizeViewEvent
        ALL.signals.on_PDFView_ResizeView.emit(
            e(eventType=e.RatioResetType, pdfview=self, ratio=1 / self.reset_ratio_value))
        self.reset_ratio_value = 1

    # def paintEvent(self, event: QtGui.QPaintEvent) -> None:
    #     if len(self.scene().selectedItems())==0:
    #         self.setDragMode(QGraphicsView.ScrollHandDrag)
    #     else:
    #         self.setDragMode(QGraphicsView.NoDrag)
    #     super().paintEvent(event)


if __name__ == "__main__":
    pass
