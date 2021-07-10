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
主要功能应该写在主要视觉单位中，
event需要有 eventType, 对应的类型用变量 XXType写成属性,比如 ClickType
利用订阅模式设计结构,让每个对象的代码可以在自己内部运行,解耦.
"""
import sys

if __name__ == '__main__':
    # from lib.fitz import fitz
    #

    from PyQt5.QtCore import QPointF, QTimer
    from PyQt5.QtWidgets import QApplication
    from lib.PageInfo import PageInfo
    from lib.Clipper import Clipper
    from lib.PDFView_ import PageItem5
    from lib.tools import ALL, funcs, objs
    from lib.tools.events import PageItemAddToSceneEvent
    from aqt import QProcess

    app = QApplication(sys.argv)

    clipper = Clipper()
    # result = objs.SrcAdmin.DB.go().select(true=True).return_all()
    # print(result.zip_up())

    sys.exit(app.exec_())
