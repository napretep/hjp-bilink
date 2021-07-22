import time
from dataclasses import dataclass, field
from collections import namedtuple
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QWidget, QGraphicsScene, QGraphicsView, QToolButton, QHBoxLayout, QApplication, \
    QVBoxLayout, QGridLayout, QTreeView, QLabel, QHeaderView, QAbstractItemView, QGraphicsItem, QGraphicsRectItem, \
    QGraphicsWidget, QGraphicsPixmapItem
from .tools import objs, events, ALL, funcs
from .Model import Entity

print, printer = funcs.logger(__name__)


class Clipper(QDialog):
    """空打开一定会加载,如果不空请手工加载."""

    def __init__(self, entity: "Entity"):
        super().__init__()
        self.E = entity
        # self.E.pagepicker.browser.worker=FrameLoadWorker(self.E)
        self.imgDir = objs.SrcAdmin.call().imgDir
        self.container0 = QWidget(self)
        self.scene = QGraphicsScene(self)
        self.pdfview = self.PDFView(self.scene, parent=self, superior=self)
        self.rightsidebar = self.RightSideBar(superior=self)
        self.widget_button_show_rightsidebar = QToolButton(self)
        self.init_UI()
        self.api = self.API(self)
        self.allevent = objs.AllEventAdmin({
            self.E.signals.on_pagepicker_open: self.on_pagepicker_open_handle
        }).bind()

    def init_UI(self):
        self.setWindowIcon(QIcon(self.imgDir.clipper))
        self.setWindowTitle("PDF clipper")
        self.setModal(False)
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.pdfview)
        self.h_layout.addWidget(self.rightsidebar)
        self.h_layout.setStretch(0, 1)
        rect = QApplication.instance().desktop().availableGeometry(self)
        self.resize(int(rect.width() * 2 / 3), int(rect.height() * 2 / 3))
        self.container0.resize(self.width(), self.height())
        self.container0.setLayout(self.h_layout)
        self.widget_button_show_rightsidebar.setIcon(QIcon(objs.SrcAdmin.imgDir.left_direction))
        self.widget_button_show_rightsidebar.move(self.geometry().width() - 20, self.geometry().height() / 2)
        self.widget_button_show_rightsidebar.hide()

    def resizeEvent(self, *args):
        self.container0.resize(self.width(), self.height())
        self.widget_button_show_rightsidebar.move(self.geometry().width() - 20, self.geometry().height() / 2)

        pass

    def start(self, pairs_li: "list[objs.Pair]" = None):
        if pairs_li:
            # 批量添加到cardlist
            # for pair in pairs_li:
            #     self.rightsidebar.card_list_add(desc=pair["desc"], card_id=pair["card_id"], newcard=False)
            # pdfinfo_dict = self.pdf_info_card_id_li_load(pairs_li)
            # pdf_page_ratio = []
            #
            # for k, v in pdfinfo_dict.items():
            #     PDF_JSON = objs.SrcAdmin.PDF_JSON
            #     if PDF_JSON.exists(k) and "ratio" in PDF_JSON[k]:
            #         ratio = PDF_JSON.read(k)["ratio"]
            #     else:
            #         ratio = 1
            #     for pagenum in v["pagenum"]:
            #         pdf_page_ratio.append((v["pdfname"], pagenum, ratio))
            #
            # if len(pdf_page_ratio) > 0:
            #     self.start_mainpage_loader(pdf_page_ratio)
            pass
        else:
            QTimer.singleShot(50, self.if_empty_start_pagepicker)

    def if_empty_start_pagepicker(self):
        if len(self.scene.items()) == 0:
            e = events.PagePickerOpenEvent
            self.E.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromMainWin))

    def on_pagepicker_open_handle(self, event: "events.PagePickerOpenEvent"):
        from .PagePicker import PagePicker
        if event.type == event.defaultType.fromMainWin:
            self.E.pagepicker.ins = PagePicker(parent=self, superior=self, root=self)

        elif event.type == event.defaultType.fromAddButton:
            self.E.pagepicker.ins = PagePicker(parent=self, superior=self, root=self)
        # self.E.pagepicker.browser.worker.start()
        self.E.pagepicker.ins.show()

    @dataclass
    class API:
        """API只能用在初始化之后的函数中,否则会出错容易"""

        def __init__(self, superior: "Clipper"):
            self.superior = superior

        def L1_PDFView_size(self):
            print(self.superior.pdfview.size())

        pass

    class PDFView(QGraphicsView):
        def __init__(self, scene, parent=None, superior: "Clipper" = None):
            super().__init__(parent)
            self.setScene(scene)
            self.superior = superior
            self.root = superior
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            # self.setRenderHints(QPainter.Antialiasing |  # 抗锯齿
            #                     QPainter.HighQualityAntialiasing |  # 高精度抗锯齿
            #                     QPainter.SmoothPixmapTransform)  # 平滑过渡 渲染设定
            self.setCacheMode(self.CacheBackground)  # 缓存背景图, 这个东西用来优化性能
            self.setViewportUpdateMode(self.SmartViewportUpdate)  # 智能地更新视口的图
            self.setDragMode(self.ScrollHandDrag)
            self.setCursor(Qt.ArrowCursor)
            self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().keyReleaseEvent(event)

        def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
            if event.buttons() == Qt.RightButton:
                self.setDragMode(QGraphicsView.RubberBandDrag)
                # funcs.show_clipbox_state()
            super().mousePressEvent(event)

        def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
            # print(self.scene().selectedItems())
            super().mouseMoveEvent(event)
            pass

        def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
            # if self.curr_selected_item is not None and self.curr_rubberBand_rect is not None:
            #     r = self.curr_rubberBand_rect
            #     pos = self.mapToScene(r.x(), r.y())
            #     x, y, w, h = pos.x(), pos.y(), r.width(), r.height()
            #     e = events.PageItemRubberBandRectSendEvent
            #     ALL.signals.on_pageItem_rubberBandRect_send.emit(
            #         e(sender=self.curr_selected_item, eventType=e.oneType, rubberBandRect=QRectF(x, y, w, h)))
            #     self.curr_selected_item = None
            #     self.curr_rubberBand_rect = None
            #     e = events.ClipboxCreateEvent
            #     ALL.signals.on_clipbox_create.emit(e(sender=self, eventType=e.rubbedType))

            super().mouseReleaseEvent(event)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            # e = events.ClipboxStateSwitchEvent
            #
            # ALL.signals.on_clipboxstate_switch.emit(
            #     e(sender=self, eventType=e.hideType)
            # )

        def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
            modifiers = QApplication.keyboardModifiers()

            if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
                # e = events.PDFViewResizeViewEvent
                # if event.angleDelta().y() > 0:
                #     self.scale(1.1, 1.1)
                #     self.reset_ratio_value *= 1.1
                #     ALL.signals.on_PDFView_ResizeView.emit(
                #         e(eventType=e.zoomInType, pdfview=self, ratio=self.reset_ratio_value))
                # else:
                #     self.scale(1 / 1.1, 1 / 1.1)
                #     self.reset_ratio_value /= 1.1
                #     ALL.signals.on_PDFView_ResizeView.emit(
                #         e(eventType=e.zoomOutType, pdfview=self, ratio=self.reset_ratio_value))
                pass
            else:
                super().wheelEvent(event)
            pass

        pass

    class RightSideBar(QWidget):
        def __init__(self, parent=None, superior: "Clipper" = None):
            super().__init__(parent)
            self.superior = superior
            self.root = superior

            self.pagelist = self.PageList(parent=self, superior=self, root=self.root)
            self.cardlist = self.CardList(parent=self, superior=self, root=self.root)
            self.buttonPanel = self.ButtonPanel(parent=self, superior=self, root=self.root)
            self.init_UI()

        def init_UI(self):
            self.V_layout = QVBoxLayout()
            self.V_layout.addWidget(self.pagelist)
            self.V_layout.addWidget(self.cardlist)
            self.V_layout.addWidget(self.buttonPanel)
            self.V_layout.setStretch(0, 1)
            self.V_layout.setStretch(1, 1)
            self.setLayout(self.V_layout)

        class PageList(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.view = QTreeView(self)
                self.model = QStandardItemModel(self)
                self.root.E.rightsidebar.pagelist.model = self.model
                self.V_layout = QVBoxLayout(self)
                self.addButton = QToolButton(self)
                self.delButton = QToolButton(self)
                self.init_UI()
                self.init_model()
                self.allevent = objs.AllEventAdmin({
                    self.addButton.clicked: self.on_addButton_clicked_handle
                }).bind()

            def on_addButton_clicked_handle(self):
                e = events.PagePickerOpenEvent
                self.root.E.signals.on_pagepicker_open.emit(e(type=e.defaultType.fromAddButton))

            def init_UI(self):
                H_layout = QHBoxLayout()
                V_layout2 = QVBoxLayout()
                self.label = QLabel("page list")
                self.addButton.setText("+")
                self.delButton.setText("-")
                self.V_layout.addLayout(H_layout)
                self.V_layout.addLayout(V_layout2)
                self.V_layout.setStretch(1, 1)
                self.view.setIndentation(0)
                H_layout.addWidget(self.label)
                H_layout.addWidget(self.addButton)
                H_layout.addWidget(self.delButton)
                V_layout2.addWidget(self.view)

            pass

            def init_model(self):
                pdfname = QStandardItem("PDFname")  # 存文件路径
                pagenum = QStandardItem("pagenum")  # 存页码和graphics_page对象
                self.model.setHorizontalHeaderItem(0, pdfname)
                self.model.setHorizontalHeaderItem(1, pagenum)
                self.pagepicker = None
                self.pageItemDict = {}
                self.view.setModel(self.model)
                self.view.header().setDefaultSectionSize(180)
                self.view.header().setSectionsMovable(False)
                self.view.header().setSectionResizeMode((QHeaderView.Stretch))
                self.view.setColumnWidth(1, 10)

        class CardList(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.model = QStandardItemModel(self)
                self.root.E.rightsidebar.cardlist.model = self.model
                self.label = QLabel(self)
                self.view = QTreeView(self)
                self.addButton = QToolButton(self)
                self.delButton = QToolButton(self)
                self.init_UI()

            def init_UI(self):
                H_layout = QHBoxLayout()
                V_layout2 = QVBoxLayout()
                self.label.setText("card list")
                self.V_layout = QVBoxLayout(self)
                self.addButton.setText("+")
                self.delButton.setText("-")
                self.view.setIndentation(0)
                self.view.header().setSectionResizeMode(QHeaderView.Stretch)

                H_layout.addWidget(self.label)
                H_layout.addWidget(self.addButton)
                H_layout.addWidget(self.delButton)
                V_layout2.addWidget(self.view)
                self.view.setDragEnabled(True)
                self.view.setDragDropMode(QAbstractItemView.InternalMove)
                self.view.setDefaultDropAction(Qt.MoveAction)
                self.view.setAcceptDrops(True)
                self.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
                self.view.dropEvent = self.dropEvent
                self.V_layout.addLayout(H_layout)
                self.V_layout.addLayout(V_layout2)
                self.V_layout.setStretch(1, 1)

            def init_model(self):
                self.newcardcount = 0
                self.ClipboxState = None
                # self.model=QStandardItemModel(self)
                # self.listView=QTreeView(self)
                self.model_rootNode = self.model.invisibleRootItem()
                self.model_rootNode.character = "root"
                self.model_rootNode.level = -1
                self.model_rootNode.primData = None
                label_id = self.CardItem("card_id", parent=self, superior=self, root=self.root)
                label_desc = self.DescItem("desc", parent=self, superior=self, root=self.root)
                self.model.setHorizontalHeaderItem(1, label_id)
                self.model.setHorizontalHeaderItem(0, label_desc)
                self.listView.setModel(self.model)
                self.listView.header().setDefaultSectionSize(150)
                self.listView.header().setSectionsMovable(False)
                self.listView.setColumnWidth(1, 10)

            class CardItem:
                def __init__(self, *agrs, parent=None, superior: "Clipper.RightSideBar.CardList" = None,
                             root: "Clipper" = None):
                    super().__init__(*agrs, parent=parent)
                    self.superior = superior
                    self.root = root

                pass

            class DescItem:
                def __init__(self, *agrs, parent=None, superior: "Clipper.RightSideBar.CardList" = None,
                             root: "Clipper" = None):
                    super().__init__(*agrs, parent=parent)
                    self.superior = superior
                    self.root = root

                pass

        class ButtonPanel(QWidget):
            def __init__(self, parent=None, superior: "Clipper.RightSideBar" = None, root: "Clipper" = None):
                super().__init__(parent)
                self.superior = superior
                self.root = root
                self.g_layout = QGridLayout(self)
                self.widget_button_QA = QToolButton(self)
                self.widget_button_hide = QToolButton(self)
                self.widget_button_confirm = QToolButton(self)
                self.widget_button_relayout = QToolButton(self)
                self.widget_button_config = QToolButton(self)
                self.widget_button_resetRatio = QToolButton(self)
                self.widget_button_clearView = QToolButton(self)
                e = events.RightSideBarButtonGroupEvent

                imgDir = objs.SrcAdmin.imgDir
                buttoninfoli = [(self.widget_button_hide, 0, imgDir.right_direction, e.hideRighsidebarType,
                                 "隐藏侧边栏\nhide rightsidebar"),
                                (self.widget_button_clearView, 1, imgDir.clear, e.clearViewType,
                                 "清空视图中的项目\nclear view items"),
                                (self.widget_button_resetRatio, 2, imgDir.reset, e.resetViewRatioType,
                                 "恢复视图为正常比例\nreset view size"),
                                (self.widget_button_QA, 3, imgDir.question, e.QAswitchType, "切换插入点为Q或A\nswitch Q or A"),
                                (self.widget_button_relayout, 4, imgDir.refresh, e.reLayoutType,
                                 "视图布局重置\nview relayout"),
                                (self.widget_button_config, 5, imgDir.config, e.configType, "配置选项\nset configuration"),
                                (self.widget_button_confirm, 6, imgDir.correct, e.correctType,
                                 "开始插入clipbox的任务\nBegin the task of inserting Clipbox",)
                                ]
                self.buttondatali = [self.ButtonData(*data) for data in buttoninfoli]
                self.init_UI()

            def init_UI(self):
                e = events.RightSideBarButtonGroupEvent
                for data in self.buttondatali:
                    data.button.setIcon(QIcon(data.icondir))
                    self.g_layout.addWidget(data.button, 0, data.layoutpos)
                    data.button.clicked.connect(
                        lambda: ALL.signals.on_rightSideBar_buttonGroup_clicked.emit(e(eventType=data.eventType)))
                    data.button.setToolTip(data.tooltip)

            @dataclass
            class ButtonData:
                button: "QToolButton"
                layoutpos: "int"
                icondir: "str"
                eventType: "int"
                tooltip: "str"

            pass

    class PageItem(QGraphicsItem):
        class PageView(QGraphicsPixmapItem):
            pass

        class ToolsBar(QGraphicsWidget):
            pass

        pass

    class ClipBox(QGraphicsRectItem):
        pass


class FrameLoadWorker(QThread):
    """专供使用"""
    on_frame_load_begin = pyqtSignal(object)  # {"frame_id","frame_list"}
    on_stop_load = pyqtSignal(object)  #
    on_1_page_load = pyqtSignal(object)  # {"frame_id","percent"}
    on_1_page_loaded = pyqtSignal(object)
    on_all_page_loaded = pyqtSignal()  #
    frame_id_default = None

    def __init__(self, E: "Entity" = None):
        super().__init__()
        self.E = E
        self.ws = self.E.pagepicker.browser.workerstate
        self.w = self.E.pagepicker.browser.worker
        self.b = self.E.pagepicker.browser
        self.p = self.E.pagepicker
        self.all_event = objs.AllEventAdmin({
            self.on_frame_load_begin: self.on_frame_load_begin_handle,
            self.on_stop_load: self.on_stop_load_handle,
            self.on_all_page_loaded: self.on_all_page_loaded_handle,
            self.on_1_page_loaded: self.on_1_page_loaded_handle,
        }).bind()

    def on_1_page_loaded_handle(self, _):
        self.ws.bussy = False
        # print("1 page loaded self.bussy = False")

    def on_all_page_loaded_handle(self):
        self.ws.killself = True

    def on_stop_load_handle(self, _):
        self.ws.do = False
        # self.frame_id = self.frame_id_default

    def on_frame_load_begin_handle(self, frame_id):
        self.ws.do = True
        self.ws.frame_id = frame_id

    def init_data(self, E: "Entity" = None, frame_list=None, doc=None, unit_size=None, col_per_row=None,
                  row_per_frame=None):
        self.E = E
        self.ws.bussy = False

    def run(self):
        while 1:
            if self.ws.killself:
                break
            # 从原有变量中提取出来, 因为很有可能在运行中变化.
            # print(self.bussy)
            print(
                f"self.do={self.ws.do},not bussy={not self.ws.bussy},self.doc={self.p.curr_doc},frame_id={self.ws.frame_id},")
            if self.ws.do and not self.ws.bussy and self.p.curr_doc is not None:
                print("begin")

                doc = self.p.curr_doc
                frame_id = self.ws.frame_id
                frame = self.b.frame_list[frame_id]
                unit_size = self.b.unit_size
                col_per_row = self.b.col_per_row
                row_per_frame = self.b.row_per_frame

                # print(f"frame.effective_len={frame.effective_len()},frame.blocks_full()={frame.blocks_full()}")
                if not frame.blocks_full():
                    self.ws.bussy = True
                    # self.on_1_page_load.emit({1:2})
                    self.browser_pageinfo_make(doc, frame, frame_id, col_per_row, row_per_frame, unit_size)
            # time.sleep(self.sleepgap())
            time.sleep(1)

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
