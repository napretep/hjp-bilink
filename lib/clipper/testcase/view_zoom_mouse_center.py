#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 2020/11/12
@author: Irony
@site: https://github.com/892768447
@email: 892768447@qq.com
@file: ImageView
@description: 图片查看控件，支持移动、放大、缩小
"""

__Author__ = 'Irony'
__Copyright__ = 'Copyright (c) 2020 Irony'
__Version__ = 1.0

import os

from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, Qt, QRectF, QSizeF, QPoint
from PyQt5.QtGui import QPainter, QColor, QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QGraphicsPixmapItem, QGraphicsScene
from lib.clipper.lib.tools import funcs


class ImageView(QGraphicsView):
    """图片查看控件"""

    def __init__(self, *args, **kwargs):
        pdfname = kwargs.pop('pdfname', None)
        pagenum = kwargs.pop('pagenum', None)
        ratio = kwargs.pop('ratio', None)
        super(ImageView, self).__init__(*args, **kwargs)
        self.pdfname = pdfname
        self.pagenum = pagenum
        self.ratio = ratio
        self.setCursor(Qt.OpenHandCursor)
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                            QPainter.SmoothPixmapTransform)
        self.setCacheMode(self.CacheBackground)
        self.setViewportUpdateMode(self.SmartViewportUpdate)
        self._item = Graph(parent=self)  # 放置图像
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self._scene = QGraphicsScene(self)  # 场景
        self.setScene(self._scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scene.addItem(self._item)
        self._scene.setSceneRect((self._item.mapRectToScene(self._item.boundingRect())))
        self.setSceneRect(self._item.mapRectToScene(self._item.boundingRect()))
        # self.resize(800,600)
        # self.setSceneRect(rect)
        self.pixmap = None
        self._delta = 0.1  # 缩放
        # self.setPixmap(image)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mousePressEvent(event)


class Graph(QGraphicsPixmapItem):
    mousecenter = 0
    viewcenter = 1

    def __init__(self, parent=None):
        super().__init__()
        self.view: "ImageView" = parent
        path = funcs.pixmap_page_load(self.view.pdfname, self.view.pagenum, self.view.ratio)
        self.setPixmap(QPixmap(path))
        self.ratio = 1
        # self.mouse_center_item_p=QPointF()

    def wheelEvent(self, event):
        self.mouse_center_item_p = [event.pos().x() / self.boundingRect().width(),
                                    event.pos().y() / self.boundingRect().height()]
        self.mouse_center_scene_p = self.mapToScene(event.pos())
        centerpos = QPointF(self.view.size().width() / 2, self.view.size().height() / 2)
        self.view_center_scene_p = self.view.mapToScene(centerpos.toPoint())
        p = self.mapFromScene(self.view_center_scene_p)
        self.view_center_item_p = [p.x() / self.boundingRect().width(), p.y() / self.boundingRect().height()]
        # print(f"""scenepos={event.scenePos()},maptoscenepos={self.mapToScene(event.pos())}""")

        if event.delta() > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    def zoomIn(self):
        """放大"""
        self.ratio *= 1.1
        self.zoom(self.ratio)

    def zoomOut(self):
        """缩小"""
        self.ratio /= 1.1
        self.zoom(self.ratio)

    def center_zoom(self, center=0):
        if center == self.mousecenter:
            X = self.mouse_center_item_p[0] * self.boundingRect().width()
            Y = self.mouse_center_item_p[1] * self.boundingRect().height()
            new_scene_p = self.mapToScene(X, Y)
            dx = new_scene_p.x() - self.mouse_center_scene_p.x()
            dy = new_scene_p.y() - self.mouse_center_scene_p.y()
        elif center == self.viewcenter:
            X = self.view_center_item_p[0] * self.boundingRect().width()
            Y = self.view_center_item_p[1] * self.boundingRect().height()
            new_scene_p = self.mapToScene(X, Y)
            dx = new_scene_p.x() - self.view_center_scene_p.x()
            dy = new_scene_p.y() - self.view_center_scene_p.y()
        scrollY = self.view.verticalScrollBar()
        scrollX = self.view.horizontalScrollBar()
        # 如果你不打算采用根据图片放大缩小,可以用下面的注释的代码实现scrollbar的大小适应
        # if scrollY.value()-dy<0:
        #     self.view.setSceneRect(rect.x(), rect.y() -dy, rect.width(), rect.height())
        # if scrollX.value()-dx<0:
        #     self.view.setSceneRect(rect.x()-dx, rect.y() , rect.width(), rect.height())
        # if scrollY.value()==scrollY.maximum():
        #     self.view.setSceneRect(rect.x(),rect.y() , rect.width(), rect.height()+dy)
        # if scrollX.value()==scrollX.maximum():
        #     self.view.setSceneRect(rect.x(), rect.y(), rect.width()+dx, rect.height())
        self.view.setSceneRect(self.mapRectToScene(self.boundingRect()))
        scrollY.setValue(scrollY.value() + int(dy))
        scrollX.setValue(scrollX.value() + int(dx))
        # p=  self.mapToScene(QPoint(1,1))
        # print(f"""scrolly={scrollY.value()},rect.height()={rect.height()}""")

    def zoom(self, factor):
        """缩放
        :param factor: 缩放的比例因子
        """
        _factor = self.transform().scale(
            factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
        if _factor < 0.07 or _factor > 100:
            # 防止过大过小
            return
        # dy= self.zoomcenter_relate_p.y() * (factor - 1)
        # dx= self.zoomcenter_relate_p.x() * (factor - 1)
        path = funcs.pixmap_page_load(self.view.pdfname, self.view.pagenum, self.view.ratio * self.ratio)
        self.setPixmap(QPixmap(path))
        # print(self.boundingRect())
        # self.setScale(factor)
        self.center_zoom(self.mousecenter)


if __name__ == '__main__':
    import sys
    import cgitb

    cgitb.enable(format='text')
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ImageView(pdfname=r'D:\备份盘\经常更新\数学书大全\分析学\数学分析\谢惠民.  数学分析讲义.第二册_书签.pdf',
                  pagenum=1, ratio=1)
    w.show()
    sys.exit(app.exec_())
