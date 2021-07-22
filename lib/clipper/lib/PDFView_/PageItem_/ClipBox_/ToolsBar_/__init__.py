from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QLineEdit, QComboBox, QGraphicsProxyWidget
from .. import ALL, events, funcs, objs

print, printer = funcs.logger(__name__)

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
        self.__toolsbar = toolsbar
        self.__imgDir = objs.SrcAdmin.imgDir
        self.__IconDict = {
            "Q": QIcon(self.__imgDir.question),
            "A": QIcon(self.__imgDir.answer)
        }
        self.__toolTipDict = {
            "Q": "将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card",
            "A": "将选框保存到卡片答案字段\nrestore the clipbox to the answer field of the card"
        }
        self.__QAButton = QToolButton()
        self.__macro_QA = None
        self.__QA = QA
        self.__init_UI()
        self.__init_data()
        self.__event_dict = {
            self.__QAButton.clicked: self.__on_QAButton_clicked_handle
        }
        self.__all_event = objs.AllEventAdmin(self.__event_dict)
        self.__all_event.bind()
        self.setWidget(self.__QAButton)

    def __init_UI(self):
        self.__QAButton.setStyleSheet(f"margin-right:-1px;margin-left:-1px;margin-top: -1px;;")
        pass

    def __init_data(self):
        if objs.macro.state == objs.macro.runningState:
            self.__macro_QA = objs.macro.get("QA")
        self.__QAButton.setText(self.__QA)
        self.__update_sginal_emit()
        self.__QAButton.setIcon(self.__IconDict[self.__QA])
        self.__QAButton.setToolTip(self.__toolTipDict[self.__QA])
        if self.__toolsbar.clipbox_dict is not None:
            self.__QAButton.setText(str(self.__toolsbar.clipbox_dict["QA"]))

    def __on_QAButton_clicked_handle(self):
        if objs.macro.state == objs.macro.runningState:
            return
        if self.__QAButton.text() == "Q":
            self.__QAButton.setText("A")
            self.__QAButton.setIcon(self.__IconDict["A"])
            self.__QAButton.setToolTip(self.__toolTipDict["A"])
        else:
            self.__QAButton.setText("Q")
            self.__QAButton.setIcon(self.__IconDict["Q"])
            self.__QAButton.setToolTip(self.__toolTipDict["Q"])
        self.__macro_QA = None
        self.update()
        self.__update_sginal_emit()

    def __update_sginal_emit(self):
        e = events.ClipBoxToolsbarUpdateEvent
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.__toolsbar.clipbox.uuid, eventType=e.QAButtonType, data=self.__QAButton.text()))

    def return_data(self):
        return self.__QAButton.text() if self.__macro_QA is None else self.__macro_QA

    def set_data(self, value):
        self.__QAButton.setText(value)

    pass


class CloseButton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.__toolsbar = toolsbar
        self.__imgDir = objs.SrcAdmin.imgDir
        self.__closeButton = QToolButton()
        self.__init_UI()
        self.__init_data()
        self.event_dict = {
            self.__closeButton.clicked: self.__closeButton_clicked_handle
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
        # self.init_events()
        self.setWidget(self.__closeButton)

    def __init_UI(self):
        self.__closeButton.setStyleSheet(
            f"margin-left:-1px;margin-top: -1px;")
        pass

    def __init_data(self):
        self.__closeButton.setIcon(QIcon(self.__imgDir.close))
        self.__closeButton.setToolTip("关闭/close")

    def __closeButton_clicked_handle(self):
        clipbox = self.__toolsbar.clipbox
        uid = self.__toolsbar.cardComboxProxy.return_data()
        ALL.signals.on_clipbox_closed.emit(
            ClipboxEvent(clipBox=clipbox, cardUuid=uid, eventType=ClipboxEvent.closeType))

    pass


class EditQAbutton(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.__macro_QA = None
        self.__toolsbar = toolsbar
        self.__imgDir = objs.SrcAdmin.imgDir
        self.__IconDict = {
            "Q": QIcon(self.__imgDir.question),
            "A": QIcon(self.__imgDir.answer)
        }
        self.__toolTipDict = {
            "Q": "将文字保存到卡片问题字段\nrestore the text to the question field of the card",
            "A": "将文字保存到卡片答案字段\nrestore the text to the answer field of the card"
        }
        self.__editQAButton = QToolButton()
        self.__init_UI()
        self.__init_data()
        self.__event = {
            self.__editQAButton.clicked: self.__editQAButton_clicked_handle

        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()
        self.setWidget(self.__editQAButton)

    def __init_UI(self):
        self.__editQAButton.setStyleSheet(f"margin-right:-1px;margin-left:-1px;margin-top: -1px;")
        pass

    def __init_data(self):
        if objs.macro.state == objs.macro.runningState:
            self.__macro_QA = objs.macro.get("textQA")
        self.__editQAButton.setText("Q")
        self.__update_sginal_emit()
        self.__editQAButton.setIcon(self.__IconDict["Q"])
        self.__editQAButton.setToolTip("将选框保存到卡片问题字段\nrestore the clipbox to the question field of the card")
        if self.__toolsbar.clipbox_dict is not None:
            self.__editQAButton.setText(str(self.__toolsbar.clipbox_dict["textQA"]))
        pass

    def __update_sginal_emit(self):
        e = events.ClipBoxToolsbarUpdateEvent
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.__toolsbar.clipbox.uuid, eventType=e.TextQAButtonType, data=self.__editQAButton.text())
        )

    def __editQAButton_clicked_handle(self):
        if objs.macro.state == objs.macro.runningState:
            return
        if self.__editQAButton.text() == "Q":
            self.__editQAButton.setText("A")
            self.__editQAButton.setIcon(self.__IconDict["A"])
            self.__editQAButton.setToolTip(self.__toolTipDict["A"])

        else:
            self.__editQAButton.setText("Q")
            self.__editQAButton.setIcon(self.__IconDict["Q"])
            self.__editQAButton.setToolTip(self.__toolTipDict["Q"])
        self.__macro_QA = None
        self.__update_sginal_emit()

    def return_data(self):
        return self.__editQAButton.text() if self.__macro_QA is None else self.__macro_QA

    def set_data(self, value):
        self.__editQAButton.setText(value)

class LineEdit(QGraphicsProxyWidget):
    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.__toolsbar = toolsbar
        self.__lineEdit = QLineEdit()
        self.__init_UI()
        self.__init_data()
        self.__event = {
            self.__lineEdit.textChanged: self.__on_lineEdit_textChanged_handle
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()
        self.setWidget(self.__lineEdit)

    def __init_UI(self):

        pass

    def __init_data(self):
        self.__lineEdit.setToolTip("在此处编辑可给选框增加文字描述\nedit here to add a description to the clipbox")
        self.__lineEdit.setPlaceholderText("edit here to add a description to the clipbox")
        if self.__toolsbar.clipbox_dict is not None:
            self.__lineEdit.setText(self.__toolsbar.clipbox_dict["text_"])

    def __on_lineEdit_textChanged_handle(self, text):
        self.__update_sginal_emit(text)

    def __update_sginal_emit(self, text):
        e = events.ClipBoxToolsbarUpdateEvent
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.__toolsbar.clipbox.uuid, eventType=e.TextType, data=text)
        )

    def return_data(self):
        return self.__lineEdit.text()

    def set_data(self, value):
        self.__lineEdit.setText(value)

    pass


class CardCombox(QGraphicsProxyWidget):
    """要做到保存选项,更新候选"""
    # on_cardlist_dataChanged = CustomSignals.start().on_cardlist_dataChanged

    def __init__(self, toolsbar: 'ToolsBar'):
        super().__init__(parent=toolsbar)
        self.__toolsbar = toolsbar
        self.__cardlistchanging = False
        self.desc_item_uuid = None
        self.__cardCombox = QComboBox()
        self.__init_UI()
        self.__init_data()
        self.__event_dict = {
            self.__cardCombox.currentIndexChanged: self.__on_CardComboxIndexChanged_handle,
            ALL.signals.on_cardlist_dataChanged: self.__on_cardlist_dataChanged_handle
        }
        self.__all_event = objs.AllEventAdmin(self.__event_dict)
        self.__all_event.bind()
        self.setWidget(self.__cardCombox)
        self.__toolsbar.clipbox.card_id = self.__toolsbar.cardlist.cardUuidDict[self.desc_item_uuid][1].text()

    def __init_UI(self):

        pass

    def __init_data(self):
        self.__data_update()

        row = self.__data_selectedRow()

        if len(row) > 0:
            self.__data_setToCurrent(row[0].uuid)
            self.desc_item_uuid = row[0].uuid

        self.__cardCombox.setToolTip("选择一张卡片用来保存当前选框\nSelect a card to store the current clip box")
        if self.__toolsbar.clipbox_dict is not None:
            self.__data_setToCurrent(self.__toolsbar.clipbox_dict["card_uuid"])
        pass

    def __data_setToCurrent(self, itemUuid):
        """将combox指向给定的uuid所在的项"""
        idx = self.__cardCombox.findData(itemUuid)
        if idx > -1:
            self.__cardCombox.setCurrentIndex(idx)
            return True
        else:
            print("item deleted")
            return False

    def __data_update(self, model_delete=False):
        """清空combox,重新导入list的数据"""
        self.__cardCombox.clear()
        model = self.__toolsbar.cardlist.model
        for row in range(model.rowCount()):
            item = model.item(row, 0)
            t = item.text()
            self.__cardCombox.addItem(t, userData=item.uuid)
        # print("self.cardCombox.addItem(t, userData=item.uuid)")
        if self.__cardCombox.count() == 0 and not model_delete:  # 这一步是为了确保更新及时完成而设计, 但不包括删除的情况
            # while self.__cardlistchanging:
            #     pass
            self.__toolsbar.cardlist.rightsidebar.card_list_add(newcard=True)  # 这里是不得不使用的功能,无法改写成订阅模式,因为需要顺序执行
            self.__data_update()
        self.update()
        pass

    def __data_selectedRow(self):
        model = self.__toolsbar.cardlist.model
        listview = self.__toolsbar.cardlist.listView
        row = [model.itemFromIndex(idx) for idx in listview.selectedIndexes()][0:2]
        return row

    def __on_CardComboxIndexChanged_handle(self):
        if not self.__cardlistchanging:
            newData = self.__cardCombox.currentData()
            if self.desc_item_uuid != newData:  # 不相等的时候,需要更新
                ALL.signals.on_clipboxCombox_updated.emit(
                    ClipboxEvent(clipBox=self.__toolsbar.clipbox, cardUuid=newData, cardUuid_old=self.desc_item_uuid))
                self.desc_item_uuid = newData

            # print(f"ComboxIndexChanged ,now self.currentData = {self.desc_item_uuid}")

    def return_data(self):
        data = self.__cardCombox.currentData(Qt.UserRole)  # descitem的uuid
        return data

    def __on_cardlist_dataChanged_handle(self, event: 'events.CardListDataChangedEvent'):
        """当cardlist变化时,先防止触发combox变化导致的信号,然后把combox的待选列表更新一遍
        更新完了,因为保存了之前的当前数据,所以可以重新设定回去.
        """
        # if event.Type == event.DataChangeType:
        # print("__on_cardlist_dataChanged_handle")
        self.__cardlistchanging = True
        self.__data_update(model_delete=event.Type == event.deleteType)
        exsit = self.__data_setToCurrent(self.desc_item_uuid)

        if not exsit:  # 如果关联的卡片没了, 那自己也要关闭
            ALL.signals.on_clipbox_closed.emit(
                ClipboxEvent(clipBox=self.__toolsbar.clipbox, cardUuid=self.desc_item_uuid, eventType=0))
            self.on_cardlist_dataChanged = None
        self.__cardlistchanging = False

    def __update_sginal_emit(self, uuid):
        if uuid is None:
            return
        e = events.ClipBoxToolsbarUpdateEvent
        card_id = self.__toolsbar.cardlist.cardUuidDict[uuid][1].text()
        # print(f"card_id:{card_id}")
        ALL.signals.on_clipbox_toolsbar_update.emit(
            e(sender=self.__toolsbar.clipbox.uuid, eventType=e.Card_id_Type, data=card_id)
        )

    def __setattr__(self, key, value):
        if key == "desc_item_uuid" and value is not None:
            self.__update_sginal_emit(value)
        self.__dict__[key] = value

    pass
