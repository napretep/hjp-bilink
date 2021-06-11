import os

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsItem, QGraphicsPixmapItem
from .tools.funcs import str_shorten, index_from_row
from .RightSideBar_ import PageList, CardList, ButtonPanel, PageList_, CardList_
from . import PDFView_
from .PageInfo import PageInfo
from .tools.objs import CustomSignals
from .tools import events


class RightSideBar(QWidget):
    on_cardlist_dataChanged = CustomSignals.start().on_cardlist_dataChanged
    on_cardlist_deleteItem = CustomSignals.start().on_cardlist_deleteItem

    def __init__(self, parent=None, clipper: 'Clipper' = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clipper = clipper
        self.init_UI()

    def init_UI(self):
        self.V_layout = QVBoxLayout()
        self.pagelist = PageList(rightsidebar=self)
        self.cardlist = CardList(rightsidebar=self)
        self.QAconfirm = ButtonPanel(rightsidebar=self)
        self.V_layout.addWidget(self.pagelist)
        self.V_layout.addWidget(self.cardlist)
        self.V_layout.addWidget(self.QAconfirm)
        self.V_layout.setStretch(0, 1)
        self.V_layout.setStretch(1, 1)
        self.setLayout(self.V_layout)

    """下面的API最好写的简单,过程隐藏在里面"""

    def get_QA(self):
        return self.QAconfirm.QAbutton.text()

    def card_list_model_load(self):
        return self.cardlist.model_rootNode

    def page_list_add(self, pageinfo: 'PageInfo'):
        """深层的不搞API,尽量都放到这一层"""
        pdfDirectory = pageinfo.doc.name
        pagenum = pageinfo.pagenum
        pageitem = PDFView_.PageItem5(pageinfo, rightsidebar=self)
        pdfname_tail = os.path.basename(pdfDirectory)
        row = [PageList_.PDFItem(itemName=str_shorten(pdfname_tail), selfData=pdfDirectory, toolTip=pdfDirectory),
               PageList_.PDFItem(itemName=str(pagenum), selfData=pageitem)]
        pageitem.belongto_pagelist_row = row
        self.pagelist.model.appendRow(row)
        self.pagelist.listView.selectionModel().clearSelection()
        self.pagelist.listView.selectionModel().select(index_from_row(self.pagelist.model, row),
                                                       QItemSelectionModel.Select)
        pageitem.setZValue(0)
        self.clipper.scene.addItem(pageitem)
        self.clipper.update()
        pass

    def page_list_select_del(self):
        pass

    def card_list_select_del(self):
        cardlist = self.cardlist
        itemli = [cardlist.model.itemFromIndex(idx) for idx in cardlist.listView.selectedIndexes()]
        rowli = [[itemli[i], itemli[i + 1]] for i in range(int(len(itemli) / 2))]
        for row in rowli:
            cardlist.model.takeRow(row[0].row())
        # row = [cardlist.model.item(cardlist.model.rowCount()-1,0),cardlist.model.item(cardlist.model.rowCount()-1,1)]
        # cardlist.listView.selectionModel().clearSelection()
        # cardlist.listView.selectionModel().select(index_from_row(cardlist.model,row),QItemSelectionModel.Select)
        self.on_cardlist_dataChanged.emit(events.CardListDataChangedEvent(cardlist=self.cardlist))
        self.on_cardlist_deleteItem.emit(events.CardListDeleteItemEvent(cardlist=self.cardlist))
        pass

    def card_list_add(self):
        cardlist = self.cardlist
        rownum = cardlist.newcardcount
        desc, card_id = CardList_.DescItem(f"new card {rownum}"), CardList_.CardItem("/")
        cardlist.cardHashDict[desc.hash] = [desc, card_id]
        cardlist.newcardcount += 1
        cardlist.model.appendRow([desc, card_id])
        cardlist.listView.selectionModel().clearSelection()
        cardlist.listView.selectionModel().select(index_from_row(cardlist.model, [desc, card_id]),
                                                  QItemSelectionModel.Select)
        self.on_cardlist_dataChanged.emit(events.CardListDataChangedEvent(cardlist=self.cardlist))
        pass
