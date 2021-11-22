from aqt import mw
# from ..dialogs.DialogCardPrev import external_card_dialog
from aqt.browser.previewer import BrowserPreviewer
from aqt.editor import Editor
from aqt.reviewer import Reviewer
from aqt.utils import showInfo

from . import funcs

CardId = funcs.Compatible.CardId()


# print, _ = clipper_imports.funcs.logger(__name__)
def find_card_from_context(context):
    from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewerMod
    if isinstance(context,Editor):
        return context.card.id
    if isinstance(context,SingleCardPreviewerMod):
        return context.card().id
    if isinstance(context,BrowserPreviewer):
        return context.card().id
    return None
def on_js_message(handled, url: str, context):
    if url.startswith("hjp-bilink-cid:"):
        cid: "CardId" = CardId(int(url.split(":")[-1]))
        card = mw.col.getCard(cid)
        if funcs.CardOperation.exists(card):
            funcs.Dialogs.open_custom_cardwindow(card).activateWindow()
        else:
            showInfo(f"""卡片不存在,id={str(card.id)}""")
        return True, None
    elif url.startswith("hjp-bilink-clipuuid:"):
        pdfuuid, pagenum = url.split(":")[-1].split("_")
        funcs.Dialogs.open_PDFprev(pdfuuid, pagenum, context)
    elif url.startswith("ankilink://"):
        if url.startswith("ankilink://opengview_id="):
            mode = funcs.GraphMode
            uuid = url[-8:]
            funcs.Utils.tooltip(str(context.__class__.__name__))
            if funcs.GviewOperation.exists(uuid = uuid):
                data = funcs.GviewOperation.load(uuid=uuid)
                card_id = find_card_from_context(context)
                pair=None
                if card_id:
                    desc = funcs.CardOperation.desc_extract(card_id)
                    pair = funcs.G.objs.LinkDataPair(card_id=str(card_id),desc=desc)
                funcs.Dialogs.open_grapher(mode=mode.view_mode,
                                           gviewdata=data,pair_li=[pair] if pair else None)
            else:
                showInfo(f"""视图不存在,id={uuid}""")
    return handled
