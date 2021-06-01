import os

from PyQt5.QtGui import QStandardItem, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog

from ...PageInfo import PageInfo
from ...tools.funcs import str_shorten
# from ...RightSideBar_ import PageList

class Item(QStandardItem):
    def __init__(self,itemName=None,selfData=None,toolTip=None):
        super().__init__(itemName)
        self.setFlags(self.flags()
            &~ Qt.ItemIsEditable
            &~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData,Qt.UserRole)
        if toolTip is not None:
            self.setToolTip(toolTip)


class PDFOpen(QDialog):
    def __init__(self, path, pagenum: int, parent = None, pagelist: 'PageList' =None):
        super().__init__(parent=parent)
        self.pagelist=pagelist
        self.pagenum=pagenum
        self.init_UI()
        self.init_label(path)
        self.init_event()

    def init_UI(self):
        self.setWindowIcon(QIcon("./resource/icon_page_pick.png"))
        self.setWindowTitle("PDF page pick")
        H_layout = QHBoxLayout()
        self.path_label = QLabel()
        self.pagenum_label = QLabel()
        self.pagenum_label.setText("page at:")
        self.open_button = QPushButton()
        self.open_button.setText("select other PDF")
        self.correct_button = QPushButton()
        self.correct_button.setText("Done")
        self.page = QSpinBox()
        self.page.setValue(self.pagenum)
        H_layout.addWidget(self.path_label)
        H_layout.addWidget(self.open_button)
        H_layout.addWidget(self.pagenum_label)
        H_layout.addWidget(self.page)
        H_layout.addWidget(self.correct_button)
        H_layout.setStretch(0, 1)
        self.setLayout(H_layout)

    def init_label(self, path, length=30):
        PDFname = os.path.basename(path)
        self.path_label.setText(str_shorten(PDFname))
        self.path_label.setToolTip(path)


    def init_event(self):
        self.open_button.clicked.connect(self.file_open)
        self.correct_button.clicked.connect(self.data_save)

    def data_save(self):
        path = self.path_label.toolTip()
        pagenum = self.page.value()
        pageinfo = PageInfo(path, pagenum)
        self.pagelist.rightsidebar.page_list_add(pageinfo)
        self.close()

    def file_open(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                "选取文件", "../../user_files",
                                                                "(*.pdf)"
                                                                )
        if fileName_choose !='':
            path = fileName_choose.__str__()
            self.init_label(path)
        pass

