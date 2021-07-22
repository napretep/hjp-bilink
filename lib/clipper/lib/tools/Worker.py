import time
from typing import Union

from PyQt5.QtCore import QThread, pyqtSignal
from . import ALL, funcs, objs

print, printer = funcs.logger(__name__)


class FrameLoadWorker(QThread):
    """
    每次载入新的PDF,就开启这个
    传入 相关参数, 设计好位置再传回去
    """
    on_frame_load_begin = pyqtSignal(object)  # {"frame_id","frame_list"}
    on_stop_load = pyqtSignal(object)  #
    on_1_page_load = pyqtSignal(object)  # {"frame_id","percent"}
    on_1_page_loaded = pyqtSignal(object)
    on_all_page_loaded = pyqtSignal()  #
    on_quit = pyqtSignal()
    frame_id_default = None

    def __init__(self, parent=None, frame_list=None, doc=None, unit_size=None, col_per_row=None):
        super().__init__(parent=parent)
        self.unit_size = unit_size
        self.doc = doc
        self.frame_list = frame_list
        self.frame_id = self.frame_id_default
        self.killself = False
        self.col_per_row = col_per_row
        # self.sleepgap = 0.01
        self.do = False
        self.bussy = False
        self.event_dict = {
            self.on_frame_load_begin: self.on_frame_load_begin_handle,
            self.on_stop_load: self.on_stop_load_handle,
            self.on_all_page_loaded: self.on_all_page_loaded_handle,
            self.on_1_page_loaded: self.on_1_page_loaded_handle,
            self.on_quit: self.on_quit_handle,
        }
        self.all_event = objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def on_quit_handle(self):
        self.all_event.unbind()
        self.quit()

    def sleepgap(self):
        gap = 1
        if self.frame_list is not None:
            return gap / (self.row_per_frame * self.col_per_row) * 0.1
        else:
            return gap / 5

    def init_data(self, frame_list=None, doc=None, unit_size=None, col_per_row=None, row_per_frame=None):
        self.frame_list, self.doc, self.unit_size, self.col_per_row = frame_list, doc, unit_size, col_per_row
        self.row_per_frame = row_per_frame
        self.bussy = False

        # print("event binded")

    def on_1_page_loaded_handle(self, _):
        # print("1 page loaded self.bussy = False")
        self.bussy = False

    def on_all_page_loaded_handle(self):
        self.killself = True

    def on_stop_load_handle(self, _):
        self.do = False
        self.frame_id = self.frame_id_default

    def on_frame_load_begin_handle(self, frame_id):
        self.do = True
        self.frame_id = frame_id

    def run(self):
        while 1:
            if self.killself:
                break
            # 从原有变量中提取出来, 因为很有可能在运行中变化.
            # print(f"self.do={self.do},not bussy={not self.bussy},self.doc={self.doc},frame_id={self.frame_id},")
            if self.do and not self.bussy and self.doc is not None:
                # print("self.do and self.frame_list is not None")

                doc = self.doc
                frame_id = self.frame_id
                frame = self.frame_list[frame_id]
                unit_size = self.unit_size
                col_per_row = self.col_per_row
                row_per_frame = self.row_per_frame

                # print(f"frame.effective_len={frame.effective_len()},frame.blocks_full()={frame.blocks_full()}")
                if not frame.blocks_full():
                    self.bussy = True
                    self.browser_pageinfo_make(doc, frame, frame_id, col_per_row, row_per_frame, unit_size)
            time.sleep(self.sleepgap())

    # def handle_do(self):

    def browser_pageinfo_make(self, doc, frame, frame_id, col_per_row, row_per_frame, unit_size):
        # printer.debug("frame.blocks_full()=False")
        total = len(frame)
        frame_item_idx = frame.effective_len()  # 直接就下一个
        # row_per_frame = int(view_size.height() / unit_size)
        pagenum = frame_id * row_per_frame * col_per_row + frame_item_idx
        d = {"frame_idx": frame_id, "frame_item_idx": frame_item_idx,
             "pagenum": pagenum}
        X = (frame_item_idx % col_per_row) * unit_size
        Y = (frame_id * row_per_frame + int(frame_item_idx / col_per_row)) * unit_size
        d["posx"] = X
        d["posy"] = Y
        d["percent"] = (frame_item_idx + 1) / total
        d["pixmapdir"] = funcs.pixmap_page_load(doc, pagenum)
        self.on_1_page_load.emit(d)
        # print(d)
        # print(self)


class MainWindowPageLoadWorker(QThread):
    """执行任务,只处理一件事,生成图片地址"""
    from . import objs, funcs, ALL
    begin_state = 0
    middle_state = 1
    end_state = 2
    on_1_pagepath_loaded = pyqtSignal(object)
    on_all_pagepath_loaded = pyqtSignal(object)
    on_continue = pyqtSignal()
    on_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 将所需的信号与槽函数在线程内部连接,随线程的结束而自动解除连接
        self.signal_func_dict: "dict[str,list[callable,callable,Union[dict,None]]]" = None  # "signal_name":[signal,funcs,kwargs] 传入的信号与槽函数
        self.signal_sequence: "list[list[str]]" = None  # [["signal_name"]] 0,1,2 分别是前,中,后的回调函数.
        self.sleep_gap = 0.01
        self.pdf_page_list: "list[list[str,int]]" = None  # [[pdfdir,pagenum]]
        self.all_event = None
        self.ratio = None
        self.do = True
        self.complete = False

    def data_clear(self):
        self.signal_func_dict = None  # "signal_name":[signal,func] 传入的信号与槽函数
        self.signal_sequence = None  # ["signal_name",{"args":[],"kwargs":{}]
        self.pdf_page_list = None  # [[pdfdir,pagenum]]
        self.all_event.unbind()

    def data_load(self, ratio, signal_func_dict=None, signal_sequence=None, pdf_page_list=None):
        self.complete = False
        self.do = True
        self.ratio = ratio
        self.signal_sequence = signal_sequence
        if len(self.signal_sequence) != 3:
            raise ValueError("signal_sequence 的元素必须是 3个数组")
        self.signal_func_dict = signal_func_dict
        self.pdf_page_list = pdf_page_list
        self.event_dict = {}
        for k, v in self.signal_func_dict.items():
            if len(v) != 3:
                raise ValueError("signal_func_dict 的value必须是长度为3的数组")
            self.event_dict[v[0]] = v[1]
            if v[2] is not None:
                v[2]["type"] = self.__class__.__name__
        self.all_event = self.objs.AllEventAdmin(self.event_dict)
        self.all_event.bind()

    def run(self):

        for event_name in self.signal_sequence[0]:
            event = self.signal_func_dict[event_name][0]
            kwargs = self.signal_func_dict[event_name][2]
            if kwargs is not None:
                kwargs["state"] = self.begin_state
            event.emit(kwargs)
        total = len(self.pdf_page_list)
        i = 0
        while 1:
            if self.complete:
                break
            if self.do and i < total:
                self.do = False
                pair = self.pdf_page_list[i]
                ratio = self.ratio if len(pair) < 3 else pair[2]
                # print(f"pdfdir={pair[0]}")
                page_path = self.funcs.pixmap_page_load(pair[0], pair[1], ratio=ratio)
                for event_name in self.signal_sequence[1]:
                    event = self.signal_func_dict[event_name][0]
                    kwargs = self.signal_func_dict[event_name][2]
                    if kwargs is not None:
                        kwargs["state"] = self.middle_state
                        kwargs["ratio"] = self.ratio
                        kwargs["page_path"] = page_path
                        kwargs["index"] = i
                        kwargs["percent"] = i / total
                        kwargs["total_page_count"] = total
                        kwargs["pdf_page_list"] = self.pdf_page_list
                        kwargs["pdf_path"] = pair[0]
                        kwargs["page_num"] = pair[1]
                    event.emit(kwargs)
                i += 1
            time.sleep(self.sleep_gap)

        for event_name in self.signal_sequence[2]:
            event = self.signal_func_dict[event_name][0]
            kwargs = self.signal_func_dict[event_name][2]
            if kwargs is not None:
                kwargs["state"] = self.end_state
            event.emit(kwargs)

        self.data_clear()
        self.quit()

# frame_load_worker = FrameLoadWorker()
