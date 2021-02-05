# -*- coding:utf-8 -*-
"""
写了个HTML toObject toJSON 解析器
"""
import json
import re

from typing import List, Tuple, Dict
from bs4 import BeautifulSoup, element

if __name__ == "__main__":
    from utils import console, MetaClass_loger, Params, Pair, BaseInfo
else:
    from .utils import *


class HTML_converter(
    metaclass=MetaClass_loger
):
    """格式转换综合对象"""

    #

    def __init__(self, **args):
        self.parse = BeautifulSoup
        self.idPrefix = "cidd"
        self.regexName = re.compile(r"div|button")
        self.regexCard_id = re.compile(r"\d+")
        self.anchor_containerId = "hjp_bilink_anchor_container"  # 最外层的容器
        self.anchor_subcontainerId = "hjp_bilink_buttonlist"  # 按钮包裹的容器
        self.buttonList_headerId = "hjp_bilink_anchor_header"  # 标题所在地
        self.buttonDivCSS = BaseInfo().anchorCSS_load().format(container=self.anchor_containerId,
                                                               subcontainer=self.anchor_subcontainerId,
                                                               header=self.buttonList_headerId)
        self.scriptId = "hjp_bilink_data"
        self.scriptVarName = "hjp_bilink_data"
        self.var_init()

    def var_init(self):
        """变量初始化"""
        self.text = ""
        self.domRoot: element = None
        self.objJSON: Dict = {}
        self.HTML_text = ""
        self.card_linked_pairLi: List[Pair] = []
        self.script_el = None

    def feed(self, text):
        """把接口变得简单一点,domRoot修改"""
        # console(text).log.end()
        self.domRoot = self.parse(text, "html.parser")
        if self.domRoot is None:
            raise ValueError("domRoot是空值!!" + type(self.domRoot))
        return self

    def getElementsByTagName(self, tagName):
        """获取TAG"""
        pass

    @debugWatcher
    def pairLi_fromOldVer(self) -> List[Pair]:
        """解决0.4,0.6两个版本的升级"""
        divLi = self.domRoot.select("div[card_id]")
        pairLi = []
        for el in divLi:
            desc = re.sub(r"^→|^←| cidd\d+", "", el.text)
            dir_ = el.attrs["dir"] if "dir" in el.attrs else "→"
            pair = Pair(card_id=el.attrs["card_id"], desc=desc, dir=dir_)
            pairLi.append(pair)
            el.extract()
        buttonContainers = self.domRoot.select("div[id=hjp_bilink_button]")
        for buttonContainer in buttonContainers:
            buttonLi = buttonContainer.select("button[card_id]")
            for el in buttonLi:
                desc = el.text
                dir_ = el.attrs["dir"] if "dir" in el.attrs else "→"
                pair = Pair(card_id=el.attrs["card_id"], desc=desc, dir=dir_)
                pairLi.append(pair)
            buttonContainer.extract()
        console("这里做完了pairLi_fromOldVer,看看root的值" + self.domRoot.__str__()).log.end()
        return pairLi

    def button_make(self, **args):
        """用来创建按钮,需要提供pair,direction"""
        # 新建bs4.element对象
        self.fbtnmk_HTMLbutton = \
            self.domRoot.new_tag(name="button", card_id=args["Id"], dir=args["direction"],
                                 onclick=f"""javascript:pycmd('{args["prefix"]}'+'{args["Id"]}');""",
                                 style=f"""'displaystyle:inline;font-size:inherit;{args["linkStyle"]};""", )
        self.fbtnmk_HTMLbutton.string = args["direction"] + args["desc"]
        self.fbtmk_div = self.domRoot.select(f"#{self.buttonDivId}")
        if len(self.fbtmk_div) == 0:
            self.fbtmk_div_ = self.domRoot.new_tag("div", id=self.buttonDivId)
            self.fbtmk_div_.append(self.fbtnmk_HTMLbutton)
            self.domRoot.append(self.domRoot.new_tag("br"))
            self.domRoot.append(self.domRoot.new_tag("br"))
            self.domRoot.append(self.fbtmk_div_)
            self.domRoot.append(self.domRoot.new_tag("br"))
            self.domRoot.append(self.domRoot.new_tag("br"))
        else:
            self.domRoot.select(f"#{self.buttonDivId}")[0].append(self.fbtnmk_HTMLbutton)
        return self

    def text_get(self, node=None):
        """外层非标签属性的所有文本"""
        self.text = self.domRoot.text
        return self

    def HTML_get(self):
        """获取整个html"""
        self.HTML_text = self.domRoot.__str__()
        return self

    def node_remove(self, name=None, **args):
        """剔除一些标签, 默认是为了我的插件服务的,临时删除所有影响获取文本的无关结点"""
        name = self.regexName if name is None else name
        args["card_id"] = self.regexCard_id if args == {} else args["card_id"]
        list(map(lambda x: x.extract(), self.domRoot.find_all(name=name, attrs=args)))
        return self

    def clear(self):
        """初始化自身"""
        self.var_init()
        return self

    @debugWatcher
    def script_el_remove(self):
        """临时删除script,减少干扰,不写入就行"""
        self.script_el_select(new=False)
        if self.script_el:
            self.script_el.extract()
        return self

    @debugWatcher
    def script_el_select(self, new=True):
        """读取script元素,保存到self.script_el, new 表示如果找不到是否要新建一个"""
        self.script_el = self.domRoot.select(f"[id={self.scriptId}]")
        if not self.script_el and new:
            self.script_el = self.domRoot.new_tag(name="script", id=self.scriptId)
            self.domRoot.append(self.script_el)
        elif self.script_el:
            self.script_el = self.script_el[0]
        else:
            self.script_el = None
        return self

    @debugWatcher
    def pairLi_removePair(self, **kwargs):
        """移除卡片数据对,操作card_linked_pairLi,接受两种参数:pair或pairLi"""
        self.pairLi_loadFromHTML()
        if not self.script_el:
            return self
        elif "pair" in kwargs:
            waitDelete = kwargs["pair"]
            for pair in self.card_linked_pairLi:
                if pair.card_id == waitDelete.card_id:
                    self.card_linked_pairLi.remove(pair)
                    break
        elif "pairLi" in kwargs:
            for pair in kwargs["pairLi"]:
                self.pairLi_removePair(pair=pair)
        return self

    def pairLi_appendPair(self, **kwargs):
        """从pair中提取html格式的JSON,操作card_linked_pairLi,接受两种参数:pair或pairLi"""
        if "pair" in kwargs:
            self.script_el_select().pairLi_loadFromHTML().card_linked_pairLi.append(kwargs["pair"])
        elif "pairLi" in kwargs:
            self.script_el_select().pairLi_loadFromHTML().card_linked_pairLi += kwargs["pairLi"]
        return self

    @debugWatcher
    def HTML_savePairLi(self):
        """小功能给他做成单个函数,保存到self.script_el.string,把JSON数据保存到字段中"""
        card_linked_JSONs = list(map(lambda x: x.__dict__, self.card_linked_pairLi))
        self.script_el_select()  # 如果不存在应该换新
        self.script_el.string = self.scriptId + "=" + json.dumps(card_linked_JSONs, ensure_ascii=False)
        console("self.script_el.string:" + self.script_el.__str__()).log.end()

        return self

    def HTML_makeButtonFromPairLi(self, **args):
        """制作按钮"""
        cfg = BaseInfo().configObj
        anchor_container: element = self.domRoot.select(f"[id={self.anchor_containerId}]")
        if not anchor_container:
            anchor_container = self.domRoot.new_tag(name="div", id=self.anchor_containerId, style=self.buttonDivCSS)
            self.domRoot.insert(1, anchor_container)
        else:
            anchor_container = anchor_container[0]
        anchor_header = self.domRoot.new_tag(name="div", id=self.buttonList_headerId)
        anchor_header.string = consolerName
        anchor_container.append(anchor_header)
        style = self.domRoot.new_tag(name="style")
        style.string = self.buttonDivCSS
        self.domRoot.insert(1, style)
        buttonWrapper = self.domRoot.new_tag(name="div", id=self.anchor_subcontainerId)
        anchor_container.append(buttonWrapper)
        for pair in self.card_linked_pairLi:
            button = \
                self.domRoot.new_tag(name="button", card_id=pair.card_id, dir=pair.dir,
                                     onclick=f"""javascript:pycmd('{self.idPrefix}'+'{pair.card_id}');""",
                                     style=f"""'margin:12px;displaystyle:inline;font-size:inherit;{cfg.linkStyle};""", )
            button.string = pair.dir + pair.desc
            buttonWrapper.append(button)
        return self

    @debugWatcher
    def pairLi_loadFromHTML(self):
        """从HTML中读取json,保存到 self.card_linked_pairLi"""
        self.script_el_select(new=False)
        if self.script_el:
            if self.script_el.string:
                console("report:script_el" + self.script_el.__str__()).log.end()
                script_str = re.sub(rf"{self.scriptId}=", "", self.script_el.string.__str__())
            else:
                script_str = "[]"

            if script_str:
                console("report:script_str" + script_str).log.end()
                self.card_linked_pairLi: List[Pair] = \
                    list(map(lambda x: Pair(card_id=x["card_id"], desc=x["desc"], dir=x["dir"]),
                             json.loads(script_str)))
        return self

    def __setattr__(self, name, value):
        console(f"""{self.__class__.__name__}.{name}={value}""").log.end()
        self.__dict__[name] = value

    def __getattr__(self, name):
        console(f""" getattr→ {self.__class__.__name__}.{name}  """).log.end()
        return self.__dict__[name]


if __name__ == "__main__":
    egHTML3 = """例6<div><img src="paste-63321a4e3844697f2f47ec4995fe3bb9c3d9c4d0.jpg"><br></div>

<div card_id="1601490254697" dir="→" style="">→杨子胥789 cidd1601490254697</div>
<div card_id="1602601817134" dir="→" style="">→例9 cidd1602601817134</div>
<div card_id="1601490361215" dir="→" style=""><br></div>
<div card_id="1601490606521" dir="→" style="">→802 cidd1601490606521</div>
"""
    egHTML = """<div class="anci_header_content">
  <div class="article-title">
    <h2>辉瑞和阿斯利康缩减供货？部分国家恐将辉瑞告上法庭</h2>
  </div>
  <div class="article-desc clearfix">
    <div class="author-icon">
      <a href="https://author.baidu.com/home?from=bjh_article&amp;app_id=1549941228125394" target="_blank">
        <img src="https://pic.rmb.bdstatic.com/b9279adf974b78d27201a0b34970c2a9.jpeg"/>
      </a>
      <i class="author-vip author-vip-2"/>
    </div>
    <div class="author-txt">
      <div class="author-name">
        <a href="https://author.baidu.com/home?from=bjh_article&amp;app_id=1549941228125394" target="_blank">北晚新视觉网</a>
      </div>
      <div class="article-source article-source-bjh">
        <span class="date">发布时间：01-28</span>
        <span class="time">09:24</span>
        <span class="account-authentication">北京晚报官网官方帐号</span>
      </div>
    </div>
  </div>
</div>"""
    egHTML2 = """<?xml version="1.0"?>
<virtualRoot>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
        <neighbor name="Colombia" direction="E"/>
    </country>
</virtualRoot>
    """
    egHTML4 = """
    <script id="hjp_bilink_data">
hjp_bilink_data=[
{"card_id":"1611035897919",
"desc":"吃饭"
}

]
</script>
    """

    eg = HTML_converter()
    # p = eg.feed(egHTML3)
    # s = p.node_removeByTagAttrs().text_get.HTML_text
    soup = BeautifulSoup(egHTML3, "html.parser")
    soupLi = soup.select("button[card_id]")
    text = soup.text  # 获取文本
    text_HTML = soup.prettify()
    print()
