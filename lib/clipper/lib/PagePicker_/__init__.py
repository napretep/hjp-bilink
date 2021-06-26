import os
import re
import time
from functools import reduce

from PyQt5 import QtGui
from PyQt5.QtCore import QRegExp, Qt, QObject, QPointF, QThread, pyqtSignal, QMutex, QRect, QRectF, QTimer
from PyQt5.QtGui import QIcon, QRegExpValidator, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QToolButton, QSpinBox, QLineEdit, QDoubleSpinBox, QWidget, QGridLayout, QFileDialog, \
    QGraphicsView, QDialog, QTreeView, QVBoxLayout, QComboBox, QGraphicsPixmapItem, QApplication, QProgressBar, \
    QGraphicsItem

from ..fitz import fitz
from ..tools import funcs, objs, events, ALL

mutex = QMutex()


class Color:
    yellow = "yellow"
    red = "#DC143C"
    white = "white"

class ToolsBar(QWidget):
    def __init__(self, parent=None, pdfDirectory=None, pageNum=None, ratio=None, frompageitem=None, clipper=None):
        super().__init__(parent=parent)
        self.clipper = clipper
        self.pagepicker = parent
        self.pdfDir = pdfDirectory
        self.config_dict = objs.SrcAdmin.get_config("clipper")
        self.frompageitem = frompageitem
        self.pagenum_valueSet = set()
        self.pagenum_value = pageNum
        self.ratio_value = ratio if ratio is not None else self.config_dict["pagepicker.bottombar.page_ratio"]["value"]
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
        self.open_button.setToolTip("选择其他PDF/select other PDF")

    def init_ratio(self):
        self.ratio_DBspinbox.setRange(0.07, 100)
        self.ratio_DBspinbox.setSingleStep(0.1)
        value = self.ratio_value
        self.ratio_DBspinbox.setValue(value)
        self.ratio.setDescText("image ratio:")

    def init_pagenum(self):
        value = self.pagenum_value if self.pagenum_value is not None else \
        self.config_dict["pagepicker.bottombar.page_num"]["value"]
        self.pagenum_valueSet.add(int(value))
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
        self.ratio_DBspinbox.valueChanged.connect(self.on_ratio_DBspinbox_valueChanged_handle)
        self.open_button.clicked.connect(self.file_open)
        self.newPage_button.clicked.connect(self.newpage_add)
        self.update_button.clicked.connect(self.update_current)
        self.bookmark_button.clicked.connect(self.bookmark_open)
        self.pagenum_lineEdit.textChanged.connect(self.on_pagenum_lineEdit_textChanged_handle)
        ALL.signals.on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)
        ALL.signals.on_pagepicker_browser_select_send.connect(
            self.on_pagepicker_browser_select_send_handle
        )
        ALL.signals.on_pagepicker_previewer_ratio_adjust.connect(
            self.on_pagepicker_previewer_ratio_adjust_handle
        )

    def on_pagepicker_previewer_ratio_adjust_handle(self, event: "events.PagePickerPreviewerRatioAdjustEvent"):
        if event.Type == event.ZoomInType:
            self.ratio_DBspinbox.setValue(self.ratio_DBspinbox.value() + 0.1)
        elif event.Type == event.ZoomOutType:
            self.ratio_DBspinbox.setValue(self.ratio_DBspinbox.value() - 0.1)
        self.ratio_value = self.ratio_DBspinbox.value()

    def on_ratio_DBspinbox_valueChanged_handle(self, value):
        print(value)
        self.ratio_value = value
        e = events.PagePickerPreviewerReadPageEvent
        ALL.signals.on_pagepicker_preivewer_read_page.emit(
            e(sender=self, eventType=e.reloadType)
        )

    def on_pagenum_lineEdit_textChanged_handle(self, string):
        if not self.pagenumText_validity(string):
            self.pagenum_highlight(Color.red)
            self.update_button.setDisabled(True)
            self.newPage_button.setDisabled(True)
            return
        else:
            self.pagenum_highlight(Color.white)
            self.newPage_button.setDisabled(False)

        self.pagenumSet_pagenumText_convert(string)
        if len(self.pagenum_valueSet) == 1 and self.pagepicker.frompageitem is not None:
            self.update_button.setDisabled(False)
        else:
            self.update_button.setDisabled(True)

    def pagenumText_validity(self, string):

        return re.search(r"^(:?\d+,|\d+-\d+,)*(:?\d+-\d+|\d+)$", string)
        pass

    def pagenumSet_pagenumText_convert(self, string):
        self.pagenum_valueSet = set()
        li = string.split(",")
        for num in li:
            if "-" in num:
                LR = num.split("-")
                for i in range(int(LR[0]), int(LR[1]) + 1):
                    self.pagenum_valueSet.add(i)
            else:
                self.pagenum_valueSet.add(int(num))
        print(self.pagenum_valueSet)

    def on_pagepicker_browser_select_send_handle(self, event: "events.PagePickerBrowserSelectSendEvent"):
        if event.Type == event.appendType:
            self.pagenum_append(event.pagenumlist)
            if len(self.pagenum_valueSet) != 1:
                self.update_button.setDisabled(True)
            else:
                self.update_button.setDisabled(False)
        elif event.Type == event.overWriteType:
            self.pagenum_append(event.pagenumlist, overwrite=True)
        self.pagenum_highlight(Color.yellow)
        self.pagenum_highlight(Color.white, delay=1500)

    def pagenum_highlight(self, color, delay=None):
        if delay is None:
            self.pagenum_lineEdit.setStyleSheet(f"background-color:{color};")
        else:
            self.pagenum_highlight_timer = QTimer()
            self.pagenum_highlight_timer.singleShot(delay, lambda: self.pagenum_highlight(color))

    def pagenum_append(self, pagenumlist, overwrite=False):
        """统一整理, 唯一,3连号以上用横杠代替"""
        if overwrite:
            self.pagenum_valueSet = set(pagenumlist)
        else:
            self.pagenum_valueSet |= set(pagenumlist)
        li = list(self.pagenum_valueSet)
        li.sort()
        appendli = []
        if len(li) > 2:
            i, j = 0, 1
            while i < len(li):
                k = i
                while j < len(li) and li[j] - li[k] == 1:
                    k = j
                    j += 1

                if j - 1 == i:
                    appendli += [li[i]]
                elif j - 2 == i:
                    appendli += [li[i], li[i + 1]]
                else:
                    appendli += [li[i], "-", li[j - 1]]
                i = j
                j += 1
        else:
            appendli = li
        print(appendli)
        finalli = [str(item) for item in appendli]
        self.pagenum_lineEdit.setText(re.sub(",-,", "-", ",".join(finalli)))

    def bookmark_open(self):
        ALL.signals.on_pagepicker_bookmark_open.emit(events.OpenBookmarkEvent())

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
            self.ratio_DBspinbox.setValue(self.config_dict["pagepicker.bottombar.page_ratio"]["value"])

    def update_current(self):
        pageinfoli = self.packup_pageinfo()
        self.on_pageItem_changePage.emit(
            events.PageItemChangeEvent(pageInfo=pageinfoli[0], pageItem=self.frompageitem,
                                       eventType=events.PageItemChangeEvent.updateType)
        )

    def newpage_add(self):
        from ..PDFView_ import PageItem5
        pageinfoli = self.packup_pageinfo()
        pageitemli = [PageItem5(item, rightsidebar=self.clipper.rightsidebar) for item in pageinfoli]
        e = events.PageItemAddToSceneEvent
        QApplication.processEvents()
        self.on_pageItem_addToScene.emit(e(sender=self, pageItemList=pageitemli, eventType=e.addMultiPageType))
        # objs.CustomSignals.start().on_pagepicker_close.emit(
        #     events.PagePickerCloseEvent()
        # )

    def packup_pageinfo(self):
        path = self.open.label.toolTip()
        pagenumli = list(self.pagenum_valueSet)
        pagenumli.sort()
        pageinfoli = []
        ratio = self.ratio_DBspinbox.value()
        from ..PageInfo import PageInfo
        for pagenum in pagenumli:
            pageinfoli.append(PageInfo(path, pagenum=pagenum, ratio=ratio))
        return pageinfoli

    def pagenum_lineEdit_extractpagenum(self):
        pass

    def file_open(self):
        default_path = self.config_dict["pagepicker.bottombar.default_path"]["value"] if \
        self.config_dict["pagepicker.bottombar.default_path"][
            "value"] != "" else "../../user_files"
        path = os.path.dirname(self.open.label.toolTip()) if self.open.label.toolTip() else default_path
        fileName_choose, filetype = QFileDialog.getOpenFileName(self, "选取文件", path, "(*.pdf)")

        e = events.PDFOpenEvent
        ALL.signals.on_pagepicker_PDFopen.emit(
            e(path=fileName_choose, sender=self, beginpage=self.config_dict["pagepicker.bottombar.page_num"]["value"]))

        pass

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        if event.Type == event.PDFInitParseType:
            if event.path:
                self.open.label.setText(funcs.str_shorten(os.path.basename(event.path)))
            else:
                self.open.label.setText(event.path)
            self.open.label.setToolTip(event.path)
            pagenum = str(self.config_dict["pagepicker.bottombar.page_num"]["value"])
            self.pagenum_lineEdit.setText(pagenum)
            self.state_check()

    def init_signals(self):
        self.on_pageItem_addToScene = ALL.signals.on_pageItem_addToScene
        self.on_pageItem_changePage = ALL.signals.on_pageItem_changePage

        pass

    pass


class Browser(QWidget):
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
        self.frame_list = None
        self.col_per_row = 4  # TODO 改成配置表中读取
        self.row_per_frame = None
        self.unit_size = None
        self.pageItemList = []
        self.selectedItemList = []
        self.setAutoFillBackground(True)
        self.scene_shift_width = 40
        from . import Browser__
        self.scene = Browser__.Scene(parent=self)
        self.view = Browser__.View(parent=self, scene=self.scene, browser=self)
        self.bottomBar = Browser__.BottomBar(parent=self)
        # self.progressBar = objs.GridHDescUnit(labelname="加载进度/loading", widget=QProgressBar())
        self.init_UI()
        self.init_events()

    def init_UI(self):
        # self.setFixedSize(600, self.pagepicker.size().height()-100)
        self.setFixedWidth(600)
        V_layout = QVBoxLayout(self)
        V_layout.addWidget(self.view)
        V_layout.addWidget(self.bottomBar)
        V_layout.setStretch(0, 1)
        V_layout.setStretch(1, 0)
        V_layout.setSpacing(0)
        self.setLayout(V_layout)
        # for i in range(6):
        #     self.setcombox.widget.addItem(f"{i+1}")

    def init_events(self):
        ALL.signals.on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)
        ALL.signals.on_pagepicker_browser_select.connect(
            self.on_pagepicker_browser_select_handle
        )
        ALL.signals.on_pagepicker_PDFlayout.connect(self.on_pagepicker_PDFlayout_handle)

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

    def on_selfcombox_currentIndexChanged_handle(self, index):
        w: "QComboBox" = self.setcombox.widget
        self.col_per_row = int(w.itemText(index))
        e = events.PDFParseEvent
        ALL.signals.on_pagepicker_PDFparse.emit(
            e(sender=self, eventType=e.PDFInitParseType, doc=self.pagepicker.doc)
        )

    def on_pagepicker_browser_select_handle(self, event: "events.PagePickerBrowserSelectEvent"):
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
            self.frame_list = None
            self.scene.clear()
            self.page_load_handle(event.doc, pagenum=event.pagenum, focus=True)
        elif event.Type == event.JumpType:
            self.page_load_handle(event.doc, pagenum=event.pagenum, focus=True, select=True)
            pass
        elif event.Type == event.ScrollType:
            self.page_load_handle(event.doc, frame_idx=event.frame_idx)

            pass
        # elif event.Type == event.FrameLoadType:
        #     if self.frame_list[event.frame_idx][0] is None:
        #         self.job_1_frame_load(event.frame_idx)
        # if event.focus:
        #     frame_idx = None
        #     if event.frame_idx is not None:
        #         frame_idx = event.frame_idx
        #     if event.pagenum is not None:
        #         frame_idx = int(event.pagenum/(self.col_per_row*self.row_per_frame))
        #     if frame_idx is not None:
        #         self.focus_on(frame_idx)

    def focus_on(self, frame_idx):
        midlle = int(len(self.frame_list[frame_idx]) / 2)
        middle_1st = midlle - (midlle) % self.col_per_row
        self.view.centerOn(self.frame_list[frame_idx][middle_1st])

    def job_1_frame_load(self, frame_idx, show=True, focus=False):
        for frame_item_idx in range(len(self.frame_list[frame_idx])):
            pagenum = frame_idx * self.row_per_frame * self.col_per_row + frame_item_idx
            d = {"frame_idx": frame_idx, "frame_item_idx": frame_item_idx,
                 "pagenum": pagenum}
            X = (frame_item_idx % self.col_per_row) * self.unit_size
            Y = (frame_idx * self.row_per_frame + int(frame_item_idx / self.col_per_row)) * self.unit_size
            d["posx"] = X
            d["posy"] = Y
            d["show"] = show
            self.on_1_page_loaded_handle(d)
            time.sleep(0.005)
            w: "QProgressBar" = self.bottomBar.progressBar.widget
            w.setValue(int(frame_item_idx / len(self.frame_list[frame_idx]) * 100))
        self.bottomBar.progressBar.widget.setValue(int(100))

    def page_load_handle(self, doc, pagenum=None, frame_idx=None, focus=False, select=False):
        from . import Browser__

        if not self.PageLoadJob_isBussy:
            self.PageLoadJob_isBussy = True
            print("pageloadjob start")
            w: "QProgressBar" = self.bottomBar.progressBar.widget
            w.setValue(0)
            self.page_init_load_job = Browser__.PageInitLoadJob(
                browser=self, frame_idx=frame_idx, focus=focus, select=select, parent=self, doc=doc, begin_page=pagenum)

            self.page_init_load_job.on_job_progress.connect(w.setValue)
            self.page_init_load_job.on_frame_partition_done.connect(self.on_frame_partition_done_handle)
            self.page_init_load_job.on_1_page_loaded.connect(self.on_1_page_loaded_handle)
            self.page_init_load_job.on_all_page_loaded.connect(self.on_all_page_loaded_handle)

            self.page_init_load_job.start()

        else:
            print("PageLoadJob_isBussy")

    def on_1_page_loaded_handle(self, item_dict):
        """

        Args:
            item_dict: {"frame_idx":int,"frame_item_idx":int,"pagenum":int,"posx":,"posy":,"show":True/False}

        Returns:

        """
        pixmap = funcs.pixmap_page_load(self.pagepicker.doc, item_dict["pagenum"], browser=True)
        from . import Browser__
        item = Browser__.Item2(pixmap=pixmap, pagenum=item_dict["pagenum"], unit_size=self.unit_size)
        item.setPos(item_dict["posx"], item_dict["posy"])
        while True:
            if self.frame_list is not None and self.frame_list[item_dict["frame_idx"]] is not None:
                break
        self.frame_list[item_dict["frame_idx"]][item_dict["frame_item_idx"]] = item

        if item_dict["show"]:
            # print(f"""frame_idx = {item_dict["frame_idx"]}""")
            self.scene.addItem(item)

    def on_all_page_loaded_handle(self, s_dict):
        """

        Args:
            s_dict: frame  focus  select pagenum

        Returns:

        """
        if s_dict["focus"]:
            middle_1st = int(len(s_dict["frame"]) / 2) - int(len(s_dict["frame"]) / 2) % self.col_per_row
            self.view.centerOn(s_dict["frame"][middle_1st])
        if s_dict["select"]:
            from . import Browser__

            frame_item_idx = s_dict["pagenum"] % (self.col_per_row * self.row_per_frame)
            item: "Browser__.Item2" = s_dict["frame"][frame_item_idx]
            print(s_dict["frame"])
            e = events.PagePickerBrowserSelectEvent
            ALL.signals.on_pagepicker_browser_select.emit(
                e(sender=self, item=item, eventType=e.singleSelectType)
            )
        self.PageLoadJob_isBussy = False
        print("pageloadjob over")
        # self.frame_list = li
        # self.pageItemList=reduce(lambda x, y: x+y,li)

    def on_frame_partition_done_handle(self, li):
        self.unit_size = li[0]
        self.row_per_frame = li[1]
        self.frame_list = li[2]
        total_row = self.row_per_frame * len(self.frame_list)
        self.scene.setSceneRect(QRectF(0, 0, self.size().width() - self.scene_shift_width,
                                       total_row * self.unit_size))
        # self.view.setSceneRect(self.scene.sceneRect())
        # print("self.frame_list is None")

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


class Previewer(QWidget):
    """
    上下页:
    放大缩小:
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.pagepicker = parent
        self.doc = self.pagepicker.doc
        # self.setFixedSize(600, self.pagepicker.size().height()-100)
        self.setFixedWidth(600)
        from . import Previewer__
        self.scene: "Previewer__.Scene" = Previewer__.Scene(parent=self)
        self.view: 'Previewer__.View' = Previewer__.View(parent=self)
        # self.toolsbar:"Previewer__.ToolsBar" = Previewer__.ToolsBar(parent=self)
        self.ratio = self.pagepicker
        # self.hasItem = False
        self.pagenum = None
        self.init_UI()
        self.init_event()

    def init_UI(self):
        V_layout = QVBoxLayout(self)
        V_layout.addWidget(self.view)
        # V_layout.addWidget(self.toolsbar)
        V_layout.setStretch(0, 1)
        # V_layout.setStretch(1,0)
        self.setLayout(V_layout)

        pass

    def init_event(self):
        ALL.signals.on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)
        ALL.signals.on_pagepicker_preivewer_read_page.connect(
            self.on_pagepicker_preivewer_read_page_handle)

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        if event.Type == event.PDFInitParseType:
            self.scene.clear()
            e = events.PagePickerPreviewerReadPageEvent
            ALL.signals.on_pagepicker_preivewer_read_page.emit(
                e(sender=self, eventType=e.loadType, pagenum=event.pagenum)
            )

    def on_pagepicker_preivewer_read_page_handle(self, event: "events.PagePickerPreviewerReadPageEvent"):
        if event.Type == event.reloadType and self.pagenum is not None:
            self.scene_page_add(0, reload=True)
        elif event.Type == event.loadType:
            print(event.pagenum)
            self.scene_page_add(event.pagenum)
        pass

    def scene_page_add(self, pagenum, reload=False):
        from ..PageInfo import PageInfo
        ratio = self.pagepicker.ratio_value_get()
        doc = self.pagepicker.doc
        if reload:
            pageinfo = PageInfo(doc.name, self.pagenum, ratio)
        else:
            pageinfo = PageInfo(doc.name, pagenum, ratio)
            self.pagenum = pagenum
        item = QGraphicsPixmapItem(pageinfo.pagepixmap)
        # item.setFlag(QGraphicsItem.ItemIsMovable)
        self.scene.clear()
        self.scene.addItem(item)
        self.scene.setSceneRect(0, 0, item.boundingRect().width(), item.boundingRect().height())

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
        ALL.signals.on_pagepicker_PDFparse.connect(self.on_pagepicker_PDFparse_handle)
        self.clicked.connect(self.on_self_clicked_handle)

    def on_self_clicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        # print(f"{item.text()},{item.pagenum}")
        row_per_frame = self.pagepicker.browser.row_per_frame
        col_per_row = self.pagepicker.browser.col_per_row
        frame_idx = int(item.pagenum / (row_per_frame * col_per_row))
        e = events.PDFParseEvent
        ALL.signals.on_pagepicker_PDFparse.emit(
            e(sender=self, eventType=e.JumpType, pagenum=item.pagenum, frame_idx=frame_idx, focus=True)
        )
        e = events.PagePickerPreviewerReadPageEvent
        ALL.signals.on_pagepicker_preivewer_read_page.emit(
            e(sender=self, eventType=e.loadType, pagenum=item.pagenum))

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        if event.Type == event.PDFInitParseType:
            self.load_bookmark(event.path, event.doc)

    def setup_toc(self, toc: 'list[list[int,str,int]]'):
        parentNode = []
        self.model.clear()
        last = BookMarkItem(name="virtual item")
        lastparent = self.root
        for i in toc:
            level, name, pagenum = i[0], i[1], i[2] + self.doc_shift
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
        self.doc_shift = -1 if doc.xref_xml_metadata() != 0 else 0
        self.toc = self.doc.get_toc()
        self.setup_toc(self.toc)

    pass
