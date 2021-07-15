from aqt import mw
from ..dialogs.DialogCardPrev import external_card_dialog
from . import funcs
from . import clipper_imports

print, _ = clipper_imports.funcs.logger(__name__)


def on_js_message(handled, url: str, context):
    if url.startswith("hjp-bilink-cid:"):
        cid = int(url.split(":")[-1])
        card = mw.col.getCard(cid)
        external_card_dialog(card)
        return True, None
    elif url.startswith("hjp-bilink-clipuuid:"):
        pdfuuid, pagenum = url.split(":")[-1].split("_")
        print(f"pagenum={pagenum}")
        funcs.PDFPreviewer_start(pdfuuid, int(pagenum), context)

    return handled
