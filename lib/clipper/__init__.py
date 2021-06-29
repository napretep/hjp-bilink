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
    # from PyQt5.QtCore import QPointF
    # from PyQt5.QtWidgets import QApplication
    # from lib.PageInfo import PageInfo
    # from lib.Clipper import Clipper
    # from lib.PDFView_ import PageItem5
    # from lib.tools import ALL,funcs
    # from lib.tools.events import PageItemAddToSceneEvent
    #
    #
    #
    # app = QApplication(sys.argv)
    # clipper = Clipper()
    # pageitem = PageItem5(PageInfo("./resource/latex的学习体会.pdf", 0), rightsidebar=clipper.rightsidebar)
    # event = PageItemAddToSceneEvent(pageItem=pageitem, eventType=PageItemAddToSceneEvent.addPageType)
    # ALL.signals.on_pageItem_addToScene.emit(event)
    # sys.exit(app.exec_())
    from lib.fitz import fitz

    doc: "fitz.Document" = fitz.open(
        r"D:\备份盘\经常更新\数学书大全\丛书系列\GTM系列\GTM201-259\gtm241 The.Arithmetic.of.Dynamical.Systems.pdf")
    toc = doc.get_toc()
    print(toc)
