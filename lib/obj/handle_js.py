from aqt import mw
from ..dialogs.DialogCardPrev import external_card_dialog


def on_js_message(handled, url: str, context):
    if url.startswith("hjp-bilink-cid:"):
        cid = int(url.split(":")[-1])
        card = mw.col.getCard(cid)
        external_card_dialog(card)
        return True, None
    return handled
