import sys, os
import tempfile
from typing import Union

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QRectF, QRect, QModelIndex
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem, QPixmap, QPainterPath, QPen, QColor
from PyQt5.QtWidgets import QDialog, QApplication, QTableView, QGraphicsView, QWidget, QGridLayout, QToolButton, \
    QHBoxLayout, QLabel, QTreeView, QStyledItemDelegate, QStyleOptionViewItem, QStyle
from aqt.utils import showInfo

if __name__ == '__main__':
    from lib.clipper.lib.tools import objs, funcs, events, ALL
    from lib.clipper.lib.PageInfo import PageInfo
    from lib.clipper.lib.PDFView_ import PageItem5
else:
    from ...tools import objs, funcs, events, ALL
    from ...PageInfo import PageInfo
    from ...PDFView_ import PageItem5


class CardClipboxPicker(QDialog):

    def __init__(self, parent, card_id, card_uuid):
        super().__init__(parent)
        self.card_uuid = card_uuid
        self.card_id = card_id
        self.pdf_clip_dict: "dict[str,list[str]]" = {}
        self.api = self.API(self)
        self.center_tree = self.CenterTree(self)
        # self.right_view=self.RightView(self)
        self.bottom_bar = self.BottomBar(self)
        self.g_layout = QGridLayout(self)
        self.init_UI()
        self.collect_info()
        self.all_event = objs.AllEventAdmin({
            self.center_tree.view.doubleClicked: self.on_center_tree_view_doubleClicked_handle,
        }).bind()

    # 先做好基础的数据收集, card_id对应的clipbox卡片和pdfuuid地址
    def collect_info(self):
        """

        Returns:
            {pdfname:{pagenum:[clip]}}

        """
        DB = objs.SrcAdmin.DB.go()
        result: "list[dict[str,Union[str,int]]]" = DB.select(
            where=DB.where_maker(colname="card_id", LIKE=True, vals=f"%{self.card_id}%")).return_all(
            callback=None).zip_up()
        DB.end()
        print(result)
        pdf_page_clip_dict: "dict[str,dict[int,list[str]]]" = {}
        for clip in result:
            pdf_path = objs.SrcAdmin.PDF_JSON[clip["pdfuuid"]]["pdf_path"]
            if clip["pdfuuid"] not in pdf_page_clip_dict:
                pdf_page_clip_dict[clip["pdfuuid"]] = {}
            if clip["pagenum"] not in pdf_page_clip_dict[clip["pdfuuid"]]:
                pdf_page_clip_dict[clip["pdfuuid"]][clip["pagenum"]] = []
            pdf_page_clip_dict[clip["pdfuuid"]][clip["pagenum"]].append(clip["uuid"])
            pass
        print(pdf_page_clip_dict)
        return pdf_page_clip_dict

        pass

    def init_UI(self):
        self.resize(800, 600)
        self.setWindowTitle("card pdf clip info")
        self.g_layout.addWidget(self.center_tree, 0, 0, 1, 1)
        # self.g_layout.addWidget(self.right_view,0,1,1,1)
        self.g_layout.addWidget(self.bottom_bar, 1, 0, 1, 2, alignment=Qt.AlignRight)
        self.setLayout(self.g_layout)

    def on_widget_button_correct_clicked_handle(self):
        # clipuuidli = [ idx.data(role=Qt.DisplayRole)  for idx in  self.center_tree.view.selectedIndexes()]
        indexli = self.center_tree.view.selectedIndexes()
        level1dict = {}
        for idx in indexli:
            page = idx.parent()
            pdf = page.parent()
            if pdf not in level1dict:
                level1dict[pdf] = {}
            if page not in level1dict[pdf]:
                level1dict[pdf][page] = []
            level1dict[pdf][page].append(idx)
        level2dict = {}
        for pdf, page in level1dict.items():  # {pdf:{pagenum:[clip]}
            for pagenum, idxli in page.items():
                pageitem = None  # 从这一层开始

                for idx in idxli:
                    clipuuid = idx.data(role=Qt.DisplayRole)
                    clipbox = objs.SrcAdmin.DB.go().select(uuid=clipuuid).return_all().zip_up()[0]
                    clipbox["card_id"] = str(self.card_id)
                    clipbox["card_uuid"] = self.card_uuid
                    # 如对应page是存在的,我们直接在这里完成插入工作
                    pdfpath = objs.SrcAdmin.PDF_JSON[clipbox["pdfuuid"]]["pdf_path"]
                    pdfpageuuid = funcs.uuid_hash_make(pdfpath + str(clipbox["pagenum"]))
                    if pdfpageuuid in ALL.clipper.all_pageitem_dict and len(
                            ALL.clipper.all_pageitem_dict[pdfpageuuid]) > 0:
                        pageitem = ALL.clipper.all_pageitem_dict[pdfpageuuid][-1]
                        self.callback_clipbox_create(kwargs=clipbox, pageitem=pageitem)
                    else:
                        if pageitem is None:
                            pageinfo = PageInfo(pdfpath, clipbox["pagenum"], clipbox["ratio"])
                            pageitem = PageItem5(pageinfo)
                            level2dict[pageitem] = []
                        level2dict[pageitem].append(clipbox)
        for pageitem, clipboxli in level2dict.items():
            e = events.PageItemAddToSceneEvent
            ALL.signals.on_pageItem_addToScene.emit(
                e(eventType=e.addPageType, pageItem=pageitem, callback=self.callback_clipboxli_create,
                  kwargs=clipboxli))

    def on_center_tree_view_doubleClicked_handle(self, index: "QModelIndex"):
        if index.data(Qt.UserRole) == self.center_tree.Item.API.clip:
            clipuuid = index.data(Qt.DisplayRole)
            if clipuuid in ALL.clipper.all_clipbox_dict:
                showInfo("选框已存在,不可重复添加\n clipbox already exists and cannot be added repeatedly")
                return
            e = events.PageItemAddToSceneEvent
            clipbox = objs.SrcAdmin.DB.go().select(uuid=clipuuid).return_all().zip_up()[0]
            clipbox["card_id"] = str(self.card_id)
            clipbox["card_uuid"] = self.card_uuid

            pdfpath = objs.SrcAdmin.PDF_JSON[clipbox["pdfuuid"]]["pdf_path"]
            pdfpageuuid = funcs.uuid_hash_make(pdfpath + str(clipbox["pagenum"]))
            if pdfpageuuid in ALL.clipper.all_pageitem_dict and len(ALL.clipper.all_pageitem_dict[pdfpageuuid]) > 0:
                pageitem = ALL.clipper.all_pageitem_dict[pdfpageuuid][-1]
                self.callback_clipbox_create(kwargs=clipbox, pageitem=pageitem)
            else:
                pageinfo = PageInfo(pdfpath, clipbox["pagenum"], clipbox["ratio"])
                pageitem = PageItem5(pageinfo)
                ALL.signals.on_pageItem_addToScene.emit(
                    e(eventType=e.addPageType, pageItem=pageitem, callback=self.callback_clipbox_create,
                      kwargs=clipbox))

    def callback_clipbox_create(self, kwargs=None, pageitem: "PageItem5" = None, pageitemlist=None):
        # 在这里创建clipbox, 发射信号
        W, H = pageitem.pageview.boundingRect().width(), pageitem.pageview.boundingRect().height()
        x, y, w, h = kwargs["x"] * W, kwargs["y"] * H, kwargs["w"] * W, kwargs["h"] * H
        rect = QRectF(x, y, w, h)
        pageitem.pageview.pageview_clipbox_add(rect=rect, clipbox_dict=kwargs)
        self.close()

    def callback_clipboxli_create(self, kwargs=None, pageitem: "PageItem5" = None, pageitemlist=None):
        for clip in kwargs:
            W, H = pageitem.pageview.boundingRect().width(), pageitem.pageview.boundingRect().height()
            x, y, w, h = clip["x"] * W, clip["y"] * H, clip["w"] * W, clip["h"] * H
            rect = QRectF(x, y, w, h)
            pageitem.pageview.pageview_clipbox_add(rect=rect, clipbox_dict=clip)
        self.close()

    class API:
        def __init__(self, parent: "CardClipboxPicker"):
            self.parent = parent
            self.on_widget_button_correct_clicked_handle = parent.on_widget_button_correct_clicked_handle

        @property
        def pdf_page_clip_dict(self):
            return self.parent.collect_info()

    class CenterTree(QWidget):
        """
        parent:pdfname [child:page]
        """

        def __init__(self, superior: "CardClipboxPicker"):
            super().__init__(superior)
            self.superior = superior
            self.view = QTreeView(self)
            self.model = QStandardItemModel(self)
            self.model_rootNode = self.model.invisibleRootItem()
            self.init_UI()

        def init_UI(self):
            H_layout = QHBoxLayout(self)
            H_layout.addWidget(self.view)
            self.setLayout(H_layout)
            self.view.setModel(self.model)
            self.view.setHeaderHidden(True)
            self.init_data()
            self.view.expandAll()
            self.view.setItemDelegate(self.Delegate(self, self.view))
            self.view.setSelectionMode(self.view.ExtendedSelection)

            pass

        def init_data(self):
            datadict: "dict[str,dict[int,list[str]]]" = self.superior.api.pdf_page_clip_dict
            for pdfuud, pagenum in datadict.items():
                pdfname = funcs.str_shorten(os.path.basename(objs.SrcAdmin.PDF_JSON[pdfuud]["pdf_path"]))
                pdfitem = self.Item(self, self.Item.API.pdf, pdfuud)
                self.model_rootNode.appendRow(pdfitem)
                for page in sorted(datadict[pdfuud].keys()):
                    pageitem = self.Item(self, self.Item.API.page, str(page))
                    pdfitem.appendRow(pageitem)
                    for clip in datadict[pdfuud][page]:
                        clipitem = self.Item(self, self.Item.API.clip, clip)
                        pageitem.appendRow(clipitem)

        class Delegate(QStyledItemDelegate):
            myRole = 999

            def __init__(self, superior: "CardClipboxPicker.CenterTree", *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.superior = superior

            def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
                item = self.superior.Item
                painter.save()
                if index.data(Qt.UserRole) == item.API.pdf:
                    pdfuuid = index.data(Qt.DisplayRole)
                    # rect=QRectF(option.rect.x(),option.rect.y(),option.rect.width()-1)
                    pdfname = funcs.str_shorten(os.path.basename(objs.SrcAdmin.PDF_JSON[pdfuuid]["pdf_path"]))
                    painter.drawText(option.rect, Qt.AlignLeft, pdfname)
                    pass
                elif index.data(Qt.UserRole) == item.API.page:
                    pdfuuid = index.parent().data(Qt.DisplayRole)
                    pagenum = int(index.data(Qt.DisplayRole))
                    page_shift = objs.SrcAdmin.PDF_JSON[pdfuuid]["page_shift"]
                    final_text = f"""PDF page at:{pagenum}  book page at:{pagenum - page_shift + 1}  """
                    painter.drawText(option.rect, Qt.AlignLeft, final_text)
                    pass
                elif index.data(Qt.UserRole) == item.API.clip:
                    DB = objs.SrcAdmin.DB.go()
                    clipuuid = index.data(Qt.DisplayRole)
                    clip = DB.select(uuid=clipuuid).return_all().zip_up()[0]
                    pdfname = objs.SrcAdmin.PDF_JSON[clip["pdfuuid"]]["pdf_path"]
                    pagenum = clip["pagenum"]
                    pixmap_ = funcs.png_pdf_clip(pdfname, pagenum, rect1=clip, ratio=clip["ratio"])
                    pixmap = funcs.Qpixmap_from_fitzpixmap(pixmap_)
                    rect = QRect(option.rect.x(), option.rect.y(), pixmap.size().width(), pixmap.size().height())
                    painter.drawPixmap(rect, pixmap)
                    if option.state & QStyle.State_Selected:
                        painter.setPen(QPen(QColor("#e3e3e5")))
                        painter.setBrush(QColor("#e3e3e5"))
                        # painter.fillRect(rect,QColor("#e3e3e5"))
                        painter.drawText(rect, Qt.AlignLeft, "✅")
                        # print("here is")

                    index.model().setData(index, [pixmap.size().width(), pixmap.size().height()], role=self.myRole)
                    pass
                else:
                    super().paint(painter, option, index)

            def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
                item = self.superior.Item
                if index.data(Qt.UserRole) == item.API.clip:
                    if index.data(self.myRole):
                        w, h = index.data(self.myRole)
                        return QSize(w + 3, h + 3)
                    else:
                        return super().sizeHint(option, index)
                else:
                    return super().sizeHint(option, index)

        class Item(QStandardItem):

            def __init__(self, superior: "CardClipboxPicker.CenterTree", character, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.superior = superior
                self.setData(character, role=Qt.UserRole)
                self.api = self.API(self)
                self.setFlags(self.flags() & ~ Qt.ItemIsEditable)
                if character != self.api.clip:
                    self.setFlags(self.flags() & ~Qt.ItemIsSelectable)

            class API:
                pdf, page, clip = 0, 1, 2

                def __init__(self, superior: "CardClipboxPicker.CenterTree.Item"):
                    self.superior = superior

    class RightView(QGraphicsView):
        def __init__(self, superior: "CardClipboxPicker"):
            super().__init__(superior)
            self.superior = superior

        def init_UI(self):
            pass

    class BottomBar(QWidget):
        def __init__(self, superior: "CardClipboxPicker"):
            super().__init__(superior)
            self.superior = superior
            self.widget_button_correct = QToolButton(self)
            self.widget_label_desc = QLabel("双击可直接添加,多选请点确认键\n"
                                            "Double-click to add directly.\n"
                                            "If to select more, click button to add →", parent=self)
            self.init_UI()
            self.all_event = objs.AllEventAdmin({
                self.widget_button_correct.clicked: self.superior.api.on_widget_button_correct_clicked_handle,
            }).bind()

        def init_UI(self):
            h_box = QHBoxLayout(self)
            self.widget_button_correct.setIcon(QIcon(objs.SrcAdmin.imgDir.correct))
            self.widget_button_correct.setIconSize(QSize(40, 40))
            self.widget_label_desc.setStyleSheet("font-size:13px;")
            h_box.addWidget(self.widget_label_desc)
            h_box.addWidget(self.widget_button_correct)
            h_box.setSpacing(0)
            self.setLayout(h_box)
            self.setContentsMargins(0, 0, 0, 0)
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = CardClipboxPicker(None, "1626526914101", "dftyhbvhj")
    p.show()
    sys.exit(app.exec_())
