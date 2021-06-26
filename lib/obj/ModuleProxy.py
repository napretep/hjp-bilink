"""用于实现跨三级模块以上的信息交互"""
from aqt.utils import showInfo

from .tools import objs, events, funcs, ALL
from .backlink_reader import BackLinkReader


def on_cardlist_addCard_handle(event: "events.CardListAddCardEvent"):
    # showInfo("parseStrType")
    if event.eventType == event.parseStrType:
        # showInfo("parseStrType2")
        pairli = [(item["desc"], item["card_id"]) for item in BackLinkReader(html_str=event.html).backlink_get()]
        e = events.CardListAddCardEvent
        ALL.signals.on_cardlist_addCard.emit(
            e(sender=on_cardlist_addCard_handle, eventType=e.returnPairLiType, pairli=pairli))
