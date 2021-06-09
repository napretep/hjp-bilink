import sys

from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QGraphicsScene, QHBoxLayout, QApplication, QShortcut
from .PageInfo import PageInfo
from .PDFView import PDFView
from .PDFView_ import PageItem5
from .PDFView_.PageItem_ import ClipBox_
from .RightSideBar import RightSideBar
from .tools import funcs, objs, events


class Clipper(QMainWindow):
    def __init__(self):
        super().__init__()  # 加载的是文档
        self.scene: 'QGraphicsScene'
        self.funcs: 'funcs' = funcs
        self.objs: 'objs' = objs
        self.events: 'events' = events
        self.pageItemList: 'list[PageItem5]' = []
        self.init_UI()
        self.init_signals()
        self.init_events()
        # self.init_view()
        self.init_shortcuts()
        # self.showMaximized()
        self.show()

    def init_view(self):
        page = PageInfo(self.doc, 0)
        self.scene_pageitem_add(page)

    def init_signals(self):
        self.on_clipbox_closed = objs.CustomSignals.start().on_clipbox_closed
        self.on_pageItem_clicked = objs.CustomSignals.start().on_pageItem_clicked
        self.on_pageItem_addToScene = objs.CustomSignals.start().on_pageItem_addToScene
        self.on_pageItem_removeFromScene = objs.CustomSignals.start().on_pageItem_removeFromScene

    def init_events(self):
        self.resizeEvent = self.OnResize
        self.on_clipbox_closed.connect(self.scene_clipbox_remove)
        self.on_pageItem_clicked.connect(self.on_pageItem_clicked_handle)
        self.on_pageItem_addToScene.connect(self.on_pageItem_addToScene_handle)
        self.on_pageItem_removeFromScene.connect(self.on_pageItem_removeFromScene_handle)

    def init_shortcuts(self):
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Tab), self,
                  activated=lambda: objs.CustomSignals.start().on_clipper_hotkey_next_card.emit())
        QShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Tab), self,
                  activated=lambda: objs.CustomSignals.start().on_clipper_hotkey_prev_card.emit())
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self,
                  activated=lambda: objs.CustomSignals.start().on_clipper_hotkey_setA.emit())
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q), self,
                  activated=lambda: objs.CustomSignals.start().on_clipper_hotkey_setQ.emit())

    def init_UI(self):
        # 经验：QGraphicsView 必须放置在 QWidget 中， 才能和其他QWidget 保持正常的大小关系
        self.setWindowIcon(QIcon("./resource/icon_window_clipper.png"))
        self.setWindowTitle("PDF clipper")
        self.container0 = QWidget(self)  # 不能删
        self.scene = QGraphicsScene()
        self.pdfview = PDFView(self.scene, parent=self, clipper=self)

        self.rightsidebar = RightSideBar(clipper=self)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.pdfview)
        self.h_layout.addWidget(self.rightsidebar)
        self.h_layout.setStretch(0, 1)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))
        self.container0.resize(self.width(), self.height())
        self.container0.setLayout(self.h_layout)

    def OnResize(self, *args):
        self.container0.resize(self.width(), self.height())
        pass

    def scene_item_downgrade_z(self, except_item):
        for item in self.pageItemList:
            item.setZValue(item.zValue() - len(self.pageItemList))
        except_item.setZValue(len(self.pageItemList))
        pass

    def on_pageItem_clicked_handle(self, event: 'events.PageItemClickEvent'):
        self.scene_item_downgrade_z(event.pageitem)

    def on_pageItem_removeFromScene_handle(self, event: 'events.PageItemDeleteEvent'):
        if event.eventType == event.deleteType:
            self.scene_pageitem_remove(event.pageItem)
        pass

    def on_pageItem_addToScene_handle(self, event: 'import lib.clipper.lib.tools.events'):
        if event.eventType == event.addPageType:
            if event.pageItem is not None:
                self.scene_pageitem_add(event.pageItem)
            elif event.pageItemList is not None:
                for pageitem in event.pageItemList:
                    self.scene_pageitem_add(event.pageItem)
            self.update()

    def scene_pageitem_add(self, pageitem):
        self.pageItemList.append(pageitem)
        self.scene.addItem(pageitem)
        pass

    def scene_pageitem_remove(self, pageitem: 'PageItem5'):
        self.pageItemList.remove(pageitem)
        self.scene.removeItem(pageitem)

    def scene_clipbox_remove(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        item = event.clipBox
        self.scene.removeItem(item)


# clipper = Clipper()
if __name__ == '__main__':
    pass
    # print("ok")
    # app = QApplication(sys.argv)
    # pageinfo = PageInfo("./resource/徐森林_数学分析_第8章.pdf")
    # clipper = Clipper()
    # clipper.scene_pixmap_add(pageinfo)
    # sys.exit(app.exec_())
