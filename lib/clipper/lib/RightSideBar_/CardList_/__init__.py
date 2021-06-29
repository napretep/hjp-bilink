from PyQt5 import QtGui
from PyQt5.QtGui import QStandardItem, QPixmap, QIcon
from PyQt5.QtCore import Qt
import time


from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QTextEdit, QToolButton, QVBoxLayout, QSpacerItem, QGridLayout
from aqt.utils import showInfo


class DescItem(QStandardItem):
    def __init__(self, itemName=None, selfData=None, toolTip=None, cardlist=None):
        super().__init__(itemName)
        self.cardlist = cardlist
        self.clipBoxList = []
        from .. import funcs
        self.uuid = funcs.uuidmake()  # 仅需要内存级别的唯一性
        self.role = "desc"
        self.setFlags(self.flags()
                      & ~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)
        if toolTip is not None:
            self.setToolTip(toolTip)


# def wrapper_settext_update_emit(func):
#     def setText(*args,**kwargs):
#
#         result = func(*args, **kwargs)
#         e = events.CardListDataChangedEvent
#         ALL.signals.on_cardlist_dataChanged.emit(
#             e(eventType=e.TextChangeType,sender=args[0],data=args[1])
#         )
#         return result


class CardItem(QStandardItem):
    def __init__(self, itemName=None, selfData=None, toolTip=None, cardlist=None):
        super().__init__(itemName)
        from .. import events, ALL
        self.events = events
        self.ALL = ALL
        self.cardlist = cardlist
        self.clipBoxList = []
        self.role = "card_id"
        self.setFlags(self.flags()
                      & ~ Qt.ItemIsEditable
                      & ~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)
        if toolTip is not None:
            self.setToolTip(toolTip)

    def setText(self, text):
        super().setText(text)
        print(f"carditem.setText modified = {text}")
        e = self.events.CardListDataChangedEvent
        self.ALL.signals.on_cardlist_dataChanged.emit(
            e(eventType=e.TextChangeType, sender=self, data=text)
        )

class ClipboxState(QDialog):
    """漂浮状态窗,ctrl+tab就会显示出来"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.cardlist: "CardList" = parent
        self.buttonPanel = self.cardlist.rightsidebar.buttonPanel
        self.clipper = self.cardlist.rightsidebar.clipper
        self.desc_label = QLabel(self)
        self.card_id_label = QLabel(self)
        self.QA_label = QLabel(self)
        self.QA_dict = {
            "Q": self.clipper.objs.SrcAdmin.imgDir.question,
            "A": self.clipper.objs.SrcAdmin.imgDir.answer
        }
        self.default_size = 40
        self.init_UI()
        self.show()

    def init_UI(self):
        self.data_update()
        h_layout = QHBoxLayout(self)
        h_layout.addWidget(self.desc_label)
        h_layout.addWidget(self.card_id_label)
        h_layout.addWidget(self.QA_label)
        self.setLayout(h_layout)
        self.setWindowFlags(Qt.CoverWindow | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        pass

    def data_update(self):
        idxLi = self.cardlist.listView.selectedIndexes()
        if len(idxLi) > 0:
            row: "list[DescItem,CardItem]" = [self.cardlist.model.itemFromIndex(idx) for idx in idxLi[-2:]]
            self.desc_label.setText(row[0].text())
            self.card_id_label.setText(row[1].text())
        else:
            self.desc_label.setText("")
            self.card_id_label.setText("")
        QA = self.buttonPanel.QAbutton.text()
        self.QA_label.setPixmap(QPixmap(self.QA_dict[QA]).scaled(self.default_size, self.default_size))
        self.card_id_label.setStyleSheet(f"font-size:{self.default_size}px;")
        self.desc_label.setStyleSheet(f"font-size:{self.default_size}px;")
        pass


class CardPicker(QDialog):
    def __init__(self, cardlist=None):
        super().__init__(parent=cardlist)
        from .. import objs, funcs, events, ALL
        self.ALL = ALL
        self.objs = objs
        self.funcs = funcs
        self.events = events
        self.cardlist = cardlist
        self.inputArea_widget = QTextEdit(self)
        self.correct_widget = QToolButton(self)
        self.init_UI()
        self.init_events()
        self.show()

    def init_UI(self):
        from .. import objs
        self.setWindowTitle("card picker")
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.bag))
        self.inputArea_widget.setPlaceholderText("请粘贴卡片的文内链接\nplease paste the In-Text link of card")
        self.correct_widget.setIcon(QIcon(objs.SrcAdmin.imgDir.item_plus))
        self.correct_widget.setLayout(QVBoxLayout(self.correct_widget))
        g_layout = QGridLayout(self)
        g_layout.addWidget(self.inputArea_widget, 0, 0, 2, 1)
        g_layout.addWidget(self.correct_widget, 1, 1, alignment=Qt.AlignBottom)

        self.setLayout(g_layout)

        pass

    def init_events(self):
        self.correct_widget.clicked.connect(self.on_correct_widget_clicked_handle)
        pass

    def on_correct_widget_clicked_handle(self):
        # print("on_correct_widget_clicked_handle")
        html = self.inputArea_widget.toPlainText()
        # showInfo(html)
        e = self.events.CardListAddCardEvent
        self.ALL.signals.on_cardlist_addCard.emit(
            e(sender=self, eventType=e.parseStrType, html=html)
        )
