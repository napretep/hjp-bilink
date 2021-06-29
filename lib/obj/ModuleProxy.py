"""用于实现跨三级模块以上的信息交互"""
from aqt import mw
from aqt.utils import showInfo

from .tools import objs, events, funcs, ALL
from .backlink_reader import BackLinkReader
from . import ModuleProxyfunc


def on_cardlist_addCard_handle(event: "events.CardListAddCardEvent"):
    """添加来自anki现有的卡片"""
    if event.eventType == event.parseStrType:
        pairli = [(item["desc"], item["card_id"]) for item in BackLinkReader(html_str=event.html).backlink_get()]
        e = events.CardListAddCardEvent
        ALL.signals.on_cardlist_addCard.emit(
            e(sender=on_cardlist_addCard_handle, eventType=e.returnPairLiType, pairli=pairli))


def on_anki_create_card_handle(event: "events.AnkiCardCreateEvent"):
    """新建卡片,并发射卡片回去"""
    e = events.AnkiCardCreatedEvent
    if event.Type == event.ClipBoxType:
        self = event.sender
        data = ModuleProxyfunc.anki_create_card_handle[event.ClipBoxType](event.model_id, event.deck_id)

        ALL.signals.on_anki_card_created.emit(
            e(eventType=e.ClipBoxType, data=data)
        )


def on_anki_field_insert_handle(event: "events.AnkiFieldInsertEvent"):
    """将clipbox的信息插入卡片字段"""
    e = events.AnkiFieldInsertEvent
    if event.Type == event.ClipBoxBeginType:
        self = event.sender
        clipboxlist = event.data
        timestamp = ModuleProxyfunc.anki_field_insert_handle[event.ClipBoxBeginType](self, clipboxlist)
        ALL.signals.on_anki_field_insert.emit(e(eventType=e.ClipBoxEndType, data=timestamp))


def on_anki_browser_activate_handle(event: "events.AnkiBrowserActivateEvent"):
    if event.Type == event.ClipperTaskFinishedType:
        mw.browser.model.search(f"tag:{event.data}")
        mw.browser.activateWindow()


def on_anki_file_create_handle(event: "events.AnkiFileCreateEvent"):
    e = events.AnkiFileCreateEvent
    if event.Type == event.ClipperCreatePNGType:
        ModuleProxyfunc.anki_file_create_handle[event.ClipperCreatePNGType](event.sender, event.data)
        ALL.signals.on_anki_file_create.emit(
            e(eventType=e.ClipperCreatePNGDoneType)
        )
