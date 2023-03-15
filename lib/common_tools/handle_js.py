import os
import platform
import re
import sys
from urllib.parse import quote, unquote

from aqt import mw
# from ..dialogs.DialogCardPrev import external_card_dialog
from aqt.browser.previewer import BrowserPreviewer
from aqt.editor import Editor
from aqt.reviewer import Reviewer
from aqt.utils import showInfo, tooltip

from . import funcs, terms

CardId = funcs.Compatible.CardId()
from .compatible_import import *
译 = funcs.译
# print, _ = clipper_imports.funcs.logger(__name__)
ankilink = funcs.G.src.ankilink

#
# def find_card_from_context(context):
#     from ..bilink.dialogs.custom_cardwindow import SingleCardPreviewerMod
#     if isinstance(context, Editor):
#         return context.card.id
#     if isinstance(context, SingleCardPreviewerMod):
#         return context.card().id
#     if isinstance(context, BrowserPreviewer):
#         return context.card().id
#     return None


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
    # elif url.startswith("hjp-bilink-clipuuid:"):
    #     pdfuuid, pagenum = url.split(":")[-1].split("_")
    #     funcs.Dialogs.open_PDFprev(pdfuuid, pagenum, context)
    elif url.startswith(f"{ankilink.protocol}://"):
        if url.startswith(f"{ankilink.protocol}://{ankilink.cmd.opengview}="):
            mode = funcs.GraphMode
            uuid = url[-8:]
            funcs.Utils.print(str(context.__class__.__name__))
            if funcs.GviewOperation.exists(uuid=uuid):
                data = funcs.GviewOperation.load(uuid=uuid)
                funcs.Dialogs.open_grapher(mode=mode.view_mode, gviewdata=data)
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
            searchstring = unquote(url[s_len + 1:])
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
                funcs.Dialogs.open_grapher(gviewdata=data, mode=funcs.GraphMode.view_mode)
        elif url.startswith(f"{ankilink.protocol}://{ankilink.Cmd.open}?{ankilink.Key.browser_search}="):
            searchstring = unquote(url.split("=")[-1])
            funcs.BrowserOperation.search(searchstring).activateWindow()
        else:
            showInfo("未知指令/unknown command:<br>" + url)
    elif url.startswith("file:/"):
        matches = re.search(r"file:/{2,3}(?P<pdfpath>.*)#page=(?P<page>\d+)$", url)
        if matches:
            pdfpath = matches.group("pdfpath")
            pdfurl = quote(pdfpath)
            pdfpath = unquote(pdfpath)
            funcs.Utils.print("pdfurl=",pdfurl,"pdfpath=",pdfpath)

            pagenum = matches.group("page")
            cmd: "str" = funcs.G.CONFIG.PDFLink_cmd.value
            if cmd.__contains__(terms.PDFLink.url):
                cmd = re.sub(f"{{{terms.PDFLink.url}}}", pdfurl, cmd)
            else:
                cmd = re.sub(f"{{{terms.PDFLink.path}}}", pdfpath, cmd)
            cmd = re.sub(f"{{{terms.PDFLink.page}}}", pagenum, cmd)
            # print(cmd)

            os.system(cmd)
            # os.system(cmd)
        else:
            matches = re.search("file:/{2,3}(?P<path>.*)$", url).group("path")
            if is_win:
                result = QMessageBox.information(None,译.你想打开链接吗, matches,QMessageBox.Yes | QMessageBox.No)
                if result == QMessageBox.Yes:
                    os.system(matches)

    return handled
