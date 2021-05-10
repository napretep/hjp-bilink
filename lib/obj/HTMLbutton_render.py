import json
from bs4 import BeautifulSoup, element
from aqt.utils import showInfo
from .inputObj import Input
from .handle_DB import LinkDataDBmanager
from .utils import BaseInfo, Pair, console, Config, THIS_FOLDER
from .HTML_converterObj import HTML_converter
from .linkData_reader import LinkDataReader
import os


class ButtonMaker(Config):
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

    def __init__(self, html: str, data: dict):
        super().__init__()
        self.anchorname = self.user_cfg["button_appendTo_AnchorId"] \
            if self.user_cfg["button_appendTo_AnchorId"] !="" else "anchor_container"
        self.html_str = html
        self.output_str = ""
        self.html_page = BeautifulSoup(self.html_str, "html.parser")
        self.data = data
        resultli = self.html_page.select(f"#{self.anchorname}")
        if len(resultli) > 0:
            self.anchor_el: element.Tag = resultli[0]
        else:
            self.anchor_el: element.Tag = self.html_page.new_tag("div", attrs={"id": self.anchorname})
            self.html_page.insert(1, self.anchor_el)

    def build(self):
        """直接的出口, 返回HTML的string"""
        self.create_style_el()
        self.create_cascadeDIV()
        return self.html_page.__str__()

    def create_cascadeDIV(self):
        L0 = self.html_page.new_tag("div", attrs={"class": "container_L0"})
        header_L1 = self.html_page.new_tag("div", attrs={"class": "container_header_L1"})
        header_L1.string = "hjp_bilink"
        body_L1 = self.html_page.new_tag("div", attrs={"class": "container_body_L1"})
        L0.append(header_L1)
        L0.append(body_L1)
        for item in self.data["root"]:
            if "card_id" in item:
                L2 = self.makebutton(item["card_id"])
            elif "nodename" in item:
                L2 = self.makedetails(item["nodename"])
            body_L1.append(L2)
        self.anchor_el.append(L0)

    def makebutton(self, card_id):
        h = self.html_page
        b = h.new_tag("button", attrs={"card_id": card_id,
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        cardinfo = self.data["node"][card_id]
        b.string = cardinfo["dir"] + cardinfo["desc"]
        return b

    def makedetails(self, nodename):
        li = self.data["node"][nodename]
        details = self.html_page.new_tag("details", attrs={"class": "hjp_bilink details"})
        summary = self.html_page.new_tag("summary")
        summary.string = nodename
        div = self.html_page.new_tag("div")
        details.append(summary)
        details.append(div)
        for item in li:
            if "card_id" in item:
                L2 = self.makebutton(item["card_id"])
            elif "nodename" in item:
                L2 = self.makedetails(item["nodename"])
            div.append(L2)
        return details

    def create_style_el(self):
        style_str = open(os.path.join(THIS_FOLDER, self.base_cfg["anchorCSSFileName"]), "r", encoding="utf-8").read()
        style = self.html_page.new_tag("style")
        style.string = style_str
        self.anchor_el.append(style)

    pass


def HTMLbutton_make(htmltext, card):
    data = LinkDataReader(str(card.id)).read()
    if len(data["link_list"]) > 0:
        return ButtonMaker(htmltext,data).build()
    else:
        return htmltext

testdata = {"version": 1,
            "link_list": [
                {"card_id": "1620315134937", "desc": "A", "dir": "→"},
                {"card_id": "1620315139164", "desc": "B", "dir": "→"},
                {"card_id": "1620315139728", "desc": "C", "dir": "→"},
                {"card_id": "1620315140556", "desc": "D", "dir": "→"}],
            "self_data":
                {"card_id": "1620315134937", "desc": ""},
            "root": [
                {"nodename":"yes"},
                {"card_id": "1620315140556"}],
            "node": {
                "yes":[{"card_id": "1620315134937"},
                       {"card_id": "1620315139164"},
                       {"nodename":"no"}
                       ],
                "no":[{"card_id": "1620315139728"}],
                "1620315134937":{"card_id": "1620315134937", "desc": "A", "dir": "→"},
                "1620315139164":{"card_id": "1620315139164", "desc": "B", "dir": "→"},
                "1620315139728":{"card_id": "1620315139728", "desc": "C", "dir": "→"},
                "1620315140556":{"card_id": "1620315140556", "desc": "D", "dir": "→"}
            }}


"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
</head>
<body>
<style>

.container_L0,
button[card_id] {
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
button[card_id] {
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
.hjp-bilink.details div{
    margin-left:6px;
}
</style>
<div class=""></div>
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
123123
</body>
</html>
"""
