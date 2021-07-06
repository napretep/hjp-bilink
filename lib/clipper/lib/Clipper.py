import sys
import time
from math import ceil

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QMainWindow, QWidget, QGraphicsScene, QHBoxLayout, QApplication, QShortcut
from .PageInfo import PageInfo
from .PDFView import PDFView
from .PDFView_ import PageItem5
from .PDFView_.PageItem_ import ClipBox_
from .RightSideBar import RightSideBar
from .tools import funcs, objs, events, ALL


class Clipper(QMainWindow):
    def __init__(self):
        super().__init__()  # 加载的是文档
        self.scene: 'QGraphicsScene'
        self.funcs: 'funcs' = funcs
        self.objs: 'objs' = objs
        self.ALL = ALL
        self.events: 'events' = events
        self.viewlayout_mode = objs.JSONschema.viewlayout_mode
        self.config = objs.SrcAdmin.get_config("clipper")
        self.clipboxstateshowed = False
        self.viewlayout_value = self.config["viewlayout.mode"]["value"]
        self.viewlayout_col_per_row = self.config["viewlayout.col_per_row"]["value"]
        self.viewlayout_row_per_col = self.config["viewlayout.row_per_col"]["value"]
        self.pageItemList: 'list[PageItem5]' = []
        self.container0 = QWidget(self)  # 不能删
        self.scene = QGraphicsScene()
        self.pdfview = PDFView(self.scene, parent=self, clipper=self)
        self.rightsidebar = RightSideBar(clipper=self)
        self.init_UI()
        self.event_dict = {
            ALL.signals.on_clipbox_closed: self.scene_clipbox_remove,
            ALL.signals.on_pageItem_clicked: self.on_pageItem_clicked_handle,
            ALL.signals.on_pageItem_addToScene: self.on_pageItem_addToScene_handle,
            ALL.signals.on_pageItem_removeFromScene: self.on_pageItem_removeFromScene_handle,
            ALL.signals.on_rightSideBar_buttonGroup_clicked: self.on_rightSideBar_buttonGroup_clicked_handle,
            ALL.signals.on_clipboxstate_switch: self.on_clipboxstate_switch_handle,
            ALL.signals.on_config_changed: self.on_config_changed_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
        self.init_shortcuts()
        # self.showMaximized()
        self.show()

    def init_view(self):
        page = PageInfo(self.doc, 0)
        self.scene_pageitem_add(page)

    def init_shortcuts(self):
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_Tab), self,
                              activated=lambda: ALL.signals.on_clipper_hotkey_next_card.emit())
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Tab), self,
                              activated=lambda: ALL.signals.on_clipper_hotkey_prev_card.emit())
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self,
                              activated=lambda: ALL.signals.on_clipper_hotkey_setA.emit())
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q), self,
                              activated=lambda: ALL.signals.on_clipper_hotkey_setQ.emit())

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if not event.modifiers() & Qt.ControlModifier:
            if self.clipboxstateshowed:
                e = events.ClipboxStateSwitchEvent
                ALL.signals.on_clipboxstate_switch.emit(
                    e(sender=self, eventType=e.hideType)
                )
            print("on_clipboxstate_hide emit")
        else:
            super().keyReleaseEvent(event)

    def init_UI(self):
        # 经验：QGraphicsView 必须放置在 QWidget 中， 才能和其他QWidget 保持正常的大小关系
        self.setWindowIcon(QIcon(objs.SrcAdmin.call().imgDir.clipper))
        self.setWindowTitle("PDF clipper")

        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.pdfview)
        self.h_layout.addWidget(self.rightsidebar)
        self.h_layout.setStretch(0, 1)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))
        self.container0.resize(self.width(), self.height())
        self.container0.setLayout(self.h_layout)

    def resizeEvent(self, *args):
        self.container0.resize(self.width(), self.height())
        pass

    def scene_item_downgrade_z(self, except_item):
        for item in self.pageItemList:
            item.setZValue(item.zValue() - len(self.pageItemList))
        except_item.setZValue(len(self.pageItemList))
        pass

    def on_clipboxstate_switch_handle(self, event: "events.ClipboxStateSwitchEvent"):
        if event.Type == event.showedType:
            self.clipboxstateshowed = True
        elif event.Type == event.hideType:
            self.clipboxstateshowed = False
        self.activateWindow()

    def on_pageItem_clicked_handle(self, event: 'events.PageItemClickEvent'):
        self.scene_item_downgrade_z(event.pageitem)
        self.pageitem_unique_toolsbar(event.pageitem)

    def on_pageItem_removeFromScene_handle(self, event: 'events.PageItemDeleteEvent'):
        if event.Type == event.deleteType:
            self.scene_pageitem_remove(event.pageItem)
        pass

    def on_pageItem_addToScene_handle(self, event: 'events.PageItemAddToSceneEvent'):
        if event.Type == event.addPageType:
            if event.pageItem is not None:
                self.scene_pageitem_add(event.pageItem)
        elif event.Type == event.addMultiPageType:
            l = len(event.pageItemList)
            for i in range(l):
                self.scene_pageitem_add(event.pageItemList[i])
                ALL.signals.on_pagepicker_browser_progress.emit(ceil((i / l) * 100))
                time.sleep(0.01)
            ALL.signals.on_pagepicker_browser_progress.emit(100)

    def pageitem_moveto_oldpage_bottom(self, old_item: 'PageItem5', new_item: 'PageItem5'):
        new_pos = QPointF(old_item.x(), old_item.y() + old_item.boundingRect().height())
        print(new_pos)
        new_item.setPos(new_pos)

    def pageitem_moveto_oldpage_left(self, old_item: 'PageItem5', new_item: 'PageItem5'):
        new_pos = QPointF(old_item.x() + old_item.boundingRect().width(), old_item.y())
        print(new_pos)
        new_item.setPos(new_pos)

    def scene_pageitem_add(self, pageitem):
        if len(self.pageItemList) > 0:
            self.pageitem_layout_arrange(pageitem)
        self.pageItemList.append(pageitem)
        self.scene.addItem(pageitem)
        ALL.signals.on_pageItem_needCenterOn.emit(events.PageItemNeedCenterOnEvent(
            eventType=events.PageItemNeedCenterOnEvent.centerOnType,
            pageitem=pageitem))

        pass

    def scene_pageitem_remove(self, pageitem: 'PageItem5'):
        self.pageItemList.remove(pageitem)
        self.scene.removeItem(pageitem)

    def scene_clipbox_remove(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        item = event.clipBox
        self.scene.removeItem(item)

    def view_relayout_arrange(self):
        newli: 'list[PageItem5]' = self.pageItemList
        newli[0].setPos(0, 0)
        self.pageItemList = [newli[0]]
        for item in newli[1:]:
            self.pageitem_layout_arrange(item)
            self.pageItemList.append(item)

    def pageitem_unique_toolsbar(self, pageitem: 'PageItem5'):
        for item in self.pageItemList:
            if item.uuid != pageitem.uuid:
                item.toolsBar.hide()

    def config_update(self):
        self.config = objs.SrcAdmin.get_config("clipper")
        self.viewlayout_value = self.config["viewlayout.mode"]["value"]
        self.viewlayout_col_per_row = self.config["viewlayout.col_per_row"]["value"]
        self.viewlayout_row_per_col = self.config["viewlayout.row_per_col"]["value"]

    def on_config_changed_handle(self):
        self.config_update()

    def pageitem_layout_arrange(self, pageitem):

        old_count = len(self.pageItemList)
        if self.viewlayout_value == self.viewlayout_mode.Horizontal:
            row = self.viewlayout_row_per_col
            rem = old_count % row
            if rem != 0:
                olditem = self.pageItemList[-1]
                self.pageitem_moveto_oldpage_bottom(olditem, pageitem)
            else:
                olditem = self.pageItemList[-row]
                self.pageitem_moveto_oldpage_left(olditem, pageitem)
            pass
        elif self.viewlayout_value == self.viewlayout_mode.Vertical:
            col = self.viewlayout_col_per_row
            rem = old_count % col
            if rem != 0:
                olditem = self.pageItemList[-1]
                self.pageitem_moveto_oldpage_left(olditem, pageitem)
            else:
                olditem = self.pageItemList[-col]
                self.pageitem_moveto_oldpage_bottom(olditem, pageitem)

    def on_rightSideBar_buttonGroup_clicked_handle(self, event: 'events.RightSideBarButtonGroupEvent'):
        if event.Type == event.reLayoutType:
            self.view_relayout_arrange()


# clipper = Clipper()
if __name__ == '__main__':
    pass
    # print("ok")
    # app = QApplication(sys.argv)
    # pageinfo = PageInfo("./resource/徐森林_数学分析_第8章.pdf")
    # clipper = Clipper()
    # clipper.scene_pixmap_add(pageinfo)
    # sys.exit(app.exec_())
