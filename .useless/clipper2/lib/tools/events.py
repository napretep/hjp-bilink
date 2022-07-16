from collections import namedtuple
from dataclasses import dataclass

from typing import Any, Callable

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QStandardItem


@dataclass
class BaseEvent:  # 基础事件
    sender: "Any" = None
    type: "int" = None


@dataclass
class AnkiBrowserActivateEvent(BaseEvent):
    class _type:
        ClipperTaskFinished = 0

    defaultType: "_type" = _type()
    timestamp: "str" = None


@dataclass
class AnkiFileCreateEvent(BaseEvent):
    class _type:
        ClipperCreatePNG = 0

    worker: "Any" = None
    clipuuid: "str" = None
    defaultType: "_type" = _type()


@dataclass
class AnkiFieldInsertEvent(BaseEvent):
    class _type:
        clipboxNeed = 0

    worker: "Any" = None
    clipuuid: "str" = None
    timestamp: "str" = None
    defaultType: "_type" = _type()


@dataclass
class AnkiCardCreateEvent(BaseEvent):
    class _type:
        clipboxNeed = 0

    worker: "Any" = None
    carditem: "QStandardItem" = None
    model_id: "int" = None
    deck_id: "int" = None
    defaultType: "_type" = _type()


@dataclass
class ClipperHotkeyPressEvent(BaseEvent):
    class _type:
        setQ = 0
        setA = 1
        nextcard = 2
        prevcard = 3
        runmacro = 4
        pausemacro = 5

    defaultType: "_type" = _type


class RightSideBarButtonGroupEvent(BaseEvent):
    class _type:
        resetViewRatio = 0
        reLayout = 1
        QAswitch = 2
        config = 3
        correct = 4
        clearView = 5
        hideRighsidebar = 6
        macro = 7

    defaultType = _type()


@dataclass
class ClipboxCardChange(BaseEvent):
    class _type:
        delete = 0
        append = 1

    defaultType = _type()
    clipboxuuid: "str" = None
    carduuid: "str" = None


@dataclass
class ClipboxCreateEvent(BaseEvent):
    class _Type:
        rubbingType = 0
        rubbedType = 1
        NewPageCreateType = 2

    rubberBandRect: "QRectF" = None
    defaultType: "_Type" = _Type()
    type: "int" = None
    # def __init__(self, sender=None, eventType=None, rubberBandRect=None, clipuuid=None):
    #     super().__init__(sender, eventType)
    #     self.clipuuid = clipuuid


@dataclass
class PageItemResizeEvent(BaseEvent):
    class _Type:
        fullscreen = 0
        fitheight = 1
        recover = 2
        custom = 3

    class _centerType:
        mousecenter = 0
        item_center = 1
        view_center = 2
        nocenter = 3

    centertype = _centerType()
    defaultType = _Type()
    center: "int" = centertype.mousecenter
    ratio: "float" = None
    pass

@dataclass
class PageItemAddToSceneEvent(BaseEvent):
    """data和datali都是pageinfo"""

    class _type:
        changePage = 0
        addPage = 1
        addMultiPage = 2

    defaultType = _type()
    data: "Any" = None
    datali: "Any" = None
    callback: "Callable" = None

    def __post_init__(self):
        from . import objs
        data: "objs.PageInfo" = None
        datali: "list[objs.PageInfo]" = None


@dataclass
class PageItemCloseEvent(BaseEvent):
    pageitem: "Any" = None

    def __post_init__(self):
        from ..Clipper import Clipper
        self.pageitem: "Clipper.PageItem" = None


@dataclass
class PagePickerPreviewerReadPageEvent(BaseEvent):
    class _type:
        fromBrowser = 0
        fromBookmark = 1
        fromSpinbox = 4
        reloadType = 2
        loadType = 3

    defaultType: "_type" = _type()
    pagenum: "Any" = None
    doc: "Any" = None


@dataclass
class PagePickerBrowserSelectEvent(BaseEvent):
    class _Type:
        multiCancel = 0
        multiSelect = 1  # 插入
        singleSelect = 2  # 直接覆盖
        singleCancel = 3
        rubberband = 4
        collect = 5

    defaultType: "_Type" = _Type()
    rubberBandRect: "Any" = None
    item: "Any" = None
    type: "int" = None


@dataclass
class PagePickerBrowserLoadFrameEvent(BaseEvent):
    class _Type:
        initParse = 0
        continueLoad = 1
        Jump = 3
        Scroll = 4

    defaultType = _Type()
    pagenum: "int" = None
    frame_idx: "int" = None


@dataclass
class PagePickerPDFOpenEvent(BaseEvent):
    pdf_path: "str" = None
    pagenum: "int" = None


@dataclass
class PagePickerPDFParseEvent(BaseEvent):
    class _Type:
        PDFRead = 0
        PDFInitParse = 1  # 初始化的加载.
        FrameLoad = 2  # 用于初始化之后加载
        Jump = 3
        Scroll = 4

    defaultType = _Type()

    path: "str" = None
    doc: "str" = None
    frame_idx: "int" = None
    pagenum: "int" = None
    focus: "str" = None


@dataclass
class PagePickerOpenEvent(BaseEvent):
    # Type=namedtuple("Type","fromPage fromAddButton from  "
    class _Type:
        fromPage = 0
        fromAddButton = 1
        fromPageList = 2
        fromMainWin = 3

    defaultType = _Type()
    clipper: "Any" = None
    fromPageItem: "Any" = None
    pdfpath: "str" = None
    pagenum: "int" = None


class AllEvent:
    def __init__(self, sender=None, eventType=None):
        self.sender = sender
        self.Type = eventType


class PDFViewClickedEvent(AllEvent):
    leftclickType = 0
    rightclickType = 1
    doubleleftclickType = 2

    def __init__(self, sender=None, eventType=None):
        super().__init__(sender, eventType)


class PageItemMouseReleasedEvent(AllEvent):
    def __init__(self, sender=None, eventType=None, ):
        super().__init__(sender, eventType)


class ConfigAnkiDataLoadEvent(AllEvent):
    modelType = 0
    deckType = 1

    def __init__(self, sender=None, eventType=None, ankidata=None):
        super().__init__(sender, eventType)
        self.ankidata = ankidata


class ConfigAnkiDataLoadEndEvent(AllEvent):
    modelType = 0
    deckType = 1

    def __init__(self, sender=None, eventType=None, ankidata=None):
        super().__init__(sender, eventType)
        self.ankidata = ankidata





class PageItemRubberBandRectSendEvent(AllEvent):
    oneType = 0

    def __init__(self, sender=None, eventType=None, rubberBandRect=None):
        super().__init__(sender, eventType)
        self.rubberBandRect = rubberBandRect


class PagePickerBrowserFrameChangedEvent(AllEvent):
    FrameChangedType = 0

    def __init__(self, sender=None, eventType=None, frame_idx=None):
        super(PagePickerBrowserFrameChangedEvent, self).__init__(sender, eventType)
        self.frame_idx = frame_idx









class AnkiCardCreatedEvent(AllEvent):
    ClipBoxType = 0
    infoUpdateType = 1

    def __init__(self, sender=None, eventType=None, data=None):
        super().__init__(sender, eventType)
        self.data = data


class PageItemUpdateEvent(AllEvent):
    pageNumType = "pagenum"
    docNameType = "docname"
    ratioType = "ratio"

    def __init__(self, sender=None, eventType=None, data=None):
        super(PageItemUpdateEvent, self).__init__(sender=sender, eventType=eventType)
        self.data = data


class ClipBoxToolsbarUpdateEvent(AllEvent):
    QAButtonType = "QA"
    TextQAButtonType = "textQA"
    TextType = "text"
    Card_id_Type = "card_id"

    def __init__(self, sender=None, eventType=None, data=None):
        super().__init__(sender, eventType)
        self.data = data


class CardListAddCardEvent:
    parseStrType = 0
    returnPairLiType = 1
    newCardType = 2

    def __init__(self, sender=None, eventType=None, html=None, pairli=None):
        self.sender = sender
        self.eventType = eventType if eventType is not None else self.parseStrType
        self.html = html
        self.pairli = pairli


class ClipboxStateSwitchEvent(AllEvent):
    showType = 0
    hideType = 1
    showedType = 3
    hiddenType = 4

    def __init__(self, sender=None, eventType=None):
        super().__init__(sender, eventType)


class PageItemCenterOnProcessEvent:
    def __init__(self, centerpos=None):
        self.centerpos = centerpos


class PagePickerPreviewerRatioAdjustEvent(AllEvent):

    def __init__(self, sender=None, eventType=None, data=None):
        super().__init__(sender, eventType)
        self.data = data


class PagePickerBrowserSelectSendEvent:
    appendType = 0
    overWriteType = 1

    def __init__(self, sender=None, eventType=None, pagenumlist=None):
        self.sender = sender
        self.Type = eventType if eventType is not None else self.appendType
        self.pagenumlist = pagenumlist


class PDFlayoutEvent:
    newLayoutType = 0  # 全新的布局,说明原来不存在

    def __init__(self, sender=None, eventType=None, pagenum=None, doc=None):
        self.sender = sender
        self.Type = eventType if eventType is not None else self.newLayoutType
        self.pagenum = pagenum


class PagePickerBrowserSceneClear:
    clearType = 0

    def __init__(self, sender=None, eventType=None):
        self.sender = sender
        self.Type = eventType if eventType is not None else self.clearType


class PagePickerRightPartPageReadEvent:
    fromBookmarkType = 0
    fromBrowserType = 1

    def __init__(self, sender=None, eventType=None):
        self.sender = sender
        self.Type = eventType if eventType is not None else self.fromBrowserType


class PagePickerBrowserPageClickedEvent:
    ClickedType = 0

    def __init__(self, sender=None, eventType=None, path=None):
        self.sender = sender
        self.Type = eventType if eventType is not None else self.ClickedType


class PDFOpenEvent:
    PDFReadType = 0
    PDFParseType = 1

    def __init__(self, sender=None, eventType=None, path=None, doc=None, beginpage=0):
        self.sender = sender
        self.beginpage = beginpage
        self.Type = eventType if eventType is not None else self.PDFReadType
        self.path = path
        self.doc = doc


class BookmarkClickedEvent:
    clickType = 0

    def __init__(self, eventType=None):
        self.Type = eventType if eventType is not None else self.clickType


class OpenBookmarkEvent:
    PagePickerOpenType = 0

    def __init__(self, eventType=None):
        self.Type = eventType if eventType is not None else self.PagePickerOpenType


class PagePickerCloseEvent:
    closeType = 0

    def __init__(self, eventType=None, sender=None):
        self.Type = eventType


class PageItemDeleteEvent:
    deleteType = 0

    def __init__(self, pageItem=None, eventType=None):
        self.Type = eventType
        self.pageItem = pageItem


class PageItemChangeEvent:
    updateType = 0

    def __init__(self, pageInfo=None, pageItem=None, eventType=None):
        self.Type = eventType
        self.pageItem = pageItem
        self.pageInfo = pageInfo





class CardListDataChangedEvent(AllEvent):
    DataChangeType = 0
    TextChangeType = 1
    DescChangeType = 2
    CardIdChangeType = 3
    deleteType = 4
    dragDropType = 5

    def __init__(self, sender=None, cardlist=None, eventType=None, data=None):
        super().__init__(sender, eventType)
        self.cardlist = cardlist
        self.data = data
        pass


class PageItemClickEvent(AllEvent):
    clickType = 0
    ctrl_rightClickType = 1
    leftClickType = 2
    rightClickType = 3

    def __init__(self, sender=None, pageitem: 'PageItem5' = None, eventType=None):
        super().__init__(sender, eventType)
        self.Type = eventType if eventType else self.clickType
        self.pageitem = pageitem


class CardListDeleteItemEvent:
    DeleteType = 0

    def __init__(self, cardlist=None, eventType=None):
        self.Type = eventType if eventType else self.DeleteType
        self.cardlist = cardlist
        pass


class CardListSelectItemEvent(AllEvent):
    singleRowType = 0

    def __init__(self, sender=None, eventType=None, rowNum=None):
        super().__init__(sender, eventType)
        self.rowNum = rowNum




class PageItemNeedCenterOnEvent:
    centerOnType = 0

    def __init__(self, eventType=None, pageitem=None):
        self.Type = eventType
        self.pageitem = pageitem
        pass


class PDFViewResizeViewEvent:
    zoomInType = 0
    zoomOutType = 1
    RatioResetType = 2

    def __init__(self, eventType=None, pdfview=None, ratio=None):
        self.Type = eventType
        self.pdfview = pdfview
        self.ratio = ratio
