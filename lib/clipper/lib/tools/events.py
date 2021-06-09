class PageItemDeleteEvent:
    deleteType = 0

    def __init__(self, pageItem=None, eventType=None):
        self.pageItem = pageItem
        self.eventType = eventType


class PageItemChangeEvent:
    updateType = 0

    def __init__(self, pageInfo=None, pageItem=None, eventType=None):
        self.eventType = eventType
        self.pageItem = pageItem
        self.pageInfo = pageInfo


class PageItemResizeEvent:
    fullscreenType = 0
    resetType = 1

    def __init__(self, pageItem=None, eventType=None):
        self.pageItem = pageItem
        self.eventType = eventType

        pass


class PagePickerEvent:
    changePageType = 0
    addPageType = 1

    def __init__(self, pageItem=None, pageItemList=None, eventType=None, parent=None):
        self.pageItem = pageItem
        self.pageItemList = pageItemList
        self.eventType = eventType
        self.parent = parent


class CardListDataChangedEvent:
    DataChangeType = 0

    def __init__(self, cardlist=None, eventType=None):
        self.Type = eventType if eventType else self.DataChangeType
        self.cardlist = cardlist
        pass


class PageItemClickEvent:
    clickType = 0

    def __init__(self, pageitem: 'PageItem5' = None, eventType=None):
        self.eventType = eventType if eventType else self.clickType
        self.pageitem = pageitem


class CardListDeleteItemEvent:
    DeleteType = 0

    def __init__(self, cardlist=None, eventType=None):
        self.Type = eventType if eventType else self.DeleteType
        self.cardlist = cardlist
        pass
