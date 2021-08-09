import sys

from PyQt5.QtWidgets import QMainWindow, QListWidget, QListWidgetItem, QCheckBox, QApplication, QHBoxLayout


class mw(QMainWindow):
    def __init__(self):
        super().__init__()
        self.listWidget = QListWidget(self)
        self.setCentralWidget(self.listWidget)
        self.insert(["a", "b", "c"])
        # l = QHBoxLayout(self)
        # l.addWidget(self.list)
        # self.setLayout(l)

    def insert(self, data_list):
        """
        :param list: 要插入的选项文字数据列表 list[str] eg：['城市'，'小区','小区ID']
        """
        for i in data_list:
            box = QCheckBox(i)  # 实例化一个QCheckBox，吧文字传进去
            item = QListWidgetItem()  # 实例化一个Item，QListWidget，不能直接加入QCheckBox

            self.listWidget.addItem(item)  # 把QListWidgetItem加入QListWidget
            self.listWidget.setItemWidget(item, box)  # 再把QCheckBox加入QListWidgetItem

        def getChoose(self) -> [str]:
            """
            得到备选统计项的字段
            :return: list[str]
            """
            count = self.listWidget.count()  # 得到QListWidget的总个数
            cb_list = [self.listWidget.itemWidget(self.listWidget.item(i))
                       for i in range(count)]  # 得到QListWidget里面所有QListWidgetItem中的QCheckBox
            # print(cb_list)
            chooses = []  # 存放被选择的数据
            for cb in cb_list:  # type:QCheckBox
                if cb.isChecked():
                    chooses.append(cb.text())
            # print(chooses)
            return chooses


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = mw()
    demo.show()
    sys.exit(app.exec_())
