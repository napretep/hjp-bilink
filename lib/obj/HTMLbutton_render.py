import json
import re

from bs4 import BeautifulSoup, element
from aqt.utils import showInfo

from .backlink_reader import BackLinkReader
from .inputObj import Input
from .handle_DB import LinkDataDBmanager
from .utils import BaseInfo, Pair, console, Config, THIS_FOLDER
from .HTML_converterObj import HTML_converter
from .linkData_reader import LinkDataReader
import os


class FieldHTMLData(Config):
    def __init__(self, html: str):
        super().__init__()
        self.html_str = html
        self.output_str = ""
        self.html_page = BeautifulSoup(self.html_str, "html.parser")


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

    def build(self, data: dict):
        """直接的出口, 返回HTML的string"""
        self.data = data
        self.anchor_el_find()
        self.style_el_create()
        self.cascadeDIV_create()
        self.backlink_create()
        return self.html_page.__str__()

    def button_make(self, card_id):
        h = self.html_page
        b = h.new_tag("button", attrs={"card_id": card_id,"class":"hjp-bilink anchor button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        cardinfo = self.data["node"][card_id]
        b.string = cardinfo["dir"] + cardinfo["desc"]
        return b

    def anchor_el_find(self):
        self.anchorname = self.user_cfg["button_appendTo_AnchorId"] \
            if self.user_cfg["button_appendTo_AnchorId"] != "" else "anchor_container"
        resultli = self.html_page.select(f"#{self.anchorname}")
        if len(resultli) > 0:
            self.anchor_el: element.Tag = resultli[0]
        else:
            self.anchor_el: element.Tag = self.html_page.new_tag("div", attrs={"id": self.anchorname})
            self.html_page.insert(1, self.anchor_el)

    def cascadeDIV_create(self):
        L0 = self.html_page.new_tag("div", attrs={"class": "container_L0"})
        header_L1 = self.html_page.new_tag("div", attrs={"class": "container_header_L1"})
        header_L1.string = "hjp_bilink"
        body_L1 = self.html_page.new_tag("div", attrs={"class": "container_body_L1"})
        L0.append(header_L1)
        L0.append(body_L1)
        for item in self.data["root"]:
            if "card_id" in item:
                L2 = self.button_make(item["card_id"])
            elif "nodename" in item:
                L2 = self.details_make(item["nodename"])
            body_L1.append(L2)
        self.anchor_el.append(L0)

    def details_make(self, nodename):
        li = self.data["node"][nodename]
        details = self.html_page.new_tag("details", attrs={"class": "hjp_bilink details"})
        summary = self.html_page.new_tag("summary")
        summary.string = nodename
        div = self.html_page.new_tag("div")
        details.append(summary)
        details.append(div)
        for item in li:
            if "card_id" in item:
                L2 = self.button_make(item["card_id"])
            elif "nodename" in item:
                L2 = self.details_make(item["nodename"])
            div.append(L2)
        return details

    def style_el_create(self):
        style_str = open(os.path.join(THIS_FOLDER, self.base_cfg["anchorCSSFileName"]), "r", encoding="utf-8").read()
        style = self.html_page.new_tag("style")
        style.string = style_str
        self.anchor_el.append(style)

    def backlink_create(self):
        h = self.html_page
        if "backlink" in self.data:
            card_id_li = self.data["backlink"]
            if len(card_id_li)==0:
                return None
        else:
            return None
        details = self.html_page.new_tag("details", attrs={"class": "hjp_bilink details","open":""})
        summary = self.html_page.new_tag("summary")
        summary.string = "referenced_in_text"
        details.append(summary)
        for card_id in card_id_li:
            data = LinkDataReader(card_id).read()["self_data"]
            b = h.new_tag("button", attrs={"card_id": card_id,"class":"hjp-bilink anchor button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
            b.string = "→"+data["desc"]
            details.append(b)
        body_L1 = self.html_page.select("div.container_body_L1")[0]
        body_L1.append(details)
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
        h = self.html_page
        b = h.new_tag("button", attrs={"card_id": card_id,"class":"hjp-bilink intext button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = desc
        return b.__str__()




def HTMLbutton_make(htmltext, card):
    html_string = htmltext
    data = LinkDataReader(str(card.id)).read()
    if "backlink" not in data: data["backlink"] =[]
    if len(data["link_list"]) > 0 or len(data["backlink"])>0:
        html_string = AnchorButtonMaker(html_string).build(data)
    hasInTextButton = len(BackLinkReader(html_str = htmltext).backlink_get()) > 0
    if hasInTextButton:
        html_string = InTextButtonMaker(html_string).build()

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