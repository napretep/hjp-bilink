import json
import re

from bs4 import BeautifulSoup, element
from aqt.utils import showInfo

from .backlink_reader import BackLinkReader
from .inputObj import Input
from .handle_DB import LinkDataDBmanager
from .utils import BaseInfo, Pair, console, Config, THIS_FOLDER

from .linkData_reader import LinkDataReader
import os
from . import funcs
from . import clipper_imports

print, _ = clipper_imports.funcs.logger(__name__)


class FieldHTMLData(Config):
    def __init__(self, html: str, card_id=None):
        super().__init__()
        self.card_id = card_id
        self.html_str = html
        self.output_str = ""
        self.html_root = BeautifulSoup(self.html_str, "html.parser")
        self.anchor_container_L0 = funcs.HTML_LeftTopContainer_make(self.html_root)
        self.anchor_body_L1 = self.anchor_container_L0.find("div", attrs={"class": "container_body_L1"})


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
        data = LinkDataReader(self.card_id).read()
        self.data = data
        if "backlink" not in data: data["backlink"] = []
        self.cascadeDIV_create()  # 这个名字其实取得不好,就是反链的设计
        self.backlink_create()  # 这个是文内链接的设计,顺便放着的,因为用的元素基本一样.
        return self.html_root.__str__()

    def button_make(self, card_id):
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        cardinfo = self.data["node"][card_id]
        b.string = cardinfo["dir"] + cardinfo["desc"]
        return b

    def cascadeDIV_create(self):
        for item in self.data["root"]:
            if "card_id" in item:
                L2 = self.button_make(item["card_id"])
            elif "nodename" in item:
                L2 = self.details_make(item["nodename"])
            self.anchor_body_L1.append(L2)

    def details_make(self, nodename):
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, nodename)
        li = self.data["node"][nodename]
        for item in li:
            if "card_id" in item:
                L2 = self.button_make(item["card_id"])
            elif "nodename" in item:
                L2 = self.details_make(item["nodename"])
            div.append(L2)
        return details

    def backlink_create(self):
        h = self.html_root
        if "backlink" in self.data:
            card_id_li = self.data["backlink"]
            if len(card_id_li) == 0:
                return None
        else:
            return None
        details, div = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "referenced_in_text",
                                                                  attr={"open": ""})
        for card_id in card_id_li:
            data = LinkDataReader(card_id).read()["self_data"]
            L2 = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor button",
                                            "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
            L2.string = "→" + data["desc"]
            div.append(L2)

        self.anchor_body_L1.append(details)
    pass

class InTextButtonMaker(FieldHTMLData):
    """负责将[[link:card-id_desc_]]替换成按钮"""
    def build(self):
        buttonli=BackLinkReader(html_str = self.html_str).backlink_get()
        if len(buttonli)>0:
            finalstring = self.html_str[0:buttonli[0]["span"][0]]
            for i in range(len(buttonli)-1):
                prevEnd,nextBegin  = buttonli[i]["span"][1],buttonli[i+1]["span"][0]
                finalstring += self.button_make(buttonli[i])+self.html_str[prevEnd:nextBegin]
            finalstring += self.button_make(buttonli[-1])+self.html_str[buttonli[-1]["span"][1]:]
        else:
            finalstring = self.html_str
        return finalstring

    def button_make(self,data):
        card_id = data["card_id"]
        desc = data["desc"]
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink intext button",
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
        PDF_baseinfo_dict = clipper_imports.objs.SrcAdmin.PDF_JSON.load().data
        details1, div1 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, "clipped_from_PDF")
        for pdfuuid, name_page in PDF_page_dict.items():  # {uuid:{pagenum:{},pdfname:""}}
            if pdfuuid in PDF_baseinfo_dict and "page_shift" in PDF_baseinfo_dict[pdfuuid]:
                page_shift = PDF_baseinfo_dict[pdfuuid]["page_shift"]
            else:
                page_shift = 0
            pdfname = clipper_imports.funcs.str_shorten(os.path.basename(name_page["pdfname"]))
            pagenumlist = list(name_page["pagenum"])
            details2, div2 = funcs.HTML_LeftTopContainer_detail_el_make(self.html_root, pdfname, attr={"open": ""})
            details1.append(details2)
            for pagenum in pagenumlist:
                uuid = pdfuuid
                desc = f""" pdf_page_at: {pagenum}, book_page_at:{pagenum - page_shift + 1} """
                button = self.button_make(uuid, pagenum, desc)
                div2.append(button)
        self.anchor_body_L1.append(details1)

    pass

def HTMLbutton_make(htmltext, card):
    html_string = htmltext
    data = LinkDataReader(str(card.id)).read()

    if len(data["link_list"]) > 0 or len(data["backlink"]) > 0:
        html_string = AnchorButtonMaker(html_string, card_id=card.id).build()
        # print(html_string)
    hasInTextButton = len(BackLinkReader(html_str=htmltext).backlink_get()) > 0
    if hasInTextButton:
        html_string = InTextButtonMaker(html_string).build()
    if funcs.HTML_clipbox_exists(html_string):
        html_string = PDFPageButtonMaker(html_string, card_id=card.id).build()
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