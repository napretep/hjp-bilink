# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = '图元测试.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/12 10:12'
"""

import sys, os, math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QColor, QBrush, QFont, QPixmap, QPolygonF, QPainterPath
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
                             QGraphicsTextItem, QGraphicsEllipseItem, QGraphicsRectItem,
                             QGraphicsPixmapItem, QGraphicsPolygonItem, QGraphicsPathItem)


class DemoGraphicsItem(QMainWindow):
    def __init__(self, parent=None):
        super(DemoGraphicsItem, self).__init__(parent)

        # 设置窗口标题
        self.setWindowTitle('实战PyQt5: QGraphicsItem Demo!')
        # 设置窗口大小
        self.resize(480, 400)

        self.initUi()

    def initUi(self):
        # 场景部分
        scene = QGraphicsScene()

        # 设置场景的背景色
        scene.setBackgroundBrush(QBrush(QColor(168, 168, 168)))

        # 添加一个文本
        text = scene.addText('Hello Graphics Item')
        text.setFont(QFont(self.font().family(), 16))
        # 添加一个圆环
        cycle = scene.addEllipse(0, 0, 60, 60)
        cycle.setPen(QPen(Qt.yellow))
        cycle.setPos(0, 30)

        # 添加一个矩形,线粗为2，虚线模式
        scene.addRect(300, 0, 80, 60, QPen(Qt.magenta, 2, Qt.DashDotLine))

        # 添加一个顺时针旋转30°的矩形
        rect = QGraphicsRectItem(0, 0, 60, 80)
        rect.setBrush(QBrush(Qt.blue))
        rect.setRotation(30)  # 旋转30度
        rect.setPos(60, 100)
        scene.addItem(rect)

        # 添加一个多边形(五角星)
        # 外点：x=Rcos(72°*k)  y=Rsin(72°*k)   k=0,1,2,3,4
        # 内点：r=Rsin18°/sin36°  x=rcos(72°*k+36°)  y=rsin(72°*k+36°)   k=0,1,2,3,4
        deg_18 = 18 * math.pi / 180
        deg_36 = 36 * math.pi / 180
        deg_72 = 72 * math.pi / 180
        r_out = 60  # 半径
        r_inner = r_out * math.sin(deg_18) / math.sin(deg_36)
        polygon = QPolygonF()
        for i in range(5):
            # 外点
            polygon.append(QPointF(r_out * math.cos(deg_72 * i), r_out * math.sin(deg_72 * i)))
            # 内点
            polygon.append(QPointF(r_inner * math.cos(deg_72 * i + deg_36), r_inner * math.sin(deg_72 * i + deg_36)))
        polygonItem = QGraphicsPolygonItem()
        polygonItem.setPolygon(polygon)
        polygonItem.setPen(QPen(Qt.red))
        polygonItem.setBrush(QBrush(Qt.red))
        polygonItem.setPos(60, 260)
        scene.addItem(polygonItem)

        # 添加一个路径(三叶草)
        path = QPainterPath()
        r = 120
        for i in range(3):
            path.cubicTo(math.cos(2 * math.pi * i / 3.0) * r,
                         math.sin(2 * math.pi * i / 3.0) * r,
                         math.cos(2 * math.pi * (i + 0.9) / 3.0) * r,
                         math.sin(2 * math.pi * (i + 0.9) / 3.0) * r, 0, 0)
        pathItem = QGraphicsPathItem()
        pathItem.setPath(path)
        pathItem.setPen(Qt.darkGreen)
        pathItem.setBrush(Qt.darkGreen)
        pathItem.setPos(300, 260)
        scene.addItem(pathItem)

        # 添加一个位图
        pixItem = QGraphicsPixmapItem(QPixmap(os.path.dirname(__file__) + "/qt_py.jpg"))
        # 缩小图像
        pixItem.setScale(0.25)
        # 设置位置
        pixItem.setPos(160, 100)
        scene.addItem(pixItem)

        self.view = QGraphicsView()
        self.view.setScene(scene)

        self.setCentralWidget(self.view)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DemoGraphicsItem()
    window.show()
    sys.exit(app.exec())