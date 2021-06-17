class PagePickerPreviewerRatioAdjustEvent:
    ZoomInType = 0
    ZoomOutType = 1

    def __init__(self, sender=None, eventType=None):
        self.sender = sender
        self.Type = eventType if eventType is not None else self.ZoomInType


class PagePickerPreviewerReadPageEvent:
    fromBrowserType = 0
    fromCollectorType = 1
    reloadType = 2
    loadType = 3

    def __init__(self, sender=None, eventType=None, pagenum=None):
        self.sender = sender
        self.pagenum = pagenum
        self.Type = eventType if eventType is not None else self.fromBrowserType


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


class PDFParseEvent:
    PDFReadType = 0
    PDFInitParseType = 1  # 初始化的加载.
    FrameLoadType = 2  # 用于初始化之后加载
    JumpType = 3
    ScrollType = 4

    def __init__(self, focus=False,
                 sender=None, eventType=None, path=None, doc=None, frame_idx=None, pagenum=None):
        self.sender = sender
        self.Type = eventType if eventType is not None else self.PDFInitParseType
        self.path = path
        self.doc = doc
        self.frame_idx = frame_idx
        self.pagenum = pagenum
        self.focus = focus


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


class PagePickerBrowserSelectEvent:
    multiCancelType = 0
    multiSelectType = 1
    singleSelectType = 2
    singleCancelType = 3
    rubberbandType = 4
    collectType = 5

    def __init__(self, sender=None, eventType=None, rect=None, item=None):
        self.sender = sender
        self.rubberBandRect = rect
        self.item = item
        self.Type = eventType if eventType is not None else self.multiCancelType


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

    def __init__(self, eventType=None):
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


class PageItemResizeEvent:
    fullscreenType = 0
    resetType = 1

    def __init__(self, pageItem=None, eventType=None):
        self.pageItem = pageItem
        self.Type = eventType if eventType is not None else self.fullscreenType

        pass


class PageItemAddToSceneEvent:
    changePageType = 0
    addPageType = 1
    addMultiPageType = 2

    def __init__(self, sender=None, pageItem=None, pageItemList=None, eventType=None, parent=None):
        self.sender = sender
        self.pageItem = pageItem
        self.pageItemList = pageItemList
        self.Type = eventType
        self.parent = parent


class CardListDataChangedEvent:
    DataChangeType = 0

    def __init__(self, cardlist=None, eventType=None):
        self.Type = eventType if eventType else self.DataChangeType
        self.cardlist = cardlist
        pass


class PageItemClickEvent:
    clickType = 0
    rightClickType = 1
    leftClickType = 2

    def __init__(self, pageitem: 'PageItem5' = None, eventType=None):
        self.Type = eventType if eventType else self.clickType
        self.pageitem = pageitem


class CardListDeleteItemEvent:
    DeleteType = 0

    def __init__(self, cardlist=None, eventType=None):
        self.Type = eventType if eventType else self.DeleteType
        self.cardlist = cardlist
        pass


class RightSideBarButtonGroupEvent:
    resetViewRatioType = 0
    reLayoutType = 1
    QAswitchType = 2
    configType = 3
    correctType = 4

    def __init__(self, eventType=None):
        self.Type = eventType
        pass


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
