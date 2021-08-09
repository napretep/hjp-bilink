"""
progressbar
card importer
page clipbox info reader
card clipbox info reader
"""
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt, QPersistentModelIndex, QRect, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QTextEdit, QSpinBox, QListWidget, QFormLayout, QLabel, QListWidgetItem, QCheckBox, \
    QListView, QGridLayout, QTabWidget, QWidget, QToolButton, QVBoxLayout, QTabBar, QStylePainter, QStyleOptionTab, \
    QStyle, QHBoxLayout
import os

from aqt.utils import showInfo

from .Clipper import Clipper
from .tools import events, funcs, objs
from ..imports import common_tools


class ClipboxInfo(QDialog):
    def __init__(self, superior: "Clipper.ClipBox", root: "Clipper"):
        super().__init__(root)
        self.superior = superior
        self.root = root
        self.immu_data = self.superior.immutable_info_get()
        self.edit_data = self.Widgets(self, root)
        self.init_UI()

    def init_UI(self):
        self.setWindowTitle("clipbox information")
        self.setWindowIcon(QIcon(objs.SrcAdmin.imgDir.ID_card))
        g = QFormLayout(self)
        for k, v in self.immu_data.items():
            if k == "pdfname":
                x = QLabel(common_tools.funcs.str_shorten(os.path.basename(str(v))), parent=self)
            else:
                x = QLabel(str(v), parent=self)
            x.setWordWrap(True)
            g.addRow(k, x)
        for k, v in self.edit_data.w_li.items():
            g.addRow(k, v)
        self.setLayout(g)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.edit_data.save_data()

    def reject(self) -> None:
        self.edit_data.save_data()
        super().reject()

    class Widgets:
        def __init__(self, superior: "ClipboxInfo", root: "Clipper"):
            self.superior = superior
            self.root = root
            self.comment = QTextEdit(superior)
            self.comment_to_field = QSpinBox(superior)
            self.clip_to_field = QSpinBox(superior)
            self.card_list = QListWidget(superior)
            # self.model = QStandardItemModel()
            self.w_li = {"clip_to_field": self.clip_to_field, "comment_to_field": self.comment_to_field,
                         "card": self.card_list, "comment": self.comment}
            self.init_UI()
            self.load_data()

        def load_data(self):

            data: "Clipper.ClipBox.Data" = self.superior.superior.editableData
            self.comment.setPlainText(data.comment)
            self.comment_to_field.setValue(data.comment_to_field)
            self.clip_to_field.setValue(data.clip_to_field)
            for uuid in data.card_list:
                item: "Clipper.RightSideBar.CardList.DescItem" = self.root.E.rightsidebar.cardlist.dict[uuid]
                widget: "QCheckBox" = self.card_list.itemWidget(self.card_list.item(item.row()))
                widget.setChecked(True)

        def save_data(self):
            card_list = self.root.rightsidebar.cardlist
            clipuuid = self.superior.superior.uuid
            data: "Clipper.ClipBox.Data" = self.superior.superior.editableData
            data.comment = self.comment.toPlainText()
            data.comment_to_field = self.comment_to_field.value()
            data.clip_to_field = self.clip_to_field.value()
            for i in range(self.card_list.count()):
                widget: "QCheckBox" = self.card_list.itemWidget(self.card_list.item(i))
                item: "Clipper.RightSideBar.CardList.DescItem" = card_list.model.item(i, 0)
                if widget.isChecked():
                    self.root.clipbox_add_card(clipuuid, item.uuid)
                else:
                    self.root.clipbox_del_card(clipuuid, item.uuid)

        def init_UI(self):
            cardlist = self.root.rightsidebar.cardlist.model
            for row in range(cardlist.rowCount()):
                desc = cardlist.item(row, 0)
                card_id = cardlist.item(row, 1)
                box = QCheckBox(desc.text())
                item = QListWidgetItem()
                item.setToolTip(card_id.text())
                item.setData(Qt.UserRole, desc)
                self.card_list.addItem(item)
                self.card_list.setItemWidget(item, box)


class ClipperStateBoard(QDialog):
    def __init__(self, superior: "Clipper", root: "Clipper"):
        super().__init__(parent=superior)
        self.superior = superior
        self.clipper = root
        self.desc_label = QLabel(self)
        self.card_id_label = QLabel(self)
        self.QA_label = QLabel(self)
        self.macro_state_label = QLabel(self)
        self.macro_step_lebel = QLabel(self)
        self.macro_QA_value_label = QLabel(self)
        self.mainview_ratio_label = QLabel(self)
        self.QA_dict = {
            "Q": objs.SrcAdmin.imgDir.question,
            "A": objs.SrcAdmin.imgDir.answer
        }
        self.macro_state_dict = {
            objs.macro.stopState: "stop",
            objs.macro.runningState: "running",
            objs.macro.pauseState: "pause"
        }
        self.default_font_size = 40
        self.default_font_color = "white"
        self.default_background_color = "green"
        self.init_UI()
        self.init_data()
        # self.show()

    def init_UI(self):
        self.setStyleSheet(f"background-color:{self.default_background_color};"
                           # f"font-size:{self.default_font_size};"
                           f"color:{self.default_font_color};")
        # self.data_update()

        g_layout = QGridLayout(self)
        h_layout = QHBoxLayout(self)
        posli = [
            (0, 0), (0, 1), (0, 2), (0, 3),
            (1, 1), (1, 2), (1, 3)
        ]
        widgetli = [
            self.QA_label, self.card_id_label, self.desc_label, self.mainview_ratio_label,
            self.macro_state_label, self.macro_step_lebel, self.macro_QA_value_label
        ]
        for i in range(len(widgetli)):
            g_layout.addWidget(widgetli[i], *posli[i])
            # h_layout.addWidget(widgetli[i])
            widgetli[i].setStyleSheet(f"font-size:{self.default_font_size}px;color:white;")
        g_layout.setSpacing(20)
        g_layout.setColumnStretch(1, 1)

        # self.setLayout(h_layout)
        self.setLayout(g_layout)
        self.setWindowFlags(Qt.CoverWindow | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.move(0, 0)
        self.setMinimumWidth(500)
        # self.setFixedSize(500,100)
        pass

    def init_data(self):
        self.desc_label.setText("desc:")
        self.card_id_label.setText("card_id:")

    def data_update(self):
        idxLi = self.clipper.rightsidebar.cardlist.view.selectedIndexes()
        if len(idxLi) > 0:
            row = [self.clipper.rightsidebar.cardlist.model.itemFromIndex(idx) for idx in idxLi[-2:]]
            self.desc_label.setText(f"desc:{row[0].text()}")
            self.card_id_label.setText(f"card_id:{row[1].text()}")
        else:
            self.desc_label.setText("desc:")
            self.card_id_label.setText("card_id:")
        QA = self.clipper.rightsidebar.buttonPanel.widget_button_QA.text()
        self.QA_label.setPixmap(QPixmap(self.QA_dict[QA]).scaled(self.default_font_size, self.default_font_size))
        macro = objs.macro

        if macro.state in [macro.runningState, macro.pauseState]:
            self.macro_state_label.setText(f"macro_state:{self.macro_state_dict[macro.state]}")
            idx = macro.step % macro.len
            data = macro.macrodata[idx]
            self.macro_step_lebel.setText(f"macro_step:{idx + 1}")
            self.macro_QA_value_label.setText(f"QA:{data[0]},textQA:{data[1]}")
        else:
            self.macro_state_label.setText(f"macro_state:{self.macro_state_dict[macro.state]}")
            self.macro_step_lebel.setText(f"macro_step:")
            self.macro_QA_value_label.setText(f"QA: ,textQA: ")
        value = self.clipper.pdfview.reset_ratio_value
        self.mainview_ratio_label.setText(f"main_view_ratio:{value}")

        pass


class CardClipInfo(QDialog):
    pass
