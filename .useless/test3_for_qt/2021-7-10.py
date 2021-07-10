import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Table(QWidget):
    def __init__(self, parent=None):
        super(Table, self).__init__(parent)
        # 设置标题与初始大小
        self.setWindowTitle('QTableView表格视图的例子')
        self.resize(500, 300)

        # 设置数据层次结构，4行4列
        self.model = QStandardItemModel(4, 4)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(['标题1', '标题2', '标题3', '标题4'])

        # #Todo 优化2 添加数据
        # self.model.appendRow([
        #     QStandardItem('row %s,column %s' % (11,11)),
        #     QStandardItem('row %s,column %s' % (11,11)),
        #     QStandardItem('row %s,column %s' % (11,11)),
        #     QStandardItem('row %s,column %s' % (11,11)),
        # ])

        for row in range(4):
            for column in range(4):
                item = QStandardItem('row %s,column %s' % (row, column))
                # 设置每个位置的文本值
                self.model.setItem(row, column, item)

        # 实例化表格视图，设置模型为自定义的模型
        self.tableView = QTableView()
        self.tableView.setDragDropMode(QAbstractItemView)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setModel(self.model)
        self.tableView.setAcceptDrops(True)

        # #todo 优化1 表格填满窗口
        # #水平方向标签拓展剩下的窗口部分，填满表格
        # self.tableView.horizontalHeader().setStretchLastSection(True)
        # #水平方向，表格大小拓展到适当的尺寸
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #
        # #TODO 优化3 删除当前选中的数据
        # indexs=self.tableView.selectionModel().selection().indexes()
        # print(indexs)
        # if len(indexs)>0:
        #     index=indexs[0]
        #     self.model.removeRows(index.row(),1)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.tableView)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    table = Table()
    table.show()
    sys.exit(app.exec_())
