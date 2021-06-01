from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QToolButton, QTreeView
from PyQt5.QtCore import Qt
from .. import RightSideBar
from . import PageList_

class CardList(QWidget):
    def __init__(self, parent=None,rightsidebar:"RightSideBar"=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.rightsidebar=rightsidebar
        self.init_UI()

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
        H_layout.addWidget(self.label)
        H_layout.addWidget(self.addButton)
        H_layout.addWidget(self.delButton)
        V_layout2.addWidget(self.listView)
        self.V_layout.addLayout(H_layout)
        self.V_layout.addLayout(V_layout2)
        self.V_layout.setStretch(1, 1)

    def init_model(self):
        self.model = QStandardItemModel()
        self.model_rootNode = self.model.invisibleRootItem()
        self.model_rootNode.character = "root"
        self.model_rootNode.level = -1
        self.model_rootNode.primData = None
        label_id = QStandardItem("card_id")
        label_desc = QStandardItem("desc")
        self.model.setHorizontalHeaderItem(0, label_id)
        self.model.setHorizontalHeaderItem(1, label_desc)
        self.listView.setModel(self.model)



class PageList(QWidget):
    """
    左边竖排添加删除按钮,右边一个QListWidget
    """

    def __init__(self, parent=None,rightsidebar:"RightSideBar"=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.rightsidebar=rightsidebar
        self.parent=parent
        self.init_UI()
        self.init_model()
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
        self.model_rootNode.character = "root"
        self.model_rootNode.level = -1
        self.model_rootNode.primData = None
        pdfname = QStandardItem("PDFname") #存文件路径
        pagenum = QStandardItem("pagenum") #存页码和graphics_page对象
        self.model.setHorizontalHeaderItem(0,pdfname)
        self.model.setHorizontalHeaderItem(1,pagenum)
        self.listView.setModel(self.model)
        self.listView.header().setDefaultSectionSize(180)
        self.listView.header().setSectionsMovable(False)
        self.listView.setColumnWidth(1, 10)

    def init_event(self):
        self.addButton.clicked.connect(self.openDialogPDFOpen)
        self.delButton.clicked.connect(self.delete_selected_item)
    def openDialogPDFOpen(self):
        count = self.model.rowCount()
        if count>0:
            PDFpath = self.model.item(count-1,0).data(Qt.UserRole)
            pagenum = int(self.model.item(count-1,1).text())
        else:
            PDFpath =""
            pagenum =0
        P = PageList_.PDFOpen(PDFpath, pagenum, pagelist=self).exec()

    def delete_selected_item(self):
        pass

class QAConfirmGroup(QWidget):
    def __init__(self, parent=None,rightsidebar:"RightSideBar"=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.rightsidebar=rightsidebar
        self.init_UI()

    def init_UI(self):
        self.h_layout = QHBoxLayout(self)
        self.Qbutton = QToolButton(self)
        self.Abutton = QToolButton(self)
        self.Confirm = QToolButton(self)
        self.Qbutton.setText("Q")
        self.Abutton.setText("A")
        self.Confirm.setText("√")
        list(map(lambda w:self.h_layout.addWidget(w),[self.Qbutton, self.Abutton, self.Confirm]))
        list(map(lambda i:self.h_layout.setStretch(i,1),range(3)))
        self.setLayout(self.h_layout)
