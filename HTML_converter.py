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


class HTML_converter(object,
                     # metaclass=MetaClass_loger
                     ):
    """格式转换综合对象"""

    def __init__(self, **args):

        self.parse = BeautifulSoup
        self.text = ""
        self.domRoot: element = None
        self.objJSON: Dict = {}
        self.HTML_text = ""
        self.idPrefix = "cidd"
        self.regexName = re.compile(r"div|button")
        self.regexCard_id = re.compile(r"\d+")
        self.buttonDivId = "hjp_bilink_button"
        self.buttonDivCSS = """
display: grid;
grid-template-columns: repeat(auto-fill,minmax(250px,auto));
grid-template-rows: repeat(2,minmax(0px,auto));
grid-auto-columns: minmax(250px,1fr);
grid-auto-flow: row;
overflow:auto;
background-color: #F7F8F8;
max-height:300px;
}
        """
        self.scriptId = "hjp_bilink_data"
        self.scriptVarName = "hjp_bilink_data"
        self.card_linked_pairs: List[Pair] = []

    def feed(self, text):
        """把接口变得简单一点,domRoot修改"""
        self.domRoot = self.parse(text, "html.parser")
        return self

    def getElementsByTagName(self, tagName):
        """获取TAG"""
        pass

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
        """外层"""
        self.text = self.domRoot.text
        return self

    def HTML_get(self):
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
        self.__init__()
        return self

    def HTML_makeButtonFromJSON(self, **args):
        """制作按钮"""
        cfg = BaseInfo().configObj
        button_container: element = self.domRoot.select(f"[id={self.buttonDivId}]")
        if not button_container:
            button_container = self.domRoot.new_tag(name="div", id=self.buttonDivId, style=self.buttonDivCSS)
            self.domRoot.insert(button_container, 0)
        else:
            button_container = button_container[0]
        for pair in self.card_linked_pairs:
            button = \
                self.domRoot.new_tag(name="button", card_id=pair.card_id, dir=pair.dir,
                                     onclick=f"""javascript:pycmd('{self.idPrefix}'+'{pair.card_id}');""",
                                     style=f"""'displaystyle:inline;font-size:inherit;margin:2px;{cfg.linkStyle};""", )
            button_container.append(button)
        return self

    def JSON_loadFromHTML(self):
        """从HTML中读取json"""
        script_el = self.domRoot.select(f"script[id={self.scriptId}]")
        if script_el:
            script_el = script_el[0]
            script_str = re.search(rf"(?<={self.scriptId}=)\[[\s\S]+?]", script_el.__str__())
            if script_str is not None:
                self.card_linked_pairs: List[Pair] = \
                    list(map(lambda x: Pair(card_id=x["card_id"], desc=x["desc"], dir=x["dir"]),
                             json.loads(script_str[0])))
        return self

    def __setattr__(self, name, value):
        # console(f"""{self.__class__.__name__}.{name}={value}""").log.end()
        self.__dict__[name] = value

    def __getattr__(self, name):
        # console(f""" getattr→ {self.__class__.__name__}.{name}  """).log.end()
        return self.__dict__[name]


if __name__ == "__main__":
    egHTML3 = """G<button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button><button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button><button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button><button card_id="1611035896519" dir="→" onclick="javascript:pycmd(&quot;cidd&quot;+&quot;1611035896519&quot;);" style="font-size:inherit;"> →A</button>"""
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
