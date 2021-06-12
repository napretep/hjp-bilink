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

    def __init__(self, pageItem=None, pageItemList=None, eventType=None, parent=None):
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
