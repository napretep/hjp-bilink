import sys
import typing

import uuid
from typing import Union

from PyQt5 import QtGui
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QRectF, QPointF, QPoint, QRect, QLineF
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPen, QColor, QBrush, QPainterPathStroker, QPainterPath
from PyQt5.QtWidgets import QDialog, QGraphicsSceneHoverEvent, QWidget, QGraphicsView, QVBoxLayout, QHBoxLayout, \
    QApplication, QGraphicsScene, \
    QGraphicsPixmapItem, QGraphicsRectItem, QCheckBox, QSlider, QLabel, QToolButton, QSpinBox, QStyleOptionGraphicsItem, \
    QGraphicsSceneMouseEvent, QMainWindow

if __name__ == "__main__":
    # from lib.clipper.lib.fitz import fitz
    from lib.obj import clipper_imports
else:
    # from ..clipper.lib.fitz import fitz
    from ..obj import clipper_imports

fitz = clipper_imports.fitz
print, _ = clipper_imports.funcs.logger(__name__)


def get_uuid(pdfname: str, pagenum: int) -> str:
    """
    """
    return str(uuid.uuid3(uuid.NAMESPACE_URL, pdfname + str(pagenum)))


class PDFPrevDialog(QDialog):
    """
    leftside_bookmark
    bottom_toolsbar
    center_view
    """
    on_page_changed = pyqtSignal(object)
    on_page_added = pyqtSignal(object)

    class AllEvent(QObject):
        def __init__(self, eventType=None, sender=None):
            super().__init__()
            self.Type = eventType
            self.sender = sender

    class PageChangedEvent(AllEvent):
        WheelType = 0
        SliderType = 1

        def __init__(self, eventType=None, sender=None, data=None):
            super().__init__(eventType, sender)
            self.data = data

    class LeftSideBookmark(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)

        pass

    class BottomToolsBar(QWidget):
        class PageSlider(QSlider):
            def __init__(self, *args, parent=None):
                super().__init__(*args, parent=parent)
                self.bottomtoolsbar = parent

            # def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
            #     self.bottomtoolsbar.pdfprevdialog.on_page_changed.emit(self.value())

        class API(QObject):
            def __init__(self, parent: "PDFPrevDialog.BottomToolsBar" = None):
                super().__init__(parent)
                self.bottomtoolsbar = parent
                self.label_pagenum_setText = self.bottomtoolsbar.widget_label_pagenum_setText
                self.slider_page_setValue = self.bottomtoolsbar.widget_slider_page_setValue

            @property
            def label_pagenum_text(self):
                return self.bottomtoolsbar.widget_label_pagenum.text()

            @property
            def slider_page_value(self):
                return self.bottomtoolsbar.widget_slider_page.value()

        def __init__(self, parent: "PDFPrevDialog" = None):
            super().__init__(parent)
            self.icon_fit_width = QIcon(clipper_imports.objs.SrcAdmin.imgDir.fit_in_width)
            self.icon_fit_height = QIcon(clipper_imports.objs.SrcAdmin.imgDir.fit_in_height)
            self.icon_single_page = QIcon(clipper_imports.objs.SrcAdmin.imgDir.singlepage)
            self.icon_double_page = QIcon(clipper_imports.objs.SrcAdmin.imgDir.doublepage)
            self.icon_bookmark = QIcon(clipper_imports.objs.SrcAdmin.imgDir.bookmark)
            self.pdfprevdialog = parent
            self.widget_spinbox_pageshift = QSpinBox(self)
            self.widget_button_bookmark = QToolButton(self)
            self.widget_button_double_page = QToolButton(self)
            # self.widget_button_zoom_enable = QToolButton(self)
            self.widget_button_fit_width = QToolButton(self)
            self.widget_button_fit_height = QToolButton(self)
            # self.widget_button_clipbox=QToolButton(self)
            # self.double_side= clipper_imports.objs.GridHDescUnit(
            #     parent=self,labelname="double side",widget=self.double_side_widget)
            self.widget_label_pagenum = QLabel(self)
            self.widget_slider_page = self.PageSlider(Qt.Horizontal, parent=self)
            self.api = self.API(parent=self)
            self._event = {
                self.widget_button_fit_width.clicked: self.on_widget_button_fit_width_clicked_handle,
                self.widget_button_fit_height.clicked: self.on_widget_button_fit_height_clicked_handle,
                self.widget_slider_page.valueChanged: self.on_widget_slider_page_valueChanged_handle,
                self.widget_button_double_page.clicked: self.on_widget_button_double_page_clicked_handle,
                self.widget_button_bookmark.clicked: self.on_widget_button_bookmark_clicked_handle,
                self.pdfprevdialog.on_page_changed: self.on_pdfprevdialog_page_changed,

            }
            self.all_event = clipper_imports.objs.AllEventAdmin(self._event)
            self.all_event.bind()
            self.init_UI()

        def on_widget_button_fit_height_clicked_handle(self):
            self.pdfprevdialog.api.fit_in_policy_set(self.pdfprevdialog.api.fit_in_height)
            self.pdfprevdialog.center_view.api.fit_in()

        def on_widget_button_fit_width_clicked_handle(self):
            self.pdfprevdialog.api.fit_in_policy_set(self.pdfprevdialog.api.fit_in_width)
            self.pdfprevdialog.center_view.api.fit_in()
            pass

        def on_widget_button_double_page_clicked_handle(self):
            if self.widget_button_double_page.text() == "1":
                self.widget_button_double_page.setText("2")
                self.widget_button_double_page.setIcon(self.icon_double_page)
                self.widget_button_double_page.setToolTip("display double page")
                self.pdfprevdialog.api.add_page()
            else:
                self.widget_button_double_page.setText("1")
                self.widget_button_double_page.setIcon(self.icon_single_page)
                self.widget_button_double_page.setToolTip("display single page")
                self.pdfprevdialog.api.del_page()

        def on_widget_slider_page_valueChanged_handle(self, value):
            e = self.pdfprevdialog.PageChangedEvent
            e = e(eventType=e.SliderType, data=value)
            self.pdfprevdialog.api.on_page_changed.emit(e)

        def on_widget_button_bookmark_clicked_handle(self):
            print("yes")

        def on_pdfprevdialog_page_changed(self, event: "PDFPrevDialog.PageChangedEvent"):
            if event.Type != event.SliderType:
                self.api.slider_page_setValue(event.data)
            self.api.label_pagenum_setText(event.data)

        def widget_slider_page_setValue(self, value):
            self.widget_slider_page.setValue(value)
            self.pdfprevdialog.api.curr_pagenum_set(value)

        def widget_label_pagenum_setText(self, value1, value2=None):
            if value2 is None:
                value2 = self.pdfprevdialog.pageshift + value1
            self.widget_label_pagenum.setText(f"pdf(book) page at {value1}({value2})")
            self.pdfprevdialog.api.curr_pagenum_set(value1)

        def init_UI(self):
            self.init_page_slider()
            self.init_label_pagenum()
            self.init_double_side_switch()
            self.init_pageshift()
            # self.init_zoom_enable()
            self.init_fit_width_height()
            self.init_bookmark()
            V_layout = QVBoxLayout(self)
            V_layout.addWidget(self.widget_slider_page)
            w_li = [self.widget_button_bookmark, self.widget_button_double_page, self.widget_button_fit_width,
                    self.widget_button_fit_height, self.widget_spinbox_pageshift,
                    self.widget_label_pagenum]
            H_layout = QHBoxLayout(self)
            for w in w_li:
                H_layout.addWidget(w)
            V_layout.addLayout(H_layout)
            self.setLayout(V_layout)

        def init_bookmark(self):
            self.widget_button_bookmark.setIcon(self.icon_bookmark)

        def init_pageshift(self):
            self.widget_spinbox_pageshift.setMaximumWidth(50)
            self.widget_spinbox_pageshift.setValue(self.pdfprevdialog.api.page_shift)

        # def init_zoom_enable(self):
        #     self.widget_button_zoom_enable.setIcon(QIcon(clipper_imports.objs.SrcAdmin.imgDir.mouse_wheel_zoom))
        #     self.widget_button_zoom_enable.setText("1")
        #     self.widget_button_zoom_enable.setToolTip("switchwheel")

        def init_fit_width_height(self):
            self.widget_button_fit_width.setIcon(self.icon_fit_width)
            self.widget_button_fit_width.setText("fit in width")
            self.widget_button_fit_height.setIcon(self.icon_fit_height)
            self.widget_button_fit_height.setText("fit in height")

        def init_double_side_switch(self):
            self.widget_button_double_page.setIcon(QIcon(clipper_imports.objs.SrcAdmin.imgDir.singlepage))
            self.widget_button_double_page.setText("1")
            self.widget_button_double_page.setToolTip("display single page")

        def init_label_pagenum(self):
            self.widget_label_pagenum.setText("pdf(book) page at " + str(self.pdfprevdialog.curr_pagenum))

        def init_page_slider(self):
            pagecount = len(self.pdfprevdialog.doc)
            self.widget_slider_page.setFixedWidth(self.pdfprevdialog.size().width() - 40)
            self.widget_slider_page.setRange(0, pagecount - 1)
            self.widget_slider_page.setSingleStep(1)
            # self.page_slider.setLayoutDirection(Qt.Horizontal)

        def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
            self.widget_slider_page.setFixedWidth(self.pdfprevdialog.size().width() - 40)
            super().resizeEvent(a0)

        pass

    class CenterView(QWidget):

        class View(QGraphicsView):
            class API(QObject):
                def __init__(self, parent: "PDFPrevDialog.CenterView.View"):
                    super().__init__(parent)
                    self.view = parent

                @property
                def mouse_pos(self) -> QPoint:
                    return self.view.mouse_pos

            def __init__(self, parent: "PDFPrevDialog.CenterView" = None):
                super().__init__(parent)
                self.centerview = parent
                self.api = self.API(self)
                self.mouse_pos: "QPoint" = None
                self._event = {
                    self.rubberBandChanged: self.on_rubberBandChanged_handle,
                }
                self.all_event = clipper_imports.objs.AllEventAdmin(self._event)
                self.all_event.bind()
                self.curr_rubberBand_rect = None
                # self.setDragMode()

            def on_rubberBandChanged_handle(self, viewportRect, fromScenePoint, toScenePoint):
                if viewportRect:  # 空的rect不要
                    self.curr_rubberBand_rect = viewportRect

            # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
            #     # print(f"""selfrect={self.rect()},scenerect={self.sceneRect()},size()={self.size()}
            #     # georect={self.geometry()}""")
            #     super().mousePressEvent(event)

            # def rubberBandRect(self) -> QtCore.QRect:

            def resizeEvent(self, event: QtGui.QResizeEvent) -> None:

                # print(f"""selfrect={self.rect()},scenerect={self.sceneRect()},size()={self.size()}
                #                 georect={self.geometry()}""")

                super().resizeEvent(event)

            def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
                if event.modifiers() == Qt.ControlModifier:
                    self.mouse_pos = event.pos()

                super().wheelEvent(event)

            def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
                if event.button() == Qt.RightButton:
                    self.setDragMode(self.RubberBandDrag)

                super().mousePressEvent(event)

            # def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
            #     if event.button() == Qt.RightButton:
            #         self.view.setDragMode(self.view.RubberBandDrag)
            #     super().mousePressEvent(event)

            def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
                super().mouseReleaseEvent(event)
                self.setDragMode(self.ScrollHandDrag)
                curr_selected_item = self.centerview.api.curr_selected_item
                if curr_selected_item is not None and self.curr_rubberBand_rect is not None:
                    r = self.curr_rubberBand_rect
                    pos = self.mapToScene(r.x(), r.y())
                    x, y, w, h = pos.x(), pos.y(), r.width(), r.height()
                    self.centerview.api.addClipbox(QRectF(x, y, w, h))
                    self.curr_rubberBand_rect = None
                    self.centerview.api.curr_selected_item_setValue(None)

                print(self.curr_rubberBand_rect)

        class Scene(QGraphicsScene):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setBackgroundBrush(Qt.black)

        class Page(QGraphicsPixmapItem):
            mousecenter = 0
            viewcenter = 1
            nocenter = 2

            class API(QObject):
                def __init__(self, parent: "PDFPrevDialog.CenterView.Page" = None):
                    super().__init__()
                    self.parent = parent
                    self.change_page = self.parent.change_page
                    self.mousecenter = self.parent.mousecenter
                    self.viewcenter = self.parent.viewcenter
                    self.nocenter = self.parent.nocenter
                    self.zoom = self.parent.zoom
                    self.keep_clipbox_in_postion = parent.keep_clipbox_in_postion

            def __init__(self, *args, parent: "PDFPrevDialog.CenterView" = None):
                super().__init__(*args)
                self.centerview = parent
                self.mouse_center_item_p = None
                self.mouse_center_scene_p = None
                self.view_center_item_p = None
                self.view_center_scene_p = None
                self.api = self.API(self)

            def mouse_center_pos_get(self, pos):
                self.mouse_center_item_p = [pos.x() / self.boundingRect().width(),
                                            pos.y() / self.boundingRect().height()]
                self.mouse_center_scene_p = self.mapToScene(pos)

            def view_center_pos_get(self):
                centerpos = QPointF(self.centerview.view.size().width() / 2, self.centerview.view.size().height() / 2)
                self.view_center_scene_p = self.centerview.view.mapToScene(centerpos.toPoint())
                p = self.mapFromScene(self.view_center_scene_p)
                self.view_center_item_p = [p.x() / self.boundingRect().width(), p.y() / self.boundingRect().height()]

            def wheelEvent(self, event):
                if event.modifiers() == Qt.ControlModifier:
                    self.mouse_center_pos_get(event.pos())
                    if event.delta() > 0:
                        self.zoomIn()
                    else:
                        self.zoomOut()
                    self.centerview.pdfprevdialog.api.fit_in_policy_set(
                        self.centerview.pdfprevdialog.api.fit_in_disabled)
                else:
                    currpage = self.centerview.pdfprevdialog.api.curr_pagenum
                    e = PDFPrevDialog.PageChangedEvent
                    e = e(eventType=e.WheelType)
                    if event.delta() > 0:
                        e.data = currpage - 1
                    else:
                        e.data = currpage + 1
                    totalcount = len(self.centerview.pdfprevdialog.api.doc)
                    if totalcount > e.data >= 0:
                        self.centerview.pdfprevdialog.api.on_page_changed.emit(e)

            def zoomIn(self):
                """放大"""
                ratio = self.centerview.pdfprevdialog.api.pageratio
                ratio *= 1.1
                self.zoom(ratio)

            def zoomOut(self):
                """缩小"""
                ratio = self.centerview.pdfprevdialog.api.pageratio
                ratio /= 1.1
                self.zoom(ratio)

            def center_zoom(self, center=0):
                view_mouse_pos = self.centerview.view.api.mouse_pos
                if center == self.mousecenter:
                    X = self.mouse_center_item_p[0] * self.boundingRect().width()
                    Y = self.mouse_center_item_p[1] * self.boundingRect().height()
                    new_scene_p = self.mapToScene(X, Y)  # page上这一点对应的场景坐标
                    mouse_scene_p = self.centerview.view.mapToScene(view_mouse_pos)
                    dx = new_scene_p.x() - mouse_scene_p.x()
                    dy = new_scene_p.y() - mouse_scene_p.y()
                elif center == self.viewcenter:
                    X = self.view_center_item_p[0] * self.boundingRect().width()
                    Y = self.view_center_item_p[1] * self.boundingRect().height()
                    new_scene_p = self.mapToScene(X, Y)
                    dx = new_scene_p.x() - self.view_center_scene_p.x()
                    dy = new_scene_p.y() - self.view_center_scene_p.y()
                else:
                    raise TypeError(f"无法处理数据:{center}")
                scrollY = self.centerview.view.verticalScrollBar()
                scrollX = self.centerview.view.horizontalScrollBar()
                # 如果你不打算采用根据图片放大缩小,可以用下面的注释的代码实现scrollbar的大小适应

                print(f"x={dx}, dy={dy}")
                # self.centerview.view.setSceneRect(self.mapRectToScene(self.boundingRect()))
                scrollY.setValue(scrollY.value() + int(dy))
                scrollX.setValue(scrollX.value() + int(dx))

                self.view_center_scene_p = None
                self.view_center_item_p = None

                # p=  self.mapToScene(QPoint(1,1))
                # print(f"""scrolly={scrollY.value()},rect.height()={rect.height()}""")

            def zoom(self, factor, center=None):
                """缩放
                :param factor: 缩放的比例因子
                """
                if center is None:
                    center = self.mousecenter
                _factor = self.transform().scale(
                    factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
                if _factor < 0.07 or _factor > 100:
                    # 防止过大过小
                    return
                if center == self.viewcenter:
                    self.view_center_pos_get()
                pagenum = self.centerview.pdfprevdialog.api.curr_pagenum

                self.centerview.api.leftpage.api.change_page(pagenum, ratio=factor)
                if self.centerview.api.rightpage:
                    self.centerview.api.rightpage.api.change_page(pagenum + 1, ratio=factor)
                self.centerview.api.relayoutpage()
                self.centerview.pdfprevdialog.api.pageratio_set(factor)
                if center != self.nocenter:
                    self.center_zoom(center)
                self.centerview.api.leftpage.api.keep_clipbox_in_postion()
                if self.centerview.api.rightpage:
                    self.centerview.api.rightpage.api.keep_clipbox_in_postion()

            def change_page(self, pagenum, pdfname=None, ratio=None):
                if pagenum >= len(self.centerview.pdfprevdialog.api.doc) or pagenum < 0:
                    return
                if pdfname is None:
                    pdfname = self.centerview.pdfprevdialog.api.pdfname
                if ratio is None:
                    ratio = self.centerview.pdfprevdialog.api.pageratio
                path = clipper_imports.funcs.pixmap_page_load(pdfname, pagenum, ratio)
                self.setPixmap(QPixmap(path))

            def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                self.centerview.api.curr_selected_item_setValue(self)
                super().mousePressEvent(event)

            def keep_clipbox_in_postion(self):
                w, h = self.boundingRect().width(), self.boundingRect().height()
                curr_page = self.centerview.pdfprevdialog.api.curr_pagenum
                count = self.centerview.pdfprevdialog.api.pagecount
                if self != self.centerview.api.leftpage:
                    curr_page = self.centerview.pdfprevdialog.api.curr_rightpagenum
                if curr_page in self.centerview.api.clipbox_dict:
                    for box in self.centerview.api.clipbox_dict[curr_page]:
                        box.api.keep_ratio()

        class Clipbox(QGraphicsRectItem):
            linewidth = 10
            toLeft, toRight, toTop, toBottom, toTopLeft, toTopRight, toBottomLeft, toBottomRight = 0, 1, 2, 3, 4, 5, 6, 7

            class API(QObject):
                def __init__(self, parent: "PDFPrevDialog.CenterView.Clipbox"):
                    super().__init__()
                    self.parent = parent
                    self.keep_ratio = parent.keep_ratio

                @property
                def pageratio(self) -> float:
                    return self.parent.pageratio

                def pageratio_setValue(self, value):
                    self.parent.pageratio = value

            def __init__(self, parent: "PDFPrevDialog.CenterView.Page" = None, rect: "QRectF" = None):
                super().__init__(parent)
                self.setParentItem(parent)
                self.atpage = parent
                self.fromrect = rect
                self.isHovered = False
                self.selected_at = None
                self.click_rect = None
                self.click_pos = QPointF()
                self.pageratio = 1
                self.api = self.API(self)
                self.setFlag(self.ItemIsMovable, True)
                self.setFlag(self.ItemIsSelectable, True)
                self.setFlag(self.ItemSendsGeometryChanges, True)
                self.setAcceptHoverEvents(True)

                b = self.atpage.boundingRect()
                if rect.right() > b.right():
                    rect.setRight(b.right())
                if rect.top() < b.top():
                    rect.setTop(b.top())
                if rect.left() < b.left():
                    rect.setLeft(b.left())
                if rect.bottom() > b.bottom():
                    rect.setBottom(b.bottom())
                self.setRect(rect)

            # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            #

            def calc_ratio(self):
                """记录上下左右所处的坐标系的比例，方便放大缩小跟随"""
                max_X, max_Y = self.atpage.boundingRect().right(), self.atpage.boundingRect().bottom()
                fix_x, fix_y = self.pos().x(), self.pos().y()
                top, left, right, bottom = self.rect().top(), self.rect().left(), self.rect().right(), self.rect().bottom()
                self.ratioTop = (top + fix_y) / max_Y
                self.ratioLeft = (left + fix_x) / max_X
                self.ratioBottom = (bottom + fix_y) / max_Y
                self.ratioRight = (right + fix_x) / max_X

            def keep_ratio(self):
                w, h, x, y = self.atpage.boundingRect().width(), self.atpage.boundingRect().height(), self.x(), self.y()
                r = self.rect()
                # R = QRectF(self.ratioLeft * w,self.ratioTop * h,self.ratioRight * w,self.ratioBottom * h)
                r.setTop(self.ratioTop * h - y)
                r.setLeft(self.ratioLeft * w - x)
                r.setBottom(self.ratioBottom * h - y)
                r.setRight(self.ratioRight * w - x)
                # 之所以减原来的x,y可行,是因为图片的放大并不是膨胀放大,每个点都是原来的点,只是增加了一些新的点而已.
                self.setRect(r)

            def cursor_position_check(self, p: "QPointF"):
                rect = self.rect()
                LT, LB = QPointF(rect.left(), rect.top()), QPointF(rect.left(), rect.bottom())
                RT, RB = QPointF(rect.right(), rect.top()), QPointF(rect.right(), rect.bottom())
                linewidth = self.linewidth
                if QLineF(p, LT).length() < linewidth:
                    self.setCursor(Qt.SizeFDiagCursor)  # 主对角线
                elif QLineF(p, LB).length() < linewidth:
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RT).length() < linewidth:
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RB).length() < linewidth:
                    self.setCursor(Qt.SizeFDiagCursor)
                elif abs(p.x() - rect.left()) < linewidth:
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.x() - rect.right()) < linewidth:
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.y() - rect.top()) < linewidth:
                    self.setCursor(Qt.SizeVerCursor)
                elif abs(p.y() - rect.bottom()) < linewidth:
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)

            def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                self.click_pos = p = event.pos()
                rect = self.rect()
                LT, LB = QPointF(rect.left(), rect.top()), QPointF(rect.left(), rect.bottom())
                RT, RB = QPointF(rect.right(), rect.top()), QPointF(rect.right(), rect.bottom())
                linewidth = self.linewidth
                if QLineF(p, LT).length() < linewidth:
                    self.selected_at = self.toTopLeft
                    self.setCursor(Qt.SizeFDiagCursor)  # 主对角线
                elif QLineF(p, LB).length() < linewidth:
                    self.selected_at = self.toBottomLeft
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RT).length() < linewidth:
                    self.selected_at = self.toTopRight
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RB).length() < linewidth:
                    self.selected_at = self.toBottomRight
                    self.setCursor(Qt.SizeFDiagCursor)
                elif abs(p.x() - rect.left()) < linewidth:
                    self.selected_at = self.toLeft
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.x() - rect.right()) < linewidth:
                    self.selected_at = self.toRight
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.y() - rect.top()) < linewidth:
                    self.selected_at = self.toTop
                    self.setCursor(Qt.SizeVerCursor)
                elif abs(p.y() - rect.bottom()) < linewidth:
                    self.selected_at = self.toBottom
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.selected_at = None
                self.click_rect = rect
                super().mousePressEvent(event)

            def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                if self.click_pos is not None and self.selected_at is not None and self.click_rect is not None:
                    # self.setFlag(self.ItemIsMovable,False)
                    pos = event.pos()
                    x_diff = pos.x() - self.click_pos.x()
                    y_diff = pos.y() - self.click_pos.y()
                    rect = QRectF(self.click_rect)
                    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
                    if self.selected_at == self.toTopRight:
                        rect.adjust(0, y_diff, x_diff, 0)
                    elif self.selected_at == self.toTopLeft:
                        rect.adjust(x_diff, y_diff, 0, 0)
                    elif self.selected_at == self.toBottomLeft:
                        rect.adjust(x_diff, 0, 0, y_diff)
                    elif self.selected_at == self.toBottomRight:
                        rect.adjust(0, 0, x_diff, y_diff)
                    elif self.selected_at == self.toTop:
                        rect.adjust(0, y_diff, 0, 0)
                    elif self.selected_at == self.toLeft:
                        rect.adjust(x_diff, 0, 0, 0)
                    elif self.selected_at == self.toBottom:
                        rect.adjust(0, 0, 0, y_diff)
                    elif self.selected_at == self.toRight:
                        rect.adjust(0, 0, x_diff, 0)
                    if rect.width() < self.linewidth:
                        if self.selected_at == self.toLeft:
                            rect.setLeft(rect.right() - self.linewidth)
                        else:
                            rect.setRight(rect.left() + self.linewidth)
                    if rect.height() < self.linewidth:
                        if self.selected_at == self.toTop:
                            rect.setTop(rect.bottom() - self.linewidth)
                        else:
                            rect.setBottom(rect.top() + self.linewidth)
                    self.setRect(rect)
                    self.calc_ratio()
                    self.move_bordercheck()
                else:
                    super().mouseMoveEvent(event)

            def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                self.click_pos = None
                self.click_rect = None
                self.selected_at = None
                # self.setFlag(self.ItemIsMovable,True)
                self.setCursor(Qt.ArrowCursor)
                super().mouseReleaseEvent(event)

            def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                # print('hoverMoveEvent')
                self.isHovered = True
                self.cursor_position_check(event.pos())
                super().hoverMoveEvent(event)

            def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                # print('hoverEnterEvent')
                self.isHovered = True
                self.cursor_position_check(event.pos())
                super().hoverEnterEvent(event)

            def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                # print('hoverLeaveEvent')
                self.isHovered = False
                self.setCursor(Qt.ArrowCursor)
                super().hoverLeaveEvent(event)

            # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            #     self.hide()

            def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                      widget: typing.Optional[QWidget] = ...) -> None:

                pen = QPen(QColor(127, 127, 127), 2.0, Qt.DashLine)
                if self.isHovered or self.isSelected():
                    pen.setWidth(5)
                    painter.setBrush(QBrush(QColor(0, 255, 0, 30)))
                painter.setPen(pen)
                painter.drawRect(self.rect())
                view = self.atpage.centerview.view

                if view.dragMode() == view.RubberBandDrag:
                    self.setFlag(self.ItemIsSelectable, False)
                else:
                    self.setFlag(self.ItemIsSelectable, True)
                if self.isVisible():
                    self.move_bordercheck()
                    self.calc_ratio()
                self.prepareGeometryChange()

            def shape(self):
                """
                shape在boundingRect里面
                """
                strokepath = QPainterPathStroker()
                # print(self.rect())
                path = QPainterPath()
                path.addRect(self.rect())
                if self.isSelected():
                    return path
                else:
                    strokepath.setWidth(2 * self.linewidth)
                    newpath = strokepath.createStroke(path)
                    return newpath

            def move_bordercheck(self):
                """根据是否越界进行一个边界的修正，超出边界就用边界的值代替,同样必须用父类来检测边界"""
                rect = self.rect()
                x, y = self.pos().x(), self.pos().y()
                view_left = 0
                view_top = 0
                view_right = self.atpage.boundingRect().width()
                view_bottom = self.atpage.boundingRect().height()
                if rect.width() > view_right:
                    rect.setWidth(view_right)
                if rect.height() > view_bottom:
                    rect.setHeight(view_bottom)

                top = rect.top() + y
                bottom = rect.bottom() + y
                left = rect.left() + x
                right = rect.right() + x
                if top < view_top:
                    # print("over top")
                    rect.translate(0, view_top - top)
                if left < view_left:
                    # print("over left")
                    rect.translate(view_left - left, 0)
                if view_bottom < bottom:
                    # print("over bottom")
                    rect.translate(0, view_bottom - bottom)
                if view_right < right:
                    # print("over right")
                    rect.translate(view_right - right, 0)
                self.setRect(rect)

        class API(QObject):
            def __init__(self, centerview: "PDFPrevDialog.CenterView" = None):
                super().__init__(centerview)
                self.centerview = centerview
                self.addpage = centerview.addpage
                self.delpage = centerview.delpage
                self.page_dict: "dict[str,PDFPrevDialog.CenterView.Page]" = self.centerview.page_dict
                self.relayoutpage = centerview.relayoutpage
                self.fit_in = centerview.fit_in
                self.clipbox_dict = centerview.clipbox_dict
                self.addClipbox = centerview.addClipbox
                self.showclipbox = centerview.showclipbox
                self.hideclipbox = centerview.hideclipbox

            def curr_selected_item_setValue(self, value):
                self.centerview.curr_selected_item = value

            @property
            def curr_selected_item(self):
                return self.centerview.curr_selected_item

            @property
            def leftpage(self):
                return self.centerview.leftpage

            @property
            def rightpage(self):
                return self.centerview.rightpage

        def __init__(self, parent: "PDFPrevDialog" = None):

            super().__init__(parent)
            self.pdfprevdialog = parent
            self.page_dict: "dict[str,PDFPrevDialog.CenterView.Page]" = {"left": None, "right": None}
            self.leftpage: "PDFPrevDialog.CenterView.Page" = None
            self.rightpage: "PDFPrevDialog.CenterView.Page" = None
            self.curr_selected_item: "PDFPrevDialog.CenterView.Page" = None
            self.clipbox_dict: "dict[int,list[PDFPrevDialog.CenterView.Clipbox]]" = {}
            self.view = self.View(self)
            self.scene = self.Scene(self)
            self.init_UI()
            self.api = self.API(self)

        def init_UI(self):
            self.view.setScene(self.scene)
            V_layout = QVBoxLayout(self)
            V_layout.addWidget(self.view)
            self.setLayout(V_layout)
            self.view.setDragMode(self.view.ScrollHandDrag)
            self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                                     QPainter.SmoothPixmapTransform)

        def addpage(self):
            pdfname = self.pdfprevdialog.api.pdfname
            pagenum = self.pdfprevdialog.api.curr_pagenum
            ratio = self.pdfprevdialog.api.pageratio
            print(f"pagenum={pagenum}")
            if self.leftpage is None:
                pixmap = QPixmap(clipper_imports.funcs.pixmap_page_load(pdfname, pagenum, ratio, callback=print))
                self.leftpage = self.Page(pixmap, parent=self)
                self.scene.addItem(self.leftpage)
            else:
                pixmap = QPixmap(clipper_imports.funcs.pixmap_page_load(pdfname, pagenum + 1, ratio))
                self.rightpage = self.Page(pixmap, parent=self)
                self.scene.addItem(self.rightpage)
                if self.pdfprevdialog.size().width() * 2 < QApplication.desktop().width():
                    self.pdfprevdialog.resize(self.pdfprevdialog.size().width() * 2, self.pdfprevdialog.size().height())
                    if self.pdfprevdialog.pos().x() + self.pdfprevdialog.size().width() > QApplication.desktop().width():
                        m = self.pdfprevdialog.pos().x() + self.pdfprevdialog.size().width() - QApplication.desktop().width()
                        x = self.pdfprevdialog.pos().x() - m
                        self.pdfprevdialog.move(x, self.pdfprevdialog.pos().y())
                else:
                    self.api.fit_in(fit_in_policy=self.pdfprevdialog.api.fit_in_width)
            self.relayoutpage()
            # self.pdfprevdialog.on_page_added.emit(pagenum)

        def delpage(self):
            self.scene.removeItem(self.rightpage)
            self.rightpage = None
            self.pdfprevdialog.resize(int(self.pdfprevdialog.size().width() / 2), self.pdfprevdialog.size().height())
            self.relayoutpage()

        def addClipbox(self, rect: "Union[QRectF,QRect]"):
            pagenum = self.pdfprevdialog.api.curr_pagenum
            totalcount = len(self.pdfprevdialog.api.doc)
            if self.curr_selected_item == self.rightpage and self.rightpage is not None and pagenum + 1 < totalcount:
                pagenum += 1
            r = self.curr_selected_item.mapRectFromScene(rect)
            clipbox = self.Clipbox(parent=self.curr_selected_item, rect=r.normalized())
            if pagenum not in self.clipbox_dict:
                self.clipbox_dict[pagenum] = []
            self.clipbox_dict[pagenum].append(clipbox)

        def fit_in(self, fit_in_policy=None):
            leftpage = self.api.leftpage
            rightpage = self.api.rightpage
            if fit_in_policy is None:
                fit_in_policy = self.pdfprevdialog.api.fit_in_policy

            if fit_in_policy == self.pdfprevdialog.api.fit_in_width:
                if rightpage is not None:
                    width = self.view.width() / 2
                else:
                    width = self.view.width()
                fit_ratio = width / leftpage.boundingRect().width() * self.pdfprevdialog.api.pageratio
                leftpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)
                if rightpage is not None:
                    rightpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)

            elif fit_in_policy == self.pdfprevdialog.api.fit_in_height:
                height = self.height()
                fit_ratio = height / leftpage.boundingRect().height() * self.pdfprevdialog.api.pageratio
                leftpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)
                if rightpage is not None:
                    rightpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)

        def relayoutpage(self):
            self.leftpage.setPos(0, 0)
            if self.rightpage:
                self.rightpage.setPos(self.leftpage.boundingRect().width(), 0)
                self.view.setSceneRect(0, 0, self.leftpage.boundingRect().width() * 2,
                                       self.leftpage.boundingRect().height())
            else:
                self.view.setSceneRect(0, 0, self.leftpage.boundingRect().width(),
                                       self.leftpage.boundingRect().height())

        def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
            self.fit_in()
            super().resizeEvent(a0)

        def hideclipbox(self):
            last_pagenum = self.pdfprevdialog.api.last_pagenum
            if last_pagenum in self.clipbox_dict:
                for clipbox in self.clipbox_dict[last_pagenum]:
                    curr_ratio = self.pdfprevdialog.api.pageratio
                    clipbox.api.pageratio_setValue(curr_ratio)
                    clipbox.hide()
            if self.rightpage:
                last_rightpagenum = self.pdfprevdialog.api.last_rightpagenum
                if last_rightpagenum in self.clipbox_dict:
                    for clipbox in self.clipbox_dict[last_rightpagenum]:
                        curr_ratio = self.pdfprevdialog.api.pageratio
                        clipbox.api.pageratio_setValue(curr_ratio)
                        clipbox.hide()

        def showclipbox(self):
            curr_pagenum: int = self.pdfprevdialog.api.curr_pagenum
            if curr_pagenum in self.clipbox_dict:
                for clipbox in self.clipbox_dict[curr_pagenum]:
                    clipbox.setParentItem(self.leftpage)
                    clipbox.api.keep_ratio()
                    clipbox.show()
            if self.rightpage:
                curr_rightpagenum = self.pdfprevdialog.api.curr_rightpagenum
                if curr_rightpagenum in self.clipbox_dict:
                    for clipbox in self.clipbox_dict[curr_rightpagenum]:
                        clipbox.setParentItem(self.rightpage)
                        clipbox.api.keep_ratio()
                        clipbox.show()

        pass

    class API(QObject):
        def __init__(self, parent: "PDFPrevDialog" = None):
            super().__init__(parent)
            self.pdfprevdialog = parent
            self.change_page = parent.change_page
            self.del_page = parent.del_page
            self.add_page = parent.add_page
            self.on_page_changed = parent.on_page_changed
            self.fit_in_width = parent.fit_in_width
            self.fit_in_height = parent.fit_in_height
            self.fit_in_disabled = parent.fit_in_disabled

        @property
        def curr_rightpagenum(self) -> int:
            return min(self.pagecount - 1, self.curr_pagenum + 1)

        @property
        def pagecount(self) -> int:
            return len(self.doc)

        @property
        def last_rightpagenum(self) -> int:
            return min(self.pagecount - 1, self.last_pagenum + 1)

        @property
        def last_pagenum(self) -> int:
            return self.pdfprevdialog.last_pagenum

        def last_pagenum_setValue(self, value):
            self.pdfprevdialog.last_pagenum = value

        @property
        def fit_in_policy(self):
            return self.pdfprevdialog.fit_in_policy

        @property
        def page_shift(self) -> int:
            return self.pdfprevdialog.pageshift

        @property
        def pdfname(self) -> str:
            return self.pdfprevdialog.pdfname

        @property
        def curr_pagenum(self) -> int:
            return self.pdfprevdialog.curr_pagenum

        @property
        def pdfuuid(self) -> str:
            return self.pdfprevdialog.pdfuuid

        @property
        def card_id(self) -> str:
            return self.pdfprevdialog.card_id

        @property
        def doc(self) -> "fitz.Document":
            return self.pdfprevdialog.doc

        @property
        def pageratio(self) -> float:
            return self.pdfprevdialog.pageratio

        def page_shift_set(self, value):
            self.pdfprevdialog.pageshift = value

        def curr_pagenum_set(self, value):
            self.pdfprevdialog.curr_pagenum = value

        def pdfuuid_set(self, value):
            self.pdfprevdialog.pdfuuid = value

        def card_id_set(self, value):
            self.pdfprevdialog.card_id = value

        def fit_in_policy_set(self, value):
            self.pdfprevdialog.fit_in_policy = value

        def pageratio_set(self, value):
            self.pdfprevdialog.pageratio = value

    fit_in_height = 0
    fit_in_width = 1
    fit_in_disabled = 2

    def __init__(self, cardwindow=None, pdfuuid=None, pdfname=None, pagenum=None, pageratio=None, card_id=None,
                 pageshift=None):
        super().__init__(parent=cardwindow)
        self.api = self.API(self)
        PDF_JSON = clipper_imports.objs.SrcAdmin.PDF_JSON
        if pageshift is not None:
            self.pageshift = pageshift
        elif pdfuuid in PDF_JSON and "page_shift" in PDF_JSON[pdfuuid]:
            self.pageshift = PDF_JSON[pdfuuid]["page_shift"]
        else:
            self.pageshift = 0
        self.card_id = card_id
        self.pdfuuid = pdfuuid
        self.fit_in_policy = self.fit_in_disabled
        self.pdfname = pdfname
        self.pagenum = pagenum
        self.last_pagenum = pagenum
        self.curr_pagenum = pagenum
        self.doc = fitz.open(pdfname)
        self.pageratio = pageratio
        self.leftSide_bookmark = self.LeftSideBookmark(parent=self)
        self.bottom_toolsbar = self.BottomToolsBar(parent=self)
        self.center_view = self.CenterView(parent=self)
        self.init_UI()
        self.init_show()
        self._event = {
            self.on_page_changed: self.on_page_changed_handle,
            # self.on_page_added:lambda x:setattr(self,"curr_pagenum",x)
        }
        self.all_event = clipper_imports.objs.AllEventAdmin(self._event)
        self.all_event.bind()

    # def __setattr__(self, key, value):
    #     # if key == "curr_pagenum" and "curr_pagenum" in self.__dict__ and value != self.__dict__["last_pagenum"]:
    #     #     self.__dict__["last_pagenum"] =self.__dict__["curr_pagenum"]
    #     #     self.on_page_changed.emit(value)
    #     self.__dict__[key]=value

    def on_page_changed_handle(self, event: "PDFPrevDialog.PageChangedEvent"):
        self.center_view.api.hideclipbox()
        self.last_pagenum = self.curr_pagenum
        self.curr_pagenum = event.data
        self.api.change_page(event.data)
        self.center_view.api.showclipbox()

    def init_UI(self):
        self.setWindowTitle("PDF previewer")
        self.setWindowModality(Qt.NonModal)
        self.setModal(False)
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        # w_li=[self.leftSide_bookmark,self.bottom_toolsbar,self.center_view]
        V_layout = QVBoxLayout(self)
        # self.center_view.setStyleSheet("margin:0px;padding:0px;")
        # self.bottom_toolsbar.setStyleSheet("margin:0px;padding:0px;")
        # self.center_view.setStyleSheet("margin:0;")
        V_layout.addWidget(self.center_view)
        V_layout.addWidget(self.bottom_toolsbar)
        H_layout = QHBoxLayout(self)
        H_layout.addWidget(self.leftSide_bookmark)
        H_layout.addLayout(V_layout)
        H_layout.setContentsMargins(0, 0, 0, 0)
        V_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(H_layout)

    def init_show(self):
        self.add_page()

    def change_page(self, pagenum):
        """用来换页,和底层的不同的是他同时换两页"""

        self.center_view.api.leftpage.api.change_page(pagenum)

        if self.center_view.api.rightpage:
            self.center_view.api.rightpage.api.change_page(pagenum + 1)
        pass

    def del_page(self):
        self.center_view.api.delpage()

    def add_page(self):
        self.center_view.api.addpage()


if __name__ == "__main__":
    UUID = "bfb206da-8d1a-3d9a-84d2-e1753f42577f"
    # DB = clipper_imports.objs.SrcAdmin.DB.go()
    # result = DB.select(uuid=UUID).return_all().zip_up()[0]
    # DB.end()
    PDF_JSON = clipper_imports.objs.SrcAdmin.PDF_JSON
    testcase = {
        "pdfname": PDF_JSON[UUID]["pdf_path"], "pdfuuid": UUID, "card_id": "123456789",
        "pagenum": 0, "pageratio": 1
    }
    app = QApplication(sys.argv)
    p = PDFPrevDialog(**testcase)
    p.show()
    sys.exit(app.exec_())
