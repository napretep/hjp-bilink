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

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication
from lib.PageInfo import PageInfo
from lib.Clipper import Clipper
from lib.PDFView_ import PageItem5
from lib.tools.objs import CustomSignals
from lib.tools.events import PagePickerEvent

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clipper = Clipper()
    pageitem = PageItem5(PageInfo("./resource/徐森林_数学分析_第8章.pdf", 0), rightsidebar=clipper.rightsidebar)
    event = PagePickerEvent(pageItem=pageitem, eventType=PagePickerEvent.addPageType)
    CustomSignals.start().on_pageItem_addToScene.emit(event)
    sys.exit(app.exec_())
