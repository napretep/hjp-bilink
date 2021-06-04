import os

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsItem, QGraphicsPixmapItem
from .tools.funcs import str_shorten,index_from_row
from .RightSideBar_ import PageList,CardList,QAConfirmGroup,PageList_
from . import PDFView_
from .PageInfo import PageInfo

class RightSideBar(QWidget):
    def __init__(self, parent=None,clipper:'Clipper'=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.clipper=clipper
        self.init_UI()

    def init_UI(self):
        self.V_layout = QVBoxLayout()
        self.pagelist = PageList(rightsidebar=self)
        self.cardlist = CardList(rightsidebar=self)
        self.QAconfirm = QAConfirmGroup(rightsidebar=self)
        self.V_layout.addWidget(self.pagelist)
        self.V_layout.addWidget(self.cardlist)
        self.V_layout.addWidget(self.QAconfirm)
        self.V_layout.setStretch(0, 1)
        self.V_layout.setStretch(1, 1)
        self.setLayout(self.V_layout)

    def page_list_add(self, pageinfo: 'PageInfo'):
        """深层的不搞API,尽量都放到这一层"""
        pdfname = pageinfo.doc.name
        pagenum = pageinfo.pagenum
        pageitem = PDFView_.PageItem5(pageinfo, rightsidebar=self)
        pdfname_tail = os.path.basename(pdfname)
        row = [PageList_.Item(itemName=str_shorten(pdfname_tail), selfData=pdfname, toolTip=pdfname),
               PageList_.Item(itemName=str(pagenum), selfData=pageitem)]
        pageitem.belongto_pagelist_row = row
        self.pagelist.model.appendRow(row)
        self.pagelist.listView.selectionModel().clearSelection()
        self.pagelist.listView.selectionModel().select(index_from_row(self.pagelist.model, row),
                                                       QItemSelectionModel.Select)
        self.clipper.scene.addItem(pageitem)
        self.clipper.update()
        pass

    def card_list_model_load(self):
        return self.cardlist.model_rootNode

    def list_card_add(self):
        pass

    def list_page_del(self):
        pass

    def list_card_del(self):
        pass
