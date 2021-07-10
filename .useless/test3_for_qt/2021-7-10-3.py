import os

from bs4 import BeautifulSoup, element

CSS_FOLDER = r"C:/Users/Administrator/AppData/Roaming/Anki2/addons21/hjp-bilink/lib/resource/data/anchor_CSS_default.css"


def HTML_LeftTopContainer_make(root: "BeautifulSoup"):
    """传入的是从html文本解析成的beautifulSoup对象
    设计的是webview页面的左上角按钮,包括的内容有:
    anchorname            ->一切的开始
        style             ->样式设计
        div.container_L0  ->按钮所在地
            div.header_L1 ->就是 hjp_bilink 这个名字所在的地方
            div.body_L1   ->就是按钮和折叠栏所在的地方
    """
    # 寻找 anchorname ,建立 anchor_el,作为总的锚点.
    # ID = utils.BaseInfo().userinfo.button_appendTo_AnchorId
    ID = ""
    anchorname = ID if ID != "" else "anchor_container"
    resultli = root.select(f"#{anchorname}")
    if len(resultli) > 0:
        anchor_el: "element.Tag" = resultli[0]
    else:
        anchor_el: "element.Tag" = root.new_tag("div", attrs={"id": anchorname})
        root.insert(1, anchor_el)
    # 设计 style
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
