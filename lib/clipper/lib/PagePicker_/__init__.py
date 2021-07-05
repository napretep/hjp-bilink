import os
import re
from math import ceil

from PyQt5 import QtGui
from PyQt5.QtCore import QRegExp, Qt, QPointF, QMutex, QRectF, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QRegExpValidator, QStandardItem, QStandardItemModel, QPixmap
from PyQt5.QtWidgets import QToolButton, QLineEdit, QDoubleSpinBox, QWidget, QGridLayout, QFileDialog, \
    QTreeView, QVBoxLayout, QGraphicsPixmapItem, QApplication, QProgressDialog
from ..tools import funcs, objs, events, ALL, Worker

print, debugger = funcs.logger(logname=__name__)

mutex = QMutex()


class Color:
    yellow = "yellow"
    red = "#DC143C"
    white = "white"

class ToolsBar(QWidget):
    def __init__(self, parent=None, pdfpath=None, pageNum=None, ratio=None, frompageitem=None, clipper=None):
        super().__init__(parent=parent)
        self.clipper = clipper
        self.pagepicker = parent
        self.pdfDir = pdfpath
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
        self.mainwin_pageload_worker = None
        self.worker_signal_func_dict = None
        self.pageload_progress = None
        for i in range(len(self.w_l)):
            self.g_layout.addWidget(self.w_l[i], self.g_pos[i][0], self.g_pos[i][1])

        self.setLayout(self.g_layout)
        self.init_signals()
        self.event_dict = {
            self.ratio_DBspinbox.valueChanged: self.on_ratio_DBspinbox_valueChanged_handle,
            self.open_button.clicked: self.on_open_button_clicked_handle,
            self.newPage_button.clicked: self.on_newPage_button_clicked_handle,
            self.update_button.clicked: self.on_update_button_clicked_handle,
            self.bookmark_button.clicked: self.on_bookmark_button_clicked_handle,
            self.pagenum_lineEdit.textChanged: self.on_pagenum_lineEdit_textChanged_handle,
            ALL.signals.on_pagepicker_PDFparse: self.on_pagepicker_PDFparse_handle,
            ALL.signals.on_pagepicker_browser_select_send: self.on_pagepicker_browser_select_send_handle,
            ALL.signals.on_pagepicker_previewer_ratio_adjust: self.on_pagepicker_previewer_ratio_adjust_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
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
        self.ratio_DBspinbox_setValue(self.ratio_value)
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
        self.newPage_button.setIcon(QIcon(objs.SrcAdmin.imgDir.download))
        self.bookmark_button.setIcon(QIcon(objs.SrcAdmin.imgDir.bookmark))
        self.update_button.setToolTip("替换当前的页面/replace the current page")
        self.newPage_button.setToolTip("作为新页面插入/insert to the View as new page")

    def on_pagepicker_previewer_ratio_adjust_handle(self, event: "events.PagePickerPreviewerRatioAdjustEvent"):
        if event.Type == event.ZoomInType:
            self.ratio_DBspinbox_setValue(self.ratio_DBspinbox.value() + 0.1)
        elif event.Type == event.ZoomOutType:
            self.ratio_DBspinbox_setValue(self.ratio_DBspinbox.value() - 0.1)
        # self.ratio_value = self.ratio_DBspinbox.value()

    def ratio_DBspinbox_setValue(self, value):
        """public"""
        self.ratio_DBspinbox.setValue(value)
        self.ratio_value = self.ratio_DBspinbox.value()

    def on_ratio_DBspinbox_valueChanged_handle(self, value):
        # print(value)
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

    def on_bookmark_button_clicked_handle(self):
        ALL.signals.on_pagepicker_bookmark_open.emit(events.OpenBookmarkEvent())

    def state_check(self):
        if self.open.label.toolTip() == "":
            self.newPage_button.setDisabled(True)
        else:
            self.newPage_button.setDisabled(False)
        if self.frompageitem is None:
            self.update_button.setDisabled(True)
        if self.frompageitem is not None:
            self.ratio_DBspinbox_setValue(self.frompageitem.pageinfo.ratio)
        else:
            self.ratio_DBspinbox_setValue(self.config_dict["pagepicker.bottombar.page_ratio"]["value"])

    def on_update_button_clicked_handle(self):
        pageinfoli = self.packup_pageinfo()
        self.on_pageItem_changePage.emit(
            events.PageItemChangeEvent(pageInfo=pageinfoli[0], pageItem=self.frompageitem,
                                       eventType=events.PageItemChangeEvent.updateType)
        )

    def on_newPage_button_clicked_handle(self):

        pdf_path = self.open.label.toolTip()
        ratio = self.ratio_DBspinbox.value()
        page_num_li = self.packup_pageinfo()
        pdf_page_li = []
        for page_num in page_num_li:
            pdf_page_li.append([pdf_path, page_num])

        if self.mainwin_pageload_worker is None:
            self.mainwin_pageload_worker = Worker.MainWindowPageLoadWorker()

        self.worker_signal_func_dict = {
            "print": [self.mainwin_pageload_worker.on_1_pagepath_loaded, self.on_job_1_pagepath_loaded_handle, {}],
            "continue": [self.mainwin_pageload_worker.on_continue,
                         lambda: setattr(self.mainwin_pageload_worker, "do", True), None],
            "complete": [self.mainwin_pageload_worker.on_complete,
                         lambda: setattr(self.mainwin_pageload_worker, "complete", True), None],
            "over": [self.mainwin_pageload_worker.on_all_pagepath_loaded, self.pagepicker.close, None]
        }
        signal_sequence = [[], ["print"], ["over"]]

        self.mainwin_pageload_worker.data_load(ratio, signal_func_dict=self.worker_signal_func_dict,
                                               signal_sequence=signal_sequence, pdf_page_list=pdf_page_li)
        self.mainwin_pageload_worker.start()
        if self.pageload_progress is None:
            self.pageload_progress = objs.UniversalProgresser(self)

        # self.progress_signal_func_dict={
        #     "complete":[self.pageload_progress.on_close,self.pageload_progress.close,None]
        # }
        # self.pageload_progress.data_load()

    def on_job_1_pagepath_loaded_handle(self, kwargs):
        from ..PageInfo import PageInfo
        from ..PDFView_ import PageItem5
        print((f"""pagenum={kwargs["page_num"]}"""))
        pageitem = PageItem5(PageInfo(kwargs["pdf_path"], pagenum=kwargs["page_num"], ratio=kwargs["ratio"]),
                             rightsidebar=self.pagepicker.clipper.rightsidebar)
        e = events.PageItemAddToSceneEvent
        ALL.signals.on_pageItem_addToScene.emit(e(sender=self, pageItem=pageitem, eventType=e.addPageType))

        if kwargs["index"] != kwargs["total_page_count"] - 1:
            self.worker_signal_func_dict["continue"][0].emit()
            self.pageload_progress.valtxt_set(ceil(kwargs["percent"] * 100))
        else:
            self.worker_signal_func_dict["complete"][0].emit()
            self.pageload_progress.valtxt_set(100)
            self.pageload_progress.close_dely(200)

    def packup_pageinfo(self):
        # path = self.open.label.toolTip()
        # 如果有选中,则导入选中.
        pagenumli = self.pagepicker.browser.scene.selected_item_pagenum()
        if len(pagenumli) == 0:
            pagenumli = sorted(list(self.pagenum_valueSet))
        # pageinfoli = []
        # ratio = self.ratio_DBspinbox.value()
        # from ..PageInfo import PageInfo
        # for pagenum in pagenumli:
        #     pageinfoli.append(PageInfo(path, pagenum=pagenum, ratio=ratio))

        return pagenumli

    def pagenum_lineEdit_extractpagenum(self):
        pass

    def on_open_button_clicked_handle(self):
        default_path = self.config_dict["pagepicker.bottombar.default_path"]["value"] if \
            self.config_dict["pagepicker.bottombar.default_path"][
                "value"] != "" else objs.SrcAdmin.get.user_files_dir()
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
            pagenum = event.pagenum if event.pagenum else str(
                self.config_dict["pagepicker.bottombar.page_num"]["value"])
            self.pagenum_lineEdit.setText(str(pagenum))
            self.state_check()

    def init_signals(self):
        self.on_pageItem_addToScene = ALL.signals.on_pageItem_addToScene
        self.on_pageItem_changePage = ALL.signals.on_pageItem_changePage

        pass

    def __setattr__(self, key, value):
        if key in self.__dict__ and key == "ratio_value" and "ratio_DBspinbox" in self.__dict__:
            self.ratio_DBspinbox.setValue(value)
        self.__dict__[key] = value

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

        self.sleepgap = 0.001
        self.curr_frame_idx = None
        self.pagepicker = parent
        self.PageLoadJob_isBussy = False
        self.frame_list = None
        self.col_per_row = 4
        self.row_per_frame = None
        self.unit_size = None
        self.wait_for_page_select = None
        self.pageItemList = []
        self.selectedItemList = []
        self.setAutoFillBackground(True)
        self.scene_shift_width = 40
        self.frame_load_worker = Worker.frame_load_worker
        from . import Browser__
        self.scene = Browser__.Scene(parent=self)
        self.view = Browser__.View(parent=self, scene=self.scene)
        self.bottomBar = Browser__.BottomBar(parent=self)
        self.event_dict = {
            ALL.signals.on_pagepicker_PDFparse: (self.on_pagepicker_PDFparse_handle),
            ALL.signals.on_pagepicker_browser_select: (self.on_pagepicker_browser_select_handle),
            ALL.signals.on_pagepicker_browser_frame_changed: (self.on_pagepicker_browser_frame_changed_handle),
            self.frame_load_worker.on_1_page_load: (self.on_1_page_load_handle)
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

        self.init_UI()
        # self.init_events()
        # print("browser_init")

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

    # def init_events(self):
    #     funcs.event_handle_connect(self.event_dict)
    #     pass
    # def unbind_events(self):
    #     funcs.event_handle_disconnect(self.event_dict)
    #     print("browser event disconnected")
    def on_pagepicker_browser_frame_changed_handle(self, event: "events.PagePickerBrowserFrameChangedEvent"):
        if event.Type == event.FrameChangedType:
            self.frame_load_worker.do = False
            self.frame_load_worker.on_frame_load_begin.emit(event.frame_idx)

    # def worker_start(self,frame_idx):

    def frameidx_pagenum_at(self, pagenum):
        # print(f"colperrow={self.col_per_row},rowperframe={self.row_per_frame}")
        frame_idx = int(pagenum / (self.col_per_row * self.row_per_frame))
        print(frame_idx)
        return frame_idx

    def on_pagepicker_browser_select_handle(self, event: "events.PagePickerBrowserSelectEvent"):
        if event.Type == event.singleSelectType:
            self.selectedItemList = [event.sender]
        elif event.Type == event.multiSelectType:
            self.selectedItemList.append(event.sender)
        elif event.Type == event.multiCancelType:
            self.selectedItemList = []

    def on_pagepicker_PDFparse_handle(self, event: "events.PDFParseEvent"):
        """在解析阶段,应该初始化场景里的东西"""
        self.frame_load_worker.do = False
        if event.Type == event.PDFInitParseType:
            self.doc = event.doc
            self.init_basedata(event.pagenum)
            self.init_framelist()
            self.init_scene_size()
            self.scene.clear()
            self.frame_load_worker.init_data(frame_list=self.frame_list, doc=self.doc, unit_size=self.unit_size,
                                             col_per_row=self.col_per_row, row_per_frame=self.row_per_frame)
            frame_idx = self.frameidx_pagenum_at(event.pagenum)
            self.frame_load_worker.on_frame_load_begin.emit(frame_idx)
            self.focus_on(frame_idx)

        elif event.Type == event.JumpType:
            # self.page_load_handle(event.doc, pagenum=event.pagenum, focus=True, select=True)
            self.frame_load_worker.on_frame_load_begin.emit(event.frame_idx)
            self.focus_on(event.frame_idx)
            self.high_light(event.pagenum)
            pass
        elif event.Type == event.ScrollType:
            # self.page_load_handle(event.doc, frame_idx=event.frame_idx)
            # print(f"scroll type,frame_idx={event.frame_idx}")
            self.frame_load_worker.on_frame_load_begin.emit(event.frame_idx)
            pass

    #
    # def init_frame_load_worker(self):
    #     """初始化子线程"""
    #

    def init_basedata(self, pagenum):
        """初始化数据"""
        view_size = self.size()
        shift_width = self.scene_shift_width
        unit_size = int((view_size.width() - shift_width) / self.col_per_row)
        row_per_frame = int(view_size.height() / unit_size)
        self.unit_size = unit_size
        self.row_per_frame = row_per_frame
        self.curr_frame_idx = self.frameidx_pagenum_at(pagenum)

    def init_scene_size(self):
        height = self.row_per_frame * len(self.frame_list) * self.unit_size
        width = self.size().width() - self.scene_shift_width
        self.scene.setSceneRect(QRectF(0, 0, width, height))

    def init_framelist(self):
        """算出有多少个frame即可"""
        totalpage = len(self.doc)
        units_per_frame = self.col_per_row * self.row_per_frame
        total_frame_count = int(ceil(totalpage / units_per_frame))
        frame_list = [None] * total_frame_count
        last_frame_count = totalpage % units_per_frame
        from . import Browser__
        for i in range(total_frame_count):
            if i < total_frame_count - 1:
                frame_list[i] = Browser__.FrameItem(frame_list=frame_list, frame_unit_count=units_per_frame)
            else:
                frame_list[i] = Browser__.FrameItem(frame_list=frame_list, frame_unit_count=last_frame_count)
        self.frame_list = frame_list

    def high_light(self, page_num):
        self.scene.clearSelection()
        at_frame_idx = int(page_num / (self.row_per_frame * self.col_per_row))
        at_item_idx = page_num % (self.row_per_frame * self.col_per_row)
        page_item = self.frame_list[at_frame_idx][at_item_idx]
        if page_item is not None:
            page_item.setSelected(True)
        else:
            self.wait_for_page_select = page_num

        pass

    def focus_on(self, frame_idx):
        frame_center_y = (frame_idx + 0.5) * self.row_per_frame * self.unit_size
        frame_center_x = self.size().width() / 2
        # midlle = int(len(self.frame_list[frame_idx]) / 2)
        # middle_1st = midlle - (midlle) % self.col_per_row
        # self.view.centerOn(self.frame_list[frame_idx][middle_1st])
        self.view.centerOn(frame_center_x, frame_center_y)

    # def job_1_frame_load(self, frame_idx, show=True, focus=False):
    #     for frame_item_idx in range(len(self.frame_list[frame_idx])):
    #         pagenum = frame_idx * self.row_per_frame * self.col_per_row + frame_item_idx
    #         d = {"frame_idx": frame_idx, "frame_item_idx": frame_item_idx,
    #              "pagenum": pagenum}
    #         X = (frame_item_idx % self.col_per_row) * self.unit_size
    #         Y = (frame_idx * self.row_per_frame + int(frame_item_idx / self.col_per_row)) * self.unit_size
    #         d["posx"] = X
    #         d["posy"] = Y
    #         d["show"] = show
    #         self.on_1_page_loaded_handle(d)
    #         time.sleep(0.005)
    #         w: "QProgressBar" = self.bottomBar.progressBar.widget
    #         w.setValue(int(frame_item_idx / len(self.frame_list[frame_idx]) * 100))
    #     self.bottomBar.progressBar.widget.setValue(int(100))

    # def page_load_handle(self, doc, pagenum=None, frame_idx=None, focus=False, select=False):
    #     from . import Browser__
    #
    #     if not self.PageLoadJob_isBussy:
    #         self.PageLoadJob_isBussy = True
    #         print("pageloadjob start")
    #         w: "QProgressBar" = self.bottomBar.progressBar.widget
    #         w.setValue(0)
    #         self.page_init_load_job = Browser__.PageInitLoadJob(
    #             browser=self, frame_idx=frame_idx, focus=focus, select=select, parent=self, doc=doc, begin_page=pagenum)
    #
    #         self.page_init_load_job.on_job_progress.connect(w.setValue)
    #         self.page_init_load_job.on_frame_partition_done.connect(self.on_frame_partition_done_handle)
    #         self.page_init_load_job.on_1_page_loaded.connect(self.on_1_page_loaded_handle)
    #         self.page_init_load_job.on_all_page_loaded.connect(self.on_all_page_loaded_handle)
    #         self.page_init_load_job.start()
    #     else:
    #         print("PageLoadJob_isBussy")

    def on_1_page_load_handle(self, item_dict):
        """

        Args:
            item_dict: {"frame_idx":int,"frame_item_idx":int,"pagenum":int,"posx":,"posy":,"show":True/False}

        Returns:

        """
        pixmap = QPixmap(funcs.pixmap_page_load(self.pagepicker.doc, item_dict["pagenum"], browser=True))
        from . import Browser__
        item = Browser__.Item2(pixmap=pixmap, pagenum=item_dict["pagenum"], unit_size=self.unit_size, browser=self)
        item.setPos(item_dict["posx"], item_dict["posy"])
        # while self.frame_list is None or self.frame_list[item_dict["frame_idx"]] is None:
        #     time.sleep(self.sleepgap)
        self.frame_list[item_dict["frame_idx"]][item_dict["frame_item_idx"]] = item
        self.scene.addItem(item)
        self.frame_load_worker.on_1_page_loaded.emit(True)
        self.bottomBar.progressBar.setValue(ceil(item_dict["percent"] * 100))
        if self.wait_for_page_select is not None and self.wait_for_page_select == item_dict["pagenum"]:
            self.high_light(item_dict["pagenum"])

        # if item_dict["show"]:
        #     # print(f"""frame_idx = {item_dict["frame_idx"]}""")
        #     self.scene.addItem(item)

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

    # def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
    #     # if self.frame_load_worker.isRunning():
    #     #     self.frame_load_worker.killself=True
    #     #     self.frame_load_worker.exit()
    #
    #     super().closeEvent(a0)


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
                e(sender=self, eventType=e.loadType, pagenum=event.pagenum, doc=event.doc)
            )

    def on_pagepicker_preivewer_read_page_handle(self, event: "events.PagePickerPreviewerReadPageEvent"):
        if event.Type == event.reloadType and self.pagenum is not None:
            self.scene_page_add(0, reload=True)
        elif event.Type == event.loadType:
            self.scene_page_add(event.pagenum, newdoc=event.doc)
        pass

    def scene_page_add(self, pagenum, reload=False, newdoc=None):
        from ..PageInfo import PageInfo
        ratio = self.pagepicker.ratio_value_get()
        doc = newdoc if newdoc is not None else self.pagepicker.doc
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
        self.event_dict = {
            ALL.signals.on_pagepicker_PDFparse: (self.on_pagepicker_PDFparse_handle),
            self.clicked: (self.on_self_clicked_handle)
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()
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



    def on_self_clicked_handle(self, index):
        item = self.model.itemFromIndex(index)
        # print(f"{item.text()},{item.pagenum}")
        row_per_frame = self.pagepicker.browser.row_per_frame
        col_per_row = self.pagepicker.browser.col_per_row
        frame_idx = int(item.pagenum / (row_per_frame * col_per_row))
        e = events.PDFParseEvent
        ALL.signals.on_pagepicker_PDFparse.emit(
            e(sender=self, eventType=e.JumpType, pagenum=item.pagenum, frame_idx=frame_idx)
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
