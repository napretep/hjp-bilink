from PyQt5 import QtGui
from PyQt5.QtGui import QStandardItem, QPixmap, QIcon
from PyQt5.QtCore import Qt
import time

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QTextEdit, QToolButton, QVBoxLayout, QSpacerItem, QGridLayout, \
    QApplication
from aqt.utils import showInfo


def print_wrap():
    from ..ButtonPanel__ import funcs
    return funcs.logger(__name__)


print, printer = print_wrap()


class DescItem(QStandardItem):
    def __init__(self, itemName=None, selfData=None, toolTip=None, cardlist=None):
        super().__init__(itemName)
        self.cardlist = cardlist
        self.clipBoxList = []
        from .. import funcs
        self.uuid = funcs.uuidmake()  # 仅需要内存级别的唯一性
        self.role = "desc"
        # self.setFlags(self.flags()
        #               & ~ Qt.ItemIsDragEnabled)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)
        if toolTip is not None:
            self.setToolTip(toolTip)

    def __repr__(self):
        return f"""{super().__repr__()},clipboxlist={self.clipBoxList}"""


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
                      & ~ Qt.ItemIsEditable)
        if selfData is not None:
            self.setData(selfData, Qt.UserRole)
        if toolTip is not None:
            self.setToolTip(toolTip)

    def setText(self, text):
        super().setText(text)
        # print(f"carditem.setText modified = {text}")
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
        self.macro_state_label = QLabel(self)
        self.macro_step_lebel = QLabel(self)
        self.macro_QA_value_label = QLabel(self)
        self.QA_dict = {
            "Q": self.clipper.objs.SrcAdmin.imgDir.question,
            "A": self.clipper.objs.SrcAdmin.imgDir.answer
        }
        from .. import objs
        self.macro_state_dict = {
            objs.macro.stopState: "stop",
            objs.macro.runningState: "running",
            objs.macro.pauseState: "pause"
        }
        self.default_font_size = 40
        self.default_font_color = "white"
        self.default_background_color = "green"
        self.init_UI()
        self.show()

    def init_UI(self):
        self.setStyleSheet(f"background-color:{self.default_background_color};"
                           # f"font-size:{self.default_font_size};"
                           f"color:{self.default_font_color};")
        self.data_update()
        self.setMinimumWidth(300)
        g_layout = QGridLayout(self)
        posli = [
            (0, 0), (0, 1), (0, 2),
            (1, 1), (1, 2), (1, 3)
        ]
        widgetli = [
            self.QA_label, self.card_id_label, self.desc_label,
            self.macro_state_label, self.macro_step_lebel, self.macro_QA_value_label
        ]
        for i in range(len(widgetli)):
            g_layout.addWidget(widgetli[i], *posli[i])
        g_layout.setSpacing(20)
        self.setLayout(g_layout)
        self.setWindowFlags(Qt.CoverWindow | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.move(0, 0)
        pass

    def data_update(self):
        from .. import objs
        idxLi = self.cardlist.listView.selectedIndexes()
        if len(idxLi) > 0:
            row: "list[DescItem,CardItem]" = [self.cardlist.model.itemFromIndex(idx) for idx in idxLi[-2:]]
            self.desc_label.setText(f"desc:{row[0].text()}")
            self.card_id_label.setText(f"card_id:{row[1].text()}")
        else:
            self.desc_label.setText("desc:")
            self.card_id_label.setText("card_id:")
        QA = self.buttonPanel.QAbutton.text()
        self.QA_label.setPixmap(QPixmap(self.QA_dict[QA]).scaled(self.default_font_size, self.default_font_size))
        macro = objs.macro

        if macro.state == macro.runningState:
            self.macro_state_label.setText(f"macro_state:{self.macro_state_dict[macro.state]}")
            # print(f"macro_state_label:{self.macro_state_label.text()}")
            idx = macro.step % macro.len
            data = macro.macrodata[idx]
            self.macro_step_lebel.setText(f"macro_step:{idx + 1}")
            self.macro_QA_value_label.setText(f"QA:{data[0]},textQA:{data[1]}")
        else:
            self.macro_state_label.setText(f"macro_state:{self.macro_state_dict[macro.state]}")
            self.macro_step_lebel.setText(f"macro_step:")
            self.macro_QA_value_label.setText(f"QA: ,textQA: ")
            # print(f"macro_state_label:{self.macro_state_label.text()}")

        self.card_id_label.setStyleSheet(f"font-size:{self.default_font_size}px;")
        self.desc_label.setStyleSheet(f"font-size:{self.default_font_size}px;")
        self.macro_step_lebel.setStyleSheet(f"font-size:{self.default_font_size}px;")
        self.macro_state_label.setStyleSheet(f"font-size:{self.default_font_size}px;")
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
        self.__event = {
            self.correct_widget.clicked: self.on_correct_widget_clicked_handle
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()
        self.show()

    def init_UI(self):
        self.setModal(True)
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

    # def init_events(self):
    #     self.correct_widget.clicked.connect(self.on_correct_widget_clicked_handle)
    #     pass

    def on_correct_widget_clicked_handle(self):
        # print("on_correct_widget_clicked_handle")
        html = self.inputArea_widget.toPlainText()
        # showInfo(html)
        e = self.events.CardListAddCardEvent
        self.ALL.signals.on_cardlist_addCard.emit(
            e(sender=self, eventType=e.parseStrType, html=html)
        )
