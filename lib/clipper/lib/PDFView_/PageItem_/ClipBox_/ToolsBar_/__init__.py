from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QLineEdit, QComboBox, QGraphicsProxyWidget


class ClipboxEvent:
    eventClose = 0

    def __init__(self, clipBox=None, cardHash=None, cardHash_old=None, eventType=None):
        self.Type = eventType
        self.clipBox = clipBox
        self.cardHash = cardHash
        self.cardHash_old = cardHash_old


class QAButton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar' = None, QA="Q"):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar
        self.IconDict = {
            "Q": QIcon("./resource/icon_question.png"),
            "A": QIcon("./resource/icon_answer.png")
        }
        self.toolTipDict = {
            "Q": "将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card",
            "A": "将选框保存到卡片答案字段\nrestore the clipbox to the answer field of the card"
        }
        self.QAButton = QToolButton()
        self.QA = QA
        self.init_UI()
        self.init_data()
        self.init_events()
        self.setWidget(self.QAButton)

    def init_UI(self):
        self.QAButton.setStyleSheet(
            f"margin-right:-1px;margin-left:-1px;margin-top: -1px;;")

        pass

    def init_data(self):
        self.QAButton.setText(self.QA)
        self.QAButton.setIcon(self.IconDict[self.QA])
        self.QAButton.setToolTip(self.toolTipDict[self.QA])

    def init_events(self):
        self.QAButton.clicked.connect(self.onQAButtonClicked)

    def onQAButtonClicked(self):
        if self.QAButton.text() == "Q":
            self.QAButton.setText("A")
            self.QAButton.setIcon(self.IconDict["A"])
            self.QAButton.setToolTip(self.toolTipDict["A"])
        else:
            self.QAButton.setText("Q")
            self.QAButton.setIcon(self.IconDict["Q"])
            self.QAButton.setToolTip(self.toolTipDict["Q"])
        self.update()

    pass


class CloseButton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar
        self.closeButton = QToolButton()
        self.init_UI()
        self.init_data()
        self.init_signals()
        self.init_events()
        self.setWidget(self.closeButton)

    def init_UI(self):
        self.closeButton.setStyleSheet(
            f"margin-left:-1px;margin-top: -1px;")
        pass

    def init_signals(self):
        self.on_clipbox_closed = \
            self.toolsbar.cardlist.rightsidebar.clipper.objs.CustomSignals.start().on_clipbox_closed

    def init_data(self):
        self.closeButton.setIcon(QIcon("./resource/icon_close_button.png"))
        self.closeButton.setToolTip("关闭/close")

    def init_events(self):
        self.closeButton.clicked.connect(self.onCloseButtonClicked)

    def onCloseButtonClicked(self):
        clipbox = self.toolsbar.clipbox
        hash_ = self.toolsbar.cardComboxProxy.currentData
        self.on_clipbox_closed.emit(ClipboxEvent(clipBox=clipbox, cardHash=hash_, eventType=0))
        # self.toolsbar.clipbox.pageview.pageview_clipbox_remove(self.toolsbar.clipbox)

    pass


class EditQAbutton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.IconDict = {
            "Q": QIcon("./resource/icon_question.png"),
            "A": QIcon("./resource/icon_answer.png")
        }
        self.toolTipDict = {
            "Q": "将文字保存到卡片问题字段\nrestore the text to the question field of the card",
            "A": "将文字保存到卡片答案字段\nrestore the text to the answer field of the card"
        }

        self.toolsbar = toolsbar
        self.editQAButton = QToolButton()
        self.init_UI()
        self.init_data()
        self.init_events()
        self.setWidget(self.editQAButton)

    def init_UI(self):
        self.editQAButton.setStyleSheet(f"margin-right:-1px;margin-left:-1px;margin-top: -1px;")

        pass

    def init_data(self):
        self.editQAButton.setText("Q")
        self.editQAButton.setIcon(self.IconDict["Q"])
        self.editQAButton.setToolTip("将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card")
        pass

    def init_events(self):
        self.editQAButton.clicked.connect(self.onEditQAButtonClicked)
        pass

    def onEditQAButtonClicked(self):
        if self.editQAButton.text() == "Q":
            self.editQAButton.setText("A")
            self.editQAButton.setIcon(self.IconDict["A"])
            self.editQAButton.setToolTip(self.toolTipDict["A"])

        else:
            self.editQAButton.setText("Q")
            self.editQAButton.setIcon(self.IconDict["Q"])
            self.editQAButton.setToolTip(self.toolTipDict["Q"])


class LineEdit(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar
        self.lineEdit = QLineEdit()
        self.init_UI()
        self.init_data()
        self.init_events()
        self.setWidget(self.lineEdit)

    def init_UI(self):
        pass

    def init_data(self):
        self.lineEdit.setToolTip("在此处编辑可给选框增加文字描述\nedit here to add a description to the clipbox")
        self.lineEdit.setPlaceholderText("edit here to add a description to the clipbox")

    def init_events(self):
        pass

    pass


class CardCombox(QGraphicsProxyWidget):
    """要做到保存选项,更新候选"""

    # on_cardlist_dataChanged = CustomSignals.start().on_cardlist_dataChanged
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar

        self.cardlistchanging = False

        self.currentData = None
        self.cardCombox = QComboBox()
        self.init_UI()
        self.init_data()
        self.init_signal()
        self.init_events()
        self.setWidget(self.cardCombox)

    def init_UI(self):

        pass

    def init_signal(self):
        self.on_cardlist_dataChanged = \
            self.toolsbar.cardlist.rightsidebar.clipper.objs.CustomSignals.start().on_cardlist_dataChanged
        self.on_clipbox_closed = \
            self.toolsbar.cardlist.rightsidebar.clipper.objs.CustomSignals.start().on_clipbox_closed
        self.on_clipboxCombox_updated = \
            self.toolsbar.cardlist.rightsidebar.clipper.objs.CustomSignals.start().on_clipboxCombox_updated

    def init_events(self):
        self.cardCombox.currentIndexChanged.connect(self.on_CardComboxIndexChanged_handle)
        self.on_cardlist_dataChanged.connect(self.on_cardlist_dataChanged_handle)

        pass

    def init_data(self):
        self.data_update()

        row = self.data_selectedRow()
        if len(row) > 0:
            self.data_setToCurrent(row[0].hash)
            self.currentData = row[0].hash
        self.cardCombox.setToolTip("选择一张卡片用来保存当前选框\nSelect a card to store the current clip box")
        pass

    def data_setToCurrent(self, _hash):
        idx = self.cardCombox.findData(_hash)
        if idx > -1:
            self.cardCombox.setCurrentIndex(idx)
            return True
        else:
            print("item deleted")
            return False

    def data_update(self):
        """清空,重新导入list的数据"""
        self.cardCombox.clear()
        model = self.toolsbar.cardlist.model
        for row in range(model.rowCount()):
            item = model.item(row, 0)
            t = item.text()
            self.cardCombox.addItem(t, userData=item.hash)
        if self.cardCombox.count() == 0 and not self.cardlistchanging:
            self.toolsbar.cardlist.on_addButton_clicked()  # 这里是不得不使用的功能,无法改写成订阅模式,因为需要顺序执行
            self.data_update()
        self.update()
        pass

    def data_selectedRow(self):
        model = self.toolsbar.cardlist.model
        listview = self.toolsbar.cardlist.listView
        row = [model.itemFromIndex(idx) for idx in listview.selectedIndexes()][0:2]
        return row

    def on_CardComboxIndexChanged_handle(self):
        if not self.cardlistchanging:
            newData = self.cardCombox.currentData()
            if self.currentData != newData:  # 不相等的时候,需要更新
                self.on_clipboxCombox_updated.emit(
                    ClipboxEvent(clipBox=self.toolsbar.clipbox, cardHash=newData, cardHash_old=self.currentData))
                self.currentData = newData
            print(f"ComboxIndexChanged ,now self.currentData = {self.currentData}")

        pass

    def on_cardlist_dataChanged_handle(self, event):
        """当cardlist变化时,先防止触发combox变化导致的信号,然后把combox的待选列表更新一遍
        更新完了,因为保存了之前的当前数据,所以可以重新设定回去.
        """
        self.cardlistchanging = True
        self.data_update()
        exsit = self.data_setToCurrent(self.currentData)
        if not exsit:
            self.on_clipbox_closed.emit(
                ClipboxEvent(clipBox=self.toolsbar.clipbox, cardHash=self.currentData, eventType=0))
            self.on_cardlist_dataChanged = None
        self.cardlistchanging = False

    pass
