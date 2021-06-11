import json
import os

from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QSpinBox, QFileDialog, QToolButton, \
    QDoubleSpinBox, QComboBox, QVBoxLayout, QFrame, QGridLayout

from .ConfigTable_ import ViewLayoutWidget, PagePresetWidget, ButtonGroup, OutPutWidget
from .funcs import str_shorten
from . import events, JSONschema_
from ..PageInfo import PageInfo
from . import SrcAdmin_

class CustomSignals(QObject):
    """用法: 在需要发射/接受信号的类中调用CustomSignals的类方法start(),并取出需要的信号绑定到本地变量,进行发射或接受"""
    instance = None
    linkedEvent = pyqtSignal()

    on_pageItem_clicked = pyqtSignal(object)  # PageItemClickEvent
    on_pageItem_clipbox_added = pyqtSignal(object)
    on_pageItem_resize_event = pyqtSignal(object)  # PageItemResizeEvent
    on_pageItem_resetSize_event = pyqtSignal(object)
    on_pageItem_nextPage_event = pyqtSignal(object)
    on_pageItem_prevPage_event = pyqtSignal(object)
    on_pageItem_changePage = pyqtSignal(object)  # PageItemChangeEvent
    on_pageItem_addToScene = pyqtSignal(object)  # PagePickerEvent
    on_pageItem_removeFromScene = pyqtSignal(object)

    on_pageItem_needCenterOn = pyqtSignal(object)  # PageItemNeedCenterOnEvent

    on_cardlist_dataChanged = pyqtSignal(object)  # CardListDataChangedEvent
    # 目前主要影响clipbox的toolsbar的cardcombox更新数据
    # 传送的数据用不起来

    on_cardlist_deleteItem = pyqtSignal(object)

    on_clipbox_closed = pyqtSignal(object)
    on_clipboxCombox_updated = pyqtSignal(object)
    on_clipboxCombox_emptied = pyqtSignal()

    on_rightSideBar_settings_clicked = pyqtSignal(object)
    on_rightSideBar_refresh_clicked = pyqtSignal(object)
    on_rightSideBar_buttonGroup_clicked = pyqtSignal(object)  #RightSideBarButtonGroupEvent

    on_clipper_hotkey_next_card = pyqtSignal()
    on_clipper_hotkey_prev_card = pyqtSignal()
    on_clipper_hotkey_setA = pyqtSignal()
    on_clipper_hotkey_setQ = pyqtSignal()

    @classmethod
    def start(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance

class PagePicker(QDialog):
    """接受目录和页码两个参数
    目录和页码可更改,加载书签,预览,
    可选择替换当前page或新增page, 如果父类不是pageItem,那自然不能替换
    """

    def __init__(self, pdfDirectory=None, pageNum=None, frompageitem=None, clipper=None, parent=None) -> object:
        super().__init__(parent=parent)
        self.pdfDir = pdfDirectory
        self.clipper = clipper
        self.frompageitem = frompageitem
        self.pageNum = pageNum
        self.path_label = QLabel()
        self.pagenum_label = QLabel()
        self.open_button = QToolButton()
        self.newPage_button = QToolButton()
        self.update_button = QToolButton()
        self.page_spinbox = QSpinBox()
        self.ratio_label = QLabel()
        self.ratio_spinbox = QDoubleSpinBox()
        self.init_UI()
        self.init_data()
        self.init_signals()
        self.init_events()
        self.init_label(pdfDirectory)
        if self.path_label.toolTip() == "":
            self.newPage_button.setDisabled(True)
        if self.frompageitem is None:
            self.update_button.setDisabled(True)
        if self.frompageitem is not None:
            self.ratio_spinbox.setValue(self.frompageitem.pageinfo.ratio)
        else:
            self.ratio_spinbox.setValue(1)
        self.show()

    def init_UI(self):
        self.setWindowIcon(QIcon(SrcAdmin.call().imgDir.bag))
        self.setWindowTitle("PDF page picker")
        H_layout = QHBoxLayout()
        self.pagenum_label.setText("page at:")
        self.open_button.setIcon(QIcon(SrcAdmin.call().imgDir.item_open))
        self.open_button.setToolTip("选择其他PDF/select other PDF")
        self.newPage_button.setIcon(QIcon(SrcAdmin.call().imgDir.item_plus))
        self.newPage_button.setToolTip("作为新页面插入/insert to the View as new page")
        self.update_button.setIcon(QIcon(SrcAdmin.call().imgDir.refresh))
        self.update_button.setToolTip("替换当前的页面/replace the current page")
        self.page_spinbox.setValue(self.pageNum)
        self.ratio_label.setText("image ratio:")
        self.ratio_spinbox.setRange(0.07, 100)
        self.ratio_spinbox.setSingleStep(0.1)
        H_layout.addWidget(self.path_label)
        H_layout.addWidget(self.open_button)
        H_layout.addWidget(self.pagenum_label)
        H_layout.addWidget(self.page_spinbox)
        H_layout.addWidget(self.ratio_label)
        H_layout.addWidget(self.ratio_spinbox)
        H_layout.addWidget(self.update_button)
        H_layout.addWidget(self.newPage_button)

        H_layout.setStretch(0, 1)
        self.setLayout(H_layout)
        self.setWindowModality(Qt.ApplicationModal)

        pass

    def init_data(self):
        pass

    def init_signals(self):
        self.on_pageItem_addToScene = CustomSignals.start().on_pageItem_addToScene
        self.on_pageItem_changePage = CustomSignals.start().on_pageItem_changePage

        pass

    def init_label(self, path, length=30):
        PDFname = os.path.basename(path)
        self.path_label.setText(str_shorten(PDFname))
        self.path_label.setToolTip(path)

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
        self.close()

    def newpage_add(self):
        pageinfo = self.packup_pageinfo()
        from ..PDFView_ import PageItem5
        pageitem = PageItem5(pageinfo, rightsidebar=self.clipper.rightsidebar)
        self.on_pageItem_addToScene.emit(
            events.PageItemAddToSceneEvent(pageItem=pageitem, eventType=events.PageItemAddToSceneEvent.addPageType))
        self.close()

    def packup_pageinfo(self):
        path = self.path_label.toolTip()
        pagenum = self.page_spinbox.value()
        ratio = self.ratio_spinbox.value()
        pageinfo = PageInfo(path, pagenum=pagenum, ratio=ratio)
        return pageinfo

    def file_open(self):
        path = os.path.dirname(self.path_label.toolTip()) if self.path_label.toolTip() != "" else "../../user_files"
        fileName_choose, filetype = QFileDialog.getOpenFileName(self,
                                                                "选取文件", path,
                                                                "(*.pdf)"
                                                                )
        if fileName_choose != '':
            path = fileName_choose.__str__()
            self.init_label(path)
            self.newPage_button.setDisabled(False)
            if self.frompageitem is not None:
                self.update_button.setDisabled(False)
        else:
            self.newPage_button.setDisabled(True)
            if self.frompageitem is not None:
                self.update_button.setDisabled(True)
        pass


class ConfigTable(QDialog):
    """
    line1 : 布局默认设置/set default layout property:方向/direction combox H/V,每行页数/pages per row spinbox
    line2 : 卡片默认设置/set default card property: 页码/pagenum spinbox , 画面比例/image ratio doublespinbox
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.config_dict = SrcAdmin.get_json("config.json")
        self.schema = JSONschema
        # self.V_layout= QVBoxLayout(self)
        self.G_Layout = QGridLayout(self)
        self.viewlayout = ViewLayoutWidget(parent=self, config_dict=self.config_dict, configtable=self)
        self.pagepreset = PagePresetWidget(parent=self, config_dict=self.config_dict, configtable=self, level=1)
        self.outputpreset = OutPutWidget(parent=self, config_dict=self.config_dict, configtable=self, level=2)
        self.buttonGroup = ButtonGroup(parent=self, configtable=self)
        self.init_UI()
        self.show()

    def init_UI(self):
        self.setWindowIcon(QIcon(SrcAdmin.imgDir.config))
        self.setWindowTitle("config")
        self.G_Layout.addWidget(self.buttonGroup, self.G_Layout.rowCount(), 2)
        self.setLayout(self.G_Layout)
        pass

    def init_data(self):
        pass


class SrcAdmin:
    """单例"""
    instance = None
    imgDir = SrcAdmin_.IMGDir()
    get_json = SrcAdmin_.get_json

    @classmethod
    def call(cls):
        """cls就相当于是self,这里的意思是如果instance不存在则创建一个,返回instance,这是单例模式"""
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance


class JSONschema:
    """JSON的数据规范"""
    type = JSONschema_.DataType()
    empty = JSONschema_.Empty()
    viewlayout_mode = JSONschema_.ViewLayout()
    needratiofix_mode = JSONschema_.NeedRatioFix()
