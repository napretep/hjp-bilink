"""
这是一个实体,要保存各种数据,所有持久数据都存在这里,其他数据都是临时局部变量.
我将全部数据写在这里.他们将用dataclass进行封装.
将功能全部写成API形式
只读写,并不做其他和UI相关的操作
clipper.addpage
    pdfview.addpage
        container.append_data
        scene.additem
    RightSideBar.addpage
        pagelist.appendrow
clipper.delpage
    pdfview.delpage
        container.remove_data
        scene.remove_data
    rightsidebar.delpage
        model.remove_row
clipper.changepage
    pageitem.changepage
    rightsidebar.changepage
"""
import sys
from dataclasses import dataclass, field
from collections import OrderedDict, Set
from typing import Any, Union

from PyQt5.QtCore import pyqtSignal, QObject, QThread, QPointF, QPoint
from PyQt5.QtGui import QStandardItemModel
from .tools import objs, Worker, funcs
from .fitz import fitz


class Entity:
    """所有变量都不可访问,只能通过方法访问"""

    def __init__(self):
        self.signals = objs.CustomSignals().start()

        from .Clipper import Clipper, ScenePageLoader
        self.rightsidebar: "Entity.RightSideBar" = self.RightSideBar()
        self.pdfview: "Entity.PDFView" = self.PDFView()
        self.clipbox_container: "OrderedDict[str,Clipper]" = OrderedDict()

        self.pagepicker: "Entity.PagePicker" = self.PagePicker()
        self.config = objs.ConfigDict()
        self.schema = objs.JSONschema

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
        frompageItem: "Clipper.PageItem" = None

        def __post_init__(self):
            from .Clipper import Clipper
            self.frompageItem: "Clipper.PageItem" = None

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
    class PDFView:
        @dataclass
        class _ViewLayoutMode:
            Horizontal: "int" = 0
            Vertical: "int" = 1

        class PageItemContainer:
            def __init__(self):
                from .Clipper import Clipper
                def append_data(caller: "Clipper.PDFView", pageitem: "Clipper.PageItem"):
                    funcs.caller_check(Clipper.PDFView.addpage, caller, Clipper.PDFView)

                    pdfuuid = funcs.uuid_hash_make(pageitem.pageinfo.pdf_path)
                    pagenum = pageitem.pageinfo.pagenum
                    if not pdfuuid in self._pageBased_data:
                        self._pageBased_data[pdfuuid] = OrderedDict()
                    if pagenum not in self._pageBased_data[pdfuuid]:
                        self._pageBased_data[pdfuuid][pagenum] = []
                    self._pageBased_data[pdfuuid][pagenum].append(pageitem)
                    self._uuidBased_data[pageitem.uuid] = pageitem
                    # TODO cardBased_data以后再做

                def remove_data(caller: "Clipper.PDFView", pageitem: "Clipper.PageItem"):
                    funcs.caller_check(Clipper.PDFView.delpage, caller, Clipper.PDFView)
                    del self._uuidBased_data[pageitem.uuid]
                    pdfuuid = funcs.uuid_hash_make(pageitem.pageinfo.pdf_path)
                    pagenum = pageitem.pageinfo.pagenum
                    self._pageBased_data[pdfuuid][pagenum].remove(pageitem)

                    # TODO cardBased_data以后再做

                self._uuidBased_data: "OrderedDict[str,Clipper.PageItem]" = OrderedDict()
                self._pageBased_data = OrderedDict()
                self._cardBased_data = OrderedDict()
                self.append_data = append_data
                self.remove_data = remove_data

            # TODO cardbased_data的删除工作
            @property
            def uuidBased_data(self):
                return self._uuidBased_data

            @property
            def pageBased_data(self):
                return self._pageBased_data

            @property
            def cardBased_data(self):
                return self._cardBased_data

        class ClipBoxContainer:
            pass

        layoutmode: "_ViewLayoutMode" = _ViewLayoutMode()

        def __init__(self):
            from .Clipper import Clipper, ScenePageLoader
            self.scenepageload_worker: "ScenePageLoader" = None
            self.progresser: "objs.UniversalProgresser" = None
            self.pageitem_container: "Entity.PDFView.PageItemContainer" = self.PageItemContainer()
            self.clipbox_container: "Entity.PDFView.ClipBoxContainer" = self.ClipBoxContainer()

        pass

    @dataclass
    class _Card:
        pass

    @dataclass
    class OnePageLoadData:
        """用在pagepicker.browser上的worker线程传输on_1_page_load信号的数据"""
        frame_idx: "int"
        frame_item_idx: "int"
        pagenum: "int"
        x: "int"
        y: "int"
        percent: "float"
        pixmapdir: "str"
