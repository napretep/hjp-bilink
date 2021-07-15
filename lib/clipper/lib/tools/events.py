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


class ClipboxCreateEvent(AllEvent):
    rubbingType = 0
    rubbedType = 1

    def __init__(self, sender=None, eventType=None, rubberBandRect=None):
        super().__init__(sender, eventType)


class PageItemRubberBandRectSendEvent(AllEvent):
    oneType = 0

    def __init__(self, sender=None, eventType=None, rubberBandRect=None):
        super().__init__(sender, eventType)
        self.rubberBandRect = rubberBandRect


class PagePickerOpenEvent(AllEvent):
    fromPageType = 0
    fromAddButtonType = 1
    fromPageListType = 2

    def __init__(self, sender=None, eventType=None, clipper=None,
                 pdfpath=None, pagenum=None, fromPageItem=None):
        super().__init__(sender=sender, eventType=eventType)
        self.clipper = clipper
        self.pdfpath = pdfpath
        self.pagenum = pagenum
        self.fromPageItem = fromPageItem


class PagePickerBrowserFrameChangedEvent(AllEvent):
    FrameChangedType = 0

    def __init__(self, sender=None, eventType=None, frame_idx=None):
        super(PagePickerBrowserFrameChangedEvent, self).__init__(sender, eventType)
        self.frame_idx = frame_idx


class AnkiFileCreateEvent(AllEvent):
    ClipperCreatePNGType = 0
    ClipperCreatePNGDoneType = 1

    def __init__(self, sender=None, eventType=None, data=None, clipboxlist=None):
        super(AnkiFileCreateEvent, self).__init__(sender, eventType)
        self.data = data


class AnkiBrowserActivateEvent(AllEvent):
    ClipperTaskFinishedType = 0

    def __init__(self, sender=None, eventType=None, data=None):
        super(AnkiBrowserActivateEvent, self).__init__(sender, eventType)
        self.data = data


class AnkiFieldInsertEvent(AllEvent):
    ClipBoxBeginType = 0
    ClipBoxEndType = 1

    def __init__(self, sender=None, eventType=None, data=None):
        super().__init__(sender, eventType)
        self.data = data


class AnkiCardCreateEvent(AllEvent):
    ClipBoxType = 0

    def __init__(self, sender=None, eventType=None, data=None, model_id=None, deck_id=None):
        super().__init__(sender, eventType)
        self.data = data
        self.model_id = model_id
        self.deck_id = deck_id


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

class PagePickerPreviewerReadPageEvent:
    fromBrowserType = 0
    fromCollectorType = 1
    reloadType = 2
    loadType = 3

    def __init__(self, sender=None, eventType=None, pagenum=None, doc=None):
        self.sender = sender
        self.pagenum = pagenum
        self.doc = doc
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


class PageItemResizeEvent:
    fullscreenType = 0
    resetType = 1

    def __init__(self, pageItem=None, eventType=None, screen_width=None):
        self.pageItem = pageItem
        self.Type = eventType if eventType is not None else self.fullscreenType
        self.screen_width = screen_width
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

class RightSideBarButtonGroupEvent:
    resetViewRatioType = 0
    reLayoutType = 1
    QAswitchType = 2
    configType = 3
    correctType = 4
    clearViewType = 5

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
