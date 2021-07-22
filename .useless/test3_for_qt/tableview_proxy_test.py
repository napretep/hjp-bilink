import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Table(QMainWindow):
    def __init__(self, parent=None):
        super(Table, self).__init__(parent)
        self.setWindowTitle('QTableView表格视图的例子')
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["选框\nclipbox", "评论\ncomment", "所在页码\npage at", "插入卡片\nto card",
                                              "插入到字段\nto field", "评论插入字段\ncomment to field", "删除\ndelete"])
        self.tableView = QTableView()
        self.tableView.setModel(self.model)
        header = self.tableView.horizontalHeader()
        header.setSectionResizeMode(header.Interactive)
        header.setSectionResizeMode(1, header.Stretch)
        header.setSectionResizeMode(0, header.Stretch)
        v_header: "QHeaderView" = self.tableView.verticalHeader()
        v_header.setSectionResizeMode(v_header.Interactive)
        # self.tableView.edit
        self.setCentralWidget(self.tableView)

        # testcase
        pixmap = r"C:\Users\Administrator\Desktop\89937761_p0.jpg"
        comment = "hello world"
        page_at = "1"
        to_card = "current_card"
        to_field = "0"
        comment_to_field = "1"
        delete = "0"
        testcase = [pixmap, comment, page_at, to_card, to_field, comment_to_field, delete]
        row = [QStandardItem(i) for i in testcase]
        self.model.appendRow(row)

        idx = self.model.item(0, 6).index()
        self.model.item(0, 3).setData(["test1", "test2"], role=Qt.UserRole)
        # self.model.item(0,3).combox=Combox()
        self.tableView.setIndexWidget(idx, QToolButton())
        # self.tableView.setRowHeight(0,150)
        self.tableView.setItemDelegate(Delegate(self.tableView))


class Combox(QComboBox):
    def __init__(self, *args):
        super().__init__(*args)
        self.currentIndexChanged.connect(self.on_currentIndexChanged)

    def on_currentIndexChanged(self, index):
        data = self.itemText(index)
        if data == "+":
            count = self.count()
            self.addItem(f"new card_{count}")
            self.setCurrentIndex(count)


class Delegate(QStyledItemDelegate):
    pixmap = 0
    comment = 1
    page_at = 2
    card_desc = 3
    to_field = 4
    comment_to_field = 5
    close = 6

    def paint(self, painter: "QPainter", option: "QStyleOptionViewItem", index: "QModelIndex"):
        value = index.model().data(index, Qt.DisplayRole)
        if index.column() == self.pixmap:
            v = min(option.rect.height(), option.rect.width())
            pixmap = QPixmap(value).scaledToHeight(v)
            middle = int(option.rect.width() / 2 - pixmap.width() / 2)
            option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
            painter.drawPixmap(QRect(middle, 0, pixmap.width(), pixmap.height()), pixmap)
        # elif index.column() == self.close and not self.parent().indexWidget(index):
        #

        else:
            super().paint(painter, option, index)

    def createEditor(self, Widget: "QWidget", Option: "QStyleOptionViewItem", Index: "QModelIndex"):
        if Index.column() in [self.pixmap, self.page_at, self.close]:
            return None
        elif Index.column() == self.card_desc:
            combox: "Combox" = Combox()
            combox.setParent(Widget)
            return combox
        elif Index.column() in [self.to_field, self.comment_to_field]:
            spinBox = QSpinBox(Widget)

            spinBox.setRange(0, 2000)
            return spinBox
        else:
            return super().createEditor(Widget, Option, Index)

    def setEditorData(self, Widget: "QWidget", Index: "QModelIndex"):
        if Index.column() == self.card_desc:
            Widget.addItem("currentpage")
            Widget.addItem("+")
            data = Index.data(role=Qt.UserRole)
            for i in data:
                Widget.addItem(i)
        else:
            super().setEditorData(Widget, Index)

    # def sizeHint(self,  option:"QStyleOptionViewItem", index:"QModelIndex"):
    #     if index.column()==0:
    #         index
    #
    #     else:
    #         super().sizeHint(option,index)
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    table = Table()
    table.show()
    sys.exit(app.exec_())
