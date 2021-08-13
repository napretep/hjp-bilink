from aqt import mw
# from ..dialogs.DialogCardPrev import external_card_dialog
from aqt.utils import showInfo

from . import funcs

CardId = funcs.Compatible.CardId()


# print, _ = clipper_imports.funcs.logger(__name__)


def on_js_message(handled, url: str, context):
    if url.startswith("hjp-bilink-cid:"):
        cid: "CardId" = CardId(int(url.split(":")[-1]))
        # try:
        card = mw.col.getCard(cid)
        # print(f"card_id={cid}")
        funcs.Dialogs.open_custom_cardwindow(card)
        return True, None
        # except:
        #     showInfo("卡片不存在")
    elif url.startswith("hjp-bilink-clipuuid:"):
        pdfuuid, pagenum = url.split(":")[-1].split("_")
        # print(f"pagenum={pagenum}")
        # funcs.Dialogs(pdfuuid, int(pagenum), context)
        funcs.Dialogs.open_PDFprev(pdfuuid, pagenum, context)

    return handled
