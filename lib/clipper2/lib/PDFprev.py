import dataclasses
import json
import os
import sys
import time
import typing

import uuid
from collections import namedtuple
from datetime import datetime
from math import ceil
from typing import Union
import tempfile
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QRectF, QPointF, QPoint, QRect, QLineF, QModelIndex, \
    QPersistentModelIndex, QThread, QSize
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QPen, QColor, QBrush, QPainterPathStroker, QPainterPath, \
    QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QDialog, QGraphicsSceneHoverEvent, QWidget, QGraphicsView, QVBoxLayout, QHBoxLayout, \
    QApplication, QGraphicsScene, \
    QGraphicsPixmapItem, QGraphicsRectItem, QCheckBox, QSlider, QLabel, QToolButton, QSpinBox, QStyleOptionGraphicsItem, \
    QGraphicsSceneMouseEvent, QMainWindow, QTreeView, QGridLayout, QScrollArea, QTextEdit, QComboBox, QTableView, \
    QStyledItemDelegate, QStyleOptionViewItem, QHeaderView, QListView, QProgressBar, QGraphicsProxyWidget, \
    QGraphicsSceneWheelEvent, QStyle

from aqt import mw

if __name__ == "__main__":
    # from lib.obj import tools, funcs, signals, events, all_objs, handles
    # from lib import clipper2
    from lib import common_tools
    from lib.clipper2.lib.fitz import fitz

    # from
else:
    from .fitz import fitz
    from . import tools
    # from ..obj import tools, funcs, signals, events, all_objs, handles
    # from ... import clipper2
    from ..imports import common_tools

    CardId = common_tools.funcs.Compatible.CardId()


# print, _ = tools.funcs.logger(__name__)


def get_uuid(pdfname: str, pagenum: int) -> str:
    return str(uuid.uuid3(uuid.NAMESPACE_URL, pdfname + str(pagenum)))


class PDFPrevDialog(QDialog):
    """
    leftside_bookmark
    bottom_toolsbar
    center_view
    """
    on_page_changed = pyqtSignal(object)
    on_page_added = pyqtSignal(object)
    on_clipbox_deleted = pyqtSignal(object)

    class API:
        def __init__(self, parent: "PDFPrevDialog" = None):
            self.pdfprevdialog = parent
            self.change_page = parent.change_page
            self.del_page = parent.del_page
            self.add_page = parent.add_page
            self.on_page_changed = parent.on_page_changed
            self.on_clipbox_deleted = parent.on_clipbox_deleted
            self.fit_in_width = parent.fit_in_width
            self.fit_in_height = parent.fit_in_height
            self.fit_in_disabled = parent.fit_in_disabled
            self.relayout = parent.relayout
            self.card_window_open = parent.card_window_open

        @property
        def curr_rightpagenum(self) -> int:
            return min(self.pagecount - 1, self.curr_pagenum + 1)

        @property
        def pagecount(self) -> int:
            return len(self.doc)

        @property
        def last_rightpagenum(self) -> int:
            return min(self.pagecount - 1, self.last_pagenum + 1)

        @property
        def last_pagenum(self) -> int:
            return self.pdfprevdialog.last_pagenum

        def last_pagenum_setValue(self, value):
            self.pdfprevdialog.last_pagenum = value

        @property
        def fit_in_policy(self):
            return self.pdfprevdialog.fit_in_policy

        @property
        def page_shift(self) -> int:
            return self.pdfprevdialog.pageshift

        @property
        def pdfname(self) -> str:
            return self.pdfprevdialog.pdfname

        @property
        def curr_pagenum(self) -> int:
            return self.pdfprevdialog.curr_pagenum

        @property
        def pdfuuid(self) -> str:
            return self.pdfprevdialog.pdfuuid

        @property
        def card_id(self) -> str:
            return self.pdfprevdialog.card_id

        @property
        def doc(self) -> "fitz.Document":
            return self.pdfprevdialog.doc

        @property
        def pageratio(self) -> float:
            return self.pdfprevdialog.pageratio

        def page_shift_set(self, value):
            self.pdfprevdialog.pageshift = value

        def curr_pagenum_set(self, value):
            self.pdfprevdialog.curr_pagenum = value

        def pdfuuid_set(self, value):
            self.pdfprevdialog.pdfuuid = value

        def card_id_set(self, value):
            self.pdfprevdialog.card_id = value

        def fit_in_policy_set(self, value):
            self.pdfprevdialog.fit_in_policy = value

        def pageratio_set(self, value):
            self.pdfprevdialog.pageratio = value

    fit_in_height = 0
    fit_in_width = 1
    fit_in_disabled = 2

    def __init__(self, cardwindow=None, pdfuuid=None, pdfname=None, pagenum=None, pageratio=None, card_id=None,
                 pageshift=None):
        super().__init__(parent=cardwindow)
        self.api = self.API(self)
        DB = common_tools.G.DB
        pdfinfo = DB.go(DB.table_pdfinfo).select(uuid=pdfuuid).return_all().zip_up().to_pdfinfo_data()[0]
        if pageshift is not None:
            self.pageshift = pageshift
        else:
            self.pageshift = pdfinfo.offset
        self.card_id = card_id
        self.pdfuuid = pdfuuid
        self.fit_in_policy = self.fit_in_disabled
        self.pdfname = pdfname
        self.pagenum = pagenum
        self.last_pagenum = int(pagenum)
        self.curr_pagenum = int(pagenum)
        self.doc = fitz.open(pdfname)
        self.pageratio = pageratio
        self.leftSide_bookmark = self.LeftSideBookmark(parent=self)
        self.bottom_toolsbar = self.BottomToolsBar(parent=self)
        self.center_view = self.CenterView(parent=self)
        self.widget_button_show = QToolButton(self)

        self.init_UI()
        self.init_show()
        self._event = {
            self.on_page_changed: self.on_page_changed_handle,
            self.widget_button_show.clicked: self.on_widget_button_show_clicked
        }
        self.all_event = common_tools.objs.AllEventAdmin(self._event).bind()

    def on_widget_button_show_clicked(self):
        self.widget_button_show.hide()
        self.bottom_toolsbar.show()

    def on_page_changed_handle(self, event: "PDFPrevDialog.PageChangedEvent"):
        self.center_view.api.hideclipbox()
        self.last_pagenum = self.curr_pagenum
        self.curr_pagenum = event.data
        self.change_page(event.data)
        self.center_view.api.showclipbox()

    def card_window_open(self, card_id):
        card = mw.col.getCard(CardId(int(card_id)))
        if not __name__ == "__main__":
            common_tools.funcs.Dialogs.open_custom_cardwindow(card)

    def init_UI(self):
        self.setWindowIcon(QIcon(tools.objs.SrcAdmin.imgDir.read))
        self.setWindowTitle(f"PDF previewer, belong to card={self.card_id}")
        self.setWindowModality(Qt.NonModal)
        self.setModal(False)
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)

        G_Layout = QGridLayout(self)
        # G_Layout.addWidget(self.leftSide_bookmark,0,0,2,1)
        G_Layout.addWidget(self.center_view, 0, 1)
        G_Layout.addWidget(self.bottom_toolsbar, 1, 1)
        # G_Layout.addWidget(self.widget_button_show,0,1)
        G_Layout.setContentsMargins(0, 0, 0, 0)
        G_Layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(G_Layout)
        self.widget_button_show.resize(100, 15)
        self.widget_button_show.setIcon(QIcon(tools.objs.SrcAdmin.imgDir.top_direction))
        self.widget_button_show.hide()

    def init_show(self):

        self.leftSide_bookmark.api.init_data()
        self.add_page()

    def change_page(self, pagenum):
        """用来换页,和底层的不同的是他同时换两页"""

        self.center_view.api.leftpage.api.change_page(pagenum)

        if self.center_view.api.rightpage:
            self.center_view.api.rightpage.api.change_page(pagenum + 1)
        pass

    def del_page(self):
        self.center_view.api.delpage()

    def add_page(self):
        self.center_view.api.addpage()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        # 保存 pageshift ratio
        DB = tools.objs.SrcAdmin.DB
        DB.go(DB.table_pdfinfo).update(values=DB.VALUEEQ(ratio=self.pageratio, offset=self.pageshift),
                                       where=DB.EQ(uuid=self.pdfuuid)).commit()
        pdf_path = DB.select(uuid=self.pdfuuid).return_all().zip_up()[0].to_pdfinfo_data().pdf_path
        pdfpageuuid = tools.funcs.uuid_hash_make(pdf_path + str(self.pagenum))
        if not __name__ == "__main__":
            common_tools.G.mw_pdf_prev[str(self.card_id)][pdfpageuuid] = None

        # print(f"closed, {all_objs.mw_pdf_prev}")

    def relayout(self):
        if self.leftSide_bookmark.isVisible():
            self.move(self.leftSide_bookmark.x() + self.leftSide_bookmark.width(), self.leftSide_bookmark.y())

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        w = int(self.geometry().width() / 2 - self.widget_button_show.geometry().width() / 2)
        h = self.geometry().height() - 15
        self.widget_button_show.move(w, h)
        # self.widget_button_show.move(int(self.size().width() / 2), self.size().height())

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
        self.leftSide_bookmark.api.relayout()

    class RightSideBakclink(QDialog):

        def __init__(self, parent: "PDFPrevDialog.BottomToolsBar", superior: "PDFPrevDialog", pagenum=None):
            super().__init__(parent)
            self.superior = superior
            self.fromToolsBar = parent
            self.view = QTreeView(self)
            self.h_layout = QHBoxLayout(self)
            self.model = QStandardItemModel()
            self.view.setModel(self.model)
            self.init_UI()
            self.all_event = tools.objs.AllEventAdmin({
                self.view.doubleClicked: self.on_view_doubleclicked_handle
            }).bind()

        def on_view_doubleclicked_handle(self, index: "QModelIndex"):
            card_id = self.model.index(index.row(), 0).data(role=Qt.DisplayRole)
            self.superior.api.card_window_open(card_id)
            self.close()

        def init_UI(self):

            self.h_layout.addWidget(self.view)
            self.setLayout(self.h_layout)
            self.init_data()
            self.view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.view.resizeColumnToContents(0)
            self.view.resizeColumnToContents(1)
            self.model.setHorizontalHeaderLabels(["card_id", "desc"])
            self.resize(self.view.columnWidth(0) + self.view.columnWidth(1) + 40, self.superior.height())
            self.view.setItemDelegate(self.Delegate(self))
            self.view.expandAll()

        def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
            self.fromToolsBar.state.backlinkwindow = None

        def reject(self) -> None:
            self.close()

        def init_data(self):
            pdfuuid = str(self.superior.api.pdfuuid)
            page = str(self.superior.api.curr_pagenum)
            DB = tools.objs.SrcAdmin.DB
            result = DB.go(DB.table_clipbox).select(pdfuuid=pdfuuid, pagenum=page).return_all(
                callback=None).zip_up().to_clipbox_data()
            self.setWindowTitle(f"current PDFpage at:{page},referenced by these cards ")
            all_card_li: "set[str]" = set()
            for record in result:
                card_li: "list[str]" = record.card_id.split(",")
                for card in card_li:
                    if card.isdecimal():
                        all_card_li.add(card)
            Item = PDFPrevDialog.RightSideBakclink.Item
            for card_id in list(all_card_li):
                card = Item(self, Item.type.card, card_id)
                desc = Item(self, Item.type.desc, common_tools.funcs.desc_extract(card_id))
                self.model.appendRow([card, desc])
                card_info = tools.funcs.card__pdf_page_clipbox_info__collect(card_id)
                for pdfuuid, pagenum_clip in card_info.items():
                    pdf = Item(self, Item.type.pdfuuid, pdfuuid)
                    card.appendRow([pdf])
                    for pagenum, clipli in pagenum_clip.items():
                        page = Item(self, Item.type.pagenum, str(pagenum))
                        pdf.appendRow([page])
                        for clipuuid in clipli:
                            clip = Item(self, Item.type.clipuuid, clipuuid)
                            page.appendRow([clip])

        class Item(QStandardItem):
            type = namedtuple("type", "card desc pdfuuid pagenum clipuuid")("0", "1", "00", "000", "0000")

            def __init__(self, superior: "PDFPrevDialog.RightSideBakclink", role, s):
                super().__init__(s)
                self.setData(role, role=Qt.UserRole)
                self.superior = superior
                self.setFlags(self.flags() & ~Qt.ItemIsEditable)

        class Delegate(QStyledItemDelegate):
            myRole = 999

            def __init__(self, superior: "PDFPrevDialog.RightSideBakclink", *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.superior = superior

            def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
                item = self.superior.Item
                painter.save()
                DB = tools.objs.SrcAdmin.DB

                if index.data(Qt.UserRole) == item.type.pdfuuid:
                    pdfuuid = index.data(Qt.DisplayRole)
                    pdfinfo = DB.go(DB.table_pdfinfo).select(uuid=pdfuuid).return_all().zip_up().to_pdfinfo_data()[0]

                    pdfname = tools.funcs.str_shorten(os.path.basename(pdfinfo.pdf_path))
                    painter.drawText(option.rect, Qt.AlignLeft, pdfname)
                    pass
                elif index.data(Qt.UserRole) == item.type.pagenum:
                    pdfuuid = index.parent().data(Qt.DisplayRole)
                    pdfinfo = DB.go(DB.table_pdfinfo).select(uuid=pdfuuid).return_all().zip_up().to_pdfinfo_data()[0]
                    pagenum = int(index.data(Qt.DisplayRole))
                    final_text = f"""PDF page at:{pagenum}  book page at:{pagenum - pdfinfo.offset + 1}  """
                    painter.drawText(option.rect, Qt.AlignLeft, final_text)
                    pass
                elif index.data(Qt.UserRole) == item.type.clipuuid:

                    clipuuid = index.data(Qt.DisplayRole)
                    clip = DB.go(DB.table_clipbox).select(uuid=clipuuid).return_all().zip_up().to_clipbox_data()[0]
                    pdfinfo = DB.go(DB.table_pdfinfo).select(uuid=clip.pdfuuid).return_all().zip_up().to_pdfinfo_data()[
                        0]
                    pixmap_ = tools.funcs.png_pdf_clip(pdfinfo.pdf_path, clip.pagenum, rect1=clip.__dict__,
                                                       ratio=clip.ratio)
                    pixmap = tools.funcs.Qpixmap_from_fitzpixmap(pixmap_).scaledToWidth(300)
                    rect = QRect(option.rect.x(), option.rect.y(), pixmap.size().width(), pixmap.size().height())
                    painter.drawPixmap(rect, pixmap)
                    # if option.state & QStyle.State_Selected:
                    #     painter.setPen(QPen(QColor("#e3e3e5")))
                    #     painter.setBrush(QColor("#e3e3e5"))
                    #     painter.drawText(rect, Qt.AlignLeft, "✅")
                    index.model().setData(index, [pixmap.size().width(), pixmap.size().height()], role=self.myRole)
                    pass
                else:
                    super().paint(painter, option, index)

            def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
                item = self.superior.Item
                if index.data(Qt.UserRole) == item.type.clipuuid:
                    if index.data(self.myRole):
                        t = self.superior.view.indentation()
                        w, h = index.data(self.myRole)
                        s = self.superior.size()

                        self.superior.resize(max(7 * t + w + 150, s.width()), s.height())
                        return QSize(w + 3, h + 3)
                    else:
                        return super().sizeHint(option, index)
                else:
                    return super().sizeHint(option, index)

        pass

    class AllEvent(QObject):
        def __init__(self, eventType=None, sender=None):
            super().__init__()
            self.Type = eventType
            self.sender = sender

    class PageChangedEvent(AllEvent):
        WheelType = 0
        SliderType = 1
        BookmarkType = 2
        PageAtType = 3

        def __init__(self, eventType=None, sender=None, data=None):
            super().__init__(eventType, sender)
            self.data = data

    class ClipboxDeleteEvent(AllEvent):
        def __init__(self, eventType=None, sender=None, data=None, pagenum=None):
            super().__init__(eventType, sender)
            self.data = data
            self.pagenum = pagenum

    class LeftSideBookmark(QDialog):
        class BookMarkItem(QStandardItem):
            def __init__(self, name=None, pagenum=None, level=1):
                super().__init__(name)
                self.pagenum = pagenum
                self.level = level
                self.setToolTip(name)
                self.setFlags(self.flags() & ~Qt.ItemIsEditable)

            pass

        class API(QObject):
            def __init__(self, father: "PDFPrevDialog.LeftSideBookmark"):
                super().__init__()
                self.father = father
                self.load_bookmark = self.father.load_bookmark
                self.init_data = self.father.init_data
                self.relayout = self.father.relayout

        def __init__(self, parent: "PDFPrevDialog" = None):
            super().__init__(parent)
            self.pdfprevdialog = parent
            self.view = QTreeView(self)
            self.init_UI()
            self.init_model()
            self.event_dict = {
                self.view.clicked: (self.on_self_clicked_handle)
            }
            self.all_event = tools.objs.AllEventAdmin(self.event_dict)
            self.all_event.bind()
            self.hide()
            self.api = self.API(self)

        def init_UI(self):
            self.setMinimumWidth(150)
            self.setWindowIcon(QIcon(tools.objs.SrcAdmin.imgDir.bookmark))
            self.setWindowTitle("bookmark")
            self.view.setIndentation(10)
            V_layout = QVBoxLayout(self)
            V_layout.addWidget(self.view)
            self.setLayout(V_layout)
            pass

        def init_model(self):
            self.model = QStandardItemModel()
            self.view.setModel(self.model)
            self.root = self.model.invisibleRootItem()
            self.root.level = 0
            self.model.setHorizontalHeaderLabels(["toc"])

        def on_self_clicked_handle(self, index):
            item = self.model.itemFromIndex(index)
            e = self.pdfprevdialog.PageChangedEvent
            self.pdfprevdialog.api.on_page_changed.emit(e(sender=self, eventType=e.BookmarkType, data=item.pagenum))

        def setup_toc(self, toc: 'list[list[int,str,int]]'):
            self.model.clear()
            self.model.setHorizontalHeaderLabels(["table of contents"])
            last = self.BookMarkItem(name="virtual item")
            lastparent = self.root
            for i in toc:
                level, name, pagenum = i[0], i[1], i[2] + self.doc_shift
                item = self.BookMarkItem(name=name, level=level, pagenum=pagenum)
                if self.model.rowCount() == 0:  # 为空时添加第一个元素
                    self.model.appendRow(item)
                else:
                    if level > 1:  # 层级大于1才在这里
                        if last.level == level:  # 同级就可以加到父辈
                            lastparent.appendRow(item)
                        elif last.level > level:  # 前面的等级高,后面的等级低说明开了一个新上级,需要找到与他相同级的父级插入.
                            templast = last
                            while templast.level >= level and templast.parent() is not None:  # 找到比他小的那一级
                                templast = templast.parent()
                            templast.appendRow(item)
                        elif last.level < level:
                            last.appendRow(item)

                    else:  #
                        self.model.appendRow(item)
                last = item
                lastparent = item.parent() if item.parent() is not None else self.root

        def init_data(self):
            doc = self.pdfprevdialog.api.doc
            self.load_bookmark(doc)
            self.relayout()

        def relayout(self):
            # print(f"self.pos={self.pos()}")
            self.move(self.pdfprevdialog.x() - self.width(), self.pdfprevdialog.y())
            self.resize(self.width(), self.pdfprevdialog.height())

        def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
            self.pdfprevdialog.api.relayout()

        def load_bookmark(self, doc: "fitz.Document"):
            # print("load_bookmark")
            self.doc_shift = -1 if doc.xref_xml_metadata() != 0 else 0
            self.toc = doc.get_toc()
            self.setup_toc(self.toc)

        pass

    class BottomToolsBar(QWidget):
        class PageSlider(QSlider):
            def __init__(self, *args, parent=None):
                super().__init__(*args, parent=parent)
                self.bottomtoolsbar = parent

            # def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
            #     self.bottomtoolsbar.pdfprevdialog.on_page_changed.emit(self.value())

        class API(QObject):
            def __init__(self, parent: "PDFPrevDialog.BottomToolsBar" = None):
                super().__init__(parent)
                self.bottomtoolsbar = parent
                self.label_pagenum_setText = self.bottomtoolsbar.widget_label_pagenum_setText
                self.slider_page_setValue = self.bottomtoolsbar.widget_slider_page_setValue
                self.page_at_setValue = self.bottomtoolsbar.widget_spinbox_page_at_setValue
                self.pageshift_setValue = self.bottomtoolsbar.widget_spinbox_pageshift_setValue
                self.pagenum_kind_blocksignal = parent.pagenum_kind_blocksignal

            @property
            def label_pagenum_text(self):
                return self.bottomtoolsbar.widget_label_pagenum.text()

            @property
            def slider_page_value(self):
                return self.bottomtoolsbar.widget_slider_page.value()

            @property
            def pageshift_value(self):
                return self.bottomtoolsbar.widget_spinbox_pageshift.value()

            @property
            def page_at_value(self):
                return self.bottomtoolsbar.widget_spinbox_page_at.value()

        def __init__(self, parent: "PDFPrevDialog" = None):
            super().__init__(parent)
            self.icon_fit_width = QIcon(tools.objs.SrcAdmin.imgDir.fit_in_width)
            self.icon_fit_height = QIcon(tools.objs.SrcAdmin.imgDir.fit_in_height)
            self.icon_single_page = QIcon(tools.objs.SrcAdmin.imgDir.singlepage)
            self.icon_double_page = QIcon(tools.objs.SrcAdmin.imgDir.doublepage)
            self.icon_bookmark = QIcon(tools.objs.SrcAdmin.imgDir.bookmark)
            self.icon_correct = QIcon(tools.objs.SrcAdmin.imgDir.correct)
            self.pdfprevdialog = parent
            self.state = self.State()
            self.widget_spinbox_pageshift = QSpinBox(self)
            self.widget_spinbox_page_at = QSpinBox(self)
            self.widget_pageshift = tools.objs.GridHDescUnit(
                parent=self, labelname="pageshift", widget=self.widget_spinbox_pageshift)
            self.widget_page_at = tools.objs.GridHDescUnit(
                parent=self, labelname="jump to book page", widget=self.widget_spinbox_page_at)
            self.widget_button_bookmark = QToolButton(self)
            self.widget_button_double_page = QToolButton(self)
            self.widget_button_correct = QToolButton(self)
            self.widget_button_backlink = QToolButton(self)
            self.widget_button_fit_width = QToolButton(self)
            self.widget_button_fit_height = QToolButton(self)
            self.widget_button_hide = QToolButton(self)

            self.widget_label_pagenum = QLabel(self)
            self.widget_slider_page = self.PageSlider(Qt.Horizontal, parent=self)
            self.api = self.API(parent=self)
            self._event = {
                self.widget_button_backlink.clicked: self.on_widget_button_backlink_clicked_handle,
                self.widget_button_fit_width.clicked: self.on_widget_button_fit_width_clicked_handle,
                self.widget_button_fit_height.clicked: self.on_widget_button_fit_height_clicked_handle,
                self.widget_slider_page.valueChanged: self.on_widget_slider_page_valueChanged_handle,
                self.widget_button_double_page.clicked: self.on_widget_button_double_page_clicked_handle,
                self.widget_button_bookmark.clicked: self.on_widget_button_bookmark_clicked_handle,
                self.widget_button_correct.clicked: self.on_widget_button_correct_clicked_handle,
                self.widget_spinbox_pageshift.valueChanged: self.on_widget_spinbox_pageshift_valueChanged_handle,
                self.widget_spinbox_page_at.valueChanged: self.on_widget_spinbox_page_at_valueChanged_handle,
                self.widget_button_hide.clicked: self.on_widget_button_hide_clicked_handle,
                self.pdfprevdialog.on_page_changed: self.on_pdfprevdialog_page_changed,
            }
            self.all_event = tools.objs.AllEventAdmin(self._event)
            self.all_event.bind()
            self.init_UI()

        def on_widget_button_backlink_clicked_handle(self):
            if self.state.backlinkwindow is None:
                self.state.backlinkwindow = PDFPrevDialog.RightSideBakclink(self, self.pdfprevdialog)
                self.state.backlinkwindow.show()
            else:
                self.state.backlinkwindow.activateWindow()

        def on_widget_button_correct_clicked_handle(self):
            data = self.pdfprevdialog.center_view.api.flatClipbox()
            p = self.pdfprevdialog.CorrectionDialog(parent=self.pdfprevdialog, data=data)
            p.show()

        def on_widget_spinbox_pageshift_valueChanged_handle(self, value):
            self.pdfprevdialog.api.page_shift_set(value)
            # self.api.page_at_setValue(self.api.slider_page_value)
            self.init_page_at()

        def on_widget_spinbox_page_at_valueChanged_handle(self, value):
            pagenum = self.widget_spinbox_pageshift.value() + value - 1  # 从1开始计数
            e = self.pdfprevdialog.PageChangedEvent
            self.pdfprevdialog.api.on_page_changed.emit(e(eventType=e.PageAtType, data=pagenum))

        def on_widget_button_fit_height_clicked_handle(self):
            self.pdfprevdialog.api.fit_in_policy_set(self.pdfprevdialog.api.fit_in_height)
            self.pdfprevdialog.center_view.api.fit_in()

        def on_widget_button_fit_width_clicked_handle(self):
            self.pdfprevdialog.api.fit_in_policy_set(self.pdfprevdialog.api.fit_in_width)
            self.pdfprevdialog.center_view.api.fit_in()
            pass

        def on_widget_button_double_page_clicked_handle(self):
            if self.widget_button_double_page.text() == "1":
                self.widget_button_double_page.setText("2")
                self.widget_button_double_page.setIcon(self.icon_double_page)
                self.widget_button_double_page.setToolTip("display double page")
                self.pdfprevdialog.api.add_page()
            else:
                self.widget_button_double_page.setText("1")
                self.widget_button_double_page.setIcon(self.icon_single_page)
                self.widget_button_double_page.setToolTip("display single page")
                self.pdfprevdialog.api.del_page()

        def on_widget_slider_page_valueChanged_handle(self, value):
            e = self.pdfprevdialog.PageChangedEvent
            e = e(eventType=e.SliderType, data=value)
            self.pdfprevdialog.api.on_page_changed.emit(e)

        def on_widget_button_bookmark_clicked_handle(self):
            # print("on_widget_button_bookmark_clicked_handle")
            bookmark = self.pdfprevdialog.leftSide_bookmark
            if not bookmark.isVisible():
                bookmark.show()
                bookmark.api.relayout()
            else:
                bookmark.hide()

        def on_pdfprevdialog_page_changed(self, event: "PDFPrevDialog.PageChangedEvent"):
            self.api.pagenum_kind_blocksignal(True)
            self.api.page_at_setValue(event.data)
            self.api.slider_page_setValue(event.data)
            self.api.label_pagenum_setText(event.data)
            self.api.pagenum_kind_blocksignal(False)

        def pagenum_kind_blocksignal(self, T_or_F):
            self.widget_spinbox_page_at.blockSignals(T_or_F)
            self.widget_slider_page.blockSignals(T_or_F)

        def widget_spinbox_page_at_setValue(self, value):
            """这是给内部调用的时候用的,内部统一使用pdf作为页码,所以value的值=pdfpagenum,但是page_at展示的值是bookpagenum,所以要减去"""
            pagenum = value - self.widget_spinbox_pageshift.value() + 1
            self.widget_spinbox_page_at.setValue(pagenum)

        def widget_spinbox_pageshift_setValue(self, value):
            self.widget_spinbox_pageshift.setValue(value)

        def widget_slider_page_setValue(self, value):
            self.widget_slider_page.setValue(value)
            self.pdfprevdialog.api.curr_pagenum_set(value)

        def widget_label_pagenum_setText(self, value1):
            self.widget_label_pagenum.setText(f"pdf page at {value1}")
            self.pdfprevdialog.api.curr_pagenum_set(value1)

        def init_UI(self):
            self.init_hide()
            self.init_page_slider()
            self.init_label_pagenum()
            self.init_correct()
            self.init_double_side_switch()
            self.init_pageshift()
            self.init_page_at()
            self.init_fit_width_height()
            self.init_bookmark()
            self.init_backlink()
            V_layout = QVBoxLayout(self)
            V_layout.addWidget(self.widget_slider_page)
            w_li = [self.widget_pageshift, self.widget_page_at, self.widget_label_pagenum, self.widget_button_hide,
                    self.widget_button_backlink, self.widget_button_bookmark, self.widget_button_double_page,
                    self.widget_button_fit_width, self.widget_button_fit_height, self.widget_button_correct]

            H_layout = QHBoxLayout(self)
            for w in w_li:
                H_layout.addWidget(w)
            H_layout.setAlignment(Qt.AlignRight)
            V_layout.addLayout(H_layout)

            self.setLayout(V_layout)

        def init_hide(self):
            self.widget_button_hide.setIcon(QIcon(tools.objs.SrcAdmin.imgDir.bottom_direction))

        def init_backlink(self):
            self.widget_button_backlink.setIcon(QIcon(tools.objs.SrcAdmin.imgDir.link2))

        def init_correct(self):
            self.widget_button_correct.setIcon(self.icon_correct)

        def init_bookmark(self):
            self.widget_button_bookmark.setIcon(self.icon_bookmark)

        def init_pageshift(self):
            self.widget_spinbox_pageshift.setMaximumWidth(50)
            self.widget_spinbox_pageshift.setValue(self.pdfprevdialog.api.page_shift)

        def init_page_at(self):
            self.widget_spinbox_page_at.setMaximumWidth(50)
            self.widget_spinbox_page_at.setValue(self.pdfprevdialog.api.curr_pagenum + 1 - self.api.pageshift_value)
            self.widget_spinbox_page_at.setRange(-self.api.pageshift_value,
                                                 self.pdfprevdialog.api.pagecount - self.api.pageshift_value)

        def on_widget_button_hide_clicked_handle(self):
            self.hide()
            self.pdfprevdialog.widget_button_show.show()

        def init_fit_width_height(self):
            self.widget_button_fit_width.setIcon(self.icon_fit_width)
            self.widget_button_fit_width.setText("fit in width")
            self.widget_button_fit_height.setIcon(self.icon_fit_height)
            self.widget_button_fit_height.setText("fit in height")

        def init_double_side_switch(self):
            self.widget_button_double_page.setIcon(QIcon(tools.objs.SrcAdmin.imgDir.singlepage))
            self.widget_button_double_page.setText("1")
            self.widget_button_double_page.setToolTip("display single page")

        def init_label_pagenum(self):
            self.widget_label_pagenum.setText(f"pdf page at {self.pdfprevdialog.api.curr_pagenum}")

        def init_page_slider(self):
            pagecount = len(self.pdfprevdialog.doc)
            self.widget_slider_page.setFixedWidth(self.pdfprevdialog.size().width() - 40)
            self.widget_slider_page.setRange(0, pagecount - 1)
            self.widget_slider_page.setSingleStep(1)
            self.widget_slider_page.setValue(self.pdfprevdialog.api.curr_pagenum)
            # self.page_slider.setLayoutDirection(Qt.Horizontal)

        def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
            self.widget_slider_page.setFixedWidth(self.pdfprevdialog.size().width() - 40)
            super().resizeEvent(a0)

        @dataclasses.dataclass
        class State:
            backlinkwindow: "PDFPrevDialog.RightSideBakclink" = None

        pass

    class CenterView(QWidget):

        class View(QGraphicsView):
            class API(QObject):
                def __init__(self, parent: "PDFPrevDialog.CenterView.View"):
                    super().__init__(parent)
                    self.view = parent

                @property
                def mouse_pos(self) -> QPoint:
                    return self.view.mouse_pos

            def __init__(self, parent: "PDFPrevDialog.CenterView" = None):
                super().__init__(parent)
                self.centerview = parent
                self.api = self.API(self)
                self.mouse_pos: "QPoint" = None
                self._event = {
                    self.rubberBandChanged: self.on_rubberBandChanged_handle,
                }
                self.all_event = tools.objs.AllEventAdmin(self._event)
                self.all_event.bind()
                self.curr_rubberBand_rect = None
                # self.setDragMode()

            def on_rubberBandChanged_handle(self, viewportRect, fromScenePoint, toScenePoint):
                if viewportRect:  # 空的rect不要
                    self.curr_rubberBand_rect = viewportRect

            # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
            #     # print(f"""selfrect={self.rect()},scenerect={self.sceneRect()},size()={self.size()}
            #     # georect={self.geometry()}""")
            #     super().mousePressEvent(event)

            # def rubberBandRect(self) -> QtCore.QRect:

            def resizeEvent(self, event: QtGui.QResizeEvent) -> None:

                # print(f"""selfrect={self.rect()},scenerect={self.sceneRect()},size()={self.size()}
                #                 georect={self.geometry()}""")

                super().resizeEvent(event)

            def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
                if event.modifiers() == Qt.ControlModifier:
                    self.mouse_pos = event.pos()
                    super().wheelEvent(event)
                else:
                    currpage = self.centerview.pdfprevdialog.api.curr_pagenum
                    e = PDFPrevDialog.PageChangedEvent
                    e = e(eventType=e.WheelType)
                    if event.angleDelta().y() > 0:
                        e.data = currpage - 1
                    else:
                        e.data = currpage + 1
                    totalcount = len(self.centerview.pdfprevdialog.api.doc)
                    if totalcount > e.data >= 0:
                        self.centerview.pdfprevdialog.api.on_page_changed.emit(e)
                    # print("响应!")

            def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
                if event.button() == Qt.RightButton:
                    self.setDragMode(self.RubberBandDrag)

                super().mousePressEvent(event)

            # def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
            #     if event.button() == Qt.RightButton:
            #         self.view.setDragMode(self.view.RubberBandDrag)
            #     super().mousePressEvent(event)

            def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
                super().mouseReleaseEvent(event)
                self.setDragMode(self.ScrollHandDrag)
                curr_selected_item = self.centerview.api.curr_selected_item
                if curr_selected_item is not None and self.curr_rubberBand_rect is not None:
                    r = self.curr_rubberBand_rect
                    pos = self.mapToScene(r.x(), r.y())
                    x, y, w, h = pos.x(), pos.y(), r.width(), r.height()
                    self.centerview.api.addClipbox(QRectF(x, y, w, h))
                    self.curr_rubberBand_rect = None
                    self.centerview.api.curr_selected_item_setValue(None)

                # print(self.curr_rubberBand_rect)

        class Scene(QGraphicsScene):
            def __init__(self, parent: "PDFPrevDialog.CenterView" = None):
                super().__init__(parent)
                self.setBackgroundBrush(Qt.black)
                self.centerview = parent
                self.all_event = tools.objs.AllEventAdmin({
                    self.centerview.pdfprevdialog.api.on_clipbox_deleted: self.on_clipbox_deleted_handle
                }).bind()

            def on_clipbox_deleted_handle(self, event: "PDFPrevDialog.ClipboxDeleteEvent"):
                self.removeItem(event.data)

        class Page(QGraphicsPixmapItem):
            mousecenter = 0
            viewcenter = 1
            nocenter = 2

            class API(QObject):
                def __init__(self, parent: "PDFPrevDialog.CenterView.Page" = None):
                    super().__init__()
                    self.parent = parent
                    self.change_page = self.parent.change_page
                    self.mousecenter = self.parent.mousecenter
                    self.viewcenter = self.parent.viewcenter
                    self.nocenter = self.parent.nocenter
                    self.zoom = self.parent.zoom
                    self.keep_clipbox_in_postion = parent.keep_clipbox_in_postion

            def __init__(self, *args, parent: "PDFPrevDialog.CenterView" = None):
                super().__init__(*args)
                self.centerview = parent
                self.mouse_center_item_p = None
                self.mouse_center_scene_p = None
                self.view_center_item_p = None
                self.view_center_scene_p = None
                self.api = self.API(self)

            def mouse_center_pos_get(self, pos):
                self.mouse_center_item_p = [pos.x() / self.boundingRect().width(),
                                            pos.y() / self.boundingRect().height()]
                self.mouse_center_scene_p = self.mapToScene(pos)

            def view_center_pos_get(self):
                centerpos = QPointF(self.centerview.view.size().width() / 2, self.centerview.view.size().height() / 2)
                self.view_center_scene_p = self.centerview.view.mapToScene(centerpos.toPoint())
                p = self.mapFromScene(self.view_center_scene_p)
                self.view_center_item_p = [p.x() / self.boundingRect().width(), p.y() / self.boundingRect().height()]

            def wheelEvent(self, event):
                if event.modifiers() == Qt.ControlModifier:
                    self.mouse_center_pos_get(event.pos())
                    if event.delta() > 0:
                        self.zoomIn()
                    else:
                        self.zoomOut()
                    self.centerview.pdfprevdialog.api.fit_in_policy_set(
                        self.centerview.pdfprevdialog.api.fit_in_disabled)
                else:
                    currpage = self.centerview.pdfprevdialog.api.curr_pagenum
                    e = PDFPrevDialog.PageChangedEvent
                    e = e(eventType=e.WheelType)
                    if event.delta() > 0:
                        e.data = currpage - 1
                    else:
                        e.data = currpage + 1
                    totalcount = len(self.centerview.pdfprevdialog.api.doc)
                    if totalcount > e.data >= 0:
                        self.centerview.pdfprevdialog.api.on_page_changed.emit(e)

            def zoomIn(self):
                """放大"""
                ratio = self.centerview.pdfprevdialog.api.pageratio
                ratio *= 1.1
                self.zoom(ratio)

            def zoomOut(self):
                """缩小"""
                ratio = self.centerview.pdfprevdialog.api.pageratio
                ratio /= 1.1
                self.zoom(ratio)

            def center_zoom(self, center=0):
                view_mouse_pos = self.centerview.view.api.mouse_pos
                if center == self.mousecenter:
                    X = self.mouse_center_item_p[0] * self.boundingRect().width()
                    Y = self.mouse_center_item_p[1] * self.boundingRect().height()
                    new_scene_p = self.mapToScene(X, Y)  # page上这一点对应的场景坐标
                    mouse_scene_p = self.centerview.view.mapToScene(view_mouse_pos)
                    dx = new_scene_p.x() - mouse_scene_p.x()
                    dy = new_scene_p.y() - mouse_scene_p.y()
                elif center == self.viewcenter:
                    X = self.view_center_item_p[0] * self.boundingRect().width()
                    Y = self.view_center_item_p[1] * self.boundingRect().height()
                    new_scene_p = self.mapToScene(X, Y)
                    dx = new_scene_p.x() - self.view_center_scene_p.x()
                    dy = new_scene_p.y() - self.view_center_scene_p.y()
                else:
                    raise TypeError(f"无法处理数据:{center}")
                scrollY = self.centerview.view.verticalScrollBar()
                scrollX = self.centerview.view.horizontalScrollBar()
                # 如果你不打算采用根据图片放大缩小,可以用下面的注释的代码实现scrollbar的大小适应

                print(f"x={dx}, dy={dy}")
                # self.centerview.view.setSceneRect(self.mapRectToScene(self.boundingRect()))
                scrollY.setValue(scrollY.value() + int(dy))
                scrollX.setValue(scrollX.value() + int(dx))

                self.view_center_scene_p = None
                self.view_center_item_p = None

                # p=  self.mapToScene(QPoint(1,1))
                # print(f"""scrolly={scrollY.value()},rect.height()={rect.height()}""")

            def zoom(self, factor, center=None):
                """缩放
                :param factor: 缩放的比例因子
                """
                if center is None:
                    center = self.mousecenter
                _factor = self.transform().scale(
                    factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
                if _factor < 0.07 or _factor > 100:
                    # 防止过大过小
                    return
                if center == self.viewcenter:
                    self.view_center_pos_get()
                pagenum = self.centerview.pdfprevdialog.api.curr_pagenum

                self.centerview.api.leftpage.api.change_page(pagenum, ratio=factor)
                if self.centerview.api.rightpage:
                    self.centerview.api.rightpage.api.change_page(pagenum + 1, ratio=factor)
                self.centerview.api.relayoutpage()
                self.centerview.pdfprevdialog.api.pageratio_set(factor)
                if center != self.nocenter:
                    self.center_zoom(center)
                self.centerview.api.leftpage.api.keep_clipbox_in_postion()
                if self.centerview.api.rightpage:
                    self.centerview.api.rightpage.api.keep_clipbox_in_postion()

            def change_page(self, pagenum, pdfname=None, ratio=None):
                if pagenum >= len(self.centerview.pdfprevdialog.api.doc) or pagenum < 0:
                    return
                if pdfname is None:
                    pdfname = self.centerview.pdfprevdialog.api.pdfname
                if ratio is None:
                    ratio = self.centerview.pdfprevdialog.api.pageratio
                path = tools.funcs.pixmap_page_load(pdfname, pagenum, ratio)
                self.setPixmap(QPixmap(path))

            def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                self.centerview.api.curr_selected_item_setValue(self)
                super().mousePressEvent(event)

            def keep_clipbox_in_postion(self):
                w, h = self.boundingRect().width(), self.boundingRect().height()
                curr_page = self.centerview.pdfprevdialog.api.curr_pagenum
                count = self.centerview.pdfprevdialog.api.pagecount
                if self != self.centerview.api.leftpage:
                    curr_page = self.centerview.pdfprevdialog.api.curr_rightpagenum
                if curr_page in self.centerview.api.clipbox_dict:
                    for box in self.centerview.api.clipbox_dict[curr_page]:
                        box.api.keep_ratio()

        class Clipbox(QGraphicsRectItem):
            linewidth = 10
            toLeft, toRight, toTop, toBottom, toTopLeft, toTopRight, toBottomLeft, toBottomRight = 0, 1, 2, 3, 4, 5, 6, 7

            class API(QObject):
                def __init__(self, parent: "PDFPrevDialog.CenterView.Clipbox"):
                    super().__init__()
                    self.parent = parent
                    self.keep_ratio = parent.keep_ratio
                    self.self_info_get = parent.self_info_get
                    self.clip_img_save = parent.clip_img_save

                @property
                def uuid(self) -> str:
                    return self.parent.uuid

                @property
                def pageratio(self) -> float:
                    return self.parent.pageratio

                def pageratio_setValue(self, value):
                    self.parent.pageratio = value

            def __init__(self, parent: "PDFPrevDialog.CenterView.Page" = None, rect: "QRectF" = None, pagenum=None):
                super().__init__(parent)
                self.uuid = tools.funcs.clipbox_uuid_random_unique()
                self.atpage = parent
                self.pagenum = pagenum
                self.fromrect = rect
                self.isHovered = False
                self.selected_at = None
                self.click_rect = None
                self.click_pos = QPointF()
                self.pageratio = 1
                self.close = self.Close(self)
                self.api = self.API(self)
                self.setFlag(self.ItemIsMovable, True)
                self.setFlag(self.ItemIsSelectable, True)
                self.setFlag(self.ItemSendsGeometryChanges, True)
                self.setAcceptHoverEvents(True)

                b = self.atpage.boundingRect()
                if rect.right() > b.right():
                    rect.setRight(b.right())
                if rect.top() < b.top():
                    rect.setTop(b.top())
                if rect.left() < b.left():
                    rect.setLeft(b.left())
                if rect.bottom() > b.bottom():
                    rect.setBottom(b.bottom())
                self.setRect(rect)
                self.inited = True

            # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            #

            def calc_ratio(self):
                """记录上下左右所处的坐标系的比例，方便放大缩小跟随"""
                max_X, max_Y = self.atpage.boundingRect().right(), self.atpage.boundingRect().bottom()
                fix_x, fix_y = self.pos().x(), self.pos().y()
                top, left, right, bottom = self.rect().top(), self.rect().left(), self.rect().right(), self.rect().bottom()
                self.ratioTop = (top + fix_y) / max_Y
                self.ratioLeft = (left + fix_x) / max_X
                self.ratioBottom = (bottom + fix_y) / max_Y
                self.ratioRight = (right + fix_x) / max_X

            def keep_ratio(self):
                w, h, x, y = self.atpage.boundingRect().width(), self.atpage.boundingRect().height(), self.x(), self.y()
                r = self.rect()
                # R = QRectF(self.ratioLeft * w,self.ratioTop * h,self.ratioRight * w,self.ratioBottom * h)
                r.setTop(self.ratioTop * h - y)
                r.setLeft(self.ratioLeft * w - x)
                r.setBottom(self.ratioBottom * h - y)
                r.setRight(self.ratioRight * w - x)
                # 之所以减原来的x,y可行,是因为图片的放大并不是膨胀放大,每个点都是原来的点,只是增加了一些新的点而已.
                self.setRect(r)

            def cursor_position_check(self, p: "QPointF"):
                rect = self.rect()
                LT, LB = QPointF(rect.left(), rect.top()), QPointF(rect.left(), rect.bottom())
                RT, RB = QPointF(rect.right(), rect.top()), QPointF(rect.right(), rect.bottom())
                linewidth = self.linewidth
                if QLineF(p, LT).length() < linewidth:
                    self.setCursor(Qt.SizeFDiagCursor)  # 主对角线
                elif QLineF(p, LB).length() < linewidth:
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RT).length() < linewidth:
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RB).length() < linewidth:
                    self.setCursor(Qt.SizeFDiagCursor)
                elif abs(p.x() - rect.left()) < linewidth:
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.x() - rect.right()) < linewidth:
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.y() - rect.top()) < linewidth:
                    self.setCursor(Qt.SizeVerCursor)
                elif abs(p.y() - rect.bottom()) < linewidth:
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)

            def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                self.click_pos = p = event.pos()
                rect = self.rect()
                LT, LB = QPointF(rect.left(), rect.top()), QPointF(rect.left(), rect.bottom())
                RT, RB = QPointF(rect.right(), rect.top()), QPointF(rect.right(), rect.bottom())
                linewidth = self.linewidth
                if QLineF(p, LT).length() < linewidth:
                    self.selected_at = self.toTopLeft
                    self.setCursor(Qt.SizeFDiagCursor)  # 主对角线
                elif QLineF(p, LB).length() < linewidth:
                    self.selected_at = self.toBottomLeft
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RT).length() < linewidth:
                    self.selected_at = self.toTopRight
                    self.setCursor(Qt.SizeBDiagCursor)
                elif QLineF(p, RB).length() < linewidth:
                    self.selected_at = self.toBottomRight
                    self.setCursor(Qt.SizeFDiagCursor)
                elif abs(p.x() - rect.left()) < linewidth:
                    self.selected_at = self.toLeft
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.x() - rect.right()) < linewidth:
                    self.selected_at = self.toRight
                    self.setCursor(Qt.SizeHorCursor)
                elif abs(p.y() - rect.top()) < linewidth:
                    self.selected_at = self.toTop
                    self.setCursor(Qt.SizeVerCursor)
                elif abs(p.y() - rect.bottom()) < linewidth:
                    self.selected_at = self.toBottom
                    self.setCursor(Qt.SizeVerCursor)
                else:
                    self.selected_at = None
                self.click_rect = rect
                super().mousePressEvent(event)

            def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                if self.click_pos is not None and self.selected_at is not None and self.click_rect is not None:
                    # self.setFlag(self.ItemIsMovable,False)
                    pos = event.pos()
                    x_diff = pos.x() - self.click_pos.x()
                    y_diff = pos.y() - self.click_pos.y()
                    rect = QRectF(self.click_rect)
                    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
                    if self.selected_at == self.toTopRight:
                        rect.adjust(0, y_diff, x_diff, 0)
                    elif self.selected_at == self.toTopLeft:
                        rect.adjust(x_diff, y_diff, 0, 0)
                    elif self.selected_at == self.toBottomLeft:
                        rect.adjust(x_diff, 0, 0, y_diff)
                    elif self.selected_at == self.toBottomRight:
                        rect.adjust(0, 0, x_diff, y_diff)
                    elif self.selected_at == self.toTop:
                        rect.adjust(0, y_diff, 0, 0)
                    elif self.selected_at == self.toLeft:
                        rect.adjust(x_diff, 0, 0, 0)
                    elif self.selected_at == self.toBottom:
                        rect.adjust(0, 0, 0, y_diff)
                    elif self.selected_at == self.toRight:
                        rect.adjust(0, 0, x_diff, 0)
                    if rect.width() < self.linewidth:
                        if self.selected_at == self.toLeft:
                            rect.setLeft(rect.right() - self.linewidth)
                        else:
                            rect.setRight(rect.left() + self.linewidth)
                    if rect.height() < self.linewidth:
                        if self.selected_at == self.toTop:
                            rect.setTop(rect.bottom() - self.linewidth)
                        else:
                            rect.setBottom(rect.top() + self.linewidth)
                    self.setRect(rect)
                    self.calc_ratio()
                    self.move_bordercheck()
                else:
                    super().mouseMoveEvent(event)

            def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
                self.click_pos = None
                self.click_rect = None
                self.selected_at = None
                # self.setFlag(self.ItemIsMovable,True)
                self.setCursor(Qt.ArrowCursor)
                super().mouseReleaseEvent(event)

            def hoverMoveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                # print('hoverMoveEvent')
                self.isHovered = True
                self.cursor_position_check(event.pos())
                super().hoverMoveEvent(event)

            def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                # print('hoverEnterEvent')
                self.isHovered = True
                self.cursor_position_check(event.pos())
                super().hoverEnterEvent(event)

            def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
                # print('hoverLeaveEvent')
                self.isHovered = False
                self.setCursor(Qt.ArrowCursor)
                super().hoverLeaveEvent(event)

            # def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            #
            # def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
            #     self.hide()

            def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
                      widget: typing.Optional[QWidget] = ...) -> None:

                pen = QPen(QColor(127, 127, 127), 2.0, Qt.DashLine)
                if "inited" in self.__dict__:
                    if ("isHovered" in self.__dict__ and self.isHovered) or self.isSelected():
                        pen.setWidth(5)
                        painter.setBrush(QBrush(QColor(0, 255, 0, 30)))
                        self.close.setTopRightCorner()
                        self.close.proxy.show()
                    else:
                        self.close.proxy.hide()
                    view = self.atpage.centerview.view

                    if view.dragMode() == view.RubberBandDrag:
                        self.setFlag(self.ItemIsSelectable, False)
                    else:
                        self.setFlag(self.ItemIsSelectable, True)
                    if self.isVisible():
                        self.move_bordercheck()
                        self.calc_ratio()
                painter.setPen(pen)
                painter.drawRect(self.rect())
                self.prepareGeometryChange()

            def shape(self):
                """
                shape在boundingRect里面
                """
                strokepath = QPainterPathStroker()
                # print(self.rect())
                path = QPainterPath()
                path.addRect(self.rect())
                if self.isSelected():
                    return path
                else:
                    strokepath.setWidth(2 * self.linewidth)
                    newpath = strokepath.createStroke(path)
                    return newpath

            def move_bordercheck(self):
                """根据是否越界进行一个边界的修正，超出边界就用边界的值代替,同样必须用父类来检测边界"""
                rect = self.rect()
                x, y = self.pos().x(), self.pos().y()
                view_left = 0
                view_top = 0
                view_right = self.atpage.boundingRect().width()
                view_bottom = self.atpage.boundingRect().height()
                if rect.width() > view_right:
                    rect.setWidth(view_right)
                if rect.height() > view_bottom:
                    rect.setHeight(view_bottom)

                top = rect.top() + y
                bottom = rect.bottom() + y
                left = rect.left() + x
                right = rect.right() + x
                if top < view_top:
                    # print("over top")
                    rect.translate(0, view_top - top)
                if left < view_left:
                    # print("over left")
                    rect.translate(view_left - left, 0)
                if view_bottom < bottom:
                    # print("over bottom")
                    rect.translate(0, view_bottom - bottom)
                if view_right < right:
                    # print("over right")
                    rect.translate(view_right - right, 0)

                # b = self.atpage.boundingRect()
                # if rect.right() > b.right():
                #     rect.setRight(b.right())
                # if rect.top() < b.top():
                #     rect.setTop(b.top())
                # if rect.left() < b.left():
                #     rect.setLeft(b.left())
                # if rect.bottom() > b.bottom():
                #     rect.setBottom(b.bottom())

                self.setRect(rect)

            def self_info_get(self):

                clipbox_info = {
                    "uuid": self.uuid,
                    "pdfname": self.atpage.centerview.pdfprevdialog.api.pdfname,
                    "pagenum": self.pagenum,
                    "ratio": self.atpage.centerview.pdfprevdialog.api.pageratio,
                    "x": self.ratioLeft,
                    "y": self.ratioTop,
                    "w": self.ratioRight - self.ratioLeft,
                    "h": self.ratioBottom - self.ratioTop,
                }
                return clipbox_info

            def clip_img_save(self, imgdir=None):
                clipinfo = self.self_info_get()
                pixmap = tools.funcs.png_pdf_clip(clipinfo["pdfname"], self.pagenum, rect1=clipinfo)
                if imgdir is None:
                    imgdir = os.path.join(tempfile.gettempdir(), f"""hjp_clipper_{self.uuid}_.png""")
                pixmap.save(imgdir)
                return imgdir

            def __setattr__(self, key, value):
                if "atpage" == key:
                    self.setParentItem(value)
                self.__dict__[key] = value

            class Close:
                def __init__(self, superior: "PDFPrevDialog.CenterView.Clipbox"):
                    self.superior = superior
                    self.widget: "QToolButton" = QToolButton()
                    self.proxy: "QGraphicsProxyWidget" = QGraphicsProxyWidget()
                    self.proxy.setParentItem(superior)
                    self.proxy.setWidget(self.widget)
                    self.widget.setIcon(QIcon(tools.objs.SrcAdmin.imgDir.close))
                    self.widget.clicked.connect(self.on_clicked)

                def setTopRightCorner(self):
                    self.proxy.setPos(
                        self.superior.boundingRect().right() - self.widget.width() - 10,
                        self.superior.boundingRect().top() + 10)

                def on_clicked(self):
                    e = PDFPrevDialog.ClipboxDeleteEvent
                    self.superior.atpage.centerview.pdfprevdialog.api.on_clipbox_deleted.emit(
                        e(data=self.superior, pagenum=self.superior.pagenum))

        class API(QObject):
            def __init__(self, centerview: "PDFPrevDialog.CenterView" = None):
                super().__init__(centerview)
                self.centerview = centerview
                self.addpage = centerview.addpage
                self.delpage = centerview.delpage
                self.page_dict: "dict[str,PDFPrevDialog.CenterView.Page]" = self.centerview.page_dict
                self.relayoutpage = centerview.relayoutpage
                self.fit_in = centerview.fit_in
                self.clipbox_dict = centerview.clipbox_dict

                # 选框的时候需要add
                self.addClipbox = centerview.addClipbox
                # 删除的时候需要del
                self.delclipbox = centerview.delClipbox

                # 换页的时候需要showhide
                self.showclipbox = centerview.showclipbox
                self.hideclipbox = centerview.hideclipbox
                self.flatClipbox = centerview.flatClipbox

            def curr_selected_item_setValue(self, value):
                self.centerview.curr_selected_item = value

            @property
            def curr_selected_item(self):
                return self.centerview.curr_selected_item

            @property
            def leftpage(self):
                return self.centerview.leftpage

            @property
            def rightpage(self):
                return self.centerview.rightpage

        def __init__(self, parent: "PDFPrevDialog" = None):

            super().__init__(parent)
            self.pdfprevdialog = parent
            self.page_dict: "dict[str,PDFPrevDialog.CenterView.Page]" = {"left": None, "right": None}
            self.leftpage: "PDFPrevDialog.CenterView.Page" = None
            self.rightpage: "PDFPrevDialog.CenterView.Page" = None
            self.curr_selected_item: "PDFPrevDialog.CenterView.Page" = None
            self.clipbox_dict: "dict[int,list[PDFPrevDialog.CenterView.Clipbox]]" = {}
            self.view = self.View(self)
            self.scene = self.Scene(self)
            self.init_UI()
            self.api = self.API(self)
            self.all_event = tools.objs.AllEventAdmin({
                self.pdfprevdialog.api.on_clipbox_deleted: self.on_clipbox_deleted_handle,

            }).bind()

        def on_clipbox_deleted_handle(self, event: "PDFPrevDialog.ClipboxDeleteEvent"):
            self.delClipbox(event.data, event.pagenum)

        def init_UI(self):
            self.view.setScene(self.scene)
            V_layout = QVBoxLayout(self)
            V_layout.addWidget(self.view)
            self.setLayout(V_layout)
            self.view.setDragMode(self.view.ScrollHandDrag)
            self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.view.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing |
                                     QPainter.SmoothPixmapTransform)

        def addpage(self):
            pdfname = self.pdfprevdialog.api.pdfname
            pagenum = self.pdfprevdialog.api.curr_pagenum
            ratio = self.pdfprevdialog.api.pageratio
            # print(f"pagenum={pagenum}")
            if self.leftpage is None:
                pixmap = QPixmap(tools.funcs.pixmap_page_load(pdfname, pagenum, ratio))
                self.leftpage = self.Page(pixmap, parent=self)
                self.scene.addItem(self.leftpage)
            else:
                pixmap = QPixmap(tools.funcs.pixmap_page_load(pdfname, pagenum + 1, ratio))
                self.rightpage = self.Page(pixmap, parent=self)
                self.scene.addItem(self.rightpage)
                if self.pdfprevdialog.size().width() * 2 < QApplication.desktop().width():
                    self.pdfprevdialog.resize(self.pdfprevdialog.size().width() * 2, self.pdfprevdialog.size().height())
                    if self.pdfprevdialog.pos().x() + self.pdfprevdialog.size().width() > QApplication.desktop().width():
                        m = self.pdfprevdialog.pos().x() + self.pdfprevdialog.size().width() - QApplication.desktop().width()
                        x = self.pdfprevdialog.pos().x() - m
                        self.pdfprevdialog.move(x, self.pdfprevdialog.pos().y())
                else:
                    self.fit_in(fit_in_policy=self.pdfprevdialog.api.fit_in_width)
            self.relayoutpage()
            self.showclipbox()
            # self.pdfprevdialog.on_page_added.emit(pagenum)

        def delpage(self):
            self.scene.removeItem(self.rightpage)
            self.rightpage = None
            # self.pdfprevdialog.resize(int(self.pdfprevdialog.size().width() / 2), self.pdfprevdialog.size().height())
            self.relayoutpage()

        def flatClipbox(self):
            li = []
            for pagenum, clipboxli in self.clipbox_dict.items():
                li += clipboxli
            return li

        def addClipbox(self, rect: "Union[QRectF,QRect]"):
            pagenum = self.pdfprevdialog.api.curr_pagenum
            totalcount = len(self.pdfprevdialog.api.doc)
            if self.curr_selected_item == self.rightpage and self.rightpage is not None and pagenum + 1 < totalcount:
                pagenum += 1
            r = self.curr_selected_item.mapRectFromScene(rect)
            clipbox = self.Clipbox(parent=self.curr_selected_item, rect=r.normalized(), pagenum=pagenum)
            if pagenum not in self.clipbox_dict:
                self.clipbox_dict[pagenum] = []
            self.clipbox_dict[pagenum].append(clipbox)

        def delClipbox(self, clipbox: "PDFPrevDialog.CenterView.Clipbox" = None, pagenum: "int" = None,
                       clipuuid: "str" = None, ):
            clipbox_not_None = clipbox is not None
            pagenum_not_None = pagenum is not None
            clipuuid_not_None = clipuuid is not None

            assert (clipbox_not_None or clipuuid_not_None)
            if pagenum_not_None:
                if clipbox_not_None:
                    if clipbox in self.clipbox_dict[pagenum]:
                        self.clipbox_dict[pagenum].remove(clipbox)
                        self.pdfprevdialog.center_view.scene.removeItem(clipbox)
                        return True
                    else:
                        return False
                else:
                    for clipbox in self.clipbox_dict[pagenum]:
                        if clipbox.api.uuid == clipuuid:
                            self.clipbox_dict[pagenum].remove(clipbox)
                            self.pdfprevdialog.center_view.scene.removeItem(clipbox)
                            return True
                    return False
            else:
                for num, clip in self.clipbox_dict.items():
                    result = self.delClipbox(clipbox=clipbox, pagenum=num, clipuuid=clipuuid)
                    if result:
                        return
            # if clipbox is not None and pagenum is not None:
            #     if clipbox in self.clipbox_dict[pagenum]:
            #         self.clipbox_dict[pagenum].remove(clipbox)
            #         return True
            #     else:
            #         return False
            # elif clipbox is None and pagenum is not None and clipuuid is not None:
            #     for clipbox in self.clipbox_dict[pagenum]:
            #         if clipbox.api.uuid==clipuuid:
            #             self.clipbox_dict[pagenum].remove(clipbox)
            #             return True
            #     return False
            # elif pagenum is None

        def fit_in(self, fit_in_policy=None):
            leftpage = self.leftpage
            rightpage = self.rightpage
            if fit_in_policy is None:
                fit_in_policy = self.pdfprevdialog.api.fit_in_policy

            if fit_in_policy == self.pdfprevdialog.api.fit_in_width:
                if rightpage is not None:
                    width = self.view.width() / 2
                else:
                    width = self.view.width()
                fit_ratio = width / leftpage.boundingRect().width() * self.pdfprevdialog.api.pageratio
                leftpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)
                if rightpage is not None:
                    rightpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)

            elif fit_in_policy == self.pdfprevdialog.api.fit_in_height:
                height = self.height()
                fit_ratio = height / leftpage.boundingRect().height() * self.pdfprevdialog.api.pageratio
                leftpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)
                if rightpage is not None:
                    rightpage.api.zoom(fit_ratio, center=leftpage.api.nocenter)

        def relayoutpage(self):
            self.leftpage.setPos(0, 0)
            if self.rightpage:
                self.rightpage.setPos(self.leftpage.boundingRect().width(), 0)
                self.view.setSceneRect(0, 0, self.leftpage.boundingRect().width() * 2,
                                       self.leftpage.boundingRect().height())
            else:
                self.view.setSceneRect(0, 0, self.leftpage.boundingRect().width(),
                                       self.leftpage.boundingRect().height())

        def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
            self.fit_in()
            super().resizeEvent(a0)

        def hideclipbox(self):
            last_pagenum = self.pdfprevdialog.api.last_pagenum
            if last_pagenum in self.clipbox_dict:
                for clipbox in self.clipbox_dict[last_pagenum]:
                    curr_ratio = self.pdfprevdialog.api.pageratio
                    clipbox.api.pageratio_setValue(curr_ratio)
                    clipbox.hide()
            if self.rightpage:
                last_rightpagenum = self.pdfprevdialog.api.last_rightpagenum
                if last_rightpagenum in self.clipbox_dict:
                    for clipbox in self.clipbox_dict[last_rightpagenum]:
                        curr_ratio = self.pdfprevdialog.api.pageratio
                        clipbox.api.pageratio_setValue(curr_ratio)
                        clipbox.hide()

        def showclipbox(self):
            curr_pagenum: int = self.pdfprevdialog.api.curr_pagenum
            if curr_pagenum in self.clipbox_dict:
                for clipbox in self.clipbox_dict[curr_pagenum]:
                    clipbox.atpage = self.leftpage
                    clipbox.api.keep_ratio()
                    clipbox.show()
            if self.rightpage:
                curr_rightpagenum = self.pdfprevdialog.api.curr_rightpagenum
                if curr_rightpagenum in self.clipbox_dict:
                    for clipbox in self.clipbox_dict[curr_rightpagenum]:
                        clipbox.atpage = self.rightpage
                        clipbox.api.keep_ratio()
                        clipbox.show()

        pass

    class CorrectionDialog(QMainWindow):

        on_pdfprev_insertClipbox_finished = pyqtSignal(object)

        class API:
            def __init__(self, parent: "PDFPrevDialog.CorrectionDialog"):
                self.data = parent.data
                self.packup_clipbox_info = parent.packup_clipbox_info
                self.on_progerss_signal = parent.widget_progressbar.on_progress
                self.table_clear = parent.table_clear
                self.on_pdfprev_insertClipbox_finished = parent.on_pdfprev_insertClipbox_finished

        def __init__(self, parent: "PDFPrevDialog" = None, data: "list[PDFPrevDialog.CenterView.Clipbox]" = None):
            super().__init__()
            self.data = data
            # self.setParent(parent)
            self.container = QWidget(self)
            self.pdfprevdialog = parent
            self.widget_progressbar = self.progressBar(self)
            self.widget_button_correct = QToolButton(self.container)
            self.table = self.Table(self.container, superior=self)
            self.api = self.API(self)
            self.all_event = tools.objs.AllEventAdmin({
                self.widget_button_correct.clicked: self.on_widget_button_correct_clicked_handle,
                self.on_pdfprev_insertClipbox_finished: self.on_pdfprev_insertClipbox_finished_handle
            }).bind()
            self.init_UI()
            self.worker_thread: "QThread" = None

        def on_pdfprev_insertClipbox_finished_handle(self, timestamp):
            common_tools.funcs.BrowserOperation.search(f"""tag:hjp-bilink::timestamp::{timestamp}""").activateWindow()
            common_tools.funcs.CardOperation.refresh()
            self.table_clear()
            self.pdfprevdialog.close()
            self.close()

        def on_widget_button_correct_clicked_handle(self):
            """
            uuid,pdfname,pagenum,ratio,x,y,w,h,
            QA,text_,textQA,card_id
            Returns:
                clipboxdict:{card_id:[clipbox,...,]}
            1,收集clipbox要保存到DB的信息
            2,根据之前设计过的经验,设计几个阶段,(需要用线程)
            2.0 开启进度条,开启线程
            2.1 新卡片设计,并将新卡片替换掉原来的"/"
            2.2 插入卡片信息
            2.3 复制图片到媒体库
            3 删除已经链接过的clipbox
            """
            if not __name__ == "__main__":
                QApplication.processEvents()
                self.worker_thread = self.Thread(self)
                QApplication.processEvents()
                self.worker_thread.start()
            else:
                self.table_clear()
                # print(json.dumps(self.api.packup_clipbox_info()))

        def table_clear(self):
            """在插入工作执行完后,执行这个函数, 分两个操作,一个是删除table的记录,一个是删除PDF上的clipbox"""
            datali: "list[list[PDFPrevDialog.CenterView.Clipbox,str]]" = self.table.api.clipbox_clear()
            for data in datali:
                self.pdfprevdialog.center_view.api.delclipbox(clipbox=data[0], pagenum=int(data[1]))

        def packup_clipbox_info(self) -> "dict[str,list[dict[str,Union[str,int]]]]":
            clipboxlist_temp = []
            for i in range(self.table.api.mymodel.rowCount()):
                clipbox_dict: "dict" = self.table.api.mymodel.item(i, self.table.pixmap).data(
                    role=Qt.UserRole).self_info_get()
                clipbox_dict["card_desc"] = self.table.api.mymodel.item(i, self.table.card_desc).data(
                    role=Qt.DisplayRole)
                clipbox_dict["QA"] = int(self.table.api.mymodel.item(i, self.table.to_field).data(role=Qt.DisplayRole))
                clipbox_dict["commentQA"] = int(
                    self.table.api.mymodel.item(i, self.table.comment_to_field).data(role=Qt.DisplayRole))
                clipbox_dict["comment"] = self.table.api.mymodel.item(i, self.table.comment).data(role=Qt.DisplayRole)
                clipboxlist_temp.append(clipbox_dict)
                clipbox_dict["pdfuuid"] = self.pdfprevdialog.pdfuuid
            # print(clipboxlist_temp)
            clipboxlist_final = {}
            for clipbox in clipboxlist_temp:
                if clipbox["card_desc"] == self.Combox.curr_card:
                    clipbox["card_id"] = self.pdfprevdialog.api.card_id
                else:
                    clipbox["card_id"] = "/"
                if clipbox["card_desc"] not in clipboxlist_final:
                    clipboxlist_final[clipbox["card_desc"]] = []
                clipboxlist_final[clipbox["card_desc"]].append(clipbox)
            return clipboxlist_final

        def init_UI(self):
            self.setWindowModality(Qt.NonModal)
            # self.setModal(False)
            # self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
            self.setWindowTitle("overview")
            self.widget_button_correct.setIcon(QIcon(tools.objs.SrcAdmin.imgDir.correct))
            v_layout = QGridLayout(self.container)
            v_layout.addWidget(self.table, 0, 0, 1, 2)
            v_layout.addWidget(self.widget_button_correct, 1, 1)
            v_layout.addWidget(self.widget_progressbar, 1, 0)
            v_layout.setAlignment(Qt.AlignRight)
            self.container.setLayout(v_layout)
            self.setCentralWidget(self.container)
            self.resize(800, 600)
            # self.showMaximized()

        def init_data(self):
            pass

        def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
            for w in self.table.api.imgli:
                w.close()
            if self.worker_thread is not None and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread = None

        class Thread(QThread):
            on_quit = pyqtSignal()

            def __init__(self, superior: "PDFPrevDialog.CorrectionDialog"):
                super().__init__(superior)
                self.superior = superior
                self.timegap = 0.1

            def on_quit_handle(self):
                self.quit()

            def run(self):
                data = self.superior.api.packup_clipbox_info()
                card = mw.col.getCard(CardId(int(self.superior.pdfprevdialog.card_id)))
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                model_id, deck_id = card.model()["id"], card.did
                part = 1
                card_desc_total = len(data)
                card_desc_count = 0
                for card_desc, clipboxli in data.items():

                    clipboxli_total = len(clipboxli)
                    clipboxli_count = 0
                    if self.superior.Combox.new_card in card_desc:
                        card_id = common_tools.funcs.CardOperation.create(model_id, deck_id)
                        for clipbox in clipboxli:
                            # 新建卡片
                            clipbox["card_id"] = card_id

                    for clipbox in clipboxli:
                        # 插入DB
                        DB = tools.objs.SrcAdmin.DB
                        DB.go(DB.table_clipbox).insert(**clipbox).commit()  # 这东西不可能是已经存在的
                        DB.end()
                        # 插入field

                        common_tools.funcs.CardOperation.clipbox_insert_field(clipbox["uuid"], timestamp=timestamp)
                        common_tools.funcs.Media.clipbox_png_save(clipbox["uuid"])
                        clipboxli_count += 1
                        self.superior.api.on_progerss_signal.emit(
                            ceil((clipboxli_count / clipboxli_total + card_desc_count) / card_desc_total * part * 100)
                        )

                    card_desc_count += 1
                    self.superior.api.on_progerss_signal.emit(
                        ceil(card_desc_count / card_desc_total * part * 100)
                    )
                    time.sleep(self.timegap)

                self.superior.api.on_pdfprev_insertClipbox_finished.emit(timestamp)
                self.quit()

        class progressBar(QProgressBar):
            on_progress = pyqtSignal(object)
            on_end = pyqtSignal(object)

            def __init__(self, parent: "PDFPrevDialog.CorrectionDialog"):
                super().__init__(parent)
                # self.events = tools.objs.AllEventAdmin({
                #     signals.ALL.on_PDFprev_work_progress: self.setValue
                # }).bind()
                self.on_progress.connect(self.setValue)

        class Combox(QComboBox):
            curr_card, new_card, plus = "当前卡片/current_card", "new_card", "+"

            def __init__(self, table: "PDFPrevDialog.CorrectionDialog.Table", index: "QModelIndex", *args):
                super().__init__(*args)
                self.index = index
                self.currentIndexChanged.connect(self.on_currentIndexChanged)
                self.addItem(self.curr_card)
                self.addItem(self.plus)
                self.table = table
                self.init_UI()

            def init_UI(self):
                data = self.index.data(role=Qt.UserRole)
                text = self.index.data(role=Qt.DisplayRole)
                for i in data:
                    self.addItem(i)
                idx = self.findText(text)
                self.setCurrentIndex(idx)

            def on_currentIndexChanged(self, index):
                data = self.itemText(index)
                if data == "+":
                    count = self.count()
                    self.addItem(f"""{self.new_card}_{count - 2}""")
                    self.table.api.on_combox_addItem_handle()
                    self.setCurrentIndex(count)

        class Delegate(QStyledItemDelegate):
            pixmap, comment, page_at, card_desc, to_field, comment_to_field, close, myRole = 0, 1, 2, 3, 4, 5, 6, 999

            def __init__(self, table: "PDFPrevDialog.CorrectionDialog.Table", *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.table = table

            def paint(self, painter: "QPainter", option: "QStyleOptionViewItem", index: "QModelIndex"):
                value = index.model().data(index, Qt.DisplayRole)
                if index.column() == self.pixmap:

                    # v = min(option.rect.height(), option.rect.height())/
                    pixmap = QPixmap(value).scaledToHeight(option.rect.height())
                    middle = int(option.rect.width() / 2 - pixmap.width() / 2)
                    option.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
                    painter.drawPixmap(QRect(middle, option.rect.top(), pixmap.width(), pixmap.height()), pixmap)
                    index.model().setData(index, [pixmap.size().width(), pixmap.size().height()], Qt.SizeHintRole)
                else:
                    super().paint(painter, option, index)

            def createEditor(self, Widget: "QWidget", Option: "QStyleOptionViewItem", Index: "QModelIndex"):
                if Index.column() in [self.pixmap, self.page_at, self.close]:
                    return None
                elif Index.column() == self.card_desc:
                    combox = PDFPrevDialog.CorrectionDialog.Combox(self.table, Index, Widget)
                    return combox
                elif Index.column() in [self.to_field, self.comment_to_field]:
                    spinBox = QSpinBox(Widget)
                    spinBox.setRange(0, 2000)
                    return spinBox
                elif Index.column() == self.comment:
                    return QTextEdit(Widget)
                else:
                    return super().createEditor(Widget, Option, Index)

            def setEditorData(self, editor, index: QtCore.QModelIndex) -> None:
                if index.column() == self.comment:
                    e: QTextEdit = editor
                    text = index.data(role=Qt.DisplayRole)
                    e.setPlainText(text)
                else:
                    super().setEditorData(editor, index)

            def setModelData(self, editor, model: QtCore.QAbstractItemModel,
                             index: QtCore.QModelIndex) -> None:
                if index.column() == self.comment:
                    e: QTextEdit = editor
                    model.setData(index, e.toPlainText(), role=Qt.DisplayRole)

                else:
                    super().setModelData(editor, model, index)

            def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
                if index.column() == self.pixmap:
                    size: list = index.data(Qt.SizeHintRole)

                    return QSize(*size)
                    # else:
                    #     return super().sizeHint(option, index)
                else:
                    return super().sizeHint(option, index)

        class ToolButton(QToolButton):
            def __init__(self, table: "PDFPrevDialog.CorrectionDialog.Table", idx: "QPersistentModelIndex",
                         icon: "QIcon", *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.setIcon(icon)
                self.table = table
                self.idx = idx
                self.clicked.connect(self.on_clicked)

            def on_clicked(self):
                self.table.api.removeRow(self.idx)

        class Table(QTableView):
            on_combox_addItem = pyqtSignal()
            pixmap, comment, page_at, card_desc, to_field, comment_to_field, close = 0, 1, 2, 3, 4, 5, 6

            class API:
                def __init__(self, parent: "PDFPrevDialog.CorrectionDialog.Table"):
                    self.table = parent
                    self.imgli = self.table.imgli
                    self.removeRow = self.table.removeRow
                    self.mymodel = self.table.mymodel
                    # self.remove_row=self.table.remove_row
                    # self.rowli=self.table.rowli
                    self.on_combox_addItem_handle = self.table.on_combox_addItem_handle
                    self.clipbox_clear = self.table.clipbox_clear

            def __init__(self, parent, superior: "PDFPrevDialog.CorrectionDialog" = None):
                super().__init__(parent)
                self.correctiondialog = superior
                # self.g_layout = QGridLayout(self)
                self.mymodel = QStandardItemModel(self)
                self.headerli = ["选框\nclipbox", "评论\ncomment", "所在PDF页码\nPDF page at", "插入卡片\nto card",
                                 "插入到字段\nto field", "评论插入字段\ncomment to field", "删除\ndelete"]
                self.rowli = {}
                self.imgli = []
                self.init_UI()
                self.api = self.API(self)
                self.all_event = tools.objs.AllEventAdmin({
                    # self.clicked:self.on_clicked_handle,
                    self.doubleClicked: self.on_doubleClicked_handle,
                }).bind()
                self.init_data()

            def on_doubleClicked_handle(self, index: "QModelIndex"):
                # print(index)
                if index.column() == self.pixmap:
                    img = index.data(role=Qt.DisplayRole)
                    pixmap = QPixmap(img)
                    dialog = QDialog(self.parent())
                    label = QLabel(dialog)
                    label.setPixmap(pixmap)
                    v_layout = QVBoxLayout(dialog)
                    v_layout.addWidget(label)
                    dialog.setLayout(v_layout)
                    dialog.resize(pixmap.size())
                    dialog.setWindowModality(Qt.NonModal)
                    dialog.setModal(False)
                    dialog.show()
                    self.imgli.append(dialog)

            def on_combox_addItem_handle(self):
                for i in range(self.mymodel.rowCount()):
                    item = self.mymodel.item(i, self.card_desc)
                    data: list = item.data(role=Qt.UserRole)
                    data.append(PDFPrevDialog.CorrectionDialog.Combox.new_card + f"_{len(data)}")
                    item.setData(data, role=Qt.UserRole)

            def init_UI(self):
                self.mymodel.setHorizontalHeaderLabels(self.headerli)
                self.modelroot = self.mymodel.invisibleRootItem()
                self.setModel(self.mymodel)
                h_header = self.horizontalHeader()
                h_header.setSectionResizeMode(h_header.Interactive)
                h_header.setSectionResizeMode(0, h_header.Stretch)
                h_header.setSectionResizeMode(1, h_header.Stretch)
                h_header.setSectionResizeMode(self.card_desc, h_header.ResizeToContents)
                self.setSelectionMode(self.NoSelection)
                v_header: "QHeaderView" = self.verticalHeader()
                v_header.setSectionResizeMode(v_header.Interactive)
                d = self.correctiondialog.Delegate(self)
                self.setItemDelegate(d)

            def init_data(self):
                for clipbox in self.correctiondialog.data:  # data:list[clipbox]
                    clipinfo = clipbox.api.self_info_get()
                    curr_card = PDFPrevDialog.CorrectionDialog.Combox.curr_card
                    row = [QStandardItem(i) for i in
                           [clipbox.api.clip_img_save(), "", str(clipinfo["pagenum"]), curr_card, "0", "0", ""]]
                    row[self.card_desc].setData([], role=Qt.UserRole)  # 用来保存combox能选择的内容
                    row[self.pixmap].setData(clipbox, role=Qt.UserRole)  # 用来删除指定的clipbox
                    self.mymodel.appendRow(row)
                for i in range(self.mymodel.rowCount()):
                    t = PDFPrevDialog.CorrectionDialog.ToolButton(
                        self,
                        QPersistentModelIndex(self.mymodel.item(i, self.close).index()),
                        QIcon(tools.objs.SrcAdmin.imgDir.close)
                    )
                    # self.mymodel.item(i,0).setData(self.correctiondialog.data[i].self_info_get(),role=Qt.UserRole)
                    self.setIndexWidget(self.mymodel.item(i, self.close).index(), t)
                    self.setRowHeight(i, 100)

            def clipbox_clear(self):
                """清空 model 并返回model中存在的clipbox为列表"""
                li = []
                for i in range(self.mymodel.rowCount() - 1, -1, -1):
                    item = self.mymodel.takeRow(i)
                    li.append([item[self.pixmap].data(Qt.UserRole), item[self.page_at].text()])
                return li

            def removeRow(self, idx: "QPersistentModelIndex"):
                # print(idx.row())
                self.mymodel.removeRow(idx.row())
        # class Proxy()


if __name__ == "__main__":
    UUID = "6878aa4a-3eea-339e-b72d-7400c4c2aa83"
    DB = tools.objs.SrcAdmin.DB
    pdfinfo = DB.go(DB.table_pdfinfo).select(uuid=UUID).return_all().zip_up().to_pdfinfo_data()[0]
    testcase = {
        "pdfname": pdfinfo.pdf_path, "pdfuuid": UUID, "card_id": "123456789",
        "pagenum": 100, "pageratio": 1
    }
    app = QApplication(sys.argv)
    p = PDFPrevDialog(**testcase)
    p.show()
    sys.exit(app.exec_())
