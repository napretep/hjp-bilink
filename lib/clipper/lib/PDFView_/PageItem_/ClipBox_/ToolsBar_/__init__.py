from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QLineEdit, QComboBox, QGraphicsProxyWidget
from .. import ALL, events, funcs, objs


class ClipboxEvent:
    closeType = 0

    def __init__(self, clipBox=None, cardUuid=None, cardUuid_old=None, eventType=None):
        self.Type = eventType
        self.clipBox = clipBox
        self.cardUuid = cardUuid
        self.cardUuid_old = cardUuid_old


class QAButton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar' = None, QA="Q"):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar
        self.imgDir = objs.SrcAdmin.imgDir
        self.IconDict = {
            "Q": QIcon(self.imgDir.question),
            "A": QIcon(self.imgDir.answer)
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
        self.update_sginal_emit()
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
        self.update_sginal_emit()

    def update_sginal_emit(self):
        e = events.ClipBoxToolsbarUpdateEvent
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.toolsbar.clipbox.uuid, eventType=e.QAButtonType, data=self.QAButton.text()))

    pass


class CloseButton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar
        self.imgDir = objs.SrcAdmin.imgDir
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
        self.on_clipbox_closed = ALL.signals.on_clipbox_closed

    def init_data(self):
        self.closeButton.setIcon(QIcon(self.imgDir.close))
        self.closeButton.setToolTip("关闭/close")

    def init_events(self):
        self.closeButton.clicked.connect(self.onCloseButtonClicked)

    def onCloseButtonClicked(self):
        clipbox = self.toolsbar.clipbox
        uid = self.toolsbar.cardComboxProxy.desc_item_uuid
        self.on_clipbox_closed.emit(ClipboxEvent(clipBox=clipbox, cardUuid=uid, eventType=ClipboxEvent.closeType))

    pass


class EditQAbutton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar
        self.imgDir = objs.SrcAdmin.imgDir
        self.IconDict = {
            "Q": QIcon(self.imgDir.question),
            "A": QIcon(self.imgDir.answer)
        }
        self.toolTipDict = {
            "Q": "将文字保存到卡片问题字段\nrestore the text to the question field of the card",
            "A": "将文字保存到卡片答案字段\nrestore the text to the answer field of the card"
        }
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
        self.update_sginal_emit()
        self.editQAButton.setIcon(self.IconDict["Q"])
        self.editQAButton.setToolTip("将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card")
        pass

    def init_events(self):
        self.editQAButton.clicked.connect(self.onEditQAButtonClicked)
        pass

    def update_sginal_emit(self):
        e = events.ClipBoxToolsbarUpdateEvent
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.toolsbar.clipbox.uuid, eventType=e.TextQAButtonType, data=self.editQAButton.text())
        )

    def onEditQAButtonClicked(self):
        if self.editQAButton.text() == "Q":
            self.editQAButton.setText("A")
            self.editQAButton.setIcon(self.IconDict["A"])
            self.editQAButton.setToolTip(self.toolTipDict["A"])

        else:
            self.editQAButton.setText("Q")
            self.editQAButton.setIcon(self.IconDict["Q"])
            self.editQAButton.setToolTip(self.toolTipDict["Q"])
        self.update_sginal_emit()

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
        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged_handle)
        pass

    def on_lineEdit_textChanged_handle(self, text):
        self.update_sginal_emit(text)

    def update_sginal_emit(self, text):
        e = events.ClipBoxToolsbarUpdateEvent
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.toolsbar.clipbox.uuid, eventType=e.TextType, data=text)
        )

    pass


class CardCombox(QGraphicsProxyWidget):
    """要做到保存选项,更新候选"""

    # on_cardlist_dataChanged = CustomSignals.start().on_cardlist_dataChanged
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.toolsbar = toolsbar
        self.cardlistchanging = False
        self.desc_item_uuid = None
        self.cardCombox = QComboBox()
        self.init_UI()
        self.init_data()
        self.init_signal()
        self.init_events()
        self.setWidget(self.cardCombox)
        self.toolsbar.clipbox.card_id = self.toolsbar.cardlist.cardUuidDict[self.desc_item_uuid][1].text()

    def init_UI(self):

        pass

    def init_signal(self):
        self.on_cardlist_dataChanged = ALL.signals.on_cardlist_dataChanged
        self.on_clipbox_closed = ALL.signals.on_clipbox_closed
        self.on_clipboxCombox_updated = ALL.signals.on_clipboxCombox_updated

    def init_events(self):
        self.cardCombox.currentIndexChanged.connect(self.on_CardComboxIndexChanged_handle)
        self.on_cardlist_dataChanged.connect(self.on_cardlist_dataChanged_handle)

        pass

    def init_data(self):
        self.data_update()

        row = self.data_selectedRow()

        if len(row) > 0:
            self.data_setToCurrent(row[0].uuid)
            self.desc_item_uuid = row[0].uuid

        self.cardCombox.setToolTip("选择一张卡片用来保存当前选框\nSelect a card to store the current clip box")
        pass

    def data_setToCurrent(self, itemUuid):
        """将combox指向给定的uuid所在的项"""
        idx = self.cardCombox.findData(itemUuid)
        if idx > -1:
            self.cardCombox.setCurrentIndex(idx)
            return True
        else:
            print("item deleted")
            return False

    def data_update(self):
        """清空combox,重新导入list的数据"""
        self.cardCombox.clear()
        model = self.toolsbar.cardlist.model
        for row in range(model.rowCount()):
            item = model.item(row, 0)
            t = item.text()
            self.cardCombox.addItem(t, userData=item.uuid)
        print("self.cardCombox.addItem(t, userData=item.uuid)")
        if self.cardCombox.count() == 0:
            while self.cardlistchanging:
                pass
            self.toolsbar.cardlist.rightsidebar.card_list_add(newcard=True)  # 这里是不得不使用的功能,无法改写成订阅模式,因为需要顺序执行
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
            if self.desc_item_uuid != newData:  # 不相等的时候,需要更新
                self.on_clipboxCombox_updated.emit(
                    ClipboxEvent(clipBox=self.toolsbar.clipbox, cardUuid=newData, cardUuid_old=self.desc_item_uuid))
                self.desc_item_uuid = newData

            # print(f"ComboxIndexChanged ,now self.currentData = {self.desc_item_uuid}")

        pass

    def on_cardlist_dataChanged_handle(self, event: 'events.CardListDataChangedEvent'):
        """当cardlist变化时,先防止触发combox变化导致的信号,然后把combox的待选列表更新一遍
        更新完了,因为保存了之前的当前数据,所以可以重新设定回去.
        """
        if event.Type == event.DataChangeType:
            self.cardlistchanging = True
            self.data_update()
            exsit = self.data_setToCurrent(self.desc_item_uuid)
            if not exsit:  # 如果关联的卡片没了, 那自己也要关闭
                self.on_clipbox_closed.emit(
                    ClipboxEvent(clipBox=self.toolsbar.clipbox, cardUuid=self.desc_item_uuid, eventType=0))
                self.on_cardlist_dataChanged = None
            self.cardlistchanging = False

    def update_sginal_emit(self, uuid):
        if uuid is None:
            return
        e = events.ClipBoxToolsbarUpdateEvent
        card_id = self.toolsbar.cardlist.cardUuidDict[uuid][1].text()
        # print(f"card_id:{card_id}")
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.toolsbar.clipbox.uuid, eventType=e.Card_id_Type, data=card_id)
        )

    def __setattr__(self, key, value):
        if key == "desc_item_uuid" and value is not None:
            self.update_sginal_emit(value)
        self.__dict__[key] = value

    pass
