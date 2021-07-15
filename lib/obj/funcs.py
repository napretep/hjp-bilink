"""
funcs 的层级比utils低 ,所以可以引用utils, 但utils 不能引用 funcs

"""

import os
from functools import reduce
from typing import *

import aqt
import uuid
from aqt import mw, dialogs
from aqt.browser import Browser
from aqt.previewer import Previewer, BrowserPreviewer
from aqt.reviewer import Reviewer
from bs4 import BeautifulSoup, element
import re, json
from . import utils

from . import clipper_imports
from ..dialogs.DialogCardPrev import SingleCardPreviewerMod
from ..dialogs.DialogPDFpreviewer import PDFPrevDialog

print, printer = clipper_imports.funcs.logger(__name__)
from . import all_objs


def on_clipper_closed():
    all_objs.mw_win_clipper = None


def PDFPreviewer_start(pdfuuid, pagenum, FROM=None):
    # print(FROM)
    if isinstance(FROM, Reviewer):
        card_id = FROM.card.id
        pass
    elif isinstance(FROM, BrowserPreviewer):
        card_id = FROM.card().id
        pass
    elif isinstance(FROM, SingleCardPreviewerMod):
        card_id = FROM.card().id
    else:
        TypeError("未能找到card_id")
    card_id = str(card_id)
    DB = clipper_imports.objs.SrcAdmin.DB.go()
    result = clipper_imports.objs.SrcAdmin.PDF_JSON.read(pdfuuid)
    DB.end()
    pdfname = result["pdf_path"]
    pdfpageuuid = str(uuid.uuid3(uuid.NAMESPACE_URL, pdfuuid + str(pagenum)))
    if card_id not in all_objs.mw_pdf_prev:
        all_objs.mw_pdf_prev[card_id] = {}
    if pdfpageuuid not in all_objs.mw_pdf_prev[card_id]:
        all_objs.mw_pdf_prev[card_id][pdfpageuuid] = None
    print(f"pagenum={pagenum}")
    if isinstance(all_objs.mw_pdf_prev[card_id][pdfpageuuid], PDFPrevDialog):
        all_objs.mw_pdf_prev[card_id][pdfpageuuid].activateWindow()
    else:
        ratio = 1
        all_objs.mw_pdf_prev[card_id][pdfpageuuid] = \
            PDFPrevDialog(pdfuuid=pdfuuid, pdfname=pdfname, pagenum=pagenum, pageratio=ratio, card_id=card_id)
        all_objs.mw_pdf_prev[card_id][pdfpageuuid].show()


def HTML_txtContent_read(html):
    """HTML文本内容的读取,如果没有就尝试找img的src文本"""
    from .backlink_reader import BackLinkReader
    cfg = utils.BaseInfo().userinfo
    root = BeautifulSoup(html, "html.parser")
    text = root.getText()
    if cfg.delete_intext_link_when_extract_desc == 1:
        newtext = text
        replace_str = ""
        intextlinks = BackLinkReader(html_str=text).backlink_get()
        for link in intextlinks:
            span = link["span"]
            replace_str += re.sub("(\])|(\[)", lambda x: "\]" if x.group(0) == "]" else "\[",
                                  text[span[0]:span[1]]) + "|"
        replace_str = replace_str[0:-1]
        text = re.sub(replace_str, "", newtext)
    if not re.search("\S", text):
        a = root.find("img")
        if a is not None:
            text = a.attrs["src"]
    return text


def desc_extract(card_id=None, fromField=False):
    """读取卡片的描述,需要卡片id"""
    from .linkData_reader import LinkDataReader
    if isinstance(card_id, utils.Pair):
        cid = card_id.int_card_id
    elif isinstance(card_id, str):
        cid = int(card_id)
    elif type(card_id) == int:
        cid = card_id
    else:
        raise TypeError("参数类型不支持:" + card_id.__str__())
    cfg = utils.BaseInfo().userinfo
    note = mw.col.getCard(cid).note()
    if fromField:  # 分成这两段, 是因为一个循环引用.
        content = reduce(lambda x, y: x + y, note.fields)
        desc = HTML_txtContent_read(content)
        desc = re.sub(r"\n+", "", desc)
        desc = desc[0:cfg.descMaxLength if len(desc) > cfg.descMaxLength != 0 else len(desc)]
    else:
        desc = LinkDataReader(cid).read()["self_data"]["desc"]
        if desc == "":
            content = reduce(lambda x, y: x + y, note.fields)
            desc = HTML_txtContent_read(content)
            desc = re.sub(r"\n+", "", desc)
            desc = desc[0:cfg.descMaxLength if len(desc) > cfg.descMaxLength != 0 else len(desc)]

    return desc


def HTML_clipbox_uuid_get(html):
    if type(html) == str:
        root = BeautifulSoup(html, "html.parser")
    elif type(html) == BeautifulSoup:
        root = html
    else:
        raise TypeError("无法处理参数类型: {}".format(type(html)))
    imgli = root.find_all("img", attrs={"class": "hjp_clipper_clipbox"})
    clipbox_uuid_li = [re.sub("hjp_clipper_(\w+)_.png", lambda x: x.group(1), img.attrs["src"]) for img in imgli]
    return clipbox_uuid_li


def HTML_clipbox_exists(html, card_id=None):
    """任务:
    1检查clipbox的uuid是否在数据库中存在,如果存在,返回True,不存在返回False,
    2当存在时,检查卡片id是否是clipbox对应card_id,如果不是,则要添加,此卡片
    3搜索本卡片,得到clipbox的uuid,如果有搜到 uuid 但是又不在html解析出的uuid中, 则将数据库中的uuid的card_id删去本卡片的id
    """
    clipbox_uuid_li = HTML_clipbox_uuid_get(html)
    DB = clipper_imports.objs.SrcAdmin.DB.go()
    # print(clipbox_uuid_li)
    true_or_false_li = [DB.exists(uuid) for uuid in clipbox_uuid_li]
    DB.end()
    return (reduce(lambda x, y: x or y, true_or_false_li, False))


def HTML_clipbox_sync_check(card_id, root):
    # 用于保持同步
    assert type(root) == BeautifulSoup
    assert type(card_id) == str and len(card_id) == 13
    DB = clipper_imports.objs.SrcAdmin.DB.go()
    clipbox_from_DB_ = DB.select(card_id="card_id", like=f"%{card_id}%").return_all().zip_up()
    clipbox_from_DB = set([clipbox["uuid"] for clipbox in clipbox_from_DB_])
    # 选取 clipbox from field
    clipbox_from_field = set(HTML_clipbox_uuid_get(root))
    # 多退少补,
    DBadd = clipbox_from_field - clipbox_from_DB
    DBdel = clipbox_from_DB - clipbox_from_field
    print(
        f"card_id={card_id},clipbox_from_DB={clipbox_from_DB}, clipbox_from_field={clipbox_from_field}, DBADD={DBadd}.  DBdel={DBdel}")
    if len(DBadd) > 0:
        for uuid in DBadd:
            record = DB.select(uuid=uuid).return_all().zip_up()[0]
            if card_id not in record["card_id"]:
                card_li: "list" = record["card_id"].split(",")
                card_li.append(card_id)
                record["card_id"] = ",".join(card_li)
                DB.update(values=DB.value_maker(**record), where=DB.where_maker(uuid=record["uuid"])).commit(print)
    if len(DBdel) > 0:
        for uuid in DBdel:
            record = DB.select(uuid=uuid).return_all().zip_up(compatible=False)[0]
            if card_id in record["card_id"]:
                card_li: "list" = record["card_id"].split(",")
                card_li.remove(card_id)
                record["card_id"] = ",".join(card_li)
                DB.update(values=DB.value_maker(**record), where=DB.where_maker(uuid=record["uuid"])).commit(print)
    DB.end()
    pass


def HTML_clipbox_PDF_info_dict_read(root):
    assert type(root) == BeautifulSoup
    clipbox_from_field = set(HTML_clipbox_uuid_get(root))
    DB = clipper_imports.objs.SrcAdmin.DB.go()
    DB.select(where=DB.where_maker(IN=True, vals=clipbox_from_field, colname="uuid"))
    # print(DB.excute_queue[-1])
    record_li = DB.return_all().zip_up()
    PDF_info_dict = {}  # {uuid:{pagenum:{},pdfname:""}}
    for record in record_li:
        if record["pdfuuid"] not in PDF_info_dict:
            PDF_info_dict[record["pdfuuid"]] = {"pagenum": set(),
                                                "pdfname": record["pdfname"]}  # 只提取页码, 大小重新再设定.偏移量也重新设定.
        PDF_info_dict[record["pdfuuid"]]["pagenum"].add(record["pagenum"])
    DB.end()
    return PDF_info_dict


def HTML_LeftTopContainer_make(root: "BeautifulSoup"):
    """传入的是从html文本解析成的beautifulSoup对象
    设计的是webview页面的左上角按钮,包括的内容有:
    anchorname            ->一切的开始
        style             ->样式设计
        div.container_L0  ->按钮所在地
            div.header_L1 ->就是 hjp_bilink 这个名字所在的地方
            div.body_L1   ->就是按钮和折叠栏所在的地方
    一开始会先检查这个anchorname元素是不是已经存在,如果存在则直接读取
    """
    # 寻找 anchorname ,建立 anchor_el,作为总的锚点.
    ID = utils.BaseInfo().userinfo.button_appendTo_AnchorId
    # ID = ""
    anchorname = ID if ID != "" else "anchor_container"
    resultli = root.select(f"#{anchorname}")
    if len(resultli) > 0:  # 如果已经存在,就直接取得并返回
        anchor_el: "element.Tag" = resultli[0]
    else:
        anchor_el: "element.Tag" = root.new_tag("div", attrs={"id": anchorname})
        root.insert(1, anchor_el)
        # 设计 style
        CSS_FOLDER = os.path.join(utils.THIS_FOLDER, utils.BaseInfo().baseinfo.anchorCSSFileName)
        style_str = open(CSS_FOLDER, "r", encoding="utf-8").read()
        style = root.new_tag("style")
        style.string = style_str
        anchor_el.append(style)
        # 设计 容器 div.container_L0, div.header_L1和div.body_L1
        L0 = root.new_tag("div", attrs={"class": "container_L0"})
        header_L1 = root.new_tag("div", attrs={"class": "container_header_L1"})
        header_L1.string = utils.BaseInfo().baseinfo.consoler_Name
        body_L1 = root.new_tag("div", attrs={"class": "container_body_L1"})
        L0.append(header_L1)
        L0.append(body_L1)
        anchor_el.append(L0)
    return anchor_el  # 已经传入了root,因此不必传出.


def HTML_LeftTopContainer_detail_el_make(root: "BeautifulSoup", summaryname, attr: "dict" = None):
    """这是一个公共的步骤,设计一个details
    details.hjp_bilink .details
        summary
        div
    """
    if attr is None:
        attr = {}
    attrs = {"class": "hjp_bilink details", **(attr.copy())}
    # print(attrs)
    details = root.new_tag("details", attrs=attrs)
    summary = root.new_tag("summary")
    summary.string = summaryname
    div = root.new_tag("div")
    details.append(summary)
    details.append(div)
    return details, div


def webview_refresh():
    def prev_refresh(p: Previewer):
        # return False
        _last_state = p._last_state
        _card_changed = p._card_changed
        p._last_state = None
        p._card_changed = True
        p._render_scheduled()
        p._last_state = _last_state
        p._card_changed = _card_changed

    # 监察对象: 自定义的预览窗,browser.previewer,mw.state == "review"
    addonName = utils.BaseInfo().baseinfo.dialogName
    position = "card_window"
    browser: Browser = dialogs._dialogs["Browser"][1]
    if browser is not None and browser._previewer is not None:
        prev_refresh(browser._previewer)
    # if mw.state == "review":  # 这个是有用的,当在其他窗口进行链接的时候,也要刷新这里.
    #     mw.reviewer.
    if addonName in mw.__dict__ and position in mw.__dict__[addonName]:
        card_window_dict = mw.__dict__[addonName][position]
        # showInfo(card_window.__str__())
        for k, v in card_window_dict.items():
            if v is not None:
                prev_refresh(v)


def browser_refresh():
    """在被包裹的函数执行完后刷新"""
    if dialogs._dialogs["Browser"][1] is not None:
        browser = dialogs._dialogs["Browser"][1]
        utils.compatible_browser_sidebar_refresh(browser)
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        utils.compatible_browser_sidebar_refresh(browser)
        browser.model.layoutChanged.emit()
        browser.editor.setNote(None)
        browser.model.reset()


def browser_and_webview_refresh():
    browser_refresh()
    webview_refresh()


def PDFprev_close(card_id, pdfpageuuid=None, all=False):
    if isinstance(card_id, int):
        card_id = str(card_id)
    if card_id not in all_objs.mw_pdf_prev:
        return
    if all:
        for pdfpageuuid in all_objs.mw_pdf_prev[card_id]:
            if isinstance(all_objs.mw_pdf_prev[card_id][pdfpageuuid], PDFPrevDialog):
                all_objs.mw_pdf_prev[card_id][pdfpageuuid].close()
    else:
        if pdfpageuuid in all_objs.mw_pdf_prev[card_id]:
            all_objs.mw_pdf_prev[card_id][pdfpageuuid].close()


if __name__ == "__main__":
    html = """vt.反对；反抗<br>[[link:1620350799499_vt.反对；反抗_]]
<br><img alt="123" src="">`"""
    s = """
    {"backlink": [], "version": 1, "link_list": [{"card_id": "1620350799500", "desc": "a. \u53cd\u5bf9\u7684", "dir": "\u2192"}, {"card_id": "1620350799501", "desc": "adj.\u5bf9\u9762\u7684\uff1b\u76f8\u5bf9\u7684", "dir": "\u2192"}, {"card_id": "1620350799502", "desc": "n. \u53cd\u5bf9\uff1b\u654c\u5bf9", "dir": "\u2192"}, {"card_id": "1620350799497", "desc": "n.\u5bf9\u624b,\u654c\u624b\uff1b\u5bf9\u6297\u8005", "dir": "\u2192"}], "self_data": {"card_id": "1620350799499", "desc": "vt.\u53cd\u5bf9\uff1b\u53cd\u6297[[link:1620350799499_vt."}, "root": [{"card_id": "1620350799500"}, {"card_id": "1620350799501"}, {"card_id": "1620350799502"}, {"card_id": "1620350799497"}], "node": {}}"""
    print(HTML_txtContent_read(html))
