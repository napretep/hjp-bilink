import os

from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolButton, QTreeView
from PyQt5.QtCore import Qt, QRect, QItemSelectionModel, pyqtSignal

from ..PDFView_.PageItem_ import ClipBox_
from ..PDFView_ import PageItem_
from . import PageList_, CardList_
from ..tools.funcs import str_shorten, index_from_row
from ..tools.objs import CustomSignals
from ..tools import events
from ..tools import objs
from ..PagePicker import PagePicker


class PageList(QWidget):
    """
    左边竖排添加删除按钮,右边一个QListWidget
    """

    def __init__(self, parent=None, rightsidebar: "RightSideBar" = None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.rightsidebar = rightsidebar
        self.parent = parent
        self.pageItemDict = {}
        self.init_UI()
        self.init_model()
        self.init_signals()
        self.init_event()

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
        self.listView.setColumnWidth(1, 10)

    def init_signals(self):
        self.on_pageItem_addToScene = CustomSignals.start().on_pageItem_addToScene
        self.on_pageItem_removeFromScene = CustomSignals.start().on_pageItem_removeFromScene
        self.on_pageItem_changePage = CustomSignals.start().on_pageItem_changePage

    def init_event(self):
        self.addButton.clicked.connect(self.openDialogPDFOpen)
        self.delButton.clicked.connect(self.delete_selected_item)
        self.listView.clicked.connect(self.on_listview_clicked)
        self.listView.doubleClicked.connect(self.on_listview_doubleClicked)
        self.on_pageItem_removeFromScene.connect(self.on_pageItem_removeFromScene_handle)
        self.on_pageItem_addToScene.connect(self.on_pageItem_addToScene_handle)
        self.on_pageItem_changePage.connect(self.on_pageItem_changePage_handle)

    def on_listview_clicked(self):
        itemli = [self.model.itemFromIndex(idx) for idx in self.listView.selectedIndexes()]
        print(itemli)
        print(itemli[0].data(Qt.UserRole))
        print(itemli[1].data(Qt.UserRole))
        pass

    def on_listview_doubleClicked(self):
        idx = self.listView.selectedIndexes()
        item = [self.model.itemFromIndex(i) for i in idx][-2:]
        PDFpath = item[0].toolTip()
        pagenum = int(item[1].text())
        pageitem = item[0].data(Qt.UserRole)
        P = PagePicker(pdfDirectory=PDFpath, pageNum=pagenum, frompageitem=pageitem,
                       clipper=self.rightsidebar.clipper).exec()

    def openDialogPDFOpen(self):
        """打开的时候，确定默认的路径和页码"""
        idx = self.listView.selectedIndexes()
        pageitem = None
        if len(idx) > 0:
            item = [self.model.itemFromIndex(i) for i in idx][-2:]
            PDFpath = item[0].toolTip()
            pagenum = int(item[1].text())
            pageitem = item[0].data(Qt.UserRole)
        else:
            count = self.model.rowCount()
            if count > 0:
                PDFpath = self.model.item(count - 1, 0).toolTip()
                pagenum = int(self.model.item(count - 1, 1).text())
            else:
                PDFpath = ""
                pagenum = 0
        P = PagePicker(pdfDirectory=PDFpath, pageNum=pagenum, frompageitem=pageitem,
                       clipper=self.rightsidebar.clipper).exec()

    def delete_selected_item(self):
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
        elif event.Type == event.changePageType:
            pass
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
        self.cardHashDict: 'dict[int,list[CardList_.DescItem,CardList_.CardItem]]' = {}
        self.rightsidebar = rightsidebar
        self.newcardcount = 0
        self.init_UI()
        self.init_model()
        self.init_signals()
        self.init_events()
        # self.test()

    def card_clipboxlist_add(self, clipbox, hash_new):
        """加入新的,删除旧的"""
        if hash_new in self.cardHashDict:
            self.cardHashDict[hash_new][0].clipBoxList.append(clipbox)

    def card_clipboxlist_del(self, clipbox, hash_):
        """从中删除"""
        if hash_ in self.cardHashDict:
            if clipbox in self.cardHashDict[hash_][0].clipBoxList:
                self.cardHashDict[hash_][0].clipBoxList.remove(clipbox)

    def on_addButton_clicked(self):
        self.rightsidebar.card_list_add()

    def on_delButton_clicked(self):
        self.rightsidebar.card_list_select_del()

    def on_listView_clicked(self, index):
        item = self.model.itemFromIndex(index)
        if item.column() == 0:
            print(item.clipBoxList)

    def on_clipbox_closed_handle(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        clipbox, hash_ = event.clipBox, event.cardHash
        if hash_ is not None:
            self.card_clipboxlist_del(clipbox, hash_)

    def on_clipboxCombox_updated_handle(self, event: 'ClipBox_.ToolsBar_.ClipboxEvent'):
        self.card_clipboxlist_add(event.clipBox, event.cardHash)
        self.card_clipboxlist_del(event.clipBox, event.cardHash_old)

    def on_pageItem_clipbox_added_handle(self, event: 'PageItem_.PageItem_ClipBox_Event'):
        """added信号"""
        self.card_clipboxlist_add(event.clipbox, event.cardhash)

    def on_clipper_hotkey_next_card_handle(self):
        """1看有没有卡, 2看有没有选中"""
        rowcount = self.model.rowCount()
        idxLi = self.listView.selectedIndexes()
        if rowcount == 0:  # 没有卡片
            self.rightsidebar.card_list_add()
            desc, card_id = self.model.item(0, 0), self.model.item(0, 1)
        else:
            if len(idxLi) > 0:  # 如有选中,走下一行
                row = [self.model.itemFromIndex(idx) for idx in idxLi[-2:]]
                if row[0].row() + 1 >= self.model.rowCount():
                    self.rightsidebar.card_list_add()
                desc, card_id = self.model.item(row[0].row() + 1, 0), self.model.item(row[0].row() + 1, 1)
                pass
            else:  # 如无选中,新建一行
                self.rightsidebar.card_list_add()
                desc, card_id = self.model.item(self.model.rowCount(), 0), self.model.item(self.model.rowCount(), 1)
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

    def init_model(self):
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.character = "root"
        self.model_rootNode.level = -1
        self.model_rootNode.primData = None
        label_id = CardList_.CardItem("card_id")
        label_desc = CardList_.DescItem("desc")
        self.model.setHorizontalHeaderItem(1, label_id)
        self.model.setHorizontalHeaderItem(0, label_desc)
        self.listView.setModel(self.model)
        self.listView.header().setDefaultSectionSize(180)
        self.listView.header().setSectionsMovable(False)
        self.listView.setColumnWidth(1, 10)

    def init_signals(self):
        self.on_clipbox_closed = CustomSignals.start().on_clipbox_closed
        self.on_clipboxCombox_updated = CustomSignals.start().on_clipboxCombox_updated
        self.on_pageItem_clipbox_added = CustomSignals.start().on_pageItem_clipbox_added

    def init_events(self):
        self.addButton.clicked.connect(self.on_addButton_clicked)
        self.delButton.clicked.connect(self.on_delButton_clicked)
        self.listView.clicked.connect(self.on_listView_clicked)
        self.on_clipbox_closed.connect(self.on_clipbox_closed_handle)
        self.on_clipboxCombox_updated.connect(self.on_clipboxCombox_updated_handle)
        self.on_pageItem_clipbox_added.connect(self.on_pageItem_clipbox_added_handle)
        CustomSignals.start().on_clipper_hotkey_next_card.connect(self.on_clipper_hotkey_next_card_handle)
        CustomSignals.start().on_clipper_hotkey_prev_card.connect(self.on_clipper_hotkey_prev_card_handle)

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
        self.on_rightSideBar_buttonGroup_clicked = objs.CustomSignals.start().on_rightSideBar_buttonGroup_clicked

    def init_UI(self):

        # list(map(lambda w: self.h_layout.addWidget(self.buttonLi[w]),self.layout_button_li))
        #
        list(map(lambda i: self.init_UI_lambda(i), range(5)))
        self.QAbutton.setText("Q")
        self.setLayout(self.h_layout)

    def init_events(self):
        CustomSignals.start().on_clipper_hotkey_setQ.connect(self.on_clipper_hotkey_setQ_handle)
        CustomSignals.start().on_clipper_hotkey_setA.connect(self.on_clipper_hotkey_setA_handle)
        CustomSignals.start().on_rightSideBar_buttonGroup_clicked.connect(
            self.on_rightSideBar_buttonGroup_clicked_handle)

    def on_rightSideBar_buttonGroup_clicked_handle(self, event: "events.RightSideBarButtonGroupEvent"):
        if event.Type == event.QAswitchType:
            self.QAbutton_switch()
        elif event.Type == event.configType:
            from ..ConfigTable import ConfigTable
            C = ConfigTable()
            C.exec()

    def on_clipper_hotkey_setQ_handle(self):
        if self.QAbutton.text() == "A":
            self.QAbutton.setText("Q")
            self.QAbutton.setIcon(QIcon(self.imgDir.question))

    def on_clipper_hotkey_setA_handle(self):
        if self.QAbutton.text() == "Q":
            self.QAbutton.setText("A")
            self.QAbutton.setIcon(QIcon(self.imgDir.answer))

    def QAbutton_switch(self):

        if self.QAbutton.text() == "Q":
            self.QAbutton.setText("A")
            self.QAbutton.setIcon(QIcon(self.imgDir.answer))
        else:
            self.QAbutton.setText("Q")
            self.QAbutton.setIcon(QIcon(self.imgDir.question))
