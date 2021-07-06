import os
import time
from math import ceil

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolButton, QTreeView, QApplication, QHeaderView
from PyQt5.QtCore import Qt, QRect, QItemSelectionModel, pyqtSignal, QTimer, QThread
from aqt.utils import showInfo

from ..PDFView_.PageItem_ import ClipBox_
from ..PDFView_ import PageItem_
from . import PageList_, CardList_
from ..tools.funcs import str_shorten, index_from_row
from ..tools.objs import CustomSignals
from ..tools import events, funcs, ALL
from ..tools import objs
from ..PagePicker import PagePicker


def show_clipbox_state():
    e = events.ClipboxStateSwitchEvent
    ALL.signals.on_clipboxstate_switch.emit(e(eventType=e.showType))


def clipboxstate_switch_done(show=True):
    e = events.ClipboxStateSwitchEvent
    ALL.signals.on_clipboxstate_switch.emit(
        e(eventType=e.showedType if show else e.hiddenType)
    )


class FinalExecution_masterJob(QThread):
    """这里是执行最终任务的地方,信息要采集保存到本地去"""
    on_job_done = pyqtSignal(object)
    on_job_progress = pyqtSignal(object)

    def __init__(self, cardlist=None):
        super().__init__()
        self.cardlist = cardlist
        self.speed = 1 if ALL.ISDEBUG else 0.01
        self.cardcreated = True
        self.fieldinserted = True
        self.pngcreated = True
        self.job_part = 4
        self.init_events()
        self.state_extract_clipbox_info = 0
        self.state_create_newcard = 1
        self.state_insert_cardfield = 2
        self.state_insert_DB = 3
        self.state_create_png = 4

    def init_events(self):
        ALL.signals.on_anki_card_created.connect(self.on_anki_card_created_handle)
        ALL.signals.on_anki_field_insert.connect(self.on_anki_field_insert_handle)
        ALL.signals.on_anki_file_create.connect(self.on_anki_file_create_handle)

    def on_anki_file_create_handle(self, event: "events.AnkiFileCreateEvent"):
        if event.Type == event.ClipperCreatePNGDoneType:
            self.pngcreated = True

    def on_anki_field_insert_handle(self, event: "events.AnkiFieldInsertEvent"):
        if event.Type == event.ClipBoxEndType:
            self.fieldinserted = True
            self.fieldinserted_timestamp = event.data

    def job_progress(self, state, part, percent):
        totalpart = self.job_part
        self.on_job_progress.emit([state, ceil(100 * (part - 1) / totalpart + percent * 100 / totalpart)])

    def on_anki_card_created_handle(self, event: "events.AnkiCardCreatedEvent"):
        if event.Type == event.ClipBoxType:
            self.item_need_update.setText(event.data)
            self.cardcreated = True

    def run(self):
        li = self.job_clipboxlist_make()
        if len(li) == 0:
            return
        self.job_clipbox_DB_insert(li)
        self.job_clipbox_field_insert(li)
        self.job_clipbox_png_create(li)
        self.on_job_done.emit(self.fieldinserted_timestamp)
        pass

    def job_clipboxlist_make(self):
        """cardHashDict:  hash:[DescItem,CardItem]
           DescItem:clipBoxList[clipbox]

            """
        clipboxlist = []
        uuidcount = len(self.cardlist.cardUuidDict)
        current = 0
        for uuid, row in self.cardlist.cardUuidDict.items():

            if row[1].text() == "/":
                self.cardcreated = False  # Debug时要关闭
                self.job_progress(self.state_create_newcard, 1, current / uuidcount)
                self.item_need_update = row[1]
                e = events.AnkiCardCreateEvent
                ALL.signals.on_anki_card_create.emit(e(sender=self, eventType=e.ClipBoxType))

                while not self.cardcreated and not ALL.ISDEBUG:
                    time.sleep(self.speed)
            self.job_progress(self.state_extract_clipbox_info, 1, current / uuidcount)
            for clipbox in row[0].clipBoxList:
                clipboxinfo: "dict" = clipbox.self_info_get()
                clipboxlist.append(clipboxinfo)
            current += 1
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
            if DB.exists(clipbox["uuid"]):
                DB.update(values=DB.value_maker(**clipbox), where=f"""uuid="{clipbox["uuid"]}" """).commit()
            else:
                DB.insert(**clipbox).commit()
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
            ALL.signals.on_pagepicker_open: (self.on_pagepicker_open_handle)
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def init_UI(self):
        H_layout = QHBoxLayout()
        V_layout2 = QVBoxLayout()
        self.label = QLabel()
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
        self.listView.setModel(self.model)
        self.listView.header().setDefaultSectionSize(180)
        self.listView.header().setSectionsMovable(False)
        self.listView.header().setSectionResizeMode((QHeaderView.Stretch))
        self.listView.setColumnWidth(1, 10)

    # def init_signals(self):
    #     self.on_pageItem_addToScene = ALL.signals.on_pageItem_addToScene
    #     self.on_pageItem_removeFromScene = ALL.signals.on_pageItem_removeFromScene
    #     self.on_pageItem_changePage = ALL.signals.on_pageItem_changePage

    def on_pagepicker_open_handle(self, event: "events.PagePickerOpenEvent"):
        # print("收到指令")
        if self.pagepicker is None:
            self.pagepicker = PagePicker(pdfpath=event.pdfpath, frompageitem=event.fromPageItem,
                                         pageNum=event.pagenum, clipper=event.clipper)
            # print("pagepicker 创建")
        self.pagepicker.init_data(pagenum=event.pagenum, PDFpath=event.pdfpath, frompageitem=event.fromPageItem)
        if event.pagenum is not None:
            self.pagepicker.start(event.pagenum)
        else:
            self.pagepicker.start(0)
        QApplication.processEvents()
        self.pagepicker.show()

    def on_listview_clicked_handle(self):
        itemli = [self.model.itemFromIndex(idx) for idx in self.listView.selectedIndexes()]
        print(itemli)
        print(itemli[0].data(Qt.UserRole))
        print(itemli[1].data(Qt.UserRole))
        pass

    def on_listview_doubleClicked_handle(self):
        idx = self.listView.selectedIndexes()
        item = [self.model.itemFromIndex(i) for i in idx][-2:]
        PDFpath = item[0].toolTip()
        pagenum = int(item[1].text())
        pageitem = item[0].data(Qt.UserRole)
        e = events.PagePickerOpenEvent
        ALL.signals.on_pagepicker_open.emit(
            e(sender=self, eventType=e.fromPageListType, clipper=self.rightsidebar.clipper
              , pdfpath=PDFpath, fromPageItem=pageitem, pagenum=pagenum, )
        )

    def on_addButton_clicked_handle(self):
        """打开的时候，确定默认的路径和页码"""
        e = events.PagePickerOpenEvent
        ALL.signals.on_pagepicker_open.emit(
            e(sender=self, eventType=e.fromAddButtonType, clipper=self.rightsidebar.clipper, pagenum=None)
        )

    def on_delButton_clicked_handle(self):
        rowli = self.model_selected_rows()
        for row in rowli:
            self.on_pageItem_removeFromScene.emit(
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

    def __init__(self, parent=None, rightsidebar: "RightSideBar" = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.cardUuidDict: 'dict[int,list[CardList_.DescItem,CardList_.CardItem]]' = {}
        self.rightsidebar = rightsidebar
        self.newcardcount = 0
        self.ClipboxState = None
        self.init_UI()
        self.init_model()
        self.init_signals()
        self.init_events()
        # self.test()

    def card_clipboxlist_add(self, clipbox, uuid_new):
        """加入新的,删除旧的"""
        if uuid_new in self.cardUuidDict:
            self.cardUuidDict[uuid_new][0].clipBoxList.append(clipbox)

    def card_clipboxlist_del(self, clipbox, cardUuid):
        """从中删除"""
        if cardUuid in self.cardUuidDict:
            if clipbox in self.cardUuidDict[cardUuid][0].clipBoxList:
                self.cardUuidDict[cardUuid][0].clipBoxList.remove(clipbox)

    def on_addButton_clicked_handle(self):
        d = CardList_.CardPicker(cardlist=self)
        d.exec_()

    def on_delButton_clicked_handle(self):
        self.rightsidebar.card_list_select_del()

    def on_listView_clicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        if item.column() == 0:
            print(item.clipBoxList)

    def on_clipbox_closed_handle(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        clipbox, uuid = event.clipBox, event.cardUuid
        if uuid is not None:
            self.card_clipboxlist_del(clipbox, uuid)
        # clipbox.close()

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
            desc, card_id = self.model.item(0, 0), self.model.item(0, 1)
        else:
            if len(idxLi) > 0:  # 如有选中,走下一行
                row = [self.model.itemFromIndex(idx) for idx in idxLi[-2:]]
                if row[0].row() + 1 >= self.model.rowCount():
                    self.newcard_signal_emit()
                desc, card_id = self.model.item(row[0].row() + 1, 0), self.model.item(row[0].row() + 1, 1)
                pass
            else:  # 如无选中,新建一行
                self.newcard_signal_emit()
                desc, card_id = self.model.item(self.model.rowCount(), 0), self.model.item(self.model.rowCount(), 1)
        self.listView.selectionModel().clearSelection()
        self.listView.selectionModel().select(index_from_row(self.model, [desc, card_id]), QItemSelectionModel.Select)
        e = events.ClipboxStateSwitchEvent
        show_clipbox_state()

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

        show_clipbox_state()

    def on_clipboxstate_switch_handle(self, event: "events.ClipboxStateSwitchEvent"):
        """clipboxstate"""
        if event.Type == event.showType:
            if self.ClipboxState is None:
                self.ClipboxState = CardList_.ClipboxState(parent=self)

            self.ClipboxState.data_update()
            self.ClipboxState.show()
            clipboxstate_switch_done()
        elif event.Type == event.hideType:
            self.ClipboxState.hide()
            clipboxstate_switch_done(False)
        pass

    def init_model(self):
        self.model = QStandardItemModel()
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

    def init_events(self):
        self.addButton.clicked.connect(self.on_addButton_clicked_handle)
        self.delButton.clicked.connect(self.on_delButton_clicked_handle)
        self.listView.clicked.connect(self.on_listView_clicked_handle)
        self.on_clipbox_closed.connect(self.on_clipbox_closed_handle)
        self.on_clipboxCombox_updated.connect(self.on_clipboxCombox_updated_handle)
        self.on_pageItem_clipbox_added.connect(self.on_pageItem_clipbox_added_handle)
        ALL.signals.on_clipper_hotkey_next_card.connect(self.on_clipper_hotkey_next_card_handle)
        ALL.signals.on_clipper_hotkey_prev_card.connect(self.on_clipper_hotkey_prev_card_handle)
        ALL.signals.on_clipboxstate_switch.connect(self.on_clipboxstate_switch_handle)
        # objs.CustomSignals.start().on_clipboxstate_hide.connect(self.on_clipboxstate_hide_handle)
        # objs.CustomSignals.start().on_cardlist_addCard.connect(self.on_cardlist_addCard_handle)

    def on_clipboxstate_hide_handle(self):
        self.hide()

    def init_UI(self):
        H_layout = QHBoxLayout()
        V_layout2 = QVBoxLayout()
        self.label = QLabel()
        self.label.setText("card list")
        self.V_layout = QVBoxLayout(self)
        self.addButton = QToolButton(self)
        self.addButton.setText("+")
        self.delButton = QToolButton(self)
        self.delButton.setText("-")
        self.listView = QTreeView(self)
        self.listView.setIndentation(0)
        self.listView.header().setSectionResizeMode((QHeaderView.Stretch))
        H_layout.addWidget(self.label)
        H_layout.addWidget(self.addButton)
        H_layout.addWidget(self.delButton)
        V_layout2.addWidget(self.listView)
        self.V_layout.addLayout(H_layout)
        self.V_layout.addLayout(V_layout2)
        self.V_layout.setStretch(1, 1)


class ButtonPanel(QWidget):
    imgDir = objs.SrcAdmin.call().imgDir

    def __init__(self, parent=None, rightsidebar: "RightSideBar" = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.init_signals()

        self.h_layout = QHBoxLayout(self)
        self.QAbutton = QToolButton(self)
        self.confirmButton = QToolButton(self)
        self.reLayoutButton = QToolButton(self)
        self.configButton = QToolButton(self)
        self.resetViewRatioButton = QToolButton(self)

        self.icon_li = [
            QIcon(self.imgDir.config),
            QIcon(self.imgDir.refresh),
            QIcon(self.imgDir.question),
            QIcon(self.imgDir.correct),
            QIcon(self.imgDir.reset)
        ]
        self.buttonLi = [
            self.configButton, self.reLayoutButton, self.QAbutton, self.confirmButton, self.resetViewRatioButton]
        self.action_li = [
            lambda: self.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.configType)),
            lambda: self.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.reLayoutType)),
            lambda: self.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.QAswitchType)),
            lambda: self.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.correctType)),
            lambda: self.on_rightSideBar_buttonGroup_clicked.emit(
                events.RightSideBarButtonGroupEvent(eventType=events.RightSideBarButtonGroupEvent.resetViewRatioType))
        ]

        self.layout_button_li = [4, 1, 2, 0, 3]

        self.rightsidebar = rightsidebar
        self.init_UI()
        self.init_events()

    def init_UI_lambda(self, i: int):
        j = self.layout_button_li[i]
        self.buttonLi[j].setIcon(self.icon_li[j])
        self.buttonLi[j].clicked.connect(self.action_li[j])
        self.h_layout.addWidget(self.buttonLi[j])
        self.h_layout.setStretch(i, 1)

    def init_signals(self):
        self.on_rightSideBar_buttonGroup_clicked = ALL.signals.on_rightSideBar_buttonGroup_clicked

    def init_UI(self):

        # list(map(lambda w: self.h_layout.addWidget(self.buttonLi[w]),self.layout_button_li))
        #
        list(map(lambda i: self.init_UI_lambda(i), range(5)))
        self.QAbutton.setText("Q")
        self.setLayout(self.h_layout)

    def init_events(self):
        ALL.signals.on_clipper_hotkey_setQ.connect(self.on_clipper_hotkey_setQ_handle)
        ALL.signals.on_clipper_hotkey_setA.connect(self.on_clipper_hotkey_setA_handle)
        ALL.signals.on_rightSideBar_buttonGroup_clicked.connect(
            self.on_rightSideBar_buttonGroup_clicked_handle)


    def on_rightSideBar_buttonGroup_clicked_handle(self, event: "events.RightSideBarButtonGroupEvent"):
        if event.Type == event.QAswitchType:
            self.QAbutton_switch()
        elif event.Type == event.configType:
            from ..ConfigTable import ConfigTable
            C = ConfigTable(self)
            C.exec()
        elif event.Type == event.correctType:
            from .ButtonPanel__ import ClipperExecuteProgresser
            c = ClipperExecuteProgresser(cardlist=self.rightsidebar.cardlist)
            ALL.signals.on_ClipperExecuteProgresser_show.emit()
            c.exec()

    def on_clipper_hotkey_setQ_handle(self):
        if self.QAbutton.text() == "A":
            self.QAbutton.setText("Q")
            self.QAbutton.setIcon(QIcon(self.imgDir.question))
        show_clipbox_state()

    def on_clipper_hotkey_setA_handle(self):
        if self.QAbutton.text() == "Q":
            self.QAbutton.setText("A")
            self.QAbutton.setIcon(QIcon(self.imgDir.answer))
        show_clipbox_state()

    def QAbutton_switch(self):

        if self.QAbutton.text() == "Q":
            self.QAbutton.setText("A")
            self.QAbutton.setIcon(QIcon(self.imgDir.answer))
        else:
            self.QAbutton.setText("Q")
            self.QAbutton.setIcon(QIcon(self.imgDir.question))
        show_clipbox_state()
