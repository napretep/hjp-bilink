"""用于实现跨三级模块以上的信息交互"""
from aqt import mw, dialogs, browser
from aqt.utils import showInfo
from . import imports
from .backlink_reader import BackLinkReader
from . import ModuleProxyfunc
from . import utils

print, printer = imports.funcs.logger(__name__)


def on_cardlist_addCard_handle(event: "imports.events.CardListAddCardEvent"):
    """添加来自anki现有的卡片"""
    if event.eventType == event.parseStrType:
        pairli = [(item["desc"], item["card_id"]) for item in BackLinkReader(html_str=event.html).backlink_get()]
        e = imports.events.CardListAddCardEvent
        imports.ALL.signals.on_cardlist_addCard.emit(
            e(sender=on_cardlist_addCard_handle, eventType=e.returnPairLiType, pairli=pairli))


def on_anki_card_create_handle(event: "imports.events.AnkiCardCreateEvent"):
    """新建卡片,并发射卡片回去"""
    e = imports.events.AnkiCardCreatedEvent
    if event.Type == event.ClipBoxType:
        self = event.sender
        data = ModuleProxyfunc.anki_card_create_handle[event.ClipBoxType](event.model_id, event.deck_id)
        # print(f"得到卡片:{data}")
        imports.ALL.signals.on_anki_card_created.emit(
            e(eventType=e.ClipBoxType, data=data)
        )


def on_anki_field_insert_handle(event: "imports.events.AnkiFieldInsertEvent"):
    """将clipbox的信息插入卡片字段"""
    e = imports.events.AnkiFieldInsertEvent
    if event.Type == event.ClipBoxBeginType:
        self = event.sender
        clipboxlist = event.data
        timestamp = ModuleProxyfunc.anki_field_insert_handle[event.ClipBoxBeginType](self, clipboxlist)
        # print("anki_field_insert_handle timestamp:{}".format(timestamp))
        imports.ALL.signals.on_anki_field_insert.emit(e(eventType=e.ClipBoxEndType, data=timestamp))


def on_anki_browser_activate_handle(event: "imports.events.AnkiBrowserActivateEvent"):
    if event.Type == event.ClipperTaskFinishedType:
        # print(f"on_anki_browser_activate_handle timestamp={event.data}")
        tag = f"""tag:hjp-bilink::timestamp::{str(event.data)}"""
        browser = dialogs._dialogs["Browser"][1]
        if browser is None:
            dialogs.open("Browser", mw)
            browser = dialogs._dialogs["Browser"][1]
        # browser
        utils.console(tag).log.end()
        browser.search_for(tag)
        browser.activateWindow()


def on_anki_file_create_handle(event: "imports.events.AnkiFileCreateEvent"):
    e = imports.events.AnkiFileCreateEvent
    if event.Type == event.ClipperCreatePNGType:
        ModuleProxyfunc.anki_file_create_handle[event.ClipperCreatePNGType](event.sender, event.data)
        imports.ALL.signals.on_anki_file_create.emit(
            e(eventType=e.ClipperCreatePNGDoneType)
        )


def on_config_ankidata_load_handle(event: "imports.events.ConfigAnkiDataLoadEvent"):
    data = {}
    if event.modelType in event.Type:
        model = mw.col.models.all_names_and_ids()
        data["model"] = []
        for i in model:
            data["model"].append({"id": i.id, "name": i.name})

    if event.deckType in event.Type:
        data["deck"] = []
        deck = mw.col.decks.all_names_and_ids()
        for i in deck:
            data["deck"].append({"id": i.id, "name": i.name})
    e = imports.events.ConfigAnkiDataLoadEndEvent
    imports.ALL.signals.on_config_ankidata_load_end.emit(e(sender=event.sender, eventType=event.Type, ankidata=data))
