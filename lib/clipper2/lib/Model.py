"""
这是一个实体,要保存各种数据,所有持久数据都存在这里,其他数据都是临时局部变量.
我将全部数据写在这里.他们将用dataclass进行封装.
将功能全部写成API形式
只读写,并不做其他和UI相关的操作
DB->Entity->[UI,Controller]
UI负责展示,Controller负责事件处理和操作.
"""
from dataclasses import dataclass, field
from collections import OrderedDict, Set
from typing import Any, Union

from PyQt5.QtCore import pyqtSignal, QObject, QThread, QPointF, QPoint
from PyQt5.QtGui import QStandardItemModel
from .tools import objs, Worker
from .fitz import fitz


class Entity:
    """所有变量都不可访问,只能通过方法访问"""

    def __init__(self):
        self.signals = objs.CustomSignals().start()
        from .Clipper import Clipper
        self.rightsidebar: "Entity.RightSideBar" = self.RightSideBar()
        self.mainwindow: "Entity._MainWin" = self._MainWin()
        self.clipbox_dict: "OrderedDict[str,Clipper]" = OrderedDict()
        self.pagepicker: "Entity.PagePicker" = self.PagePicker()
        self.config = objs.ConfigDict()
        pass

    @dataclass
    class PagePicker:
        @dataclass
        class BookMark:
            model: "QStandardItemModel" = None

        @dataclass
        class Previewer:
            pagenum: "int" = None  # 仅供previewer使用,其他地方不可参考

        @dataclass
        class Browser:
            @dataclass
            class WorkerState:
                do: "bool" = False
                bussy: "bool" = False
                killself: "bool" = False
                frame_id: "int" = None

            @dataclass
            class View:
                begin_dragband: "bool" = False
                mousePressed: "bool" = False
                origin: "Union[QPointF,QPoint]" = None

            selectedItemList: "list" = field(default_factory=list)
            workerstate: "WorkerState" = WorkerState()
            view: "View" = View()
            worker: "Worker.FrameLoadWorker" = None
            col_per_row: "int" = None
            unit_size: "int" = None
            curr_frame_idx: "int" = None
            scene_shift_width: "int" = 40
            frame_list: "Any" = None
            row_per_frame: "int" = None
            wait_for_page_select: "int" = None  # 等待被选中的页面加载完成,才去highlight

        @dataclass
        class ToolsBar:
            collect_page_isvalide: "bool" = False
            collect_page_set: "set" = field(default_factory=set)

        toolsbar: "ToolsBar" = ToolsBar()
        browser: "Entity.PagePicker.Browser" = Browser()
        previewer: "Entity.PagePicker.Previewer" = Previewer()
        bookmark: "Entity.PagePicker.BookMark" = BookMark()
        ins: "Any" = None
        curr_pdf_path: "str" = None
        curr_pagenum: "int" = None  # 与jumpage的spinbox绑定.
        curr_doc: "fitz.Document" = None
        frompageItem: "Any" = None

        pass

    @dataclass
    class RightSideBar:
        @dataclass
        class CardList:
            model: "QStandardItemModel" = None
            pass

        @dataclass
        class PageList:
            model: "QStandardItemModel" = None

        cardlist: "Entity.RightSideBar.CardList" = CardList()
        pagelist: "Entity.RightSideBar.PageList" = PageList()
        pass

    @dataclass
    class _MainWin:
        pass

    @dataclass
    class _ClipBox:
        pass

    @dataclass
    class _PageItem:
        pass

    @dataclass
    class _Card:
        pass

    @dataclass
    class OnePageLoadData:
        frame_idx: "int"
        frame_item_idx: "int"
        pagenum: "int"
        x: "int"
        y: "int"
        percent: "float"
        pixmapdir: "str"
