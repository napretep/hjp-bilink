# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'qtreeview拖拽实验.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/7 22:38'
"""

import sys

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMainWindow, QTreeView, QApplication


class DemoTreeView(QMainWindow):
    class Item(QStandardItem):
        def __init__(self, text):
            super().__init__(text)
            self.original_text = text

        def clone(self) -> 'DemoTreeView.Item':
            return DemoTreeView.Item(self.original_text)

        def say(self):
            print(self.original_text)

        def parent(self):
            if super().parent() is None:
                return self.model().invisibleRootItem()
            else:
                return super().parent()

    class View(QTreeView):
        def __init__(self, parent):
            super().__init__(parent)
            self.setSelectionMode(self.ExtendedSelection)
            self.setDragDropMode(self.InternalMove)
            self.clicked.connect(self.on_clicked_handle)

        def on_clicked_handle(self, index):
            item = self.model().itemFromIndex(index)
            item.say()

        def dropEvent(self, event: QtGui.QDropEvent) -> None:
            item_from: "list[DemoTreeView.Item]" = [self.model().itemFromIndex(index) for index in
                                                    self.selectedIndexes()]
            item_to: "DemoTreeView.Item" = self.model().itemFromIndex(self.indexAt(event.pos()))

            parent_from = [item.parent() for item in item_from]
            parent_to = item_to.parent() if item_to is not None else self.model().invisibleRootItem()

            if self.dropIndicatorPosition() == self.OnItem:
                # for i in item_from:
                for i in range(len(item_from)):
                    item = parent_from[i].takeRow(item_from[i].row())
                    item_to.appendRow(item)
            elif self.dropIndicatorPosition() == self.OnViewport:
                for i in range(len(item_from)):
                    item = parent_from[i].takeRow(item_from[i].row())
                    self.model().appendRow(item)
            elif self.dropIndicatorPosition() == self.BelowItem:
                for i in range(len(item_from)):
                    item = parent_from[i].takeRow(item_from[i].row())
                    parent_to.insertRow(item_to.row() + 1, item)
            elif self.dropIndicatorPosition() == self.AboveItem:
                for i in range(len(item_from)):
                    item = parent_from[i].takeRow(item_from[i].row())
                    parent_to.insertRow(item_to.row(), item)
                pass

    def __init__(self, parent=None):
        super(DemoTreeView, self).__init__(parent)
        self.initUi()

    def on_model_data_changed_handle(self, index):
        print("emit")
        data=self.model.invisibleRootItem().child(0,0).data(Qt.UserRole)
        print(data)
    def initUi(self):
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['test'])
        self.model.appendRow([self.Item("A")])
        self.model.appendRow([self.Item("B")])
        self.model.appendRow([self.Item("C")])
        self.model.appendRow([self.Item("D")])
        self.model.setItemPrototype(DemoTreeView.Item("x"))
        self.model.dataChanged.connect(self.on_model_data_changed_handle)
        self.treeView = self.View(self)
        self.treeView.setModel(self.model)
        self.treeView.expandAll()
        self.setCentralWidget(self.treeView)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DemoTreeView()
    window.show()
    sys.exit(app.exec())
