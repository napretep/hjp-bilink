import json
import os
import time
import uuid
from math import ceil

from PyQt5 import QtGui
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolButton, QTreeView, QApplication, \
    QHeaderView, QAbstractItemView, QGridLayout
from PyQt5.QtCore import Qt, QRect, QItemSelectionModel, pyqtSignal, QTimer, QThread, QPoint, QModelIndex
from aqt.utils import showInfo

from ..PDFView_.PageItem_ import ClipBox_
from ..PDFView_ import PageItem_
from . import PageList_, CardList_
from ..tools.funcs import str_shorten, index_from_row
from ..tools import events, funcs, ALL, objs
from ..PagePicker import PagePicker

print, printer = funcs.logger(__name__)




class FinalExecution_masterJob(QThread):
    """这里是执行最终任务的地方,信息要采集保存到本地去"""
    on_job_done = pyqtSignal(object)
    on_job_progress = pyqtSignal(object)
    def __init__(self, cardlist=None):
        super().__init__()
        self.cardlist = cardlist
        self.fieldinserted_timestamp = None
        self.speed = 0.5 if ALL.ISDEBUG else 0.01
        self.cardcreated = True
        self.fieldinserted = True
        self.pngcreated = True
        self.job_part = 4
        self.model_id = ALL.CONFIG.clipbox.newcard_model_id
        self.deck_id = ALL.CONFIG.clipbox.newcard_deck_id
        self.state_extract_clipbox_info = 0
        self.state_create_newcard = 1
        self.state_insert_cardfield = 2
        self.state_insert_DB = 3
        self.state_create_png = 4
        self.__event = {
            ALL.signals.on_anki_card_created: self.on_anki_card_created_handle,
            ALL.signals.on_anki_field_insert: self.on_anki_field_insert_handle,
            ALL.signals.on_anki_file_create: self.on_anki_file_create_handle,
            # self.on_cardcreate_done:self.on_cardcreate_done_handle,
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()


    def on_anki_file_create_handle(self, event: "events.AnkiFileCreateEvent"):
        if event.Type == event.ClipperCreatePNGDoneType:
            self.pngcreated = True

    def on_anki_field_insert_handle(self, event: "events.AnkiFieldInsertEvent"):
        if event.Type == event.ClipBoxEndType:
            self.fieldinserted = True
            self.fieldinserted_timestamp = event.data
            # print(f"fieldinserted_timestamp = {event.data}")

    def job_progress(self, state, part, percent):
        totalpart = self.job_part
        self.on_job_progress.emit([state, ceil(100 * (part - 1) / totalpart + percent * 100 / totalpart)])

    def on_anki_card_created_handle(self, event: "events.AnkiCardCreatedEvent"):
        if event.Type == event.ClipBoxType:  # 由于是异步操作，这里可能会滞后完成，需要确保他在别的之前完成。
            self.item_need_update.setText(event.data)
        if event.Type == event.infoUpdateType:
            self.cardcreated = True

    def run(self):
        li = self.job_clipboxlist_make()
        # print(li)
        # print("job_clipboxlist_make")
        if len(li) == 0:
            # print("return")
            self.on_job_done.emit(self.fieldinserted_timestamp)
            return
        self.job_clipbox_DB_insert(li)
        self.job_clipbox_field_insert(li)
        # print("job_clipbox_field_insert")
        self.job_clipbox_png_create(li)
        while self.fieldinserted_timestamp is None and len(li) != 0:
            self.msleep(10)
        # print(f"self.on_job_done.emit(self.fieldinserted_timestamp)={self.fieldinserted_timestamp}")
        self.on_job_done.emit(self.fieldinserted_timestamp)
        pass

    def job_clipboxlist_make(self):
        """cardHashDict:  hash:[DescItem,CardItem]
           DescItem:clipBoxList[clipbox]

            """
        # print("job_clipboxlist_make start")
        clipboxlist = []
        uuidcount = len(self.cardlist.cardUuidDict)
        current = 0
        print((self.cardlist.cardUuidDict))
        for uuid, row in self.cardlist.cardUuidDict.items():
            # print("job_clipboxlist_make start2")
            if len(row[0].clipBoxList) == 0:
                continue

            if row[1].text() == "/":
                self.cardcreated = False  # Debug时要关闭
                self.job_progress(self.state_create_newcard, 1, current / uuidcount)
                self.item_need_update = row[1]
                e = events.AnkiCardCreateEvent
                ALL.signals.on_anki_card_create.emit(
                    e(sender=self, eventType=e.ClipBoxType, model_id=self.model_id, deck_id=self.deck_id))

                while not self.cardcreated:
                    # print("waiting for cardcreated")
                    time.sleep(self.speed)
            # print("new card create done")
            self.job_progress(self.state_extract_clipbox_info, 1, current / uuidcount)
            for clipbox in row[0].clipBoxList:
                clipboxinfo: "dict" = clipbox.self_info_get()
                # print(clipboxinfo)
                clipboxlist.append(clipboxinfo)
            current += 1
            # print("clipboxinfo create done")
            time.sleep(self.speed)

        return clipboxlist
        pass

    def job_clipbox_field_insert(self, clipboxlist):
        self.fieldinserted = False
        e = events.AnkiFieldInsertEvent
        ALL.signals.on_anki_field_insert.emit(
            e(eventType=e.ClipBoxBeginType, sender=self, data=clipboxlist)
        )
        while not self.fieldinserted and not ALL.ISDEBUG:
            time.sleep(self.speed)

    def job_clipbox_png_create(self, clipboxlist):
        self.pngcreated = False
        e = events.AnkiFileCreateEvent
        ALL.signals.on_anki_file_create.emit(
            e(eventType=e.ClipperCreatePNGType, sender=self, data=clipboxlist)
        )
        while not self.pngcreated and not ALL.ISDEBUG:
            time.sleep(self.speed)

        pass

    def job_clipbox_DB_insert(self, clipboxlist):
        uuidcount = len(clipboxlist)
        current = 0
        DB = objs.SrcAdmin.DB
        DB.go()
        for clipbox in clipboxlist:
            pdfname = clipbox["pdfname"]
            pdfuuid = str(uuid.uuid3(uuid.NAMESPACE_URL, pdfname))
            objs.SrcAdmin.PDF_JSON.mount(pdfuuid, pdfname, page_shift=0, ratio=1).save()

            clipbox["pdfuuid"] = pdfuuid
            # print(clipbox)
            if DB.exists(clipbox["uuid"]):
                result = DB.select(uuid=clipbox["uuid"]).return_all().zip_up()[0]
                if clipbox["card_id"] in result["card_id"]:
                    clipbox["card_id"] = result["card_id"]
                else:
                    result["card_id"] = clipbox["card_id"] + "," + result["card_id"]
                DB.update(values=DB.value_maker(**clipbox), where=f"""uuid="{clipbox["uuid"]}" """).commit(print)
            else:
                DB.insert(**clipbox).commit(print)
            current += 1
            self.job_progress(self.state_insert_DB, 2, current / uuidcount)
            time.sleep(self.speed)
        DB.end()
        pass


class PageList(QWidget):
    """
    左边竖排添加删除按钮,右边一个QListWidget
    """

    def __init__(self, parent=None, rightsidebar: "RightSideBar" = None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.rightsidebar = rightsidebar
        self.parent = parent
        self.pagepicker = None
        self.pageItemDict = {}
        self.init_UI()
        self.init_model()
        self.event_dict = {
            self.addButton.clicked: (self.on_addButton_clicked_handle),
            self.delButton.clicked: (self.on_delButton_clicked_handle),
            self.listView.clicked: (self.on_listview_clicked_handle),
            self.listView.doubleClicked: (self.on_listview_doubleClicked_handle),
            ALL.signals.on_pageItem_removeFromScene: (self.on_pageItem_removeFromScene_handle),
            ALL.signals.on_pageItem_addToScene: (self.on_pageItem_addToScene_handle),
            ALL.signals.on_pageItem_changePage: (self.on_pageItem_changePage_handle),
            ALL.signals.on_pagepicker_open: (self.on_pagepicker_open_handle),
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def init_UI(self):
        H_layout = QHBoxLayout()
        V_layout2 = QVBoxLayout()
        self.label = QLabel("page list")
        self.label.setText("page list")
        self.V_layout = QVBoxLayout(self)
        self.addButton = QToolButton(self)
        self.addButton.setText("+")
        self.delButton = QToolButton(self)
        self.delButton.setText("-")
        self.listView = QTreeView(self)
        self.V_layout.addLayout(H_layout)
        self.V_layout.addLayout(V_layout2)
        self.V_layout.setStretch(1, 1)
        self.listView.setIndentation(0)
        H_layout.addWidget(self.label)
        H_layout.addWidget(self.addButton)
        H_layout.addWidget(self.delButton)
        V_layout2.addWidget(self.listView)


    def init_model(self):
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        pdfname = QStandardItem("PDFname")  # 存文件路径
        pagenum = QStandardItem("pagenum")  # 存页码和graphics_page对象
        self.model.setHorizontalHeaderItem(0, pdfname)
        self.model.setHorizontalHeaderItem(1, pagenum)
        self.pagepicker = None
        self.pageItemDict = {}
        self.listView.setModel(self.model)
        self.listView.header().setDefaultSectionSize(180)
        self.listView.header().setSectionsMovable(False)
        self.listView.header().setSectionResizeMode((QHeaderView.Stretch))
        self.listView.setColumnWidth(1, 10)

    # def init_signals(self):
    #     self.on_pageItem_addToScene = ALL.signals.on_pageItem_addToScene
    #     self.on_pageItem_removeFromScene = ALL.signals.on_pageItem_removeFromScene
    #     self.on_pageItem_changePage = ALL.signals.on_pageItem_changePage

    # def on_pagepicker_close_handle(self,event:"events.PagePickerCloseEvent"):
    #     self.pagepicker.close()

    def on_pagepicker_open_handle(self, event: "events.PagePickerOpenEvent"):
        # print("收到指令")
        if self.pagepicker is None:
            self.pagepicker = PagePicker(pdfpath=event.pdfpath, frompageitem=event.fromPageItem,
                                         pageNum=event.pagenum, clipper=self.rightsidebar.clipper)
            # print("pagepicker 创建")
        self.pagepicker.init_data(pagenum=event.pagenum, PDFpath=event.pdfpath, frompageitem=event.fromPageItem)
        page = event.pagenum
        if page is None:
            page = 0
        QTimer.singleShot(50, lambda: self.pagepicker.start(page))
        QApplication.processEvents()
        self.pagepicker.exec()

    def on_listview_clicked_handle(self):
        itemli = [self.model.itemFromIndex(idx) for idx in self.listView.selectedIndexes()]
        # print(itemli)
        # print(itemli[0].data(Qt.UserRole))
        # print(itemli[1].data(Qt.UserRole))
        pass

    def on_listview_doubleClicked_handle(self):
        idx = self.listView.selectedIndexes()
        item = [self.model.itemFromIndex(i) for i in idx][-2:]
        PDFpath = item[0].toolTip()
        pagenum = int(item[1].text())
        pageitem = item[0].data(Qt.UserRole)
        e = events.PagePickerOpenEvent
        ALL.signals.on_pagepicker_open.emit(
            e(sender=self, eventType=e.fromPageListType
              , pdfpath=PDFpath, fromPageItem=pageitem, pagenum=pagenum, )
        )

    def on_addButton_clicked_handle(self):
        """打开的时候，确定默认的路径和页码"""
        e = events.PagePickerOpenEvent
        ALL.signals.on_pagepicker_open.emit(
            e(sender=self, eventType=e.fromAddButtonType, pagenum=None)
        )

    def on_delButton_clicked_handle(self):
        rowli = self.model_selected_rows()
        for row in rowli:
            objs.signals.on_pageItem_removeFromScene.emit(
                events.PageItemDeleteEvent(pageItem=row[0].data(Qt.UserRole),
                                           eventType=events.PageItemDeleteEvent.deleteType))
        pass

    def update_from_pageinfo(self, pageinfo, pageitem):
        p1: 'PageList_.PDFItem' = self.pageItemDict[pageitem][0]
        p2: 'PageList_.PageNumItem' = self.pageItemDict[pageitem][1]
        p1.update_data(PDFName=str_shorten(os.path.basename(pageinfo.doc.name)), PDFpath=pageinfo.doc.name)
        p2.setText(str(pageinfo.pagenum))

    def on_pageItem_changePage_handle(self, event: 'events.PageItemChangeEvent'):
        if event.Type == event.updateType:
            self.update_from_pageinfo(event.pageInfo, event.pageItem)

    def on_pageItem_addToScene_handle(self, event: 'events.PageItemAddToSceneEvent'):
        if event.Type == event.addPageType:
            self.model_pageItem_add(event.pageItem)
        elif event.Type == event.addMultiPageType:
            for pageitem in event.pageItemList:
                self.model_pageItem_add(pageitem)
        if event.callback:
            event.callback(kwargs=event.kwargs, pageitem=event.pageItem, pageitemlist=event.pageItemList)
        pass

    def on_pageItem_removeFromScene_handle(self, event: 'events.PageItemDeleteEvent'):
        if event.Type == event.deleteType:
            self.model_pageItem_remove(event.pageItem)

    def model_selected_rows(self):
        itemli = [self.model.itemFromIndex(idx) for idx in self.listView.selectedIndexes()]
        rowli = [[itemli[i], itemli[i + 1]] for i in range(int(len(itemli) / 2))]
        return rowli

    def model_pageItem_remove(self, pageitem: 'PageItem5'):
        row = self.pageItemDict[pageitem]
        self.model.takeRow(row[0].row())
        del self.pageItemDict[pageitem]
        pass

    def model_pageItem_add(self, pageitem: 'PageItem5'):
        name = str_shorten(os.path.basename(pageitem.pageinfo.doc.name))
        row = [
            PageList_.PDFItem(PDFName=name, selfData=pageitem, PDFpath=pageitem.pageinfo.doc.name),
            PageList_.PageNumItem(pagenum=str(pageitem.pageinfo.pagenum), selfData=pageitem)
        ]
        self.model.appendRow(row)
        self.pageItemDict[pageitem] = row

class CardList(QWidget):
    """这个list需要有 card_id,desc,若是新卡片则用new card number 代替 desc, 此时card_id留空"""
    itemMiddlePosi = 0
    itemTopPosi = 1
    itemBottomPosi = -1
    treeBottomPosi = -2

    def __init__(self, parent=None, rightsidebar: "RightSideBar" = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.cardUuidDict: 'dict[int,list[CardList_.DescItem,CardList_.CardItem]]' = {}
        self.rightsidebar = rightsidebar
        self.newcardcount = 0
        self.ClipboxState = None
        self.addButton = QToolButton(self)
        self.delButton = QToolButton(self)
        self.model = QStandardItemModel(self)
        self.label = QLabel(self)
        self.listView = QTreeView(self)
        self.init_UI()
        self.init_model()
        self.init_signals()
        self.__event = {
            self.addButton.clicked: self.on_addButton_clicked_handle,
            self.delButton.clicked: self.on_delButton_clicked_handle,
            self.listView.clicked: self.on_listView_clicked_handle,
            # list变化的
            self.listView.doubleClicked: self.on_listView_doubleClicked_handle,
            self.model.dataChanged: self.on_model_data_changed_handle,
            self.on_clipbox_closed: self.on_clipbox_closed_handle,
            self.on_clipboxCombox_updated: self.on_clipboxCombox_updated_handle,
            self.on_pageItem_clipbox_added: self.on_pageItem_clipbox_added_handle,
            ALL.signals.on_clipper_hotkey_next_card: self.on_clipper_hotkey_next_card_handle,
            ALL.signals.on_clipper_hotkey_prev_card: self.on_clipper_hotkey_prev_card_handle,
            ALL.signals.on_clipboxstate_switch: self.on_clipboxstate_switch_handle,
            ALL.signals.on_cardlist_selectItem: self.on_cardlist_selectItem_handle,
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()
        # self.init_events()
        # self.test()

    def on_listView_doubleClicked_handle(self, idx: "QModelIndex"):
        if idx.column() == 1 and idx.data(Qt.DisplayRole) != "/":
            from .CardList_.card_clipbox_picker import CardClipboxPicker
            card_uuid = self.model.item(idx.row(), 0).uuid
            p = CardClipboxPicker(self, idx.data(Qt.DisplayRole), card_uuid)
            p.show()
            pass  # 一个新的窗口

    def card_clipboxlist_add(self, clipbox, uuid_new):
        """加入新的,删除旧的"""
        if uuid_new in self.cardUuidDict:
            self.cardUuidDict[uuid_new][0].clipBoxList.append(clipbox)

    def card_clipboxlist_del(self, clipbox, cardUuid=None):
        """从中删除"""
        if cardUuid is not None:
            if cardUuid in self.cardUuidDict and clipbox in self.cardUuidDict[cardUuid][0].clipBoxList:
                self.cardUuidDict[cardUuid][0].clipBoxList.remove(clipbox)
        else:
            for card_uuid, card_desc_pair_item in self.cardUuidDict.items():
                if clipbox in card_desc_pair_item[0].clipBoxList:
                    card_desc_pair_item[0].clipBoxList.remove(clipbox)

    def on_cardlist_selectItem_handle(self, event: "events.CardListSelectItemEvent"):
        if event.Type == event.singleRowType:
            self.selectRow(event.rowNum)

    def on_addButton_clicked_handle(self):
        d = CardList_.CardPicker(cardlist=self)
        d.exec_()

    def on_model_data_changed_handle(self, topleft, bottomright, roles):

        e = events.CardListDataChangedEvent
        item = self.model.itemFromIndex(topleft)
        Type = e.TextChangeType
        if isinstance(item, CardList_.CardItem):
            Type = e.CardIdChangeType
        sender = self.model.item(item.row(), 0)
        # print("on_model_data_changed_handle")
        ALL.signals.on_cardlist_dataChanged.emit(e(sender=sender, eventType=Type, data=item.text()))
        pass

    def on_delButton_clicked_handle(self):
        self.rightsidebar.card_list_select_del()

    def on_listView_clicked_handle(self, index):
        # TODO 未完成的信号
        item = self.model.itemFromIndex(index)
        if item.column() == 0:
            # print(item.clipBoxList)
            pass

    def on_clipbox_closed_handle(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        clipbox, uuid = event.clipBox, event.cardUuid
        self.card_clipboxlist_del(clipbox, uuid)

    def on_clipboxCombox_updated_handle(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        self.card_clipboxlist_add(event.clipBox, event.cardUuid)
        self.card_clipboxlist_del(event.clipBox, event.cardUuid_old)

    def on_pageItem_clipbox_added_handle(self, event: 'PageItem_.PageItem_ClipBox_Event'):
        """added信号"""
        self.card_clipboxlist_add(event.clipbox, event.cardUuid)

    def newcard_signal_emit(self):
        e = events.CardListAddCardEvent
        ALL.signals.on_cardlist_addCard.emit(
            e(sender=self, eventType=e.newCardType)
        )

    def on_clipper_hotkey_next_card_handle(self):
        """1看有没有卡, 2看有没有选中"""
        rowcount = self.model.rowCount()
        idxLi = self.listView.selectedIndexes()
        if rowcount == 0:  # 没有卡片
            self.newcard_signal_emit()
            # desc, card_id = self.model.item(0, 0), self.model.item(0, 1)
            rownum = 0
        else:
            if len(idxLi) > 0:  # 如有选中,走下一行
                row = [self.model.itemFromIndex(idx) for idx in idxLi[-2:]]
                if row[0].row() + 1 >= self.model.rowCount():
                    self.newcard_signal_emit()
                # desc, card_id = self.model.item(row[0].row() + 1, 0), self.model.item(row[0].row() + 1, 1)
                rownum = row[0].row() + 1
                pass
            else:  # 如无选中,新建一行
                self.newcard_signal_emit()
                rownum = self.model.rowCount()
                # desc, card_id = self.model.item(self.model.rowCount(), 0), self.model.item(self.model.rowCount(), 1)
        self.selectRow(rownum)
        # self.listView.selectionModel().clearSelection()
        # self.listView.selectionModel().select(index_from_row(self.model, [desc, card_id]), QItemSelectionModel.Select)
        e = events.ClipboxStateSwitchEvent
        funcs.show_clipbox_state()

    def selectRow(self, rowNum):
        """这是一个可公开的API"""
        desc, card_id = self.model.item(rowNum, 0), self.model.item(rowNum, 1)
        self.listView.selectionModel().clearSelection()
        self.listView.selectionModel().select(index_from_row(self.model, [desc, card_id]), QItemSelectionModel.Select)

    def on_clipper_hotkey_prev_card_handle(self):
        rowcount = self.model.rowCount()
        idxLi = self.listView.selectedIndexes()
        if rowcount == 0:
            return
        if len(idxLi) > 0:
            row = [self.model.itemFromIndex(idx) for idx in idxLi[-2:]]
            if row[0].row() == 0:
                return
            else:
                desc, card_id = self.model.item(row[0].row() - 1, 0), self.model.item(row[0].row() - 1, 1)
        else:
            desc, card_id = self.model.item(self.model.rowCount(), 0), self.model.item(self.model.rowCount(), 1)
        self.listView.selectionModel().clearSelection()
        self.listView.selectionModel().select(index_from_row(self.model, [desc, card_id]), QItemSelectionModel.Select)

        funcs.show_clipbox_state()

    def on_clipboxstate_switch_handle(self, event: "events.ClipboxStateSwitchEvent"):
        """clipboxstate"""
        if event.Type == event.showType:
            if self.ClipboxState is None:
                self.ClipboxState = CardList_.ClipboxState(parent=self)

            self.ClipboxState.data_update()
            QApplication.processEvents()
            self.ClipboxState.show()
            funcs.clipboxstate_switch_done()
        elif event.Type == event.hideType:
            # print("self.ClipboxState.hide()")
            if self.ClipboxState:
                self.ClipboxState.hide()
                funcs.clipboxstate_switch_done(False)
        pass

    def init_model(self):
        self.newcardcount = 0
        self.ClipboxState = None
        # self.model=QStandardItemModel(self)
        # self.listView=QTreeView(self)
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.character = "root"
        self.model_rootNode.level = -1
        self.model_rootNode.primData = None
        label_id = CardList_.CardItem("card_id", cardlist=self)
        label_desc = CardList_.DescItem("desc", cardlist=self)
        self.model.setHorizontalHeaderItem(1, label_id)
        self.model.setHorizontalHeaderItem(0, label_desc)
        self.listView.setModel(self.model)
        self.listView.header().setDefaultSectionSize(150)
        self.listView.header().setSectionsMovable(False)
        self.listView.setColumnWidth(1, 10)

    def init_signals(self):
        self.on_clipbox_closed = ALL.signals.on_clipbox_closed
        self.on_clipboxCombox_updated = ALL.signals.on_clipboxCombox_updated
        self.on_pageItem_clipbox_added = ALL.signals.on_pageItem_clipbox_added

    def on_clipboxstate_hide_handle(self):
        self.hide()

    def init_UI(self):
        H_layout = QHBoxLayout()
        V_layout2 = QVBoxLayout()

        self.label.setText("card list")
        self.V_layout = QVBoxLayout(self)

        self.addButton.setText("+")

        self.delButton.setText("-")

        self.listView.setIndentation(0)
        self.listView.header().setSectionResizeMode((QHeaderView.Stretch))

        H_layout.addWidget(self.label)
        H_layout.addWidget(self.addButton)
        H_layout.addWidget(self.delButton)
        V_layout2.addWidget(self.listView)
        self.listView.setDragEnabled(True)
        self.listView.setDragDropMode(QAbstractItemView.InternalMove)
        self.listView.setDefaultDropAction(Qt.MoveAction)
        self.listView.setAcceptDrops(True)
        self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listView.dropEvent = self.dropEvent
        self.V_layout.addLayout(H_layout)
        self.V_layout.addLayout(V_layout2)
        self.V_layout.setStretch(1, 1)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        """
        利用光标偏移的结果是否还在原item中,判断属于何种插入方式.(上中下,底层)代码分别是1,0,-1,-2
        允许组嵌套,但不允许重复.
        """
        pos = event.pos()
        drop_index = self.listView.indexAt(pos)
        item_target = self.model.itemFromIndex(drop_index)  # 获取目标项
        insert_posi = self.position_insert_check(pos, drop_index)  # 位置检查
        item_target, insert_posi = self.item_target_recorrect(item_target, insert_posi)  # 通过修正函数重新确定位置
        selected_row_li = self.rowli_index_make()  # 选中的行的检查
        # 下面是根据不同的插入情况做出选择。
        self.rowli_selected_insert(insert_posi, selected_row_li, item_target)
        e = events.CardListDataChangedEvent
        ALL.signals.on_cardlist_dataChanged.emit(e(sender=self, eventType=e.dragDropType))

        # self.listView.expandAll()
        # self.data_save()

    def position_insert_check(self, pos, drop_index):
        """测定插入位置"""

        index_height = self.listView.rowHeight(drop_index)  #
        drop_index_offset_up = self.listView.indexAt(pos - QPoint(0, index_height / 4))  # 高处为0
        drop_index_offset_down = self.listView.indexAt(pos + QPoint(0, index_height / 4))
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

    def rowli_index_make(self):
        """# 源item每次都会选择一行的所有列,而且所有列编成1维数组,所以需要下面的步骤重新组回来."""
        selected_indexes_li = self.listView.selectedIndexes()
        selected_items_li = list(map(self.model.itemFromIndex, selected_indexes_li))
        selected_row_li = []
        for i in range(int(len(selected_items_li) / 2)):
            selected_row_li.append([selected_items_li[2 * i], selected_items_li[2 * i + 1]])
        return selected_row_li

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


class ButtonPanel(QWidget):
    imgDir = objs.SrcAdmin.call().imgDir

    def __init__(self, parent=None, rightsidebar: "RightSideBar" = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.init_signals()
        self.h_layout = QGridLayout(self)
        self.QAbutton = QToolButton(self)
        self.widget_button_hide = QToolButton(self)
        self.confirmButton = QToolButton(self)
        self.reLayoutButton = QToolButton(self)
        self.configButton = QToolButton(self)
        self.resetViewRatioButton = QToolButton(self)
        self.clearViewButton = QToolButton(self)

        self.icon_li = [
            QIcon(self.imgDir.config),
            QIcon(self.imgDir.refresh),
            QIcon(self.imgDir.question),
            QIcon(self.imgDir.correct),
            QIcon(self.imgDir.reset),
            QIcon(self.imgDir.clear),
            QIcon(self.imgDir.right_direction)
        ]

        e = events.RightSideBarButtonGroupEvent
        self.action_li = [
            lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.configType)),
            lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.reLayoutType)),
            lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.QAswitchType)),
            lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.correctType)),
            lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.resetViewRatioType)),
            lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(e(eventType=e.clearViewType)),
            lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(e(eventType=e.hideRighsidebarType))
        ]

        self.toolTipLi = ["配置选项\n"
                          "set configuration",
                          "视图布局重置\n"
                          "view relayout",
                          "切换插入点为Q或A\n"
                          "switch Q or A",
                          "开始插入clipbox的任务\n"
                          "Begin the task of inserting Clipbox",
                          "恢复视图为正常比例\n"
                          "reset view size",
                          "清空视图中的项目\n"
                          "clear view items", "隐藏侧边栏\nhide rightsidebar"]
        self.buttonLi = [
            self.configButton, self.reLayoutButton, self.QAbutton,
            self.confirmButton, self.resetViewRatioButton, self.clearViewButton,
            self.widget_button_hide
        ]
        self.layout_button_li = [6, 4, 1, 5, 2, 0, 3]  # 排在第0个的是第4个button,

        self.rightsidebar = rightsidebar
        self.init_UI()
        self.__event = {
            ALL.signals.on_clipper_hotkey_setQ: self.on_clipper_hotkey_setQ_handle,
            ALL.signals.on_clipper_hotkey_setA: self.on_clipper_hotkey_setA_handle,
            ALL.signals.on_rightSideBar_buttonGroup_clicked: self.on_rightSideBar_buttonGroup_clicked_handle,
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()
        # self.widget_button_hide.setText("5678")
        # self.init_events()

    def init_UI_lambda(self, i: int):
        j = self.layout_button_li[i]
        self.buttonLi[j].setIcon(self.icon_li[j])
        self.buttonLi[j].setToolTip(self.toolTipLi[j])
        self.buttonLi[j].clicked.connect(self.action_li[j])
        self.h_layout.addWidget(self.buttonLi[j], 0, i)
        # self.h_layout.setStretch(i, 1)

    # def init_signals(self):
    # self.on_rightSideBar_buttonGroup_clicked = ALL.signals.on_rightSideBar_buttonGroup_clicked

    def init_UI(self):

        # list(map(lambda w: self.h_layout.addWidget(self.buttonLi[w]),self.layout_button_li))
        #
        list(map(lambda i: self.init_UI_lambda(i), range(len(self.layout_button_li))))

        self.QAbutton.setText("Q")
        ALL.QA = "Q"
        self.setLayout(self.h_layout)

    # def init_events(self):
    #     ALL.signals.on_clipper_hotkey_setQ.connect(self.on_clipper_hotkey_setQ_handle)
    #     ALL.signals.on_clipper_hotkey_setA.connect(self.on_clipper_hotkey_setA_handle)
    #     ALL.signals.on_rightSideBar_buttonGroup_clicked.connect(
    #         self.on_rightSideBar_buttonGroup_clicked_handle)

    def on_rightSideBar_buttonGroup_clicked_handle(self, event: "events.RightSideBarButtonGroupEvent"):
        if event.Type == event.QAswitchType:
            self.QAbutton_switch()
        elif event.Type == event.configType:
            from ..ConfigTable import ConfigTable
            C = ConfigTable(self)
            C.exec()
        elif event.Type == event.correctType:
            from .ButtonPanel__ import ClipperExecuteProgresser
            c = ClipperExecuteProgresser(rightsidebar=self.rightsidebar)
            ALL.signals.on_ClipperExecuteProgresser_show.emit()
            c.exec()

    def on_clipper_hotkey_setQ_handle(self):
        if self.QAbutton.text() == "A":
            self.QAbutton.setText("Q")
            self.QAbutton.setIcon(QIcon(self.imgDir.question))
        funcs.show_clipbox_state()

    def on_clipper_hotkey_setA_handle(self):
        if self.QAbutton.text() == "Q":
            self.QAbutton.setText("A")
            self.QAbutton.setIcon(QIcon(self.imgDir.answer))
        funcs.show_clipbox_state()

    def QAbutton_switch(self):

        if self.QAbutton.text() == "Q":
            self.QAbutton.setText("A")
            self.QAbutton.setIcon(QIcon(self.imgDir.answer))
        else:
            self.QAbutton.setText("Q")
            self.QAbutton.setIcon(QIcon(self.imgDir.question))
        funcs.show_clipbox_state()
        ALL.QA = self.QAbutton.text()
