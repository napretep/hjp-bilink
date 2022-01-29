from urllib.parse import quote, unquote

from aqt import mw
# from ..dialogs.DialogCardPrev import external_card_dialog
from aqt.browser.previewer import BrowserPreviewer
from aqt.editor import Editor
from aqt.reviewer import Reviewer
from aqt.utils import showInfo

from . import funcs

CardId = funcs.Compatible.CardId()


# print, _ = clipper_imports.funcs.logger(__name__)
ankilink = funcs.G.src.ankilink
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
    """onAppMsgWrapper 这个函数也控制一些读取, 这里搞不懂的去那看看"""
    if url.startswith("hjp-bilink-cid:"):
        cid: "CardId" = CardId(int(url.split(":")[-1]))

        if funcs.CardOperation.exists(cid):
            card = mw.col.getCard(cid)
            funcs.Dialogs.open_custom_cardwindow(card).activateWindow()
        else:
            showInfo(f"""卡片不存在,id={str(cid)}""")
        return True, None
    elif url.startswith("hjp-bilink-clipuuid:"):
        pdfuuid, pagenum = url.split(":")[-1].split("_")
        funcs.Dialogs.open_PDFprev(pdfuuid, pagenum, context)
    elif url.startswith(f"{ankilink.protocol}://"):
        if url.startswith(f"{ankilink.protocol}://{ankilink.cmd.opengview}="):
            mode = funcs.GraphMode
            uuid = url[-8:]
            funcs.Utils.print(str(context.__class__.__name__))
            if funcs.GviewOperation.exists(uuid = uuid):
                data = funcs.GviewOperation.load(uuid=uuid)
                # card_id = find_card_from_context(context)
                # pair=None
                # if card_id:
                #     desc = funcs.CardOperation.desc_extract(card_id)
                #     pair = funcs.G.objs.LinkDataPair(card_id=str(card_id),desc=desc)
                funcs.Dialogs.open_grapher(mode=mode.view_mode,gviewdata=data)
                                           # [pair] if pair else None)
            else:
                showInfo(f"""视图不存在,id={uuid}""")
        elif url.startswith(f"{ankilink.protocol}://{ankilink.cmd.opencard}="):
            card_id = url[-13:]
            if funcs.CardOperation.exists(card_id):
                funcs.Dialogs.open_custom_cardwindow(card_id).activateWindow()
            else:
                showInfo(f"""卡片不存在,card_id={card_id}""")
        elif url.startswith(f"{ankilink.protocol}://{ankilink.cmd.openbrowser_search}="):
            s_len = len(f"{ankilink.protocol}://{ankilink.cmd.openbrowser_search}=")
            searchstring =unquote(url[s_len+1:])
            funcs.BrowserOperation.search(searchstring).activateWindow()
        elif url.startswith(f"{ankilink.protocol}://{ankilink.Cmd.open}?{ankilink.Key.card}="):
            card_id = url[-13:]
            if funcs.CardOperation.exists(card_id):
                funcs.Dialogs.open_custom_cardwindow(card_id).activateWindow()
            else:
                showInfo(f"""卡片不存在,card_id={card_id}""")
        elif url.startswith(f"{ankilink.protocol}://{ankilink.Cmd.open}?{ankilink.Key.gview}="):
            gview_id = url[-8:]
            if funcs.GviewOperation.exists(uuid=gview_id):
                data = funcs.GviewOperation.load(uuid=gview_id)
                funcs.Dialogs.open_grapher(gviewdata=data,mode=funcs.GraphMode.view_mode)
        elif url.startswith(f"{ankilink.protocol}://{ankilink.Cmd.open}?{ankilink.Key.browser_search}="):
            searchstring = unquote(url.split("=")[-1])
            funcs.BrowserOperation.search(searchstring).activateWindow()
        else:
            showInfo("未知指令/unknown command:<br>"+url)
    return handled

