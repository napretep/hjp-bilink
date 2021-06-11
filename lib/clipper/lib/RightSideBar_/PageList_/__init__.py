import os

from PyQt5.QtGui import QStandardItem, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog

from ...PageInfo import PageInfo
from ...tools.funcs import str_shorten
# from ...RightSideBar_ import PageList

class PDFItem(QStandardItem):
    def __init__(self, PDFName=None, selfData=None, PDFpath=None):
        super().__init__(PDFName)
        self.setFlags(self.flags()
                      & ~ Qt.ItemIsEditable
                      & ~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)
        if PDFpath is not None:
            self.setToolTip(PDFpath)

    def update_data(self, PDFName=None, PDFpath=None):
        if PDFName is not None:
            self.setText(PDFName)
        if PDFpath is not None:
            self.setToolTip(PDFpath)


class PageNumItem(QStandardItem):
    def __init__(self, pagenum=None, selfData=None):
        super().__init__(pagenum)
        self.setFlags(self.flags()
                      & ~ Qt.ItemIsEditable
                      & ~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)


