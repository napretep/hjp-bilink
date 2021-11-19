from datetime import datetime
import os.path
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from collections import namedtuple, OrderedDict
from math import ceil
from typing import Union

import typing
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPointF, QPoint, QRectF, QPersistentModelIndex, QModelIndex, \
    QLineF, QItemSelection, QItemSelectionModel, QRect
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QPixmap, QPen, QColor, QBrush, QPainterPathStroker, \
    QPainterPath, QKeySequence, QFont, QPainter
from PyQt5.QtWidgets import QDialog, QWidget, QGraphicsScene, QGraphicsView, QToolButton, QHBoxLayout, QApplication, \
    QVBoxLayout, QGridLayout, QTreeView, QLabel, QHeaderView, QAbstractItemView, QGraphicsItem, QGraphicsRectItem, \
    QGraphicsWidget, QGraphicsPixmapItem, QGraphicsSceneMouseEvent, QGraphicsGridLayout, QGraphicsProxyWidget, \
    QGraphicsSceneWheelEvent, QStyleOptionGraphicsItem, QGraphicsSceneHoverEvent

from aqt.utils import tooltip

from .tools import objs, events, ALL, funcs, Wrappers
from .Model import Entity
from .fitz import fitz

print, printer = funcs.logger(__name__)


class Clipper(QDialog):
    """空打开一定会加载,如果不空请手工加载."""

    def __init__(self, entity: "Entity" = None):
        super().__init__()
        self.E = Entity()
        # self.E.pagepicker.browser.worker=FrameLoadWorker(self.E)
        self.imgDir = objs.SrcAdmin.call().imgDir
        self.setAttribute(Qt.WA_DeleteOnClose, on=True)
        self.signals = self.E.signals
        from .LittleWidgets import ClipperStateBoard
        self.E.state.board = ClipperStateBoard(self, self)
        self.container0 = QWidget(self)
        self.scene = QGraphicsScene(self)

        self.pdfview = self.PDFView(self.scene, parent=self, superior=self)
        self.rightsidebar = self.RightSideBar(superior=self)
        self.widget_button_show_rightsidebar = QToolButton(self)
        self.init_UI()
        self.init_shortcuts()
        self.api = self.API(self)
        self.allevent = objs.AllEventAdmin([
            [self.E.signals.on_pagepicker_open, self.on_pagepicker_open_handle],
            [self.signals.on_pageItem_addToScene, self.on_pageItem_addToScene_handle],
            [self.pdfview.verticalScrollBar().valueChanged, self.on_pdfview_verticalScrollBar_valueChanged_handle],
            [self.pdfview.horizontalScrollBar().valueChanged, self.on_pdfview_horizontalScrollBar_valueChanged_handle],
            [self.pdfview.rubberBandChanged, self.on_pdfview_rubberBandChanged_handle],
            [self.signals.on_clipbox_create, self.on_clipbox_create_handle],
            [self.signals.on_pageitem_close, self.on_pageitem_close_handle],
            [self.rightsidebar.pagelist.addButton.clicked, self.on_righsidebar_pagelist_addButton_clicked_handle],
            [self.rightsidebar.pagelist.view.clicked, self.on_rightsidebar_pagelist_view_clicked_handle],
            [self.rightsidebar.pagelist.view.doubleClicked, self.on_rightsidebar_pagelist_view_doubleClicked_handle],
            [self.rightsidebar.cardlist.addButton.clicked, self.on_righsidebar_cardlist_addButton_clicked_handle],
            [self.rightsidebar.cardlist.delButton.clicked, self.on_righsidebar_cardlist_delButton_clicked_handle],
            [self.rightsidebar.cardlist.view.selectionModel().selectionChanged, self.on_cardlist_selectionChanged_handle],
            [self.rightsidebar.cardlist.view.doubleClicked, self.rightsidebar_cardlist_view_doubleClicked_handle],
            [self.widget_button_show_rightsidebar.clicked, self.on_rightsidebar_show],
            [self.signals.on_rightSideBar_buttonGroup_clicked, self.on_rightSideBar_buttonGroup_clicked_handle],
            [self.signals.on_clipper_hotkey_press, self.on_clipper_hotkey_press_handle],
            [self.signals.on_cardlist_selectRow, self.on_cardlist_selectRow_handle],
            # self.signals.on_anki_file_create,self.on_anki_file_create_handle,
            # self.signals.on_anki_field_insert,self.on_anki_field_insert_handle,
            # self.signals.on_anki_card_create,self.on_anki_card_create_handle,
        ]).bind()

    def rightsidebar_cardlist_view_doubleClicked_handle(self, index: "QModelIndex"):
        # print(index)
        from .CardClipPicker import CardClipboxPicker
        if index.column() != 1:
            return
        if index.data(Qt.DisplayRole) == "/":
            return
        else:
            p = CardClipboxPicker(self.rightsidebar.cardlist, self, index.data(Qt.DisplayRole))
            p.exec()

    def on_cardlist_selectRow_handle(self, row):
        cardlist = self.rightsidebar.cardlist
        if cardlist.model.rowCount() == 0:
            if row == 0:
                self.addCard()
            else:
                raise ValueError(f"row={row}  out of cardlist index ")
        self.rightsidebar.selectRow(row, cardlist.model, cardlist.view)

    def on_clipper_hotkey_press_handle(self, event: "events.ClipperHotkeyPressEvent"):
        if event.type == event.defaultType.setA:
            self.rightsidebar.QAswitch("A")
        elif event.type == event.defaultType.setQ:
            self.rightsidebar.QAswitch("Q")
        elif event.type == event.defaultType.prevcard:
            self.rightsidebar.prevCard()
        elif event.type == event.defaultType.nextcard:
            self.rightsidebar.nextCard()
        elif event.type == event.defaultType.runmacro:
            objs.macro.on_switch.emit()
        elif event.type == event.defaultType.pausemacro:
            objs.macro.on_pause.emit()

        if event.type in event.defaultType.__dict__.values():
            self.E.state.board.data_update()


    def on_rightSideBar_buttonGroup_clicked_handle(self, event: "events.RightSideBarButtonGroupEvent"):
        from ..imports import common_tools
        def clipbox_insert_card_worker_on_quit(timestamp):
            # e=events.AnkiBrowserActivateEvent
            # self.signals.on_anki_browser_activate.emit(e(type=e.defaultType.ClipperTaskFinished,timestamp=timestamp))
            common_tools.funcs.BrowserOperation.search(f"""tag:hjp-bilink::timestamp::{timestamp}""").activateWindow()
            common_tools.funcs.LinkPoolOperation.both_refresh()
            self.E.state.progresser.close()
            if self.E.config.output.close_clipper_after_insert:
                self.close()
                return
            elif self.E.config.output.close_clipbox_after_insert:
                self.clearView({"clipbox"})

        def on_card_create_handle(event: "events.AnkiCardCreateEvent"):

            e = events.AnkiCardCreatedEvent
            card_id = common_tools.funcs.CardOperation.create(event.model_id, event.deck_id,
                                                              failed_callback=on_worker_failed)
            event.carditem.setText(card_id)
            event.worker.waitting = False
            pass

        def on_png_create_handle(event: "events.AnkiFileCreateEvent"):
            common_tools.funcs.Media.clipbox_png_save(event.clipuuid)
            event.worker.waitting = False
            pass

        def on_field_insert_handle(event: "events.AnkiFieldInsertEvent"):

            common_tools.funcs.CardOperation.clipbox_insert_field(event.clipuuid, timestamp=event.timestamp)
            event.worker.waitting = False
            pass
        def on_worker_failed():
            self.E.state.progresser.close()
            self.E.clipbox_insert_card_worker.terminate()

        if event.type == event.defaultType.hideRighsidebar:
            self.rightsidebar_hide()
        elif event.type == event.defaultType.config:
            from .ConfigTable import ConfigTable
            p = ConfigTable(self, self)
            p.exec()
        elif event.type == event.defaultType.clearView:
            self.clearView()
        elif event.type == event.defaultType.resetViewRatio:
            self.pdfview.viewRatioReset()
        elif event.type == event.defaultType.QAswitch:
            self.rightsidebar.QAswitch()
        elif event.type == event.defaultType.reLayout:
            self.pdfview.pageitem_relayout()
            pass
        elif event.type == event.defaultType.correct:
            self.E.clipbox_insert_card_worker = ClipInsertCardWorker(self)
            self.E.state.progresser = objs.UniversalProgresser(self)
            self.E.clipbox_insert_card_worker.allevent = common_tools.objs.AllEventAdmin([
                [self.E.clipbox_insert_card_worker.on_progress, self.E.state.progresser.value_set],
                [self.E.clipbox_insert_card_worker.on_quit, clipbox_insert_card_worker_on_quit],
                [self.E.clipbox_insert_card_worker.on_card_create, on_card_create_handle],
                [self.E.clipbox_insert_card_worker.on_png_create, on_png_create_handle],
                [self.E.clipbox_insert_card_worker.on_field_insert, on_field_insert_handle],
            ]).bind()
            # self.E.clipbox_insert_card_worker.on_progress.connect(self.E.state.progresser.value_set)
            # self.E.clipbox_insert_card_worker.on_quit.connect(clipbox_insert_card_worker_on_quit)
            self.E.clipbox_insert_card_worker.start()
            pass

        elif event.type == event.defaultType.macro:
            objs.macro.on_switch_handle(callback=self.rightsidebar.macro_switch)


    def on_righsidebar_cardlist_delButton_clicked_handle(self):
        indexli = self.rightsidebar.cardlist.view.selectedIndexes()
        if len(indexli) == 0:
            return
        index = indexli[0]
        item: "Clipper.RightSideBar.CardList.DescItem" = self.rightsidebar.cardlist.model.itemFromIndex(index)
        self.delCard(item.uuid)
        if self.rightsidebar.cardlist.model.rowCount()>0:
            self.rightsidebar.selectRow(index.row()-1,self.rightsidebar.cardlist.model,self.rightsidebar.cardlist.view)

    def on_cardlist_selectionChanged_handle(self, selected: "QItemSelection", deselected: "QItemSelection"):
        # print(selected)
        # print(f"deselected.indexes()={deselected.indexes()}")
        # print(f"selected.indexes()={selected.indexes()}")
        indexli = selected.indexes()
        if indexli:
            item: "Clipper.RightSideBar.CardList.DescItem" = self.rightsidebar.cardlist.model.itemFromIndex(
                selected.indexes()[0])
            self.E.rightsidebar.cardlist.curr_selected_uuid = item.uuid
        else:
            self.E.rightsidebar.cardlist.curr_selected_uuid = None

    def on_righsidebar_cardlist_addButton_clicked_handle(self):
        self.addCard()

    def on_clipbox_create_handle(self, event: "events.ClipboxCreateEvent"):
        assert event.rubberBandRect is not None and event.sender is not None
        self.addClipbox(event.sender.pageview, event.rubberBandRect)

    def on_pdfview_rubberBandChanged_handle(self, viewportRect, fromScenePoint, toScenePoint):
        if viewportRect:  # 空的rect不要
            self.E.last_rubberBand_rect = viewportRect

    def on_rightsidebar_pagelist_view_doubleClicked_handle(self, index: "QModelIndex"):
        item: "Clipper.RightSideBar.PageList.PDFItem" = self.rightsidebar.pagelist.model.item(index.row(), 0)
        e = events.PagePickerOpenEvent
        self.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromPage, fromPageItem=item.pageitem))

    def on_rightsidebar_pagelist_view_clicked_handle(self, index: "QModelIndex"):
        item: "Clipper.RightSideBar.PageList.PDFItem" = self.rightsidebar.pagelist.model.item(index.row(), 0)
        self.pdfview.centerOn(item=item.pageitem)

    def on_pagepicker_open_handle(self, event: "events.PagePickerOpenEvent"):
        from .PagePicker import PagePicker
        if event.type == event.defaultType.fromMainWin:
            pass
        elif event.type == event.defaultType.fromPage:
            self.E.pagepicker.frompageItem = event.fromPageItem
        elif event.type == event.defaultType.fromAddButton:
            pass
        # self.E.pagepicker.browser.worker.start()
        self.E.pagepicker.ins = PagePicker(parent=self, superior=self, root=self)
        self.E.pagepicker.ins.show()

    def on_righsidebar_pagelist_addButton_clicked_handle(self):
        self.rightsidebar.pagelist.on_addButton_clicked_handle()

    def on_pageitem_close_handle(self, event: "events.PageItemCloseEvent"):
        self.delpage(event.pageitem)

    def on_pdfview_horizontalScrollBar_valueChanged_handle(self, value):
        rect = self.pdfview.sceneRect()
        if value == self.pdfview.horizontalScrollBar().maximum():
            rect.setRight(rect.right() + 50)
        elif value == self.pdfview.horizontalScrollBar().minimum():
            rect.setLeft(rect.left() - 50)
        self.pdfview.setSceneRect(rect)

    def on_pdfview_verticalScrollBar_valueChanged_handle(self, value):
        rect = self.pdfview.sceneRect()
        if value == self.pdfview.verticalScrollBar().maximum():
            rect.setBottom(rect.bottom() + 50)
            # self.pdfview.setSceneRect(rect.x(), rect.y(), rect.width(), rect.height() + 10)
        elif value <= self.pdfview.verticalScrollBar().minimum() + 1:
            rect.setTop(rect.top() - 50)
            # self.pdfview.verticalScrollBar().setMinimum(self.pdfview.verticalScrollBar().value()-50)
        self.pdfview.setSceneRect(rect)

        # self.pdfview.setSceneRect(rect.x(), rect.y() - 10, rect.width(), rect.height())

    def on_ScenePageLoader_1_page_load_handle(self, data: "pageloaddata"):
        # print(f"on_ScenePageLoader_1_page_load_handle,{data}")
        pageitem = Clipper.PageItem(data.pixdir, data.pageinfo, superior=self.pdfview, root=self)
        self.addpage(pageitem)
        self.E.state.progresser.valtxt_set(data.progress)
        if data.progress >= 100:
            self.E.state.progresser.close()

        pass

    def on_pageItem_addToScene_handle(self, event: "events.PageItemAddToSceneEvent"):
        """#分别控制两个地方"""
        if event.type == event.defaultType.addPage:
            data: "objs.PageInfo" = event.data
            png_path = funcs.pixmap_page_load(data.pdf_path, data.pagenum, data.ratio)
            pageitem = self.PageItem(png_path, data, superior=self.pdfview, root=self)
            self.addpage(pageitem)
            pass
        elif event.type == event.defaultType.addMultiPage:
            self.E.pdfview.scenepageload_worker = ScenePageLoader(event.datali)
            self.E.pdfview.scenepageload_worker.on_1_page_load.connect(self.on_ScenePageLoader_1_page_load_handle)
            self.E.state.progresser = objs.UniversalProgresser(parent=self)
            self.E.state.progresser.show()
            self.E.pdfview.scenepageload_worker.start()
            pass
        elif event.type == event.defaultType.changePage:
            pageitem: "Clipper.PageItem" = event.sender
            data: "objs.PageInfo" = event.data
            self.E.pdfview.pageitem_container.remove_data(self,pageitem,must=False)
            self.changepage(pageitem, data)
            self.E.pdfview.pageitem_container.append_data(self,pageitem,must=False)
            # QTimer.singleShot(100, lambda: self.pdfview.centerOn(item=pageitem))
            pass

    def addpage(self, pageitem: "Clipper.PageItem" = None, pdf_path=None, page_num=None, ratio=None):
        """尽管调用这个,其他的都不必管,已经帮你处理好了"""
        assert pageitem is not None or (pdf_path is not None and page_num is not None and ratio is not None)
        if pageitem is None:  # 如果为空,我们就自己制作一个pageitem
            png_path = funcs.pixmap_page_load(pdf_path, page_num, ratio)
            pageinfo = objs.PageInfo(pdf_path, page_num, ratio)
            pageitem = self.PageItem(png_path, pageinfo, self.pdfview, self)
        self.E.pdfview.pageitem_container.append_data(self, pageitem)
        self.pdfview.addpage(self, pageitem)
        self.rightsidebar.addpage(self, pageitem)

    def delpage(self, pageitem: "Clipper.PageItem"):
        self.pdfview.delpage(self, pageitem)
        self.rightsidebar.delpage(self, pageitem)
        self.E.pdfview.pageitem_container.remove_data(self, pageitem)

    def changepage(self, pageitem: "Clipper.PageItem", data: "objs.PageInfo"):
        assert isinstance(pageitem, Clipper.PageItem) and isinstance(data, objs.PageInfo)
        pageitem.changepage(self, data)
        self.rightsidebar.changepage(self, pageitem)

    def clearView(self, constrain=None):
        """
        默认全部清空,如果要指定清空的对象,请添加对应的参数

        Args:
            constrain: one of ["clipbox","pageitem","cardlist","centerOn"]

        Returns:

        """
        # 删光 1 pagedict, 2 clipboxdict 3 carddict
        if constrain is None:
            constrain = {"clipbox", "pageitem", "cardlist", "centerOn"}

        if "clipbox" in constrain:
            for clipitem in self.E.clipbox.container.values():
                self.pdfview.scene().removeItem(clipitem)
            self.E.clipbox.clear_data(self)

        if "pageitem" in constrain:
            for page_it in self.E.pdfview.pageitem_container.uuidBased_data.values():
                self.pdfview.scene().removeItem(page_it)
            self.E.pdfview.pageitem_container.clear_data(self)

        if "cardlist" in constrain:
            self.E.rightsidebar.cardlist.clear_data(self)
            self.rightsidebar.pagelist.init_model()

        if "centerOn" in constrain:
            self.pdfview.centerOn(QPoint(0, 0))

        pass

    def addClipbox(self, pageview: "Clipper.PageItem.PageView" = None, rect: "QRectF" = None, clipuuid: "str" = None):
        """要解决的事情:
        1 创建clipbox, 2 将卡片与clipbox绑定, 3将pageitem与clipbox绑定 4建立clipbox实体,5考察状态机,6考察是否是读取类型的clipbox
        7 插入scene
        """

        if pageview is None:
            pageview = self.E.curr_selected_pageitem
        if rect is None:
            rect = self.E.last_rubberBand_rect
        # 1pageitem, 2model,3scene
        clipbox = self.ClipBox(superior=pageview, root=self, rect=rect.normalized(), clipuuid=clipuuid)  # 创建本体

        self.E.clipbox.add_keyValue(self, clipbox.uuid, clipbox)  # 进入字典

        if not self.E.rightsidebar.cardlist.curr_selected_uuid:  # 更新卡片为当前选中卡片
            if self.rightsidebar.cardCount() == 0:
                self.rightsidebar.nextCard()
            else:
                self.rightsidebar.selectCardRow(self.rightsidebar.cardCount() - 1)
        self.clipbox_add_card(clipbox.uuid, self.E.rightsidebar.cardlist.curr_selected_uuid)

        clipbox.superior.superior.clipbox_dict_add_keyValue(self, clipbox.uuid, clipbox)  # 更新pageitem中的卡片列表

        if clipuuid is not None:
            clipbox.update_editabledata()

        elif objs.macro.state == objs.macro.runningState:  # 如果开着macro,就再次刷新
            QA, commentQA = objs.macro.get("QA"), objs.macro.get("commentQA")
            clipbox.editableData.clip_to_field = QA
            clipbox.editableData.comment_to_field = commentQA

        pass

    def delClipbox(self, clipbox: "Clipper.ClipBox" = None, uuid: "str" = None):
        assert type(clipbox) == Clipper.ClipBox or uuid is not None
        if clipbox is None:
            clipbox = self.E.clipbox.container[uuid]
        if uuid is None:
            uuid = clipbox.uuid
        # 1pageitem,2model,3scene
        clipbox.superior.superior.clipbox_dict_del_key(self, uuid)
        self.E.clipbox.del_key(self, uuid)
        self.pdfview.scene().removeItem(clipbox)

        pass

    def clipbox_add_card(self, clipuuid: "str", carduuid):
        clipbox: "Clipper.ClipBox" = self.E.clipbox.container[clipuuid]
        clipbox.editableData.card_list_append(self, carduuid)
        item: "Clipper.RightSideBar.CardList.DescItem" = self.E.rightsidebar.cardlist.dict[carduuid]
        item.info.clipbox_add(self, clipuuid)

    def clipbox_del_card(self, clipuuid, carduuid):
        clipbox: "Clipper.ClipBox" = self.E.clipbox.container[clipuuid]
        clipbox.editableData.card_list_remove(self, carduuid)
        item: "Clipper.RightSideBar.CardList.DescItem" = self.E.rightsidebar.cardlist.dict[carduuid]
        item.info.clipbox_del(self, clipuuid)

    def addCard(self, adesc: "str" = None, acard_id: "str" = None, empty=True):
        if acard_id in self.E.rightsidebar.cardlist.card_id_dict:
            tooltip(f"{acard_id} already exists so will not load")
            return
        if empty:
            count = self.rightsidebar.cardlist.new_card_count()
            desc = Clipper.RightSideBar.CardList.DescItem(f"new_card_{count}", superior=self.rightsidebar.cardlist,
                                                          root=self)
            card_id = Clipper.RightSideBar.CardList.CardItem("/", superior=self.rightsidebar.cardlist, root=self)
            desc.cardItem = card_id
        else:
            desc = Clipper.RightSideBar.CardList.DescItem(adesc, superior=self.rightsidebar.cardlist, root=self)
            card_id = Clipper.RightSideBar.CardList.CardItem(acard_id, superior=self.rightsidebar.cardlist, root=self)
            desc.cardItem = card_id
            pass
        self.rightsidebar.cardlist.model.appendRow([desc, card_id])
        self.E.rightsidebar.cardlist.dict_add_keyValue(self, desc.uuid, desc, card_id=acard_id)

    def delCard(self, carduuid):
        item: "Clipper.RightSideBar.CardList.DescItem" = self.E.rightsidebar.cardlist.dict[carduuid]
        for clipboxuuid in item.info.clipboxuuid_list:
            clipbox: "Clipper.ClipBox" = self.E.clipbox.container[clipboxuuid]
            self.clipbox_del_card(clipbox.uuid, item.uuid)
        self.E.rightsidebar.cardlist.dict_del_key(self, item.uuid, card_id=item.cardItem.text())
        self.rightsidebar.cardlist.model.removeRow(item.row())

    def on_rightsidebar_show(self):
        self.widget_button_show_rightsidebar.hide()
        self.rightsidebar.show()
        pass

    def rightsidebar_hide(self):
        self.rightsidebar.hide()
        self.updateGeometry()
        self.widget_button_show_rightsidebar.show()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.modifiers() & Qt.ControlModifier:
            self.E.state.board.data_update()
            self.E.state.board.show()
            self.activateWindow()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if not event.modifiers() & Qt.ControlModifier:
            from .LittleWidgets import ClipperStateBoard
            board: "ClipperStateBoard" = self.E.state.board
            if board.isVisible():
                board.hide()
                self.activateWindow()
        super().keyReleaseEvent(event)

    def init_shortcuts(self):
        e = events.ClipperHotkeyPressEvent
        signal = self.signals.on_clipper_hotkey_press
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_Tab), self,
                              activated=lambda: signal.emit(e(type=e.defaultType.nextcard)))
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_Tab), self,
                              activated=lambda: signal.emit(e(type=e.defaultType.prevcard)))
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_A), self,
                              activated=lambda: signal.emit(e(type=e.defaultType.setA)))
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_Q), self,
                              activated=lambda: signal.emit(e(type=e.defaultType.setQ)))
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_M), self,
                              activated=lambda : objs.macro.on_switch_handle(callback=self.rightsidebar.macro_switch))
        objs.NoRepeatShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self,
                              activated=lambda : objs.macro.on_pause_handle(callback=self.rightsidebar.macro_switch))

    def init_UI(self):
        self.setWindowIcon(QIcon(self.imgDir.clipper))
        self.setWindowTitle("PDF clipper")
        self.setModal(False)
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(0,0,0,0)
        self.h_layout.addWidget(self.pdfview)
        self.h_layout.addWidget(self.rightsidebar)
        self.h_layout.setStretch(0, 1)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))
        self.container0.resize(self.width(), self.height())
        self.container0.setLayout(self.h_layout)
        self.widget_button_show_rightsidebar.setIcon(QIcon(objs.SrcAdmin.imgDir.left_direction))
        self.widget_button_show_rightsidebar.move(self.geometry().width() - 20, self.geometry().height() / 2)
        self.widget_button_show_rightsidebar.hide()

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:

        self.E.state.board.hide()
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() == Qt.RightButton:
            self.E.state.board.data_update()
            self.E.state.board.show()
        super().mousePressEvent(event)

    def resizeEvent(self, *args):
        self.container0.resize(self.width(), self.height())
        self.widget_button_show_rightsidebar.move(self.geometry().width() - 20, self.geometry().height() / 2)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.E.rightsidebar.cardlist.curr_selected_uuid = None
        self.clearView()
        self.allevent.unbind()
        objs.macro.stop()
        from ...common_tools import G
        G.signals.on_clipper_closed.emit()
        # self.signals.on_clipper_closed.emit()

    def reject(self) -> None:
        self.close()

        pass

    def start(self, pairs_li: "list[objs.Pair]" = None, clipboxlist=None):
        """用于clipper启动时添加一些特别条件"""
        if pairs_li:
            # print(f"card_id_li before={self.E.rightsidebar.cardlist.dict}")
            # 批量添加到cardlist
            for pair in pairs_li:
                self.addCard(adesc=pair.desc, acard_id=pair.card_id, empty=False)
            # print(f"pairs_li={pairs_li}")
            # print(f"card_id_li after={self.E.rightsidebar.cardlist.dict}")
            pdfinfo_dict = funcs.pdf_from_card_id_li([pair.card_id for pair in pairs_li])
            # 批量添加有关的图片
            DB = objs.SrcAdmin.DB
            for pdfuuid, pagenum_ratio in pdfinfo_dict.items():
                pdf_path = DB.go(DB.table_pdfinfo).select(DB.EQ(uuid=pdfuuid)).return_all().zip_up()[
                    0].to_pdfinfo_data().pdf_path
                for pagenum, ratio in pagenum_ratio.items():
                    self.addpage(pdf_path=pdf_path, page_num=pagenum, ratio=ratio)
            pass
        else:
            QTimer.singleShot(50, self.if_empty_start_pagepicker)

    def if_empty_start_pagepicker(self):
        if len(self.scene.items()) == 0:
            e = events.PagePickerOpenEvent
            self.E.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromMainWin))


    @dataclass
    class API:
        """API只能用在初始化之后的函数中,否则会出错容易"""

        def __init__(self, superior: "Clipper"):
            self.superior = superior

        pass

    class PDFView(QGraphicsView):
        def __init__(self, scene, parent=None, superior: "Clipper" = None):
            super().__init__(parent)
            self.setScene(scene)
            self.superior = superior
            self.root = superior
            self.reset_ratio_value = 1
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            # self.verticalScrollBar().setRange(0,10)
            self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
                                QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
                                QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
            self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
            self.setViewportUpdateMode(self.FullViewportUpdate)
            self.setDragMode(self.ScrollHandDrag)

            self.setCursor(Qt.ArrowCursor)
            self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        def addpage(self, caller: "Clipper", pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.addpage, caller, Clipper)

            self.pageitem_layout_arrange()  # 先布局后插入
            self.scene().addItem(pageitem)
            self.centerOn(item=pageitem)

        def delpage(self, caller: "Clipper", pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.delpage, caller, Clipper)

            self.scene().removeItem(pageitem)

        def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().keyReleaseEvent(event)

        def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:

            if event.buttons() == Qt.RightButton:

                self.setDragMode(QGraphicsView.RubberBandDrag)
                self.superior.E.state.board.data_update()
                self.superior.E.state.board.show()
                if self.itemAt(event.pos()):
                    item = self.itemAt(event.pos())
                    final_item = item if isinstance(item,Clipper.PageItem) else item.parentItem()
                    self.root.E.curr_selected_pageitem=final_item
                else:
                    self.root.E.curr_selected_pageitem=None
                    self.root.E.last_rubberBand_rect=None
                tooltip(self.root.E.curr_selected_pageitem.__str__())

            # if event.buttons() == Qt.LeftButton:
            #     if not event.modifiers() == Qt.ControlModifier:
            #         self.setInteractive(False)
            #         if self.itemAt(event.pos()):
            #             item = self.itemAt(event.pos())
            #             if not isinstance(item,Clipper.PageItem):
            #                 item = item.parentItem()


            super().mousePressEvent(event)

        def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
            # print(self.scene().selectedItems())
            super().mouseMoveEvent(event)
            pass

        def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
            self.setInteractive(True)
            self.superior.E.state.board.hide()
            if self.root.E.curr_selected_pageitem is not None and self.root.E.last_rubberBand_rect is not None:
                pageitem: "Clipper.PageItem" = self.root.E.curr_selected_pageitem
                r = self.root.E.last_rubberBand_rect
                pos = pageitem.pageview.mapFromScene(self.mapToScene(r.x(), r.y()))
                x, y, w, h = pos.x(), pos.y(), r.width(), r.height()

                e = events.ClipboxCreateEvent
                self.root.signals.on_clipbox_create.emit(e(sender=pageitem, rubberBandRect=QRectF(x, y, w, h)))
            # self.root.E.curr_selected_pageitem = None
            self.root.E.last_rubberBand_rect = None

            super().mouseReleaseEvent(event)
            self.setDragMode(QGraphicsView.ScrollHandDrag)

        def viewRatioReset(self):
            self.scale(1 / self.reset_ratio_value, 1 / self.reset_ratio_value)
            self.reset_ratio_value = 1

        def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
            modifiers = QApplication.keyboardModifiers()

            if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
                e = events.PDFViewResizeViewEvent
                if event.angleDelta().y() > 0:
                    self.scale(1.1, 1.1)
                    self.reset_ratio_value *= 1.1
                    # ALL.signals.on_PDFView_ResizeView.emit(
                    #     e(eventType=e.zoomInType, pdfview=self, ratio=self.reset_ratio_value))
                else:
                    self.scale(1 / 1.1, 1 / 1.1)
                    self.reset_ratio_value /= 1.1
                    # ALL.signals.on_PDFView_ResizeView.emit(
                    #     e(eventType=e.zoomOutType, pdfview=self, ratio=self.reset_ratio_value))
                pass
            else:
                super().wheelEvent(event)
            pass

        def pageitem_moveto_oldpage_bottom(self, old_item: 'Clipper.PageItem', new_item: 'Clipper.PageItem'):
            new_pos = QPointF(old_item.x(), old_item.y() + old_item.boundingRect().height())
            # print(new_pos)
            new_item.setPos(new_pos)

        def pageitem_moveto_oldpage_left(self, old_item: 'Clipper.PageItem', new_item: 'Clipper.PageItem'):
            new_pos = QPointF(old_item.x() + old_item.boundingRect().width(), old_item.y())
            # print(new_pos)
            new_item.setPos(new_pos)

        def pageitem_relayout(self):
            oldList = list(self.root.E.pdfview.pageitem_container.uuidBased_data.values())
            newList = []
            for pageitem in oldList:
                newList.append(pageitem)
                self.pageitem_layout_arrange(newList)

        def pageitem_layout_arrange(self, pageItemList=None):

            config = self.root.E.config.mainview
            viewlayoutmode = config.layout_mode
            pdfview = self.root.E.pdfview
            if pageItemList is None:
                pageItemList = list(self.root.E.pdfview.pageitem_container.uuidBased_data.values())
            newitem: 'Clipper.PageItem' = pageItemList[-1]
            old_count = len(pageItemList) - 1
            if old_count == 0:  # 由于每次进来必然加载了一个所以这里可能用不太到
                newitem.setPos(0, 0)
                return
            if viewlayoutmode == pdfview.layoutmode.Horizontal:
                row = config.layout_row_per_col
                rem = old_count % row  #
                if rem != 0:
                    olditem = pageItemList[-2]
                    self.pageitem_moveto_oldpage_bottom(olditem, newitem)
                else:
                    olditem = pageItemList[-row - 1]
                    self.pageitem_moveto_oldpage_left(olditem, newitem)
                pass

            elif viewlayoutmode == pdfview.layoutmode.Vertical:
                col = config.layout_col_per_row
                rem = old_count % col
                if rem != 0:
                    olditem = pageItemList[-2]
                    self.pageitem_moveto_oldpage_left(olditem, newitem)
                else:
                    olditem = pageItemList[-col - 1]
                    self.pageitem_moveto_oldpage_bottom(olditem, newitem)

        def centerOn(self, pos: "Union[QPoint]" = None, item: "QGraphicsItem" = None):
            """居中显示"""
            assert pos is not None or item is not None
            if pos is None:
                x, y, r, b = item.boundingRect().left(), item.boundingRect().top(), item.boundingRect().right(), item.boundingRect().bottom()

                pos = item.mapToScene(int((x + r) / 2), int((y + b) / 2)).toPoint()
            curr_view_center = self.mapToScene(int(self.viewport().width() / 2),
                                               int(self.viewport().height() / 2)).toPoint()
            dp = pos - curr_view_center
            self.safeScroll(dp.x(), dp.y())

        def safeScroll(self, x, y):
            """遇到边界会扩大scene"""
            x_scroll = self.horizontalScrollBar()
            y_scroll = self.verticalScrollBar()
            rect = self.sceneRect()
            if x_scroll.value() + x > x_scroll.maximum():
                rect.setRight(rect.right() + x)
                # self.setSceneRect(rect.x(),rect.y(),rect.width()+x,rect.height())
            if x_scroll.value() + x < x_scroll.minimum():
                rect.setLeft(rect.left() + x)
                # self.setSceneRect(rect.x()+x, rect.y(), rect.width() + x, rect.height())
            if y_scroll.value() + y > y_scroll.maximum():
                # self.setSceneRect(rect.x(),rect.y(),rect.width(),rect.height()+y)
                rect.setBottom(rect.bottom() + y)
            if y_scroll.value() + y < y_scroll.minimum():
                rect.setTop(rect.top() + y)
                # self.setSceneRect(rect.x(),rect.y()+y,rect.width(),rect.height())
            self.setSceneRect(rect)
            x_scroll.setValue(x_scroll.value() + x)
            y_scroll.setValue(y_scroll.value() + y)

        # pass
        # def smoothScroll(self,x,y,times=5,gap=0.1):
        #     x_scroll = self.horizontalScrollBar()
        #     y_scroll = self.verticalScrollBar()
        #     x,y=int(x/times),int(y/times)
        #     for i in range(times):
        #         x_scroll.setValue(x_scroll.value() + x)
        #         y_scroll.setValue(y_scroll.value() + y)
        #         time.sleep(0.1/times)

    class RightSideBar(QWidget):
        def __init__(self, parent=None, superior: "Clipper" = None):
            super().__init__(parent)
            self.superior = superior
            self.root = superior

            self.pagelist = self.PageList(parent=self, superior=self, root=self.root)
            self.cardlist = self.CardList(parent=self, superior=self, root=self.root)
            self.buttonPanel = self.ButtonPanel(parent=self, superior=self, root=self.root)
            self.init_UI()

        def addpage(self, caller, pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.addpage, caller, Clipper)
            pdfname = funcs.str_shorten(os.path.basename(pageitem.pageinfo.pdf_path))
            # pagenum = str(pageitem.pageinfo.pagenum)
            item_pdf = self.PageList.PDFItem(pdfname, pageitem)
            item_page = self.PageList.PageNumItem(pageitem)
            self.pagelist.model.appendRow([item_pdf, item_page])
            pageitem.pagelist_index = QPersistentModelIndex(item_pdf.index())

        def delpage(self, caller, pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.delpage, caller, Clipper)
            self.pagelist.model.removeRow(pageitem.pagelist_index.row())

        def changepage(self, caller, pageitem: "Clipper.PageItem"):
            funcs.caller_check(Clipper.changepage, caller, Clipper)
            row, col = pageitem.pagelist_index.row(), pageitem.pagelist_index.column()
            item_pdf: "Clipper.RightSideBar.PageList.PDFItem" = self.pagelist.model.item(row, col)
            item_page: "Clipper.RightSideBar.PageList.PageNumItem" = self.pagelist.model.item(row, col + 1)
            item_pdf.update_data(self, pageitem)
            item_page.update_data(self, pageitem)

        def nextCard(self):
            selectionModel: "QItemSelectionModel" = self.cardlist.view.selectionModel()
            if len(selectionModel.selectedIndexes()) == 0:
                if self.cardlist.model.rowCount() == 0:
                    self.root.addCard()
                self.selectRow(0, self.cardlist.model, self.cardlist.view)
            else:
                index: "list[QModelIndex]" = selectionModel.selectedIndexes()[0:2]
                row = index[0].row()
                if row + 1 < self.cardlist.model.rowCount():
                    self.selectRow(row + 1, self.cardlist.model, self.cardlist.view)
                else:
                    self.root.addCard()
                    self.selectRow(row + 1, self.cardlist.model, self.cardlist.view)
            pass

        def prevCard(self):
            selectionModel: "QItemSelectionModel" = self.cardlist.view.selectionModel()
            rowcount = self.cardlist.model.rowCount() - 1
            if len(selectionModel.selectedIndexes()) == 0:
                if self.cardlist.model.rowCount() == 0:
                    self.root.addCard()
                    self.selectRow(0, self.cardlist.model, self.cardlist.view)
                else:
                    self.selectRow(rowcount, self.cardlist.model, self.cardlist.view)
            else:
                index: "QModelIndex" = selectionModel.selectedIndexes()[0:2]
                row = index[0].row()
                if row > 0:
                    self.selectRow(row - 1, self.cardlist.model, self.cardlist.view)

            pass

        def cardCount(self):
            return self.cardlist.model.rowCount()

        def selectCardRow(self, rownum):
            self.selectRow(rownum, self.cardlist.model, self.cardlist.view)

        def selectRow(self, rownum, model: "QStandardItemModel", view: "QAbstractItemView"):
            row = [model.index(rownum, 0), model.index(rownum, 1)]
            view.selectionModel().clearSelection()
            view.selectionModel().select(QItemSelection(*row), QItemSelectionModel.Select)

        def QAswitch(self, given=None):
            d = {
                "A": objs.SrcAdmin.imgDir.answer,
                "Q": objs.SrcAdmin.imgDir.question,
            }
            if given:
                self.buttonPanel.widget_button_QA.setText(given)
                self.buttonPanel.widget_button_QA.setIcon(QIcon(d[given]))
            else:
                if self.buttonPanel.widget_button_QA.text() == "Q":
                    self.buttonPanel.widget_button_QA.setText("A")
                    self.buttonPanel.widget_button_QA.setIcon(QIcon(objs.SrcAdmin.imgDir.answer))
                else:
                    self.buttonPanel.widget_button_QA.setText("Q")
                    self.buttonPanel.widget_button_QA.setIcon(QIcon(objs.SrcAdmin.imgDir.question))
        def macro_switch(self):
            # objs.macro.on_switch_handle()
            if objs.macro.state == objs.macro.runningState:
                self.buttonPanel.widget_button_macro.setIcon(QIcon(objs.SrcAdmin.imgDir.robot_red))
            elif objs.macro.state == objs.macro.pauseState:
                self.buttonPanel.widget_button_macro.setIcon(QIcon(objs.SrcAdmin.imgDir.robot_green))
            else:
                self.buttonPanel.widget_button_macro.setIcon(QIcon(objs.SrcAdmin.imgDir.robot_black))

        def init_UI(self):
            self.V_layout = QVBoxLayout()
            self.V_layout.addWidget(self.pagelist)
            self.V_layout.addWidget(self.cardlist)
            self.V_layout.addWidget(self.buttonPanel)
            self.V_layout.setStretch(0, 1)
            self.V_layout.setStretch(1, 1)
            self.setLayout(self.V_layout)

        class PageList(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.view = QTreeView(self)
                self.model = QStandardItemModel(self)
                self.root.E.rightsidebar.pagelist.model = self.model
                self.V_layout = QVBoxLayout(self)
                self.addButton = QToolButton(self)
                self.delButton = QToolButton(self)
                self.init_UI()
                self.init_model()

            def on_addButton_clicked_handle(self):
                e = events.PagePickerOpenEvent
                self.root.E.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromAddButton))

            def init_UI(self):
                H_layout = QHBoxLayout()
                V_layout2 = QVBoxLayout()
                self.label = QLabel("page list")
                self.addButton.setText("+")
                self.delButton.setText("-")
                self.V_layout.addLayout(H_layout)
                self.V_layout.addLayout(V_layout2)
                self.V_layout.setStretch(1, 1)
                self.view.setIndentation(0)
                H_layout.addWidget(self.label)
                H_layout.addWidget(self.addButton)
                H_layout.addWidget(self.delButton)
                V_layout2.addWidget(self.view)

            pass

            def init_model(self):
                self.model.clear()
                pdfname = QStandardItem("PDFname")  # 存文件路径
                pagenum = QStandardItem("pagenum")  # 存页码和graphics_page对象
                self.model.setHorizontalHeaderItem(0, pdfname)
                self.model.setHorizontalHeaderItem(1, pagenum)
                self.pagepicker = None
                self.pageItemDict = {}
                self.view.setModel(self.model)
                self.view.header().setDefaultSectionSize(180)
                self.view.header().setSectionsMovable(False)
                self.view.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                self.view.header().setSectionResizeMode(0, QHeaderView.Interactive)
                self.view.header().setSectionResizeMode(1, QHeaderView.Stretch)
                self.view.setColumnWidth(1, 10)

            class PDFItem(QStandardItem):
                def __init__(self, PDFName, selfData: "Clipper.PageItem"):
                    super().__init__(PDFName)
                    self.setFlags(self.flags() & ~ Qt.ItemIsEditable & ~ Qt.ItemIsDragEnabled)
                    self.pageitem: "Clipper.PageItem" = selfData
                    self.setData(selfData, Qt.UserRole)
                    self.setToolTip(selfData.pageinfo.pdf_path)

                def update_data(self, caller, pageitem: "Clipper.PageItem"):
                    funcs.caller_check(Clipper.RightSideBar.changepage, caller, Clipper.RightSideBar)
                    PDFName = funcs.str_shorten(os.path.basename(pageitem.pageinfo.pdf_path))
                    self.setText(PDFName)
                    self.setToolTip(pageitem.pageinfo.pdf_path)

            class PageNumItem(QStandardItem):
                def __init__(self, selfData: "Clipper.PageItem"):
                    super().__init__(str(selfData.pageinfo.pagenum))
                    self.setFlags(self.flags() & ~ Qt.ItemIsEditable & ~ Qt.ItemIsDragEnabled)
                    self.pageitem: "Clipper.PageItem" = selfData
                    self.setData(selfData, Qt.UserRole)

                def update_data(self, caller, pageitem: "Clipper.PageItem"):
                    funcs.caller_check(Clipper.RightSideBar.changepage, caller, Clipper.RightSideBar)
                    self.setText(str(pageitem.pageinfo.pagenum))

        class CardList(QWidget):
            itemMiddlePosi = 0
            itemTopPosi = 1
            itemBottomPosi = -1
            treeBottomPosi = -2

            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.model = QStandardItemModel(self)
                self.root.E.rightsidebar.cardlist.model = self.model
                self.label = QLabel(self)
                self.view = QTreeView(self)
                self.addButton = QToolButton(self)
                self.delButton = QToolButton(self)
                self.init_UI()
                self.init_model()
                self.total_new_card = 0

            def new_card_count(self):
                self.total_new_card += 1
                return self.total_new_card

            def init_UI(self):
                H_layout = QHBoxLayout()
                V_layout2 = QVBoxLayout()
                self.label.setText("card list")
                self.V_layout = QVBoxLayout(self)
                self.addButton.setText("+")
                self.delButton.setText("-")
                self.view.setIndentation(0)
                self.view.header().setSectionResizeMode(QHeaderView.Stretch)

                H_layout.addWidget(self.label)
                H_layout.addWidget(self.addButton)
                H_layout.addWidget(self.delButton)
                V_layout2.addWidget(self.view)
                self.view.setDragEnabled(True)
                self.view.setDragDropMode(QAbstractItemView.InternalMove)
                self.view.setDefaultDropAction(Qt.MoveAction)
                self.view.setAcceptDrops(True)
                # self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.view.dropEvent = self.dropEvent
                self.V_layout.addLayout(H_layout)
                self.V_layout.addLayout(V_layout2)
                self.V_layout.setStretch(1, 1)

            def dropEvent(self, event: QtGui.QDropEvent) -> None:
                """
                利用光标偏移的结果是否还在原item中,判断属于何种插入方式.(上中下,底层)代码分别是1,0,-1,-2
                允许组嵌套,但不允许重复.
                """
                pos = event.pos()
                drop_index = self.view.indexAt(pos)
                item_target = self.model.itemFromIndex(drop_index)  # 获取目标项
                insert_posi = self.position_insert_check(pos, drop_index)  # 位置检查
                item_target, insert_posi = self.item_target_recorrect(item_target, insert_posi)  # 通过修正函数重新确定位置
                selected_row_li = self.rowli_index_make()  # 选中的行的检查
                # 下面是根据不同的插入情况做出选择。
                self.rowli_selected_insert(insert_posi, selected_row_li, item_target)

            def itemChild_row_remove(self, item):
                """不需要parent,自己能产生parent"""
                parent = item[0].parent() if item[0].parent() is not None else self.model_rootNode
                return parent.takeRow(item[0].row())

            def rowli_selected_insert(self, insert_posi, selected_row_li, item_target):
                for row in selected_row_li: self.itemChild_row_remove(row)
                temp_rows_li = []
                if insert_posi != self.treeBottomPosi:
                    posi_row = item_target.row()
                    parent = self.model_rootNode
                    while parent.rowCount() > 0:
                        temp_rows_li.append(parent.takeRow(0))
                    if insert_posi == self.itemTopPosi:  # 上面
                        final_rows_li = temp_rows_li[0:posi_row] + selected_row_li + temp_rows_li[posi_row:]
                    else:
                        final_rows_li = temp_rows_li[0:posi_row + 1] + selected_row_li + temp_rows_li[posi_row + 1:]
                    for row in final_rows_li:
                        parent.appendRow(row)
                else:
                    for row in selected_row_li:
                        # row[0].level = self.model_rootNode.level + 1
                        # row[1].level = self.model_rootNode.level + 1
                        self.model_rootNode.appendRow(row)

            def rowli_index_make(self):
                """# 源item每次都会选择一行的所有列,而且所有列编成1维数组,所以需要下面的步骤重新组回来."""
                selected_indexes_li = self.view.selectedIndexes()
                selected_items_li = list(map(self.model.itemFromIndex, selected_indexes_li))
                selected_row_li = []
                for i in range(int(len(selected_items_li) / 2)):
                    selected_row_li.append([selected_items_li[2 * i], selected_items_li[2 * i + 1]])
                return selected_row_li

            def position_insert_check(self, pos, drop_index):
                """测定插入位置"""

                index_height = self.view.rowHeight(drop_index)  #
                drop_index_offset_up = self.view.indexAt(pos - QPoint(0, index_height / 4))  # 高处为0
                drop_index_offset_down = self.view.indexAt(pos + QPoint(0, index_height / 4))
                insertPosi = self.itemMiddlePosi  # 0中间,1上面,-1下面,-2底部
                if drop_index_offset_down == drop_index_offset_up:
                    insertPosi = self.itemMiddlePosi
                else:
                    if drop_index != drop_index_offset_up:
                        insertPosi = self.itemTopPosi
                    elif drop_index != drop_index_offset_down:
                        insertPosi = self.itemBottomPosi
                return insertPosi

            def item_target_recorrect(self, item_target, insertPosi):
                """修正插入的对象和插入的位置"""
                # 拉到底部
                if item_target is None:
                    insertPosi = self.treeBottomPosi
                    item_target = self.model_rootNode

                if item_target.column() > 0:
                    item_target = self.model_rootNode.child(item_target.row(), 0)

                return item_target, insertPosi

            def init_model(self):
                self.newcardcount = 0
                self.ClipboxState = None
                # self.model=QStandardItemModel(self)
                # self.listView=QTreeView(self)
                self.model_rootNode = self.model.invisibleRootItem()
                self.model_rootNode.character = "root"
                self.model_rootNode.level = -1
                self.model_rootNode.primData = None
                label_id = self.CardItem("card_id", parent=self, superior=self, root=self.root)
                label_desc = self.DescItem("desc", parent=self, superior=self, root=self.root)
                self.model.setHorizontalHeaderItem(1, label_id)
                self.model.setHorizontalHeaderItem(0, label_desc)
                self.view.setModel(self.model)
                self.view.header().setDefaultSectionSize(150)
                self.view.header().setSectionsMovable(False)
                self.view.setColumnWidth(1, 10)

            class CardItem(QStandardItem):
                def __init__(self, s, parent=None, superior: "Clipper.RightSideBar.CardList" = None,
                             root: "Clipper" = None):
                    super().__init__(s)
                    self.superior = superior
                    self.root = root
                    self.setFlags(self.flags() & ~Qt.ItemIsEditable)
                    self.newCard = s == "/"

                def setText(self, atext: str) -> None:
                    super().setText(atext)
                    self.newCard = self.text() == "/"

                pass

            class DescItem(QStandardItem):
                def __init__(self, s, parent=None, superior: "Clipper.RightSideBar.CardList" = None,
                             root: "Clipper" = None, cardItem=None):
                    super().__init__(s)
                    self.superior = superior
                    self.cardItem: "Clipper.RightSideBar.CardList.CardItem" = cardItem

                    self.root = root
                    self.info = self.Info()

                    self.uuid = funcs.uuid_random_make()
                    # self.root.E.rightsidebar.cardlist.dict[self.uuid]=self

                def del_self(self, caller):
                    funcs.caller_check(Clipper.delCard, self, Clipper)
                    for clipboxuuid in self.info.clipboxuuid_list:
                        clipbox: "Clipper.ClipBox" = self.root.E.clipbox.container[clipboxuuid]
                        clipbox.editableData.card_list_remove(self, self.uuid, True)

                @dataclass
                class Info:
                    clipboxuuid_list: "list[str]" = field(default_factory=list)

                    def clipbox_del(self, caller, s):
                        if s in self.clipboxuuid_list:
                            self.clipboxuuid_list.remove(s)

                    def clipbox_add(self, caller, s):
                        funcs.caller_check(Clipper.clipbox_add_card, caller, Clipper)
                        if s not in self.clipboxuuid_list:
                            self.clipboxuuid_list.append(s)

                pass

        class ButtonPanel(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.g_layout = QGridLayout(self)
                self.widget_button_QA = QToolButton(self)
                self.widget_button_hide = QToolButton(self)
                self.widget_button_confirm = QToolButton(self)
                self.widget_button_relayout = QToolButton(self)
                self.widget_button_config = QToolButton(self)
                self.widget_button_resetRatio = QToolButton(self)
                self.widget_button_clearView = QToolButton(self)
                self.widget_button_macro = QToolButton(self)
                e = events.RightSideBarButtonGroupEvent

                imgDir = objs.SrcAdmin.imgDir
                buttoninfoli = [(self.widget_button_hide, 0, imgDir.right_direction, e.defaultType.hideRighsidebar,
                                 "隐藏侧边栏\nhide rightsidebar"),
                                (self.widget_button_clearView, 1, imgDir.clear, e.defaultType.clearView,
                                 "清空视图中的项目\nclear view items"),
                                (self.widget_button_resetRatio, 2, imgDir.reset, e.defaultType.resetViewRatio,
                                 "恢复视图为正常比例\nreset view size"),
                                (self.widget_button_QA, 3, imgDir.question, e.defaultType.QAswitch,
                                 "切换插入点为Q或A\nswitch Q or A"),
                                (self.widget_button_relayout, 4, imgDir.refresh, e.defaultType.reLayout,
                                 "视图布局重置\nview relayout"),
                                (self.widget_button_config, 5, imgDir.config, e.defaultType.config,
                                 "配置选项\nset configuration"),
                                (self.widget_button_confirm, 7, imgDir.correct, e.defaultType.correct,
                                 "开始插入clipbox的任务\nBegin the task of inserting Clipbox"),
                                (self.widget_button_macro,6,imgDir.robot_black,e.defaultType.macro,
                                 "启动或暂停宏\nstart or stop macro")
                                ]
                self.buttondatali = [self.ButtonData(*data) for data in buttoninfoli]
                self.widget_button_QA.setText("Q")
                self.init_UI()

            def init_UI(self):
                e = events.RightSideBarButtonGroupEvent
                # def handle(buttontype):
                #     return lambda: self.root.on_rightSideBar_buttonGroup_clicked_handle(e(type=buttontype))
                for data in self.buttondatali:
                    data.button.setIcon(QIcon(data.icondir))
                    self.g_layout.addWidget(data.button, 0, data.layoutpos)
                    handle = lambda x: lambda: self.root.signals.on_rightSideBar_buttonGroup_clicked.emit(e(type=x))
                    data.button.clicked.connect(handle(data.eventType))
                    data.button.setToolTip(data.tooltip)

            @dataclass
            class ButtonData:
                button: "QToolButton"
                layoutpos: "int"
                icondir: "str"
                eventType: "int"
                tooltip: "str"

            pass

    class PageItem(QGraphicsItem):
        def __init__(self, png_path: "str", data: "objs.PageInfo", superior: "Clipper.PDFView", root: "Clipper", *args,
                     **kwargs):
            super().__init__(*args, **kwargs)

            self.superior = superior
            self.root = root
            self.signals = self.root.signals
            self.ratio = 1  # 这个ratio是需要通过1:1恢复的方式去掉的., 所以必须有,不能直接修改pageinfo里的ratio
            self.pageinfo = data
            self.png_path = png_path
            self.pagelist_index: "QPersistentModelIndex" = None
            self._clipbox_dict: "OrderedDict[str,Clipper.ClipBox]" = OrderedDict()
            self.uuid = hash(self).__str__()  # 这个uuid不用做存储,仅在内存中标记唯一性

            self.pageview = self.PageView(superior=self, root=self.root)
            self.toolsbar = self.ToolsBar(superior=self, root=self.root)
            self.setAcceptHoverEvents(True)
            # self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            self.events = objs.AllEventAdmin([
                [self.toolsbar.widget_button_close.clicked, self.on_widget_button_close_clicked_handle],
                [self.toolsbar.widget_button_pageinfo.clicked, self.on_widget_button_pageinfo_clicked_handle],
                [self.toolsbar.widget_button_prev.clicked, self.on_widget_button_prev_clicked_handle],
                [self.toolsbar.widget_button_next.clicked, self.on_widget_button_next_clicked_handle],
                [self.toolsbar.widget_button_fullscreen.clicked, self.on_widget_button_fullscreen_clicked_handle],
                [self.toolsbar.widget_button_recover.clicked, self.on_widget_button_recover_clicked_handle],
                [self.signals.on_pageItem_resize_event, self.on_pageItem_resize_event_handle],
            ]).bind()

        def clipbox_dict_del_key(self, caller, key):
            funcs.caller_check(Clipper.delClipbox, caller, Clipper)
            del self._clipbox_dict[key]

        @property
        def clipbox_dict(self):
            return self._clipbox_dict.copy()

        def clipbox_dict_add_keyValue(self, caller, key, value):
            funcs.caller_check(Clipper.addClipbox, caller, Clipper)
            if key in self._clipbox_dict:
                raise ValueError(f"{key} already in dict")
            self._clipbox_dict[key] = value

        def on_pageItem_resize_event_handle(self, event: "events.PageItemResizeEvent"):
            v_size_width = self.superior.size().width()
            v_size_height = self.superior.size().height()
            v_viewport_width = self.superior.viewport().width()
            v_viewport_height = self.superior.viewport().height()
            v_framerect_width = self.superior.frameRect().width()
            v_framerect_height = self.superior.frameRect().height()
            if event.type == event.defaultType.fullscreen:
                ratio = v_viewport_width / self.pageview.boundingRect().width()
                self.pageview.zoom(ratio, center=event.center)
            elif event.type == event.defaultType.fitheight:
                ratio = v_viewport_height / self.pageview.boundingRect().height()
                self.pageview.zoom(ratio, center=event.center)
            elif event.type == event.defaultType.recover:
                ratio = 1
                self.pageview.zoom(ratio, center=event.center)

        def on_widget_button_recover_clicked_handle(self):
            e = events.PageItemResizeEvent
            self.on_pageItem_resize_event_handle(e(type=e.defaultType.recover, center=e.centertype.item_center))
            pass

        def on_widget_button_fullscreen_clicked_handle(self):
            e = events.PageItemResizeEvent
            # self.signals.on_pageItem_resize_event.emit(
            #     e(type=e.defaultType.fullscreen, center=e.centertype.item_center))
            self.on_pageItem_resize_event_handle(e(type=e.defaultType.fullscreen, center=e.centertype.item_center))
            pass

        def on_widget_button_prev_clicked_handle(self):
            e = events.PageItemAddToSceneEvent
            if self.pageinfo.pagenum > 0:
                modifiers = QApplication.keyboardModifiers()
                if modifiers & Qt.ControlModifier:
                    self.widget_button_next_prev_clicked(-1, e.defaultType.changePage)
                else:
                    self.widget_button_next_prev_clicked(-1, e.defaultType.addPage)

        def on_widget_button_next_clicked_handle(self):
            e = events.PageItemAddToSceneEvent
            if self.pageinfo.pagenum < len(fitz.Document(self.pageinfo.pdf_path)):
                modifiers = QApplication.keyboardModifiers()
                if modifiers & Qt.ControlModifier:
                    self.widget_button_next_prev_clicked(1, e.defaultType.changePage)
                else:
                    self.widget_button_next_prev_clicked(1, e.defaultType.addPage)

        def widget_button_next_prev_clicked(self, inc, addtype):
            pageinfo = objs.PageInfo(self.pageinfo.pdf_path, self.pageinfo.pagenum + inc, self.pageinfo.ratio)
            e = events.PageItemAddToSceneEvent
            self.signals.on_pageItem_addToScene.emit(e(type=addtype, data=pageinfo, sender=self))

        def on_widget_button_pageinfo_clicked_handle(self):
            # print("on_widget_button_pageinfo_clicked_handle")
            e = events.PagePickerOpenEvent
            self.root.on_pagepicker_open_handle(e(type=e.defaultType.fromPage, fromPageItem=self))
            # self.root.signals.on_pagepicker_PDFopen.emit(e(type=e.defaultType.fromPage,fromPageItem=self))

        def on_widget_button_close_clicked_handle(self):
            e = events.PageItemCloseEvent()
            e.pageitem = self
            self.signals.on_pageitem_close.emit(e)

        def boundingRect(self) -> QtCore.QRectF:
            w = self.pageview.boundingRect().width()
            h = self.pageview.boundingRect().height()
            rect = QRectF(0, 0, w, h)

            return rect

        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:
            self.prepareGeometryChange()  # 这个 非常重要. https://www.cnblogs.com/ybqjymy/p/13862382.html
            painter.setPen(QPen(QColor(127, 127, 127), 2.0, Qt.DashLine))
            painter.drawRect(self.boundingRect())
            width1 = self.toolsbar.boundingRect().width()
            width2 = self.pageview.boundingRect().width()
            height2 = self.pageview.boundingRect().height()
            self.toolsbar.setPos(width2 - width1, height2)
            if self.root.E.curr_selected_pageitem == self:
                self.toolsbar.show()
                count = len(self.root.E.pdfview.pageitem_container.uuidBased_data)
                self.setZValue(count)
            else:
                self.toolsbar.hide()
                self.setZValue(0)

        def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            self.setFlag(QGraphicsItem.ItemIsMovable, False)
            # self.setFlag(QGraphicsItem.ItemIsSelectable, False)
            super().mouseReleaseEvent(event)

        def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            self.root.E.curr_selected_pageitem = self
            modifiers = QApplication.keyboardModifiers()
            if (event.modifiers() & Qt.ControlModifier):
                if event.button() == Qt.LeftButton:
                    self.setFlag(QGraphicsItem.ItemIsMovable, True)
                    # self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            else:
                if event.buttons() == Qt.MidButton:
                    pass  # 本来这里有一个全屏功能,删掉了.
                elif event.button() == Qt.RightButton:  # 了解当前选中的是哪个pageitem,因为我之前已经取消了selectable功能,

                    e = events.PageItemClickEvent
                    # ALL.signals.on_pageItem_clicked.emit(e(sender=self, pageitem=self, eventType=e.rightClickType))
                    super().mousePressEvent(event)
                elif event.button() == Qt.LeftButton:
                    # self.on_pageItem_clicked.emit(
                    #     PageItemClickEvent(sender=self, pageitem=self, eventType=PageItemClickEvent.leftClickType))
                    # self.toolsBar.hide()
                    self.toolsbar.show()
                    super().mousePressEvent(event)

            super().mousePressEvent(event)

        def changepage(self, caller, data: "objs.PageInfo"):
            """事先加载好pixdir"""
            assert type(data) == objs.PageInfo
            funcs.caller_check(Clipper.changepage, caller, Clipper)
            self.png_path = funcs.pixmap_page_load(data.pdf_path, data.pagenum, data.ratio)
            self.pageview.setPixmap(QPixmap(self.png_path))
            self.pageview.zoom(self.ratio,center=self.pageview.nocenter)
            self.pageinfo = data
            self.toolsbar.update_from_pageinfo(self)

        class PageView(QGraphicsPixmapItem):
            mousecenter = 0
            item_center = 1
            view_center = 2
            nocenter = 3

            def __init__(self, superior: "Clipper.PageItem" = None, root: "Clipper" = None, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.superior = superior
                self.root = root
                self.setPixmap(QPixmap(self.superior.png_path))
                self.setParentItem(self.superior)
                self.is_fullscreen = False
                self.setAcceptHoverEvents(True)
                self.mousecenter_pos = None
                # self.mouse_item_percent_p: "objs.Position" = None  # 鼠标在图元中的比例位置
                # self.mouse_item_old_abs_p: "QPointF" = None
                # self.item_center_percent_p: "objs.Position" = None
                # self.item_center_old_abs_p: "QPointF" = None
                # self.view_center_scene_p: "QPoint" = None
                self.item_percent_p_at_view_center: "objs.Position" = None
                # self.viewcenter_pos = None
                # self.itemcenter_pos = None
                self.view_center_scene_p = None
                self.view_center_item_p = None
                self.item_center_item_size = None

            # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            #     print(f"event.pos={event.pos()},self.mapToScene(event.pos())={self.mapToScene(event.pos())}")
            #     super().mousePressEvent(event)

            def __repr__(self):
                return self.superior.pageinfo.__repr__()

            def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                e = events.PageItemResizeEvent
                if not self.is_fullscreen:
                    self.is_fullscreen = True
                    self.superior.on_pageItem_resize_event_handle(
                        e(type=e.defaultType.fullscreen, center=e.centertype.mousecenter))
                else:
                    self.is_fullscreen = False
                    self.superior.on_pageItem_resize_event_handle(e(type=e.defaultType.recover))

            def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                self.mouse_center_pos_get(event.pos())
                super().hoverEnterEvent(event)

            def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                self.mouse_center_pos_get(event.pos())
                super().hoverMoveEvent(event)

            def wheelEvent(self, event):
                modifiers = QApplication.keyboardModifiers()  # 判断ctrl键是否按下
                if modifiers == QtCore.Qt.ControlModifier:
                    self.mouse_center_pos_get(event.pos())
                    # print(event.delta().__str__())
                    if event.delta() > 0:
                        self.zoomIn()
                    else:
                        self.zoomOut()
                else:
                    super().wheelEvent(event)

            def zoomIn(self):
                """放大"""
                self.zoom(self.superior.ratio * 1.1)

            def zoomOut(self):
                """缩小"""
                self.zoom(self.superior.ratio / 1.1)

            def item_center_pos_get(self):
                self.item_center_item_size = [0.5, 0.5]
                self.view_center_pos_get()

            def mouse_center_pos_get(self, pos):
                self.mouse_center_item_p = [pos.x() / self.boundingRect().width(),
                                            pos.y() / self.boundingRect().height()]
                self.mouse_center_scene_p = self.mapToScene(pos)

            def view_center_pos_get(self):
                view = self.superior.superior
                centerpos = QPointF(view.size().width() / 2, view.size().height() / 2)
                self.view_center_scene_p = view.mapToScene(centerpos.toPoint())
                p = self.mapFromScene(self.view_center_scene_p)
                self.view_center_item_p = [p.x() / self.boundingRect().width(), p.y() / self.boundingRect().height()]

            def center_zoom(self, center=0):
                if center == self.mousecenter:
                    X = self.mouse_center_item_p[0] * self.boundingRect().width()
                    Y = self.mouse_center_item_p[1] * self.boundingRect().height()
                    new_scene_p = self.mapToScene(X, Y)
                    dx = new_scene_p.x() - self.mouse_center_scene_p.x()
                    dy = new_scene_p.y() - self.mouse_center_scene_p.y()
                elif center == self.item_center:
                    # 获取放大后的中心坐标
                    new_x = self.item_center_item_size[0] * self.boundingRect().width()
                    new_y = self.item_center_item_size[1] * self.boundingRect().height()
                    # 转为场景坐标
                    new_p = self.mapToScene(new_x, new_y)
                    # 当前场景加上dx,dy就能移动到放大后的中心坐标
                    dx = new_p.x() - self.view_center_scene_p.x()
                    dy = new_p.y() - self.view_center_scene_p.y()
                elif center == self.view_center:  # 以视图中心放大
                    view = self.superior.superior
                    new_x = self.item_percent_p_at_view_center.x * self.boundingRect().width()
                    new_y = self.item_percent_p_at_view_center.y * self.boundingRect().height()
                    new_p = self.mapToScene(new_x, new_y)
                    # new_view_center = view.mapToScene(int(view.viewport().width() / 2), int(view.viewport().height() / 2))
                    dx = new_p.x() - self.view_center_scene_p.x()
                    dy = new_p.y() - self.view_center_scene_p.y()
                    print(f"比例点的场景坐标={new_p},当前视口中心的场景坐标={self.view_center_scene_p}")
                self.superior.superior.safeScroll(dx, dy)
                pass

            def zoom(self, factor, center=None, needbase=True):
                """

                Args:
                    factor: 比例因子
                    center: 放大后中心的位置,跟随鼠标,或者图元中心,或者视口中心
                    needbase: base是指pageinfo里自带的比例是否要乘进去

                Returns:

                """
                if center is None:  # 默认是指针为中心放大
                    center = self.mousecenter
                    # center =self.view_center
                if center == self.item_center:  # 图元中心放大,需要获取图元的中心
                    self.view_center_pos_get()
                    self.item_center_pos_get()
                if center == self.view_center:  # 图元中心放大,需要获取图元的中心
                    self.item_center_pos_get()
                    self.view_center_pos_get()

                self.prepareGeometryChange()
                if factor < 0.07 or factor > 100:
                    # 防止过大过小
                    return
                pdf_path, pagenum, baseratio = self.path_page_ratio_get()
                factor2 = factor * baseratio if needbase else factor
                p = funcs.pixmap_page_load(pdf_path, pagenum, ratio=factor * baseratio)
                self.setPixmap(QPixmap(p))
                if center != self.nocenter:  # 只要不是 nocenter, 都要执行 center_zoom
                    self.center_zoom(center)

                self.keep_clipbox_in_postion()

                self.superior.ratio = factor

            def boundingRect(self) -> QtCore.QRectF:
                return QtCore.QRectF(0, 0, self.pixmap().width(), self.pixmap().height())

            def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem', widget: QWidget) -> None:
                super().paint(painter, option, widget)

            def path_page_ratio_get(self):
                pageinfo = self.superior.pageinfo
                return pageinfo.pdf_path, pageinfo.pagenum, pageinfo.ratio

            def keep_clipbox_in_postion(self):
                for box in self.superior.clipbox_dict.values():
                    box.keep_ratio()

            pass

        class ToolsBar(QGraphicsWidget):
            def __init__(self, superior: "Clipper.PageItem" = None, root: "Clipper" = None, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.superior = superior
                self.root = root
                self.imgdir = objs.SrcAdmin.imgDir
                self.setParentItem(self.superior)
                self.widget_button_close = QToolButton()
                self.widget_button_prev = QToolButton()
                self.widget_button_next = QToolButton()
                self.widget_button_recover = QToolButton()
                self.widget_button_fullscreen = QToolButton()
                self.widget_button_pageinfo = QToolButton()

                self.widgetdata_li = [self.widgetdata(*data) for data in [
                    (self.widget_button_close, self.imgdir.close, 0, 5, "关闭/close"),
                    (self.widget_button_next, self.imgdir.next, 0, 1,
                     "新建下一页/create next page to the view \n ctrl+click=改变当前页到下一页/Change the current page to the next"),
                    (self.widget_button_prev, self.imgdir.prev, 0, 0,
                     "新建上一页/create previous page to the view \n ctrl+click=改变当前页到上一页/Change the current page to the previous"),
                    (self.widget_button_recover, self.imgdir.reset, 0, 2, "重设大小/reset size"),
                    (self.widget_button_fullscreen, self.imgdir.expand, 0, 3, "全屏/fullscreen"),
                    (self.widget_button_pageinfo, None, 0, 4, "")
                ]]
                g = QGraphicsGridLayout(self)
                g.setSpacing(0.0)
                g.setContentsMargins(0.0, 0.0, 0.0, 0.0)
                self.widget_proxy_dict: "dict[QToolButton,QGraphicsProxyWidget]" = {}
                for data in self.widgetdata_li:
                    if data.imgdir:
                        data.widget.setIcon(QIcon(data.imgdir))
                    if data.tooltip != "":
                        data.widget.setToolTip(data.tooltip)
                    else:
                        data.widget.setStyleSheet(f"height:{self.widget_button_close.height() - 6}px")
                        self.update_from_pageinfo(self, needCheck=False)

                    self.widget_proxy_dict[data.widget] = QGraphicsProxyWidget(self)
                    self.widget_proxy_dict[data.widget].setContentsMargins(0.0, 0.0, 0.0, 0.0)
                    self.widget_proxy_dict[data.widget].setWidget(data.widget)
                    g.addItem(self.widget_proxy_dict[data.widget], data.x, data.y)
                self.setLayout(g)

            def update_from_pageinfo(self, caller, needCheck=True):
                if needCheck:
                    funcs.caller_check(Clipper.PageItem.changepage, caller, Clipper.PageItem)
                pdfname = funcs.str_shorten(os.path.basename(self.superior.pageinfo.pdf_path[:-4]))
                pdfpage = self.superior.pageinfo.pagenum
                DB = objs.SrcAdmin.DB.go(objs.SrcAdmin.DB.table_pdfinfo)
                pdfuuid = funcs.uuid_hash_make(self.superior.pageinfo.pdf_path)
                if DB.exists(DB.EQ(uuid=pdfuuid)):
                    offset = DB.select(DB.EQ(uuid=pdfuuid)).return_all().zip_up()[0]["offset"]
                else:
                    offset = 0
                bookpage = pdfpage + 1 - offset
                self.widget_button_pageinfo.setText(f"{pdfname} pdfpage={pdfpage},bookpage={bookpage}")
                self.widget_button_pageinfo.setToolTip(self.superior.pageinfo.pdf_path)

            def boundingRect(self) -> QtCore.QRectF:
                x, y = self.x(), self.y()
                w = 0
                for k, v in self.widget_proxy_dict.items():
                    w += v.boundingRect().width()
                h = self.widget_proxy_dict[self.widget_button_pageinfo].boundingRect().height()
                return QRectF(x, y, w, h)

            @dataclass
            class widgetdata:
                widget: "QToolButton"
                imgdir: "str"
                x: "int"
                y: "int"
                tooltip: "str"

            pass

        pass

    class ClipBox(QGraphicsRectItem):
        linewidth = 10
        toLeft, toRight, toTop, toBottom, toTopLeft, toTopRight, toBottomLeft, toBottomRight = 0, 1, 2, 3, 4, 5, 6, 7

        def __init__(self, superior: "Clipper.PageItem.PageView", root: "Clipper", rect: "QRectF", QA=None,
                     commentQA=None, clipuuid=None):
            super().__init__()
            b = superior.boundingRect()
            if rect.right() > b.right():
                rect.setRight(b.right())
            if rect.bottom() > b.bottom():
                rect.setBottom(b.bottom())
            if not b.contains(rect):
                raise ValueError(f"superior.boundingRect={superior.boundingRect()},rect={rect},选框不包含")
            self.superior = superior
            self.root = root

            self.uuid = clipuuid if clipuuid else funcs.clipbox_uuid_random_unique()
            self.setParentItem(self.superior)
            # self.comment_label=self.CommentLabel(self)
            self.close = self.Close(self)
            self.editableData = self.Data()
            self.editableData.clip_to_field = self.clip_to_field_initQA(QA)
            self.editableData.comment_to_field = self.comment_to_field_initQA(commentQA)

            self.setRect(rect)

            self.isHovered = False
            self.handle_at = None  # 选中的调整位置
            self.rect_when_click = None
            self.pos_when_click = QPointF()
            self.pageratio = 1
            self.setFlag(self.ItemIsMovable, True)
            self.setFlag(self.ItemIsSelectable, True)
            self.setFlag(self.ItemSendsGeometryChanges, True)
            self.setAcceptHoverEvents(True)

            self.setRect(rect)

        def calc_ratio(self):
            """记录上下左右所处的坐标系的比例，方便放大缩小跟随"""
            max_X, max_Y = self.superior.boundingRect().right(), self.superior.boundingRect().bottom()
            top, left, right, bottom = self.rect().top(), self.rect().left(), self.rect().right(), self.rect().bottom()
            self.ratioTop = (top) / max_Y
            self.ratioLeft = (left) / max_X
            self.ratioBottom = (bottom) / max_Y
            self.ratioRight = (right) / max_X

        def keep_ratio(self):
            w, h, x, y = self.superior.boundingRect().width(), self.superior.boundingRect().height(), self.x(), self.y()
            r = self.rect()
            # R = QRectF(self.ratioLeft * w,self.ratioTop * h,self.ratioRight * w,self.ratioBottom * h)
            r.setTop(self.ratioTop * h)
            r.setLeft(self.ratioLeft * w)
            r.setBottom(self.ratioBottom * h)
            r.setRight(self.ratioRight * w)
            # 之所以减原来的x,y可行,是因为图片的放大并不是膨胀放大,每个点都是原来的点,只是增加了一些新的点而已.
            self.setRect(r)

        def cursor_position_check(self, p: "QPointF"):
            """根据指针的位置,更改其样式"""
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
            self.pos_when_click = p = event.pos()
            rect = self.rect()
            self.rect_when_click = rect
            LT, LB = QPointF(rect.left(), rect.top()), QPointF(rect.left(), rect.bottom())
            RT, RB = QPointF(rect.right(), rect.top()), QPointF(rect.right(), rect.bottom())
            linewidth = self.linewidth
            if QLineF(p, LT).length() < linewidth:
                self.handle_at = self.toTopLeft
                self.setCursor(Qt.SizeFDiagCursor)  # 主对角线
            elif QLineF(p, LB).length() < linewidth:
                self.handle_at = self.toBottomLeft
                self.setCursor(Qt.SizeBDiagCursor)
            elif QLineF(p, RT).length() < linewidth:
                self.handle_at = self.toTopRight
                self.setCursor(Qt.SizeBDiagCursor)
            elif QLineF(p, RB).length() < linewidth:
                self.handle_at = self.toBottomRight
                self.setCursor(Qt.SizeFDiagCursor)
            elif abs(p.x() - rect.left()) < linewidth:
                self.handle_at = self.toLeft
                self.setCursor(Qt.SizeHorCursor)
            elif abs(p.x() - rect.right()) < linewidth:
                self.handle_at = self.toRight
                self.setCursor(Qt.SizeHorCursor)
            elif abs(p.y() - rect.top()) < linewidth:
                self.handle_at = self.toTop
                self.setCursor(Qt.SizeVerCursor)
            elif abs(p.y() - rect.bottom()) < linewidth:
                self.handle_at = self.toBottom
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.handle_at = None

            super().mousePressEvent(event)

        def borderUpdate(self):
            """边界取自父类pageview的边界,是坐标,也可以称作container_coord_update"""
            self.leftBorder = 0
            self.topBorder = 0
            self.rightBorder = self.leftBorder + self.superior.pixmap().width()
            self.bottomBorder = self.topBorder + self.superior.pixmap().height()

        def resize_bordercheck(self, toX=None, toY=None):
            """根据是否越界进行一个边界的修正，超出边界就用边界的值代替"""
            X, Y = None, None
            if toX is not None:
                X = toX if self.leftBorder < toX + self.pos().x() < self.rightBorder \
                    else self.rightBorder - self.pos().x() if toX + self.pos().x() >= self.rightBorder \
                    else self.leftBorder - self.pos().x()
            if toY is not None:
                Y = toY if self.topBorder < toY + self.pos().y() < self.bottomBorder \
                    else self.bottomBorder - self.pos().y() if toY + self.pos().y() >= self.bottomBorder \
                    else self.topBorder - self.pos().y()
            return X, Y

        def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            self.borderUpdate()
            if self.pos_when_click is not None and self.handle_at is not None and self.rect_when_click is not None:
                # self.setFlag(self.ItemIsMovable,False)
                pos = event.pos()
                x_diff = pos.x() - self.pos_when_click.x()
                y_diff = pos.y() - self.pos_when_click.y()
                # rect = QRectF(self.rect_when_click)
                mousePos = event.pos()
                pageview: 'pageview' = self.superior
                MAXRect = pageview.boundingRect()  # 外边界

                offset = 0
                boundingRect = self.boundingRect()
                rect = self.rect()
                self.prepareGeometryChange()
                x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
                # 将其限制在父类图元的坐标系中
                if self.handle_at == self.toTopRight:
                    self.rightBorder = MAXRect.x() + MAXRect.width()
                    self.leftBorder = rect.x() + self.pos().x()
                    self.topBorder = MAXRect.y()
                    self.bottomBorder = rect.y() + self.pos().y() + rect.height()
                    fromX = self.rect_when_click.right()
                    fromY = self.rect_when_click.top()
                    toX = fromX + mousePos.x() - self.rect_when_click.x()
                    toY = fromY + mousePos.y() - self.rect_when_click.y()
                    finalX, finalY = self.resize_bordercheck(toX=mousePos.x(), toY=toY)
                    rect.setRight(finalX)
                    rect.setTop(finalY)
                elif self.handle_at == self.toTopLeft:
                    fromX = self.rect_when_click.left()
                    fromY = self.rect_when_click.top()
                    # 全部换算成pageview中的坐标,公式 :pageviewpos = selfpos+rectpos
                    self.rightBorder = rect.x() + self.pos().x() + rect.width()
                    self.leftBorder = MAXRect.x()
                    self.topBorder = MAXRect.y()
                    self.bottomBorder = rect.y() + self.pos().y() + rect.height()
                    toX = fromX + mousePos.x() - self.rect_when_click.x()
                    toY = fromY + mousePos.y() - self.rect_when_click.y()
                    finalX, finalY = self.resize_bordercheck(toX=mousePos.x(), toY=toY)
                    rect.setLeft(finalX)
                    rect.setTop(finalY)
                elif self.handle_at == self.toBottomLeft:
                    self.leftBorder = MAXRect.left()
                    self.rightBorder = rect.right() + self.pos().x()
                    self.topBorder = rect.top() + self.pos().y()
                    self.bottomBorder = MAXRect.bottom()
                    finalX, finalY = self.resize_bordercheck(toX=mousePos.x(), toY=mousePos.y())
                    rect.setLeft(finalX)
                    rect.setBottom(finalY)
                elif self.handle_at == self.toBottomRight:
                    self.leftBorder = rect.left() + self.pos().x()
                    self.rightBorder = MAXRect.right()
                    self.topBorder = rect.top() + self.pos().y()
                    self.bottomBorder = MAXRect.bottom()
                    finalX, finalY = self.resize_bordercheck(toX=mousePos.x(), toY=mousePos.y())
                    rect.setRight(finalX)
                    rect.setBottom(finalY)
                elif self.handle_at == self.toTop:
                    fromY = self.rect_when_click.top()
                    toY = fromY + mousePos.y() - self.rect_when_click.y()
                    self.topBorder = MAXRect.y()
                    self.bottomBorder = rect.y() + self.pos().y() + rect.height()
                    finalX, finalY = self.resize_bordercheck(toY=toY)
                    boundingRect.setTop(finalY)
                    rect.setTop(finalY)
                elif self.handle_at == self.toLeft:
                    self.leftBorder = MAXRect.left()
                    self.rightBorder = rect.right() + self.pos().x()
                    finalX, finalY = self.resize_bordercheck(toX=mousePos.x())
                    rect.setLeft(finalX)
                elif self.handle_at == self.toBottom:
                    self.topBorder = rect.top() + self.pos().y()
                    self.bottomBorder = MAXRect.bottom()
                    finalX, finalY = self.resize_bordercheck(toY=mousePos.y())
                    rect.setBottom(finalY)
                elif self.handle_at == self.toRight:
                    self.leftBorder = rect.left() + self.pos().x()
                    self.rightBorder = MAXRect.right()
                    finalX, finalY = self.resize_bordercheck(toX=mousePos.x())
                    rect.setRight(finalX)
                if rect.width() < self.linewidth:
                    if self.handle_at == self.toLeft:
                        rect.setLeft(rect.right() - self.linewidth)
                    else:
                        rect.setRight(rect.left() + self.linewidth)
                if rect.height() < self.linewidth:
                    if self.handle_at == self.toTop:
                        rect.setTop(rect.bottom() - self.linewidth)
                    else:
                        rect.setBottom(rect.top() + self.linewidth)
                # b = self.superior.boundingRect()
                # if rect.right() > b.right():
                #     rect.setRight(b.right())
                # if rect.top() < b.top():
                #     rect.setTop(b.top())
                # if rect.left() < b.left():
                #     rect.setLeft(b.left())
                # if rect.bottom() > b.bottom():
                #     rect.setBottom(b.bottom())

                # print(rect)
                self.setRect(rect)

                self.calc_ratio()
                # self.move_bordercheck()
            else:
                super().mouseMoveEvent(event)

        def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            self.pos_when_click = None
            self.rect_when_click = None
            self.handle_at = None
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

        def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            from .LittleWidgets import ClipboxInfo
            p = ClipboxInfo(self, self.root)
            p.exec()
            super().mouseDoubleClickEvent(event)

        # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        #     self.hide()

        def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                  widget: typing.Optional[QWidget] = ...) -> None:

            pen = QPen(QColor(127, 127, 127), 2.0, Qt.DashLine)
            if self.isHovered or self.isSelected():
                pen.setWidth(5)
                painter.setBrush(QBrush(QColor(0, 0, 0, 70)))
                painter.setPen(pen)

                painter.drawRect(self.rect())
                self.close.show()
                painter.setPen(QColor(255, 255, 255))
                painter.setFont(QFont('SimSun', pointSize=15, weight=300))
                r = self.rect()
                painter.drawText(self.rect(), Qt.TextWordWrap, self.editableData.comment)
                # self.comment_label.show()
            else:
                self.close.hide()
                painter.setPen(pen)
                painter.drawRect(self.rect())
                # self.comment_label.hide()

            view = self.superior.superior.superior

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
            view_right = self.superior.boundingRect().width()
            view_bottom = self.superior.boundingRect().height()
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

        def del_self(self):
            del self.superior.superior.clipbox_dict[self.uuid]
            del self.root.E.clipbox.container[self.uuid]
            self.superior.superior.superior.scene().removeItem(self)

        def immutable_info_get(self):
            """搞插入数据库的需要去掉zoom和pdfname"""
            clipbox_info = OrderedDict({
                "uuid": self.uuid,
                "pdfname": self.superior.superior.pageinfo.pdf_path,
                "pdfuuid": funcs.uuid_hash_make(self.superior.superior.pageinfo.pdf_path),
                "pagenum": self.superior.superior.pageinfo.pagenum,
                "ratio": self.superior.superior.pageinfo.ratio,
                "zoom": self.pageratio,
                "x": self.ratioLeft,
                "y": self.ratioTop,
                "w": self.ratioRight - self.ratioLeft,
                "h": self.ratioBottom - self.ratioTop,
            })
            return clipbox_info

        def mutable_info_get(self):
            info = OrderedDict({
                "card_id": ",".join(self.card_list_id_get()),
                "comment": self.editableData.comment,
                "commentQA": self.editableData.comment_to_field,
                "QA": self.editableData.clip_to_field
            })
            return info

        def clip_img_save(self, imgdir=None):
            clipinfo = self.immutable_info_get()
            pixmap = funcs.png_pdf_clip(clipinfo["pdfname"], self.superior.superior.pageinfo.pagenum, rect1=clipinfo)
            if imgdir is None:
                imgdir = os.path.join(tempfile.gettempdir(), f"""hjp_clipper_{self.uuid}_.png""")
            pixmap.save(imgdir)
            return imgdir

        def clip_to_field_initQA(self, QA=None):
            """决定QA的途径有很多个,先排查直接指定,然后排查按钮指定"""
            if QA is not None:
                return QA
            else:
                d = {
                    "Q": self.root.E.config.clipbox.Q_map_Field,
                    "A": self.root.E.config.clipbox.A_map_Field,
                }
                buttonQA = self.root.rightsidebar.buttonPanel.widget_button_QA.text()
            return d[buttonQA]

        def comment_to_field_initQA(self, QA=None):
            if QA is not None:
                return QA
            else:
                d = {
                    "Q": self.root.E.config.clipbox.comment_Q_map_Field,
                    "A": self.root.E.config.clipbox.comment_A_map_Field,
                }
                buttonQA = self.root.rightsidebar.buttonPanel.widget_button_QA.text()
            return d[buttonQA]

        def card_list_id_get(self):
            """默认存的是descitem的uuid,真正要用的是card_id"""
            li = []
            for descuuid in self.editableData.card_list:
                desc: "Clipper.RightSideBar.CardList.DescItem" = self.root.E.rightsidebar.cardlist.dict[descuuid]
                li.append(desc.cardItem.text())
            return li

        def update_editabledata(self):
            clipuuid = self.uuid
            DB = objs.SrcAdmin.DB
            if DB.go(DB.table_clipbox).exists(DB.EQ(uuid=clipuuid)):
                clipbox = DB.go(DB.table_clipbox).select(uuid=clipuuid).return_all().zip_up().to_clipbox_data()[0]
                self.editableData.clip_to_field = clipbox.QA
                self.editableData.comment_to_field = clipbox.commentQA
                self.editableData.comment = clipbox.comment
                card_id_dict = self.root.E.rightsidebar.cardlist.card_id_dict
                carduuid_li = [card_id_dict[card_id].uuid for card_id in clipbox.card_id.split(",") if
                               card_id in card_id_dict]
                for carduuid in carduuid_li:  # 如果clipbox对应了多张卡片,则只加载被读取到clipper的部分.
                    self.root.clipbox_add_card(self.uuid, carduuid)

        class CommentLabel(QGraphicsWidget):
            def __init__(self, superior: "Clipper.ClipBox"):
                super().__init__()
                self.superior = superior
                self.comment_label = QLabel()
                self.comment_label.setStyleSheet("color:white;")
                self.proxy = QGraphicsProxyWidget(superior)
                self.proxy.setWidget(self.comment_label)
                self.proxy.setParentItem(superior)
                # self.proxy.setPos(10,10)
                g = QGraphicsGridLayout(self)
                self.setLayout(g)
                self.setPos(10, 10)
                self.hide()

            def set_text(self, s):
                self.comment_label.setText(s)

            def show(self):
                self.set_text(self.superior.editableData.comment)
                # print(self.comment_label.text())
                self.proxy.updateGeometry()
                self.proxy.show()

            def hide(self):
                self.proxy.hide()

        @dataclass
        class Data:
            _card_list: "list[str]" = field(default_factory=list)  # 保存descitem
            clip_to_field: "int" = None
            comment_to_field: "int" = None
            comment: "str" = ""

            @property
            def card_list(self):
                return self._card_list

            def card_list_append(self, caller, s, EXCEPT=False):

                if not EXCEPT:
                    funcs.caller_check(Clipper.clipbox_add_card, caller, Clipper)
                if s not in self._card_list:
                    self._card_list.append(s)

            def card_list_remove(self, caller, s, EXCEPT=False):
                if not EXCEPT:
                    funcs.caller_check(Clipper.clipbox_del_card, caller, Clipper)
                if s in self._card_list:
                    self._card_list.remove(s)

        class Close:
            def __init__(self, superior: "Clipper.ClipBox"):
                self.superior: "Clipper.Clipbox" = superior
                self.widget: "QToolButton" = QToolButton()
                self.proxy: "QGraphicsProxyWidget" = QGraphicsProxyWidget()
                self.proxy.setParentItem(superior)
                self.proxy.setWidget(self.widget)
                self.widget.setIcon(QIcon(objs.SrcAdmin.imgDir.close))
                self.widget.clicked.connect(self.on_clicked)

            def show(self):
                self.setTopRightCorner()
                self.proxy.show()

            def hide(self):
                self.proxy.hide()

            def setTopRightCorner(self):
                self.proxy.setPos(
                    self.superior.boundingRect().right() - self.widget.width() - 10,
                    self.superior.boundingRect().top() + 10)

            def on_clicked(self):
                self.superior.root.delClipbox(uuid=self.superior.uuid)

        pass


class ScenePageLoader(QThread):
    on_1_page_load = pyqtSignal(object)

    def __init__(self, datali: "list[objs.PageInfo]"):
        super().__init__()
        self.datali = datali

    def run(self) -> None:
        total = len(self.datali)
        count = 0
        for data in self.datali:
            count += 1
            pixdir = funcs.pixmap_page_load(data.pdf_path, data.pagenum, data.ratio)
            self.on_1_page_load.emit(pageloaddata(pixdir, data, int(count / total * 100)))
            time.sleep(0.1)


class ClipInsertCardWorker(QThread):
    on_quit = pyqtSignal(object)
    on_progress = pyqtSignal(object)  # 用来调节进度条,在GUI线程进行connect
    on_card_create = pyqtSignal(object)
    on_png_create = pyqtSignal(object)
    on_field_insert = pyqtSignal(object)

    def __init__(self, superior: "Clipper"):
        super().__init__(superior)
        self.superior = superior
        self.waitting = False
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.allevent = None

    def run(self):
        from ..imports import common_tools
        gap = 0.05
        data: "OrderedDict[str,Clipper.ClipBox]" = self.superior.E.clipbox.container
        deck_id = self.superior.E.config.clipbox.newcard_deck_id
        model_id = self.superior.E.config.clipbox.newcard_model_id
        totalpart = 4  # 新建卡片,插入DB,插入Field,生成图片地址
        # 第一个part,新建卡片
        part = 0
        clip_total = len(data)
        clip_count = 0
        e = events.AnkiCardCreateEvent
        for clipuuid, clipbox in data.items():
            clip_count += 1
            card_list = clipbox.editableData.card_list
            for carduuid in card_list:
                desc_item: "Clipper.RightSideBar.CardList.DescItem" = self.superior.E.rightsidebar.cardlist.dict[
                    carduuid]
                if desc_item.cardItem.newCard:
                    common_tools.funcs.write_to_log_file(f"deck_id={deck_id}")
                    self.on_card_create.emit(
                        e(type=e.defaultType.clipboxNeed, worker=self, carditem=desc_item.cardItem,
                          model_id=model_id,
                          deck_id=deck_id))
                    self.waitting = True
                while self.waitting:
                    time.sleep(gap)
            self.on_progress.emit(
                objs.Progress(value=ceil((clip_count / clip_total / totalpart + part / totalpart) * 100),
                              text="card_created"))
            time.sleep(gap)

        # 第二个part,插入DB
        part = 1
        clip_total = len(data)
        clip_count = 0
        for clipuuid, clipbox in data.items():
            clip_count += 1
            immutable = clipbox.immutable_info_get()
            immutable.pop("pdfname")
            immutable.pop("zoom")
            mutable = clipbox.mutable_info_get()
            record = objs.ClipboxRecord(**immutable, **mutable)
            DB = objs.SrcAdmin.DB.go(objs.SrcAdmin.DB.table_clipbox)
            if DB.exists(DB.EQ(uuid=record.uuid)):
                old_record = DB.select(uuid=record.uuid).return_all().zip_up()[0].to_clipbox_data()
                record.card_id = ",".join(set(old_record.card_id.split(",")) | set(record.card_id.split(",")))
                DB.update(values=DB.VALUEEQ(**record.__dict__), where=DB.EQ(uuid=record.uuid)).commit()
            else:
                DB.insert(**record.__dict__).commit()
            self.on_progress.emit(
                objs.Progress(value=ceil((clip_count / clip_total / totalpart + part / totalpart) * 100),
                              text="DB_inserted"))
            time.sleep(gap)
        # 第三个part,插入Field
        part = 2
        clip_total = len(data)
        clip_count = 0
        e = events.AnkiFieldInsertEvent
        for clipuuid, clipbox in data.items():
            clip_count += 1
            self.on_field_insert.emit(
                e(type=e.defaultType.clipboxNeed, worker=self, clipuuid=clipuuid, timestamp=self.timestamp))

            # self.superior.signals.on_anki_field_insert.emit(
            #     e(type=e.defaultType.clipboxNeed,worker=self,clipuuid=clipuuid,timestamp=self.timestamp))
            self.waitting = True
            while self.waitting:
                time.sleep(gap)
            self.on_progress.emit(
                objs.Progress(value=ceil((clip_count / clip_total / totalpart + part / totalpart) * 100),
                              text="field_inserted"))
            time.sleep(gap)

        # 第四个part,生成clip地址
        part = 3
        clip_total = len(data)
        clip_count = 0
        e = events.AnkiFileCreateEvent
        for clipuuid, clipbox in data.items():
            clip_count += 1
            self.on_png_create.emit(e(type=e.defaultType.ClipperCreatePNG, worker=self, clipuuid=clipuuid))
            # self.superior.signals.on_anki_file_create.emit(e(type=e.defaultType.ClipperCreatePNG,worker=self,clipuuid=clipuuid))
            self.waitting = True
            while self.waitting:
                time.sleep(gap)
            self.on_progress.emit(
                objs.Progress(value=ceil((clip_count / clip_total / totalpart + part / totalpart) * 100),
                              text="png_file_created"))
            time.sleep(gap)
        self.on_quit.emit(self.timestamp)
        self.quit()

    pass


pageloaddata = namedtuple("pageloaddata", "pixdir pageinfo progress")
