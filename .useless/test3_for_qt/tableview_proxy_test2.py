import sys
from PyQt5.QtCore import (Qt, QAbstractTableModel, QModelIndex, QVariant)
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QItemDelegate, QPushButton, QTableView, QWidget,
                             QStyledItemDelegate)


class MyModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(MyModel, self).__init__(parent)

    def rowCount(self, QModelIndex):
        return 4

    def columnCount(self, QModelIndex):
        return 3

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            return 'Row %d, Column %d' % (row + 1, col + 1)
        return QVariant()


class MyButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(MyButtonDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            button_read = QPushButton(
                self.tr('读'),
                self.parent(),
                clicked=self.parent().cellButtonClicked
            )
            button_write = QPushButton(
                self.tr('写'),
                self.parent(),
                clicked=self.parent().cellButtonClicked
            )
            button_read.index = [index.row(), index.column()]
            button_write.index = [index.row(), index.column()]
            h_box_layout = QHBoxLayout()
            h_box_layout.addWidget(button_read)
            h_box_layout.addWidget(button_write)
            h_box_layout.setContentsMargins(0, 0, 0, 0)
            h_box_layout.setAlignment(Qt.AlignCenter)
            widget = QWidget()
            widget.setLayout(h_box_layout)
            self.parent().setIndexWidget(
                index,
                widget
            )


class MyTableView(QTableView):
    def __init__(self, parent=None):
        super(MyTableView, self).__init__(parent)
        self.setItemDelegateForColumn(0, MyButtonDelegate(self))

    def cellButtonClicked(self):
        print("Cell Button Clicked", self.sender().index)


if __name__ == '__main__':
    a = QApplication(sys.argv)
    tableView = MyTableView()
    myModel = MyModel()
    tableView.setModel(myModel)
    tableView.show()
    a.exec_()
