"""用于实现跨三级模块以上的信息交互"""
from aqt import mw, dialogs, browser
from aqt.utils import showInfo
from .backlink_reader import BackLinkReader
from . import ModuleProxyfunc, utils, events, clipper_imports, signals, funcs
import time

print, printer = clipper_imports.funcs.logger(__name__)


def on_cardlist_addCard_handle(event: "clipper_imports.events.CardListAddCardEvent"):
    """添加来自anki现有的卡片"""
    if event.eventType == event.parseStrType:
        pairli = [(item["desc"], item["card_id"]) for item in BackLinkReader(html_str=event.html).backlink_get()]
        e = clipper_imports.events.CardListAddCardEvent
        clipper_imports.ALL.signals.on_cardlist_addCard.emit(
            e(sender=on_cardlist_addCard_handle, eventType=e.returnPairLiType, pairli=pairli))


def on_anki_card_create_handle(event: "clipper_imports.events.AnkiCardCreateEvent"):
    """新建卡片,并发射卡片回去"""
    e = clipper_imports.events.AnkiCardCreatedEvent
    if event.type == event.defaultType.clipboxNeed:
        self = event.worker
        card_id = ModuleProxyfunc.anki_card_create_handle[event.type](event.model_id, event.deck_id)
        event.carditem.setText(card_id)
        self.waitting = False


def on_anki_field_insert_handle(event: "clipper_imports.events.AnkiFieldInsertEvent"):
    """将clipbox的信息插入卡片字段"""
    e = clipper_imports.events.AnkiFieldInsertEvent
    if event.type == event.defaultType.clipboxNeed:
        self = event.worker
        funcs.clipbox_insert_cardField_suite(event.clipuuid, timestamp=event.timestamp)
        self.waitting = False
        # print("anki_field_insert_handle timestamp:{}".format(timestamp))



def on_anki_browser_activate_handle(event: "clipper_imports.events.AnkiBrowserActivateEvent"):
    if event.type == event.defaultType.ClipperTaskFinished:
        # print(f"on_anki_browser_activate_handle timestamp={event.data}")
        tag = f"""tag:hjp-bilink::timestamp::{str(event.timestamp)}"""
        browser = dialogs._dialogs["Browser"][1]
        if browser is None:
            dialogs.open("Browser", mw)
            browser = dialogs._dialogs["Browser"][1]
        # browser
        # utils.console(tag).log.end()
        browser.search_for(tag)
        browser.activateWindow()


def on_anki_file_create_handle(event: "clipper_imports.events.AnkiFileCreateEvent"):
    if event.type == event.defaultType.ClipperCreatePNG:
        funcs.clipbox_png_save_to_media(event.clipuuid)
        event.worker.waitting = False

def on_config_ankidata_load_handle(event: "clipper_imports.events.ConfigAnkiDataLoadEvent"):
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
    e = clipper_imports.events.ConfigAnkiDataLoadEndEvent
    clipper_imports.ALL.signals.on_config_ankidata_load_end.emit(
        e(sender=event.sender, eventType=event.Type, ankidata=data))
