import json
import re
from typing import Iterator



import bs4
from anki.cards import CardId,Card
from aqt import mw
from bs4 import BeautifulSoup, element
from aqt.utils import showInfo, tooltip

# from .backlink_reader import BackLinkReader

# from .linkData_reader import LinkDataReader
import os
from . import funcs
from . import G


# from . import clipper_imports

# print, _ = clipper_imports.funcs.logger(__name__)


class FieldHTMLData:
    def __init__(self, html: BeautifulSoup, card_id=None):

        super().__init__()
        self.card_id = card_id
        self.html_str = html.__str__()
        self.output_str = ""
        self.html_root = html
        self.anchor_container_L0 = funcs.HTML.LeftTopContainer_make(self.html_root)
        self.anchor_body_L1 = self.anchor_container_L0.find("div", attrs={"class": "container_body_L1"})
        self.data: "G.objs.LinkDataJSONInfo" = None


# anchor中的backlink maker
class BacklinkButtonMaker(FieldHTMLData):
    """用来制作按钮
    div.container_L0
        div.header_L1
        div.body_L1
            button.card_id
            details.hjp_bilink
                summary
                div
                    button
                    details
                        summary
                        div
    """

    def build(self):
        """直接的出口, 返回HTML的string"""
        from .objs import LinkDataPair
        from ..bilink import linkdata_admin
        # data = LinkDataReader(self.card_id).read()
        # self.data = data
        self.data = linkdata_admin.read_card_link_info(self.card_id)
        if not self.data.root and not self.data.backlink:
            # funcs.Utils.print(f"self.data.root = {self.data.root.__str__()}", need_timestamp=True)
            return self.html_root.__str__()
        self.cascadeDIV_create()  # 这个名字其实取得不好,就是反链的设计
        # funcs.Utils.print("next backlink_create", need_timestamp=True)
        self.backlink_create()  # 这个是文内链接的设计,顺便放着的,因为用的元素基本一样.
        return self.html_root

    def button_make(self, card_id):
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor backlink button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        cardinfo = self.data.link_dict[card_id]
        b.string = "→" + cardinfo.desc  # funcs.CardOperation.desc_extract(card_id)
        return b

    # 创建 anchor中的backlink专区
    def cascadeDIV_create(self):
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "backlink", attr={"open": "", "class": "backlink"})
        self.anchor_body_L1.append(details)
        for item in self.data.root:
            if item.card_id != "":
                L2 = self.button_make(item.card_id)
            elif item.nodeuuid != "":
                L2 = self.details_make(item.nodeuuid)
            else:
                raise ValueError(f"{item}没有值")
            div.append(L2)

    # 每个按钮的细节设计
    def details_make(self, nodeuuid):
        node = self.data.node[nodeuuid]
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, node.name)
        li = node.children
        for item in li:
            if item.card_id != "":
                L2 = self.button_make(item.card_id)
            elif item.nodeuuid != "":
                L2 = self.details_make(item.nodeuuid)
            else:
                raise ValueError(f"{item}没有值")
            div.append(L2)
        return details

    # 反链的铺垫
    def backlink_create(self):
        from ..bilink import linkdata_admin
        h = self.html_root
        # funcs.Utils.print("make backlink", need_timestamp=True)
        if len(self.data.backlink) == 0:
            return None
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "referenced_in_text",
                                                                  attr={"open": "", "class": "referenced_in_text"})
        for card_id in self.data.backlink:
            data: "G.objs.LinkDataJSONInfo" = linkdata_admin.read_card_link_info(card_id)
            L2 = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor button",
                                            "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
            L2.string = "→" + data.self_data.desc
            div.append(L2)

        self.anchor_body_L1.append(details)

    pass


def InTextButtonMakeProcess(html_string):
    from ..bilink.in_text_admin.backlink_reader import BackLinkReader
    buttonli = BackLinkReader(html_str=html_string).backlink_get()
    if len(buttonli) > 0:
        finalstring = html_string[0:buttonli[0]["span"][0]]
        for i in range(len(buttonli) - 1):
            prevEnd, nextBegin = buttonli[i]["span"][1], buttonli[i + 1]["span"][0]
            finalstring += funcs.HTML.InTextButtonMake(buttonli[i]) + html_string[prevEnd:nextBegin]
        finalstring += funcs.HTML.InTextButtonMake(buttonli[-1]) + html_string[buttonli[-1]["span"][1]:]
    else:
        finalstring = html_string
    return finalstring

class InTextButtonMaker(FieldHTMLData):
    """负责将[[link:card-id_desc_]]替换成按钮"""

    def build(self):
        from ..bilink.in_text_admin.backlink_reader import BackLinkReader
        buttonli = BackLinkReader(html_str=self.html_str).backlink_get()
        if len(buttonli) > 0:
            finalstring = self.html_str[0:buttonli[0]["span"][0]]
            for i in range(len(buttonli) - 1):
                prevEnd, nextBegin = buttonli[i]["span"][1], buttonli[i + 1]["span"][0]
                finalstring += self.button_make(buttonli[i]) + self.html_str[prevEnd:nextBegin]
            finalstring += self.button_make(buttonli[-1]) + self.html_str[buttonli[-1]["span"][1]:]
        else:
            finalstring = self.html_str
        return finalstring

    def button_make(self, data):
        card_id = data["card_id"]
        desc = data["desc"]
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor intext button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = desc
        return b.__str__()


class PDFPageButtonMaker(FieldHTMLData):
    def build(self):
        """
        需要在  CLIPBOX_INFO_TABLE 先搜索card_id,获得clipbox from DB,后 根据卡片里的 class.clipbox 获得clipbox from field
        作差, DB-Field>0, 删除多余的card_id
        作差, Field-DB>0, 将多出来的加card_id
        以上工作做完后, 开始插入链接,链接的href格式: hjp-bilink-clipid:clipboxUuid.
        js监听器获得clipboxUuid后再选出文件进行打开
        Returns:

        """
        funcs.HTML_clipbox_sync_check(self.card_id.__str__(), self.html_root)
        PDF_page_dict = funcs.HTML_clipbox_PDF_info_dict_read(self.html_root)
        self.cascadeDIV_create(PDF_page_dict)
        return self.html_root

    def button_make(self, uuid, pagenum, desc):
        """"""
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": "card_id", "class": "hjp-bilink anchor button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-clipuuid:{uuid}_{pagenum}');"""})

        b.string = desc
        return b

    def cascadeDIV_create(self, PDF_page_dict):
        """层级只有两层,PDF名字和页码,页码显示为PDFpage:,BookPage:
        PDF_page_dict={uuid:{pagenum:{},pdfname:{}}}
        """
        assert isinstance(PDF_page_dict, dict)
        from .objs import PDFinfoRecord

        # PDF_baseinfo_dict = clipper_imports.objs.SrcAdmin.PDF_JSON.load().data
        details1, div1 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "clipped_from_PDF", attr={"open" : "",
                                                                                                              "class": "PDFclipper"})
        for pdfuuid, page_pdf in PDF_page_dict.items():  # {uuid:{pagenum:{},pdfname:""}}
            pdfinfo: PDFinfoRecord = page_pdf["info"]
            pdfname = funcs.str_shorten(os.path.basename(pdfinfo.pdf_path))
            pagenumlist = list(page_pdf["pagenum"])
            details2, div2 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, pdfname, attr={"open": ""})
            div1.append(details2)
            for pagenum in pagenumlist:
                uuid = pdfuuid
                desc = f""" pdf_page_at: {pagenum}, book_page_at:{pagenum - pdfinfo.offset + 1} """
                button = self.button_make(uuid, pagenum, desc)
                div2.append(button)
        self.anchor_body_L1.append(details1)

    pass


class GroupReviewButtonMaker(FieldHTMLData):
    """
    打开卡片后,首先判断配置开了没有,
    """

    def build(self):
        if funcs.Config.get().group_review.value == True and int(self.card_id) in G.GroupReview_dict.card_group:
            self.cascadeDIV_create()
        return self.html_root

    def button_make(self, card_id):
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor groupreview button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = "→" + funcs.CardOperation.desc_extract(card_id)
        return b

    def cascadeDIV_create(self):
        details1, div1 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "group_review_list", attr={"open" : "",
                                                                                                               "class": "groupreview"})
        searchs = G.GroupReview_dict.card_group[int(self.card_id)]
        for search in searchs:
            details2, div2 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, search, attr={"open": ""})
            div1.append(details2)
            cids = G.GroupReview_dict.search_group[search]
            for cid in cids:
                button = self.button_make(cid)
                div2.append(button)
        self.anchor_body_L1.append(details1)
        pass


class GViewButtonMaker(FieldHTMLData):
    def build(self, view_li: "set[funcs.GViewData]" = None):
        if not view_li: view_li = funcs.GviewOperation.find_by_card([funcs.LinkDataPair(self.card_id)])
        self.cascadeDIV_create(view_li)
        return self.html_root

    def button_make(self, view: "funcs.GViewData"):
        ankilink = funcs.G.src.ankilink
        pycmd = f"""{ankilink.protocol}://{ankilink.cmd.opengview}={view.uuid}"""
        h = self.html_root
        b = h.new_tag("button", attrs={"view_id": view.uuid, "class": "hjp-bilink anchor view button",
                                       "onclick": f"""javascript:pycmd('{pycmd}');"""})
        b.string = view.name
        return b

    def cascadeDIV_create(self, view_li: "set[funcs.GViewData]"):
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "related view", attr={"open": "", "class": "gview"})
        for view in view_li:
            button = self.button_make(view)
            div.append(button)
        self.anchor_body_L1.append(details)
        pass


def HTMLbutton_make(htmltext, card:"Card"):
    """
    htmltext长什么样? 只有卡片本身+卡片模板的html代码, 没有header body 之类的, 非完整html
    这里的工程就是,
    创建一个div, 然后根据需要一层层过滤, 可能比较适合函数式的方法.
    涉及的注入内容
    anchor中
        backlink
        grahpView
        groupReview
        pdfclipbox
    正文中
        file_protocol_detect
        InTextButton
    """

    html_string = htmltext
    from ..bilink import linkdata_admin
    from ..bilink.in_text_admin import backlink_reader
    data = linkdata_admin.read_card_link_info(str(card.id))
    """

    """
    anchor = bs4.BeautifulSoup("", "html.parser")

    # 以下ButtonMaker是用来生成左上角按钮的
    if len(data.link_list) > 0 or len(data.backlink) > 0:
        # funcs.Utils.print(f"{card.id} hasbacklink")
        anchor = BacklinkButtonMaker(anchor, card_id=card.id).build()
    if funcs.HTML.clipbox_exists(html_string):
        # funcs.Utils.print(f"{card.id} clipbox_exists")
        anchor = PDFPageButtonMaker(anchor, card_id=card.id).build()
    if G.GroupReview_dict and card.id in G.GroupReview_dict.card_group:
        # funcs.Utils.print(f"{card.id} GroupReview")
        anchor = GroupReviewButtonMaker(anchor, card_id=card.id).build()
    view_li = funcs.GviewOperation.find_by_card([funcs.LinkDataPair(str(card.id))])
    if len(view_li) > 0:
        # funcs.Utils.print(f"{card.id} len(view_li)>0:")
        anchor = GViewButtonMaker(anchor, card_id=card.id).build(view_li=view_li)

    # 以下内容来替换文本, 替换文本是
    hasInTextButton = len(backlink_reader.BackLinkReader(html_str=htmltext).backlink_get()) > 0
    if hasInTextButton:
        # funcs.Utils.print(f"{card.id} hasInTextButton")
        html_string = funcs.HTML.InTextButtonDeal(html_string)
        # html_string = InTextButtonMaker(html_string).build()

    html_string = funcs.HTML.file_protocol_support(html_string)

    # 如果左上角确实有内容则将其插入htmltext
    # funcs.Utils.print(anchor)
    container_body_L1_exists = anchor.find("div", attrs={"class": "container_body_L1"})
    if container_body_L1_exists:
        container_body_L1_children = [child for child in anchor.find("div", attrs={"class": "container_body_L1"}).children]
        if len(container_body_L1_children) > 0:
            script = funcs.HTML.cardHTMLShadowDom(anchor.__str__())
            html_string = script.__str__() + html_string

    # funcs.Utils.print(html_string)
    return html_string


testdata = {"version"  : 1,
            "link_list": [
                    {"card_id": "1620315134937", "desc": "A", "dir": "→"},
                    {"card_id": "1620315139164", "desc": "B", "dir": "→"},
                    {"card_id": "1620315139728", "desc": "C", "dir": "→"},
                    {"card_id": "1620315140556", "desc": "D", "dir": "→"}],
            "self_data":
                {"card_id": "1620315134937", "desc": ""},
            "root"     : [
                    {"nodename": "yes"},
                    {"card_id": "1620315140556"}],
            "node"     : {
                    "yes"          : [{"card_id": "1620315134937"},
                                      {"card_id": "1620315139164"},
                                      {"nodename": "no"}
                                      ],
                    "no"           : [{"card_id": "1620315139728"}],
                    "1620315134937": {"card_id": "1620315134937", "desc": "A", "dir": "→"},
                    "1620315139164": {"card_id": "1620315139164", "desc": "B", "dir": "→"},
                    "1620315139728": {"card_id": "1620315139728", "desc": "C", "dir": "→"},
                    "1620315140556": {"card_id": "1620315140556", "desc": "D", "dir": "→"}
            }}

teststring = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<style>

.container_L0,
button[card_id].hjp-bilink.anchor.button {
        margin:0 !important;
        display:block;
        color:#fff; /*锚点字体的颜色*/
        background-color:green;/*锚点的背景色*/
        border:none;
        border-radius:1px;
        position:relative;
        max-width:150px;
        color:white;
        overflow-wrap: anywhere;
        font-size:15px
}
button[card_id].hjp-bilink.anchor.button {
    width:100%;
    text-align:left;
    margin:1px !important;
    padding:1px;
}

.container_body_L1 {
    position:absolute;
    display:none;
}

.container_L0:hover .container_body_L1
{
    width:100%;
    background-color:green;/*锚点的背景色*/
    position:absolute;
    display:grid;
}
.hjp_bilink.details{
    text-align:left;
}

.hjp_bilink.details div{
    text-align:left;
    margin-left:6px;
}
</style>
<div class="">
[[link:1620468288991_A啊!_]]_]] "
</div>
<div class = "container_L0">
    <div class="container_header_L1">hjp-bilink</div>
    <div class = "container_body_L1">
        <button card_id="123">1234</button>
        <details class="hjp-bilink details">
            <summary >123</summary>
            <div >
                <button card_id="123">1234</button>
                <details>
                    <summary>456</summary>
                    <div >
                    <button card_id="123">1234</button>
                    </div>
                </details>
            </div>
        </details>
    </div>
</div>
[[link:1620468289832_b_]]
123123
 [[link:1620468290938_c_]] 
 [[link:1620468291507_d1231_]]
</body>
</html>
"""

if __name__ == "__main__":
    I = InTextButtonMaker(teststring)
    s = I.build()
