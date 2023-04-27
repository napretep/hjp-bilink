
from .basic_funcs import *
from anki.cards import CardId,Card


class FieldHTMLData:
    def __init__(self, html: BeautifulSoup, card_id=None):

        super().__init__()
        self.card_id = card_id
        self.html_str = html.__str__()
        self.output_str = ""
        self.html_root = html
        self.anchor_container_L0 = G.safe.funcs.HTML.LeftTopContainer_make(self.html_root)
        self.anchor_body_L1 = self.anchor_container_L0.find("div", attrs={"class": "container_body_L1"})
        self.data: "G.objs.LinkDataJSONInfo" = None


# anchor中的全局backlink maker
class 全局双链按钮生成(FieldHTMLData):
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
        # from .objs import LinkDataPair
        LinkDataPair = G.objs.LinkDataPair
        # from ..bilink import linkdata_admin
        # data = LinkDataReader(self.card_id).read()
        linkdata_admin = G.safe.linkdata_admin
        # self.data = data
        self.data = imports.link.GlobalLinkDataOperation.read_from_db(self.card_id)
        # self.data = linkdata_admin.read_card_link_info(self.card_id)
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
        b.string = "→" + G.safe.funcs.CardOperation.desc_extract(card_id)
        return b

    # 创建 anchor中的backlink专区
    def cascadeDIV_create(self):
        details, div = G.safe.funcs.HTML_左上角容器_detail元素_制作(self.html_root, "card global backlink", attr={"open": "", "class": "backlink"})
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
        details, div = G.safe.funcs.HTML_左上角容器_detail元素_制作(self.html_root, node.name)
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
        linkdata_admin = G.safe.linkdata_admin
        h = self.html_root
        # funcs.Utils.print("make backlink", need_timestamp=True)
        if len(self.data.backlink) == 0:
            return None
        details, div = G.safe.funcs.HTML_左上角容器_detail元素_制作(self.html_root, "referenced_in_text",
                                                           attr={"open": "", "class": "referenced_in_text"})
        for card_id in self.data.backlink:
            data: "G.objs.LinkDataJSONInfo" = linkdata_admin.read_card_link_info(card_id)
            L2 = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor button",
                                            "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
            L2.string = "→" + G.safe.funcs.CardOperation.desc_extract(card_id)
            div.append(L2)

        self.anchor_body_L1.append(details)

    pass



# 文内链接的按钮设置

def InTextButtonMakeProcess(html_string):
    # from ..bilink.in_text_admin.backlink_reader import BackLinkReader
    BackLinkReader = G.safe.in_text_admin.backlink_reader.BackLinkReader
    buttonli = BackLinkReader(html_str=html_string).backlink_get()
    if len(buttonli) > 0:
        finalstring = html_string[0:buttonli[0]["span"][0]]
        for i in range(len(buttonli) - 1):
            prevEnd, nextBegin = buttonli[i]["span"][1], buttonli[i + 1]["span"][0]
            finalstring += G.safe.funcs.HTML.InTextButtonMake(buttonli[i]) + html_string[prevEnd:nextBegin]
        finalstring += G.safe.funcs.HTML.InTextButtonMake(buttonli[-1]) + html_string[buttonli[-1]["span"][1]:]
    else:
        finalstring = html_string
    return finalstring

class InTextButtonMaker(FieldHTMLData):
    """负责将[[link:card-id_desc_]]替换成按钮"""

    def build(self):
        # from ..bilink.in_text_admin.backlink_reader import BackLinkReader
        BackLinkReader = G.safe.in_text_admin.backlink_reader.BackLinkReader
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
        desc = G.safe.funcs.CardOperation.desc_extract(card_id)
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": card_id, "class": "hjp-bilink anchor intext button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = desc
        return b.__str__()


# 创建视图的反向链接
class 视图双链按钮生成(FieldHTMLData):
    def build(self, view_li: "set[G.safe.funcs.GViewData]" = None):
        # if not view_li: view_li = G.safe.funcs.GviewOperation.find_by_card([G.objs.LinkDataPair(self.card_id)])
        self.cascadeDIV_create(view_li)
        return self.html_root

    def button_make(self, 结点编号,结点名称, 方向="→", 数据类型=None):
        ankilink = G.safe.funcs.G.src.ankilink
        if 数据类型 is None:
            数据类型 = G.safe.baseClass.视图结点类型.卡片
        if 数据类型 is None  or 数据类型 == G.safe.baseClass.视图结点类型.卡片:
            pycmd = f"""{ankilink.protocol}://{ankilink.cmd.opencard}={结点编号}"""
        elif 数据类型 == G.safe.baseClass.视图结点类型.视图:
            pycmd = f"""{ankilink.protocol}://{ankilink.cmd.opengview}={结点编号}"""
        else:
            raise ValueError(f"未知的数据类型={数据类型}")
        h = self.html_root
        b = h.new_tag("button", attrs={"card_id": 结点编号, "class": "hjp-bilink anchor view button",
                                       "onclick": f"""javascript:pycmd('{pycmd}');"""})
        b.string = 方向+数据类型+":"+结点名称
        return b

    def cascadeDIV_create(self, 视图集: "set[G.safe.configsModel.GViewData]"):

        cid=str(self.card_id)
        for 视图 in 视图集:
            details, div = G.safe.funcs.HTML_左上角容器_detail元素_制作(self.html_root, "view:" + 视图.name, attr={"open": "", "class": "gview"})
            边集 = 视图.数据获取.获取对应边(cid)

            出边集 = [边.split(",")[1] for 边 in 边集 if 边.startswith(cid)]
            入边集 = [边.split(",")[0] for 边 in 边集 if 边.endswith(cid)]
            for 出边 in 出边集:
                if 视图.nodes[出边].预览可见.值:
                    结点类型 = 视图.nodes[出边].数据类型.值
                    结点名称 = 视图.nodes[出边].描述.值
                    button = self.button_make(出边,结点名称,数据类型=结点类型)
                    div.append(button)
            for 入边 in 入边集:
                if 视图.nodes[入边].预览可见.值:
                    结点类型 = 视图.nodes[入边].数据类型.值
                    结点名称= 视图.nodes[入边].描述.值
                    button = self.button_make(入边,结点名称,"←",结点类型)
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

    linkdata_admin = G.safe.linkdata_admin
    backlink_reader = G.safe.in_text_admin.backlink_reader
    全局双链数据 = linkdata_admin.read_card_link_info(str(card.id))
    """

    """
    左上角下拉菜单 = BeautifulSoup("", "html.parser")

    # 以下ButtonMaker是用来生成左上角按钮的
    有全局反链 = len(全局双链数据.link_list) > 0 or len(全局双链数据.backlink) > 0
    if 有全局反链:
        # funcs.Utils.print(f"{card.id} hasbacklink")
        左上角下拉菜单 = 全局双链按钮生成(左上角下拉菜单, card_id=card.id).build()
    print(左上角下拉菜单)

    view_li = G.safe.funcs.GviewOperation.find_by_card([G.objs.LinkDataPair(str(card.id))])
    有视图反链 = len(view_li) > 0
    if 有视图反链:
        # funcs.Utils.print(f"{card.id} len(view_li)>0:")
        左上角下拉菜单 = 视图双链按钮生成(左上角下拉菜单, card_id=card.id).build(view_li=view_li)
    print(左上角下拉菜单)
    # 以下内容来替换文本, 替换文本是
    有文内链接 = len(backlink_reader.BackLinkReader(html_str=htmltext).backlink_get()) > 0
    if 有文内链接:
        # funcs.Utils.print(f"{card.id} hasInTextButton")
        html_string = G.safe.funcs.HTML.InTextButtonDeal(html_string)
        # html_string = InTextButtonMaker(html_string).build()

    html_string = G.safe.funcs.HTML.file_protocol_support(html_string)

    # 如果左上角确实有内容则将其插入htmltext
    # funcs.Utils.print(anchor)
    右上角下拉菜单需要显示 = 左上角下拉菜单.find("div", attrs={"class": "container_body_L1"})
    if 右上角下拉菜单需要显示:
        container_body_L1_children = [child for child in 左上角下拉菜单.find("div", attrs={"class": "container_body_L1"}).children]
        if len(container_body_L1_children) > 0:
            script = G.safe.funcs.HTML.cardHTMLShadowDom(左上角下拉菜单.__str__())
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
