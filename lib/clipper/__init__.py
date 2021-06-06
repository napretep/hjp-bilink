# test3 目标: 在scene中添加PDF页面,实现PDF页面可随滚轮放缩,而且精度保持变化,
# 实现在mainwindow里布局两个不同的东西
# 做好PDF对话框返回信号布置
"""
对象结构:
data_package :DocAndPage
Clipper
    PDFViewPort
        PageItem
            PageItemPixmap
            PageItemToolsBar
    RightSideBar
        PageList
        CardList
        QAConfirm_group

"""
import sys

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication
from lib.PageInfo import PageInfo
from lib.Clipper import Clipper


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pageinfo = PageInfo("./resource/徐森林_数学分析_第8章.pdf")
    clipper = Clipper()
    clipper.scene_pixmap_add(pageinfo)
    sys.exit(app.exec_())
