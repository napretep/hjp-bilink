import os
from functools import reduce
from typing import *
from aqt import mw
from bs4 import BeautifulSoup, element
import re, json
from . import utils
from .linkData_reader import LinkDataReader
from .backlink_reader import BackLinkReader
from . import imports

print, printer = imports.funcs.logger(__name__)


def HTML_txtContent_read(html):
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


def desc_extract(c=None):
    """读取卡片的描述,需要卡片id"""
    if isinstance(c, utils.Pair):
        cid = c.int_card_id
    elif isinstance(c, str):
        cid = int(c)
    elif type(c) == int:
        cid = c
    else:
        raise TypeError("参数类型不支持:" + c.__str__())

    cfg = utils.BaseInfo().userinfo
    note = mw.col.getCard(cid).note()
    desc = LinkDataReader(cid).read()["self_data"]["desc"]
    if desc == "":
        content = reduce(lambda x, y: x + y, note.fields)
        desc = HTML_txtContent_read(content)
        desc = re.sub(r"\n+", "", desc)
        desc = desc[0:cfg.descMaxLength if len(desc) > cfg.descMaxLength != 0 else len(desc)]
    return desc


def HTML_clipbox_exists(html, card_id=None):
    """任务:
    1检查clipbox的uuid是否在数据库中存在,如果存在,返回True,不存在返回False,
    2当存在时,检查卡片id是否是clipbox对应card_id,如果不是,则要添加,此卡片
    3搜索本卡片,得到clipbox的uuid,如果有搜到 uuid 但是又不在html解析出的uuid中, 则将数据库中的uuid的card_id删去本卡片的id
    """
    root = BeautifulSoup(html, "html.parser")
    imgli = root.find_all("img", attrs={"class": "hjp_clipper_clipbox"})
    clipbox_uuid_li = [re.sub("hjp_clipper_(\w+)_.png", lambda x: x.group(1), img.attrs["src"]) for img in imgli]
    DB = imports.objs.SrcAdmin.DB.go()
    # print(clipbox_uuid_li)
    true_or_false_li = [DB.exists(uuid) for uuid in clipbox_uuid_li]
    DB.end()
    return (reduce(lambda x, y: x or y, true_or_false_li, False))


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
        body_L1 = root.new_tag("div", attrs={"class": "container_body_L1"})
        L0.append(header_L1)
        L0.append(body_L1)
        anchor_el.append(L0)
    return anchor_el  # 已经传入了root,因此不必传出.


def HTML_LeftTopContainer_detail_el_make(root: "BeautifulSoup", summaryname, attr=None):
    """这是一个公共的步骤,设计一个details
    details.hjp_bilink .details
        summary
        div
    """
    if attr is None:
        attr = {}
    attrs = {"class": "hjp_bilink details"}.update(attr.copy())
    details = root.new_tag("details", attrs=attrs)
    summary = root.new_tag("summary")
    summary.string = summaryname
    div = root.new_tag("div")
    details.append(summary)
    details.append(div)
    return details, div


if __name__ == "__main__":
    html = """vt.反对；反抗<br>[[link:1620350799499_vt.反对；反抗_]]
<br><img alt="123" src="">`"""
    s = """
    {"backlink": [], "version": 1, "link_list": [{"card_id": "1620350799500", "desc": "a. \u53cd\u5bf9\u7684", "dir": "\u2192"}, {"card_id": "1620350799501", "desc": "adj.\u5bf9\u9762\u7684\uff1b\u76f8\u5bf9\u7684", "dir": "\u2192"}, {"card_id": "1620350799502", "desc": "n. \u53cd\u5bf9\uff1b\u654c\u5bf9", "dir": "\u2192"}, {"card_id": "1620350799497", "desc": "n.\u5bf9\u624b,\u654c\u624b\uff1b\u5bf9\u6297\u8005", "dir": "\u2192"}], "self_data": {"card_id": "1620350799499", "desc": "vt.\u53cd\u5bf9\uff1b\u53cd\u6297[[link:1620350799499_vt."}, "root": [{"card_id": "1620350799500"}, {"card_id": "1620350799501"}, {"card_id": "1620350799502"}, {"card_id": "1620350799497"}], "node": {}}"""
    print(HTML_txtContent_read(html))
