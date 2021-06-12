import os

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtWidgets import QToolButton, QSpinBox, QLineEdit, QDoubleSpinBox, QWidget, QGridLayout, QFileDialog, \
    QGraphicsView, QDialog

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
        self.parent = parent
        self.open_button = QToolButton()
        self.open = objs.GridHDescUnit(parent=self.parent, widget=self.open_button)
        self.pagenum_lineEdit = QLineEdit()
        self.pagenum = objs.GridHDescUnit(parent=self.parent, widget=self.pagenum_lineEdit)
        self.ratio_DBspinbox = QDoubleSpinBox()
        self.ratio = objs.GridHDescUnit(parent=self.parent, widget=self.ratio_DBspinbox)
        self.newPage_button = QToolButton()
        self.update_button = QToolButton()
        self.config_dict = objs.SrcAdmin.get_json()
        self.w_l = [self.open, self.pagenum, self.ratio, self.update_button, self.newPage_button]
        self.g_pos = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
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
        if self.pdfDir != "" and self.pdfDir is not None:
            self.open.setDescText(funcs.str_shorten(os.path.basename(self.pdfDir)))
            self.open.setDescTooltip(self.pdfDir)
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
        self.update_button.setToolTip("替换当前的页面/replace the current page")
        self.newPage_button.setToolTip("作为新页面插入/insert to the View as new page")

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

    def init_events(self):
        self.open_button.clicked.connect(self.file_open)
        self.newPage_button.clicked.connect(self.newpage_add)
        self.update_button.clicked.connect(self.update_current)

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
        path = os.path.dirname(self.open.label.toolTip()) if self.open.label.toolTip() != "" else "../../user_files"
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                "选取文件", path,
                                                                "(*.pdf)"
                                                                )
        if fileName_choose != "":
            self.open.label.setText(funcs.str_shorten(os.path.basename(fileName_choose)))
            self.open.label.setToolTip(fileName_choose)
        self.state_check()
        pass

    def init_signals(self):
        self.on_pageItem_addToScene = objs.CustomSignals.start().on_pageItem_addToScene
        self.on_pageItem_changePage = objs.CustomSignals.start().on_pageItem_changePage

        pass

    pass


class LeftPart(QGraphicsView):
    """
    选择:多选，ctrl+多选，框选，
    书签:点击新增栏
    加载:缩略图(定制类)
        下拉刷新,每次刷一个屏幕,需要预先计算一个屏幕多少
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(400, 500)
        self.setAutoFillBackground(True)

    pass


class RightPart(QGraphicsView):
    """
    上下页:
    放大缩小:
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(400, 500)
        self.setStyleSheet("background-color:red;")
        self.setAutoFillBackground(True)

    pass


class BookMark(QDialog):
    """
    读取书签,treeview,点击加载,清空当前的内容进行加载
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    pass
