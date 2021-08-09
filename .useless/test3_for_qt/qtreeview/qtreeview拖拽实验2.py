import sys
from PyQt5 import QtCore, QtGui, QtWidgets

IDRole = QtCore.Qt.UserRole + 1000


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()

        self.tree = QtWidgets.QTreeWidget(columnCount=1,
                                          dragDropMode=QtWidgets.QAbstractItemView.DragDrop,
                                          dragEnabled=True)
        self.tree.hideColumn(1)

        self.tree.itemDoubleClicked.connect(self.rename)
        self.tree.itemChanged.connect(self.postRename)

        # add treewidgetitems
        data = [['Folder 1', '1'],
                ['Folder 2', '2'],
                ['Folder 3', '3']
                ]
        for d in data:
            text, itemid = d
            item = QtWidgets.QTreeWidgetItem([text])
            item.setData(0, IDRole, itemid)
            self.tree.addTopLevelItem(item)

        frame = QtWidgets.QWidget()
        self.setCentralWidget(frame)
        hl = QtWidgets.QVBoxLayout(frame)
        hl.addWidget(self.tree)

    @QtCore.pyqtSlot()
    def rename(self):
        item = self.tree.selectedItems()
        if item:
            item = item[0]
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.tree.scrollToItem(item)
            self.tree.editItem(item)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def postRename(self, item, column):
        print('postRename: column counts', item.columnCount())
        text = item.text(0)
        itemid = item.data(0, IDRole)
        print('postRename: item text=', text, 'item id', itemid)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
