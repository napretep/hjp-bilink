import json
import re
from typing import Iterator

from anki.cards import CardId
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
    def __init__(self, html: str, card_id=None):
        super().__init__()
        self.card_id = card_id
        self.html_str = html
        self.output_str = ""
        self.html_root = BeautifulSoup(self.html_str, "html.parser")
        self.anchor_container_L0 = funcs.HTML_LeftTopContainer_make(self.html_root)
        self.anchor_body_L1 = self.anchor_container_L0.find("div", attrs={"class": "container_body_L1"})
        self.data: "G.objs.LinkDataJSONInfo" = None


class AnchorButtonMaker(FieldHTMLData):
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
            funcs.Utils.print(f"self.data.root = {self.data.root.__str__()}",need_timestamp=True)
            return self.html_root.__str__()
        self.cascadeDIV_create()  # 这个名字其实取得不好,就是反链的设计
        funcs.Utils.print("next backlink_create",need_timestamp=True)
        self.backlink_create()  # 这个是文内链接的设计,顺便放着的,因为用的元素基本一样.
        return self.html_root.__str__()

    def button_make(self, card_id):
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor backlink button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        cardinfo = self.data.link_dict[card_id]
        b.string = "→"+cardinfo.desc #funcs.CardOperation.desc_extract(card_id)
        return b

    def cascadeDIV_create(self):
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "backlink",attr={"open": "","class":"backlink"})
        self.anchor_body_L1.append(details)
        for item in self.data.root:
            if item.card_id != "":
                L2 = self.button_make(item.card_id)
            elif item.nodeuuid != "":
                L2 = self.details_make(item.nodeuuid)
            else:
                raise ValueError(f"{item}没有值")
            div.append(L2)

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

    def backlink_create(self):
        from ..bilink import linkdata_admin
        h = self.html_root
        funcs.Utils.print("make backlink",need_timestamp=True)
        if len(self.data.backlink) == 0:
            return None
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "referenced_in_text",
                                                                  attr={"open": "","class":"referenced_in_text"})
        for card_id in self.data.backlink:
            data: "G.objs.LinkDataJSONInfo" = linkdata_admin.read_card_link_info(card_id)
            L2 = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor button",
                                            "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
            L2.string = "→" + data.self_data.desc
            div.append(L2)

        self.anchor_body_L1.append(details)



    pass


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
        return self.html_root.__str__()

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
        details1, div1 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "clipped_from_PDF",attr={"open": "",
                                                                                                             "class":"PDFclipper"})
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
        if funcs.Config.get().group_review.value==True and int(self.card_id) in G.GroupReview_dict.card_group:
            self.cascadeDIV_create()
        return self.html_root.__str__()

    def button_make(self, card_id):
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor groupreview button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = "→" + funcs.CardOperation.desc_extract(card_id)
        return b

    def cascadeDIV_create(self):
        details1, div1 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "group_review_list",attr={"open": "",
                                                                                                             "class":"groupreview"})
        searchs = G.GroupReview_dict.card_group[int(self.card_id)]
        for search in searchs:
            details2,div2=funcs.HTML_LeftTopContainer_detail_el_make(self.html_root,search,attr={"open": ""})
            div1.append(details2)
            cids = G.GroupReview_dict.search_group[search]
            for cid in cids:
                button = self.button_make(cid)
                div2.append(button)
        self.anchor_body_L1.append(details1)
        pass

class GViewButtonMaker(FieldHTMLData):
    def build(self,view_li:"set[funcs.GViewData]"=None):
        if not view_li:view_li = funcs.GviewOperation.find_by_card([funcs.LinkDataPair(self.card_id)])
        self.cascadeDIV_create(view_li)
        return self.html_root.__str__()

    def button_make(self,view:"funcs.GViewData"):
        ankilink = funcs.G.src.ankilink
        pycmd = f"""{ankilink.protocol}://{ankilink.cmd.opengview}={view.uuid}"""
        h = self.html_root
        b = h.new_tag("button",attrs={"view_id":view.uuid,"class": "hjp-bilink anchor view button",
                                      "onclick": f"""javascript:pycmd('{pycmd}');"""})
        b.string = view.name
        return b

    def cascadeDIV_create(self,view_li:"set[funcs.GViewData]"):
        details,div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root,"related view",attr={"open": "","class":"gview"})
        for view in view_li:
            button = self.button_make(view)
            div.append(button)
        self.anchor_body_L1.append(details)
        pass



def HTMLbutton_make(htmltext, card):
    html_string = htmltext
    from ..bilink import linkdata_admin
    from ..bilink.in_text_admin import backlink_reader
    data = linkdata_admin.read_card_link_info(str(card.id))

    if len(data.link_list) > 0 or len(data.backlink) > 0:
        funcs.Utils.print(f"{card.id} hasbacklink")
        html_string = AnchorButtonMaker(html_string, card_id=card.id).build()
    hasInTextButton = len(backlink_reader.BackLinkReader(html_str=htmltext).backlink_get()) > 0
    if hasInTextButton:
        funcs.Utils.print(f"{card.id} hasInTextButton")
        html_string = InTextButtonMaker(html_string).build()
    if funcs.HTML_clipbox_exists(html_string):
        funcs.Utils.print(f"{card.id} clipbox_exists")
        html_string = PDFPageButtonMaker(html_string, card_id=card.id).build()
    if G.GroupReview_dict and card.id in G.GroupReview_dict.card_group:
        funcs.Utils.print(f"{card.id} GroupReview")
        html_string = GroupReviewButtonMaker(html_string, card_id=card.id).build()

    view_li = funcs.GviewOperation.find_by_card([funcs.LinkDataPair(str(card.id))])
    if len(view_li)>0:
        funcs.Utils.print(f"{card.id} len(view_li)>0:")
        html_string = GViewButtonMaker(html_string,card_id=card.id).build(view_li=view_li)
    html_string = funcs.AnchorOperation.if_empty_then_remove(html_string)
    html_string = funcs.HTML.file_protocol_support(html_string)

    return html_string


testdata = {"version": 1,
            "link_list": [
                {"card_id": "1620315134937", "desc": "A", "dir": "→"},
                {"card_id": "1620315139164", "desc": "B", "dir": "→"},
                {"card_id": "1620315139728", "desc": "C", "dir": "→"},
                {"card_id": "1620315140556", "desc": "D", "dir": "→"}],
            "self_data":
                {"card_id": "1620315134937", "desc": ""},
            "root": [
                {"nodename": "yes"},
                {"card_id": "1620315140556"}],
            "node": {
                "yes": [{"card_id": "1620315134937"},
                        {"card_id": "1620315139164"},
                        {"nodename": "no"}
                        ],
                "no": [{"card_id": "1620315139728"}],
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
