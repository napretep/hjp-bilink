# -*- coding:utf-8 -*-
"""
写了个HTML toObject toJSON 解析器
"""
import functools
import re
import types
import xml.dom.minidom as XMLParser
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup, element

if __name__ == "__main__":
    from utils import console, MetaClass_loger, Params
else:
    from .utils import console, MetaClass_loger, Params

class HTML_converter(object, metaclass=MetaClass_loger):
    """格式转换综合对象"""

    def __init__(self, **args):
        self.parse = BeautifulSoup
        self.text = ""
        self.domRoot: element = None
        self.objJSON: Dict = {}
        self.HTML_text = ""
        self.regexName = re.compile(r"div|button")
        self.regexCard_id = re.compile(r"\d+")

    def feed(self, text):
        """把接口变得简单一点,domRoot修改"""
        self.domRoot = self.parse(self.text, "html.parser")
        return self

    def getElementsByTagName(self, tagName):
        """获取TAG"""
        pass

    def text_get(self, node=None):
        """外层"""
        self.text = self.domRoot.text
        return self

    def HTML_get(self):
        self.HTML_text = self.domRoot.__str__()
        return self

    def node_remove(self, name=None, **args):
        """剔除一些标签, 默认是为了我的插件服务的,临时删除所有影响获取文本的无关结点"""
        if name is None:
            name = self.regexName
        if args == {}:
            args["card_id"] = self.regexCard_id
        list(map(lambda x: x.extract(), self.domRoot.find_all(name=name, **args)))
        return self

    def clear(self):
        self.__init__()
        return self

    def __setattr__(self, name, value):
        console(f"""{self.__class__.__name__}.{name}={value}""").log.end()
        self.__dict__[name] = value

    def __getattr__(self, name):
        console(f""" get {self.__class__.__name__}.{name}""").log.end()
        return self.__dict__[name]


def text_get(node: XMLParser.Element):
    rc = []
    nodeli = node.childNodes

    for n in nodeli:
        if n.nodeType == n.TEXT_NODE:
            console("data=" + n.data).log.end()
            if re.search(r"\S", n.data) is not None:
                rc += [n.data]
            else:
                rc += [re.sub(r"\s+", " ", n.data)]
        else:
            rc += text_get(n)
    return rc


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

    eg = HTML_converter()
    # p = eg.feed(egHTML3)
    # s = p.node_removeByTagAttrs().text_get.HTML_text
    soup = BeautifulSoup(egHTML3, "html.parser")
    soupLi = soup.select("button[card_id]")
    text = soup.text  # 获取文本
    text_HTML = soup.prettify()
    print()
