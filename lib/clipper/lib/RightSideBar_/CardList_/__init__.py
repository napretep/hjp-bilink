from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt


class DescItem(QStandardItem):
    def __init__(self, itemName=None, selfData=None, toolTip=None):
        super().__init__(itemName)
        self.clipBoxList = []
        self.role = "desc"
        self.setFlags(self.flags()
                      & ~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)
        if toolTip is not None:
            self.setToolTip(toolTip)


class CardItem(QStandardItem):
    def __init__(self, itemName=None, selfData=None, toolTip=None):
        super().__init__(itemName)
        self.clipBoxList = []
        self.role = "card_id"
        self.setFlags(self.flags()
                      & ~ Qt.ItemIsEditable
                      & ~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)
        if toolTip is not None:
            self.setToolTip(toolTip)
