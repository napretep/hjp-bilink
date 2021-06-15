import os
import time
from functools import reduce

from PyQt5 import QtGui
from PyQt5.QtCore import QRegExp, Qt, QObject, QPointF, QThread, pyqtSignal, QMutex, QRect, QRectF
from PyQt5.QtGui import QIcon, QRegExpValidator, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QToolButton, QSpinBox, QLineEdit, QDoubleSpinBox, QWidget, QGridLayout, QFileDialog, \
    QGraphicsView, QDialog, QTreeView, QVBoxLayout, QComboBox, QGraphicsPixmapItem, QApplication, QProgressBar

from ..fitz import fitz
from ..tools import funcs, objs, events


class ToolsBar(QWidget):
    def __init__(self, parent=None, pdfDirectory=None, pageNum=None, ratio=None, frompageitem=None, clipper=None):
        super().__init__(parent=parent)
        self.clipper = clipper
        self.pdfDir = pdfDirectory
        self.frompageitem = frompageitem
        self.pagenum_value = pageNum
        self.ratio_value = ratio
        self.g_layout = QGridLayout(self)
        self.open_button = QToolButton()
        self.open = objs.GridHDescUnit(parent=parent, widget=self.open_button)
        self.pagenum_lineEdit = QLineEdit()
        self.pagenum = objs.GridHDescUnit(parent=parent, widget=self.pagenum_lineEdit)
        self.ratio_DBspinbox = QDoubleSpinBox()
        self.ratio = objs.GridHDescUnit(parent=parent, widget=self.ratio_DBspinbox)
        self.newPage_button = QToolButton()
        self.update_button = QToolButton()
        self.bookmark_button = QToolButton()
        self.config_dict = objs.SrcAdmin.get_json()
        self.w_l = [self.bookmark_button, self.open, self.pagenum, self.ratio, self.update_button, self.newPage_button]
        self.g_pos = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
        self.init_UI()
        for i in range(len(self.w_l)):
            self.g_layout.addWidget(self.w_l[i], self.g_pos[i][0], self.g_pos[i][1])
        self.setLayout(self.g_layout)
        self.init_signals()
        self.init_events()
        self.state_check()

    def init_UI(self):
        self.init_open()
        self.init_ratio()
        self.init_button()
        self.init_pagenum()

    def init_open(self):
        self.open_button.setIcon(QIcon(objs.SrcAdmin.imgDir.item_open))
        self.open.widget.setToolTip("选择其他PDF/select other PDF")

    def init_ratio(self):
        self.ratio_DBspinbox.setRange(0.07, 100)
        self.ratio_DBspinbox.setSingleStep(0.1)
        value = self.ratio_value if self.ratio_value is not None else self.config_dict["page_ratio"]["value"]
        self.ratio_DBspinbox.setValue(value)
        self.ratio.setDescText("image ratio:")

    def init_pagenum(self):
        value = self.pagenum_value if self.pagenum_value is not None else self.config_dict["page_num"]["value"]
        self.pagenum_lineEdit.setText(str(value))
        self.pagenum_lineEdit.setValidator(QRegExpValidator(QRegExp("[\d,\-]+")))
        self.pagenum.setDescText("page at:")

    def init_button(self):
        self.update_button.setIcon(QIcon(objs.SrcAdmin.imgDir.refresh))
        self.newPage_button.setIcon(QIcon(objs.SrcAdmin.imgDir.item_plus))
        self.bookmark_button.setIcon(QIcon(objs.SrcAdmin.imgDir.bookmark))
        self.update_button.setToolTip("替换当前的页面/replace the current page")
        self.newPage_button.setToolTip("作为新页面插入/insert to the View as new page")

    def init_events(self):
        self.open_button.clicked.connect(self.file_open)
        self.newPage_button.clicked.connect(self.newpage_add)
        self.update_button.clicked.connect(self.update_current)
        self.bookmark_button.clicked.connect(self.bookmark_open)
        objs.CustomSignals.start().on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)

    def bookmark_open(self):
        objs.CustomSignals.start().on_pagepicker_bookmark_open.emit(events.OpenBookmarkEvent())

    def state_check(self):
        if self.open.label.toolTip() == "":
            self.newPage_button.setDisabled(True)
        else:
            self.newPage_button.setDisabled(False)
        if self.frompageitem is None:
            self.update_button.setDisabled(True)
        if self.frompageitem is not None:
            self.ratio_DBspinbox.setValue(self.frompageitem.pageinfo.ratio)
        else:
            self.ratio_DBspinbox.setValue(self.config_dict["page_ratio"]["value"])

    def update_current(self):
        pageinfo = self.packup_pageinfo()
        self.on_pageItem_changePage.emit(
            events.PageItemChangeEvent(pageInfo=pageinfo, pageItem=self.frompageitem,
                                       eventType=events.PageItemChangeEvent.updateType)
        )

    def newpage_add(self):
        pageinfo = self.packup_pageinfo()
        from ..PDFView_ import PageItem5
        pageitem = PageItem5(pageinfo, rightsidebar=self.clipper.rightsidebar)
        self.on_pageItem_addToScene.emit(
            events.PageItemAddToSceneEvent(pageItem=pageitem, eventType=events.PageItemAddToSceneEvent.addPageType))
        objs.CustomSignals.start().on_pagepicker_close.emit(
            events.PagePickerCloseEvent()
        )

    def packup_pageinfo(self):
        path = self.open.label.toolTip()
        pagenum = int(self.pagenum_lineEdit.text())
        ratio = self.ratio_DBspinbox.value()
        from ..PageInfo import PageInfo
        pageinfo = PageInfo(path, pagenum=pagenum, ratio=ratio)
        return pageinfo

    def pagenum_lineEdit_extractpagenum(self):
        pass

    def file_open(self):
        default_path = self.config_dict["default_path"]["value"] if self.config_dict["default_path"][
                                                                        "value"] != "" else "../../user_files"
        path = os.path.dirname(self.open.label.toolTip()) if self.open.label.toolTip() != "" else default_path
        fileName_choose, filetype = QFileDialog.getOpenFileName(self, "选取文件", path, "(*.pdf)")
        e = events.PDFOpenEvent
        objs.CustomSignals.start().on_pagepicker_PDFopen.emit(e(path=fileName_choose, sender=self))
        pass

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        if event.Type == event.PDFInitParseType:
            if event.path:
                self.open.label.setText(funcs.str_shorten(os.path.basename(event.path)))
            else:
                self.open.label.setText(event.path)
            self.open.label.setToolTip(event.path)
            self.state_check()

    def init_signals(self):
        self.on_pageItem_addToScene = objs.CustomSignals.start().on_pageItem_addToScene
        self.on_pageItem_changePage = objs.CustomSignals.start().on_pageItem_changePage

        pass

    pass


class LeftPart2(QWidget):
    """
    选择:多选，ctrl+多选，框选，checkbox
    书签:点击新增栏 button
    加载:缩略图(定制类) QGraphicsView
        下拉刷新,每次刷一个屏幕,需要 预先计算一个屏幕多少
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.pagepicker = parent
        self.PageLoadJob_isBussy = False
        self.col_per_row = 4  # TODO 改成配置表中读取
        self.pageItemList = []
        self.selectedItemList = []
        self.setAutoFillBackground(True)
        from . import LeftPart__
        self.scene = LeftPart__.Scene(parent=self)
        self.view = LeftPart__.View(parent=self, scene=self.scene, leftpart=self)
        self.progressBar = objs.GridHDescUnit(labelname="加载进度/loading progress", widget=QProgressBar())
        self.init_UI()
        self.init_events()

    def init_UI(self):
        self.setFixedSize(600, 800)
        V_layout = QVBoxLayout(self)
        V_layout.addWidget(self.view)
        V_layout.addWidget(self.progressBar)
        V_layout.setStretch(0, 1)
        V_layout.setStretch(1, 0)
        V_layout.setSpacing(0)
        self.setLayout(V_layout)
        # for i in range(6):
        #     self.setcombox.widget.addItem(f"{i+1}")

    def init_events(self):
        objs.CustomSignals.start().on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)
        objs.CustomSignals.start().on_pagepicker_leftpart_select.connect(
            self.on_pagepicker_leftpart_select_handle
        )
        objs.CustomSignals.start().on_pagepicker_PDFlayout.connect(self.on_pagepicker_PDFlayout_handle)

        pass

    def on_pagepicker_PDFlayout_handle(self, event: "events.PDFlayoutEvent"):
        if event.newLayoutType == event.Type and "col_per_row" in self.__dict__:
            main_frame_num = int(event.pagenum / (self.col_per_row * self.row_per_frame))
            for item in self.frame_list[main_frame_num]:
                if item is not None:
                    self.scene.addItem(item)
            if main_frame_num > 0:
                for item in self.frame_list[main_frame_num - 1]:
                    if item is not None:
                        self.scene.addItem(item)
            if main_frame_num < len(self.frame_list) - 1:
                for item in self.frame_list[main_frame_num + 1]:
                    if item is not None:
                        self.scene.addItem(item)
            firstItem: "Item2" = self.frame_list[main_frame_num][0]
            self.view.centerOn(firstItem)  # 只能用第一个item,不能用中间item
            #
            # from . import LeftPart__
            # job = LeftPart__.ReLayoutJob(frame_list=self.frame_list,)

    def on_selfcombox_currentIndexChanged_handle(self, index):
        w: "QComboBox" = self.setcombox.widget
        self.col_per_row = int(w.itemText(index))
        e = events.PDFParseEvent
        objs.CustomSignals.start().on_pagepicker_PDFparse.emit(
            e(sender=self, eventType=e.PDFInitParseType, doc=self.pagepicker.doc)
        )

    def on_pagepicker_leftpart_select_handle(self, event: "events.PagePickerLeftPartSelectEvent"):
        if event.Type == event.singleSelectType:
            self.selectedItemList = [event.sender]
        elif event.Type == event.multiSelectType:
            self.selectedItemList.append(event.sender)
        elif event.Type == event.multiCancelType:
            self.selectedItemList = []

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        """在解析阶段,应该初始化场景里的东西"""
        if event.Type == event.PDFInitParseType:
            self.pageItemList = []
            self.scene.clear()
            self.page_init_load(event.doc)
        elif event.Type == event.FrameLoadType:
            if self.frame_list[event.frame_idx][0] is None:
                self.job_1_frame_load(event.frame_idx)

    def job_1_frame_load(self, frame_idx):
        for frame_item_idx in range(len(self.frame_list[frame_idx])):
            pagenum = frame_idx * self.row_per_frame * self.col_per_row + frame_item_idx
            d = {"frame_idx": frame_idx, "frame_item_idx": frame_item_idx,
                 "pagenum": pagenum}
            X = (frame_item_idx % self.col_per_row) * self.unit_size
            Y = (frame_idx * self.row_per_frame + int(frame_item_idx / self.col_per_row)) * self.unit_size
            d["posx"] = X
            d["posy"] = Y
            d["show"] = True
            self.on_1_page_loaded_handle(d)
            w: "QProgressBar" = self.progressBar.widget
            w.setValue(int(frame_item_idx / len(self.frame_list[frame_idx]) * 100))
        self.progressBar.widget.setValue(int(100))

    def page_init_load(self, doc):
        from . import LeftPart__
        if not self.PageLoadJob_isBussy:
            w: "QProgressBar" = self.progressBar.widget
            w.setValue(0)
            self.page_init_load_job = LeftPart__.PageInitLoadJob(
                parent=self, doc=doc, view_size=self.size(), col_per_row=self.col_per_row, begin_page=100)
            self.page_init_load_job.on_job_begin.connect(lambda: self.__setattr__("PageLoadJob_isBussy", True))
            self.page_init_load_job.on_job_progress.connect(w.setValue)
            self.page_init_load_job.on_job_end.connect(lambda: self.__setattr__("PageLoadJob_isBussy", False))
            self.page_init_load_job.on_all_page_loaded.connect(self.on_all_page_loaded_handle)
            self.page_init_load_job.on_frame_partition_done.connect(self.on_frame_partition_done_handle)
            self.page_init_load_job.on_1_page_loaded.connect(self.on_1_page_loaded_handle)
            self.page_init_load_job.start()
        else:
            print("PageLoadJob_isBussy")

    def on_1_page_loaded_handle(self, item_dict):
        """

        Args:
            item_dict: {"frame_idx":int,"frame_item_idx":int,"pagenum":int,"posx":,"posy":,"show":True/False}

        Returns:

        """
        pixmap = funcs.pixmap_page_load(self.pagepicker.doc, item_dict["pagenum"], preview=True)
        from . import LeftPart__
        item = LeftPart__.Item2(pixmap=pixmap, pagenum=item_dict["pagenum"], unit_size=self.unit_size)
        item.setPos(item_dict["posx"], item_dict["posy"])
        self.frame_list[item_dict["frame_idx"]][item_dict["frame_item_idx"]] = item
        midlle = int(len(self.frame_list[item_dict["frame_idx"]]) / 2)
        middle_1st = midlle - (midlle) % self.col_per_row
        if item_dict["show"]:
            # print(f"""frame_idx = {item_dict["frame_idx"]}""")
            self.scene.addItem(item)
        if item_dict["frame_item_idx"] == middle_1st:
            print(middle_1st)
            self.view.centerOn(self.frame_list[item_dict["frame_idx"]][middle_1st])

    def on_all_page_loaded_handle(self, li):
        print(len(self.frame_list))
        # self.frame_list = li
        # self.pageItemList=reduce(lambda x, y: x+y,li)

    def on_frame_partition_done_handle(self, li):
        self.unit_size = li[0]
        self.row_per_frame = li[1]
        self.frame_list = li[2]
        total_row = self.row_per_frame * len(self.frame_list)
        self.scene.setSceneRect(QRectF(0, 0, self.col_per_row * self.unit_size, total_row * self.unit_size))

    def page_relayout(self, pagelist):
        for item in pagelist:
            self.scene.addItem(item)
        self.PageLoadJob_isBussy = False

    def pageitem_moveto_oldpage_bottom(self, old_item, new_item):
        new_pos = QPointF(old_item.x(), old_item.y() + old_item.boundingRect().height())
        new_item.setPos(new_pos)

    def pageitem_moveto_oldpage_left(self, old_item, new_item):
        new_pos = QPointF(old_item.x() + old_item.boundingRect().width(), old_item.y())
        new_item.setPos(new_pos)

    def pageitem_layout_arrange(self, pageitem, col_count):
        olditems_count = len(self.pageItemList)
        col = col_count
        rem = olditems_count % col
        if rem != 0:
            olditem = self.pageItemList[-1]
            self.pageitem_moveto_oldpage_left(olditem, pageitem)
        else:
            olditem = self.pageItemList[-col]
            self.pageitem_moveto_oldpage_bottom(olditem, pageitem)


class RightPart(QWidget):
    """
    上下页:
    放大缩小:
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(600, 800)
        self.init_UI()
        from . import RightPart__
        self.view: 'RightPart__.View'
        self.scene: "RightPart__.Scene"

    def init_UI(self):
        pass

    pass


class BookMarkItem(QStandardItem):
    def __init__(self, name=None, pagenum=None, level=1):
        super().__init__(name)
        self.pagenum = pagenum
        self.level = level
        self.setToolTip(name)
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)


class BookMark(QTreeView):
    """
    读取书签,treeview,点击加载,清空当前的内容进行加载
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        from ..PagePicker import PagePicker
        self.pagepicker: "PagePicker" = parent
        self.init_UI()
        self.init_model()
        self.init_events()
        self.hide()

    def init_UI(self):
        self.setMinimumWidth(150)
        self.setIndentation(10)
        pass

    def init_model(self):
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.root = self.model.invisibleRootItem()
        self.root.level = 0
        self.model.setHorizontalHeaderItem(0, QStandardItem("toc"))

    def init_events(self):
        objs.CustomSignals.start().on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)
        self.clicked.connect(self.on_self_clicked_handle)

    def on_self_clicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        # print(f"{item.text()},{item.pagenum}")
        row_per_frame = self.pagepicker.leftpart.row_per_frame
        col_per_row = self.pagepicker.leftpart.col_per_row
        frame_idx = int(item.pagenum / (row_per_frame * col_per_row))
        e = events.PDFParseEvent
        objs.CustomSignals.start().on_pagepicker_PDFparse.emit(
            e(sender=self, eventType=e.FrameLoadType, frame_idx=frame_idx)
        )

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        if event.Type == event.PDFInitParseType:
            self.load_bookmark(event.path, event.doc)

    def setup_toc(self, toc: 'list[list[int,str,int]]'):
        parentNode = []
        self.model.clear()
        last = BookMarkItem(name="virtual item")
        lastparent = self.root
        for i in toc:
            level, name, pagenum = i[0], i[1], i[2]
            item = BookMarkItem(name=name, level=level, pagenum=pagenum)
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

    def load_bookmark(self, path: str, doc):
        self.doc = doc
        self.toc = self.doc.get_toc()
        self.setup_toc(self.toc)

    pass
