import sys
import time
from math import ceil

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QGraphicsScene, QHBoxLayout, QApplication, QShortcut, QDialog
from .PageInfo import PageInfo
from .PDFView import PDFView
from .PDFView_ import PageItem5
from .PDFView_.PageItem_ import ClipBox_
from .RightSideBar import RightSideBar
from .tools import funcs, objs, events, ALL, Worker

print, printer = funcs.logger(__name__)


class Clipper(QDialog):
    """空打开一定会加载,如果不空请手工加载."""

    def __init__(self):
        super().__init__()  # 加载的是文档
        self.funcs: 'funcs' = funcs
        self.objs: 'objs' = objs
        self.ALL = ALL
        ALL.clipper = self
        ALL.signals = objs.CustomSignals.start()
        self.events: 'events' = events
        self.viewlayout_mode = objs.JSONschema.viewlayout_mode
        self.config = objs.SrcAdmin.get_config("clipper")
        self.mainwin_pageload_worker = None
        self.pageload_progress = None
        self.clipboxstateshowed = False
        self.viewlayout_value = self.config["mainview.layout_mode"]["value"]
        self.viewlayout_col_per_row = self.config["mainview.layout_col_per_row"]["value"]
        self.viewlayout_row_per_col = self.config["mainview.layout_row_per_col"]["value"]
        self.pageItemList: 'list[PageItem5]' = []
        self.container0 = QWidget(self)  # 不能删
        self.scene = QGraphicsScene(self)
        self.pdfview = PDFView(self.scene, parent=self, clipper=self)
        self.rightsidebar = RightSideBar(clipper=self)
        # print(f"{sys._getframe(1).f_code.co_name},Clipper.__init__")
        self.init_UI()
        self.event_dict = {
            ALL.signals.on_clipbox_closed: self.scene_clipbox_remove,
            ALL.signals.on_pageItem_clicked: self.on_pageItem_clicked_handle,
            ALL.signals.on_pageItem_addToScene: self.on_pageItem_addToScene_handle,
            ALL.signals.on_pageItem_removeFromScene: self.on_pageItem_removeFromScene_handle,
            ALL.signals.on_rightSideBar_buttonGroup_clicked: self.on_rightSideBar_buttonGroup_clicked_handle,
            ALL.signals.on_clipboxstate_switch: self.on_clipboxstate_switch_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
        self.init_shortcuts()
        if ALL.ISDEBUG:
            self.show()
        else:
            self.showMaximized()
        self.frame_load_worker = Worker.FrameLoadWorker()
        self.frame_load_worker.start()

    def check_empty(self):
        if len(self.scene.items()) == 0:
            e = events.PagePickerOpenEvent
            objs.signals.on_pagepicker_open.emit(e(eventType=e.fromAddButtonType))

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
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_M), self, activated=lambda: objs.macro.on_switch.emit())
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self, activated=lambda: objs.macro.on_pause.emit())

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if not event.modifiers() & Qt.ControlModifier:
            if self.clipboxstateshowed:
                e = events.ClipboxStateSwitchEvent
                ALL.signals.on_clipboxstate_switch.emit(
                    e(sender=self, eventType=e.hideType)
                )
            # print("on_clipboxstate_hide emit")
        else:
            super().keyReleaseEvent(event)

    def init_UI(self):
        # 经验：QGraphicsView 必须放置在 QWidget 中， 才能和其他QWidget 保持正常的大小关系
        self.setWindowIcon(QIcon(objs.SrcAdmin.call().imgDir.clipper))
        self.setWindowTitle("PDF clipper")
        self.setModal(False)
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
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
        # print(new_pos)
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

    def pageitem_layout_arrange(self, pageitem):
        self.viewlayout_value = ALL.CONFIG.mainview.layout_mode
        old_count = len(self.pageItemList)
        if self.viewlayout_value == self.viewlayout_mode.Horizontal:
            row = ALL.CONFIG.mainview.layout_row_per_col
            rem = old_count % row
            if rem != 0:
                olditem = self.pageItemList[-1]
                self.pageitem_moveto_oldpage_bottom(olditem, pageitem)
            else:
                olditem = self.pageItemList[-row]
                self.pageitem_moveto_oldpage_left(olditem, pageitem)
            pass

        elif self.viewlayout_value == self.viewlayout_mode.Vertical:
            col = ALL.CONFIG.mainview.layout_col_per_row
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
        if event.Type == event.clearViewType:
            self.clear()

    def on_job_1_pagepath_loaded_handle(self, kwargs):
        from .PageInfo import PageInfo
        from .PDFView_ import PageItem5
        # 新建page对象
        # print((f"""pagenum={kwargs["page_num"]}"""))
        pageitem = PageItem5(PageInfo(kwargs["pdf_path"], pagenum=kwargs["page_num"], ratio=kwargs["ratio"]),
                             rightsidebar=self.rightsidebar)
        e = events.PageItemAddToSceneEvent
        ALL.signals.on_pageItem_addToScene.emit(e(sender=self, pageItem=pageitem, eventType=e.addPageType))

        # 进度条部分
        if kwargs["index"] != kwargs["total_page_count"] - 1:
            self.worker_signal_func_dict["continue"][0].emit()
            self.pageload_progress.valtxt_set(ceil(kwargs["percent"] * 100))
        else:
            self.worker_signal_func_dict["complete"][0].emit()
            self.pageload_progress.valtxt_set(100)
            self.pageload_progress.close_dely(200)

    def start(self, pairs_li: "list[dict[str,str]]" = None, clipboxlist=None):
        """

        Args:
            pairs_li: 应当提前准备好卡片和卡片的描述再来,即pairs_li=[{"card_id":"123456789","desc":"ABCDE"},...]
            clipboxli: 应当是一个uuid列表,[uuid1,uuid2,...]

        Returns:

        """
        # self.clear()
        if pairs_li:
            # 批量添加到cardlist
            for pair in pairs_li:
                self.rightsidebar.card_list_add(desc=pair["desc"], card_id=pair["card_id"], newcard=False)
            pdf_page_li = self.pdf_info_card_id_li_load(pairs_li)
            if len(pdf_page_li) > 0:
                self.start_mainpage_loader(pdf_page_li)
            pass
        else:
            QTimer.singleShot(50, self.check_empty)

    def start_mainpage_loader(self, pdf_page_li):
        if self.mainwin_pageload_worker is None:
            self.mainwin_pageload_worker = Worker.MainWindowPageLoadWorker()
        self.worker_signal_func_dict = {
            "print": [self.mainwin_pageload_worker.on_1_pagepath_loaded, self.on_job_1_pagepath_loaded_handle, {}],
            "continue": [self.mainwin_pageload_worker.on_continue,
                         lambda: setattr(self.mainwin_pageload_worker, "do", True), None],
            "complete": [self.mainwin_pageload_worker.on_complete,
                         lambda: setattr(self.mainwin_pageload_worker, "complete", True), None],
            "over": [self.mainwin_pageload_worker.on_all_pagepath_loaded,
                     lambda: self.pageload_progress.close_dely(200), None]
        }
        signal_sequence = [[], ["print"], []]
        self.mainwin_pageload_worker.data_load(1, signal_func_dict=self.worker_signal_func_dict,
                                               signal_sequence=signal_sequence, pdf_page_list=pdf_page_li)
        self.mainwin_pageload_worker.start()
        self.pageload_progress = objs.UniversalProgresser(self)

    def pdf_info_card_id_li_load(self, pairli):
        DB = objs.SrcAdmin.DB.go()
        pdf_info = []  # 每个单元为 pdf地址与页码
        for pair in pairli:
            results = DB.select(card_id="card_id", like=f"%{pair['card_id']}%").return_all().zip_up()
            if len(results) > 0:
                for result in results:
                    d = (result["pdfname"], result["pagenum"], result["ratio"])
                    if d not in pdf_info:
                        pdf_info.append(d)
        # print(pdf_info)
        return pdf_info

    def clear(self):
        self.scene.clear()
        self.pageItemList.clear()
        self.rightsidebar.pagelist.model.clear()
        self.rightsidebar.cardlist.model.clear()
        self.rightsidebar.pagelist.init_model()
        self.rightsidebar.cardlist.init_model()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        funcs.event_handle_disconnect(objs.AllEvents)
        self.frame_load_worker.quit()
        objs.signals.on_clipper_closed.emit()
        # Worker.frame_load_worker.quit()
    #
    # def __del__(self):
    #     funcs.event_handle_disconnect(objs.AllEvents)


if __name__ == '__main__':
    pass
    # print("ok")
    # app = QApplication(sys.argv)
    # pageinfo = PageInfo("./resource/徐森林_数学分析_第8章.pdf")
    # clipper = Clipper()
    # clipper.scene_pixmap_add(pageinfo)
    # sys.exit(app.exec_())
