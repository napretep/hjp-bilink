# -*- coding:utf-8 -*-
"""
写了个HTML toObject toJSON 解析器
"""
from typing import Dict

from bs4 import BeautifulSoup, element

# from ..obj.inputObj import Input

if __name__ == "__main__":
    from ...lib.obj.utils import console, MetaClass_loger, Params, Pair, BaseInfo
else:
    from ...lib.obj.utils import *


class HTML_converter(
    # metaclass=MetaClass_loger
):
    """格式转换综合对象, 主要的工作都是基于pairli在做,script用来读取和写入.
    """

    #

    def __init__(self, **args):
        self.parse = BeautifulSoup
        self.idPrefix = "cidd"
        self.baseInfo = BaseInfo()
        self.consolerName = self.baseInfo.consoler_Name
        self.config = self.baseInfo.config_obj
        self.regexName = re.compile(r"div|button")
        self.regexCard_id = re.compile(r"\d+")
        self.text = ""
        self.domRoot: element = None
        self.objJSON: Dict = {}
        self.HTML_text = ""
        self.cardinfo_dict = {}
        self.exist_pairli = []
        self.card_linked_pairLi: List[Pair] = []
        self.card_selfdata_dict = {}
        self.script_el_dict = {}
        self.comment_el = None
        self.container_L0_Id = self.baseInfo.config_obj.button_appendTo_AnchorId  # 最外层的容器
        self.container_body_L1_class = self.consolerName + self.baseInfo.container_body_L1_className  # 按钮包裹的容器
        self.container_header_L1_class = self.consolerName + self.baseInfo.container_header_L1_className  # 标题所在地
        self.accordion_L2_class = self.consolerName + self.baseInfo.accordion_L2_className
        self.accordion_header_L3_class = self.consolerName + self.baseInfo.accordion_header_L3_className
        self.accordion_body_L3_class = self.consolerName + self.baseInfo.accordion_body_L3_className
        self.accordion_checkbox_L3_Id = self.consolerName + self.baseInfo.accordion_checkbox_L3_IdName
        self.containerDivCSS: str = self.baseInfo.str_AnchorCSS_get()
        self.linkdata_scriptId = self.consolerName + self.baseInfo.linkdata_scriptIdName  # 这个不好轻易变化, 大家的原始数据都在这里呢
        self.carddata_scriptId = self.consolerName + self.baseInfo.carddata_scriptIdName
        self.linkdata_scriptVarName = self.consolerName + self.baseInfo.linkdata_scriptVarName  # 这个不好轻易变化, 大家的原始数据都在这里呢

    def var_init(self):
        """变量初始化"""
        self.text = ""
        self.domRoot: element = None
        self.objJSON: Dict = {}
        self.HTML_text = ""
        self.cardinfo_dict = {}
        self.syncpairli = []
        self.card_linked_pairLi: List[Pair] = []
        self.card_selfdata_dict = {}
        self.script_el_dict = {}
        self.comment_el = None
        self.container_L0_Id = self.baseInfo.config_obj.button_appendTo_AnchorId  # 最外层的容器
        self.container_body_L1_class = self.consolerName + self.baseInfo.container_body_L1_className  # 按钮包裹的容器
        self.container_header_L1_class = self.consolerName + self.baseInfo.container_header_L1_className  # 标题所在地
        self.accordion_L2_class = self.consolerName + self.baseInfo.accordion_L2_className
        self.accordion_header_L3_class = self.consolerName + self.baseInfo.accordion_header_L3_className
        self.accordion_body_L3_class = self.consolerName + self.baseInfo.accordion_body_L3_className
        self.accordion_checkbox_L3_Id = self.consolerName + self.baseInfo.accordion_checkbox_L3_IdName
        self.containerDivCSS: str = self.baseInfo.anchorCSSFile
        self.linkdata_scriptId = self.consolerName + self.baseInfo.linkdata_scriptIdName  # 这个不好轻易变化, 大家的原始数据都在这里呢
        self.carddata_scriptId = self.consolerName + self.baseInfo.carddata_scriptIdName
        self.linkdata_scriptVarName = self.consolerName + self.baseInfo.linkdata_scriptVarName  # 这个不好轻易变化, 大家的原始数据都在这里呢

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

    # @debugWatcher
    def pairLi_fromOldVer(self) -> List[Pair]:
        """解决0.4,0.6两个版本的升级"""
        divLi = self.domRoot.select("div[card_id]")
        pairLi = []
        for el in divLi:
            desc = re.sub(r"^→|^←|\s*cidd\d+", "", el.text)
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
        # console("这里做完了pairLi_fromOldVer,看看root的值" + self.domRoot.__str__()).log.end()
        return pairLi

    def text_get(self, node=None):
        """外层非标签属性的所有文本"""
        self.text = self.domRoot.text
        return self

    def HTML_get(self):
        """获取整个html"""
        script_str = "\n".join(list(map(lambda x: re.sub(r"\n", "", x.__str__()), self.script_el_dict.values())))
        root = re.sub(r"\n+$", "", self.domRoot.__str__())
        self.HTML_text = root + "\n<!--" + script_str + "-->"
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

    # @debugWatcher
    def script_el_remove(self):
        """临时删除script,减少干扰,不写入就行"""
        self.script_el_select(if_not_exist_then_new=False)
        if self.script_el_dict != {}:
            list(map(lambda x: x.extract(), self.script_el_dict.values()))
        return self

    def comment_el_select(self):
        """读到注释后, 会从dom树中取出"""
        parent_el, dataType = self.domRoot, self.consolerName
        self.comment_el = parent_el.find(text=lambda text: isinstance(text, element.Comment) and dataType in text)
        if self.comment_el is not None:
            self.comment_el.extract()
        return self

    # @debugWatcher
    def script_el_select(self, if_not_exist_then_new=True, scriptId=""):
        """读取script元素,保存到self.script_el_dict, new 表示如果找不到是否要新建一个
        20210212222602: 数据类型更新为注释中的HTML, 所以读取前要把它从注释中解放出来,对于旧版直接读取,并且会从DOM树中删除读取到的
        """
        # 如果注释不存在, 那么可能1是旧版锚点,2是新卡片没有打过锚点
        self.comment_el_select()
        parent_el = self.parse(self.comment_el, "html.parser") if self.comment_el is not None else self.domRoot
        # 默认取的是dataID, 以后会取其他ID,比如 selfID
        scriptId = scriptId if scriptId != "" else self.consolerName
        tempel = {}
        for el in parent_el.findAll(name="script", attrs={"id": re.compile(fr"{self.consolerName}\w+")}):
            self.script_el_dict[el.attrs["id"]] = el
        if self.script_el_dict == {} and if_not_exist_then_new:
            self.script_el_dict = {
                self.linkdata_scriptId: parent_el.new_tag(name="script", id=self.linkdata_scriptId),
                self.carddata_scriptId: parent_el.new_tag(name="script", id=self.carddata_scriptId)
            }
        elif self.script_el_dict != {}:
            if self.carddata_scriptId not in self.script_el_dict:
                self.script_el_dict[self.carddata_scriptId] = parent_el.new_tag(name="script",
                                                                                id=self.carddata_scriptId)
            for k, v in self.script_el_dict.items():
                v.extract()
        else:
            self.script_el_dict = {}
        return self

    # @debugWatcher
    def pairLi_pair_remove(self, **kwargs):
        """移除卡片数据对,操作card_linked_pairLi,接受两种参数:pair或pairLi"""
        self.HTMLdata_load()
        if self.script_el_dict == {}:
            return self
        elif "pair" in kwargs:
            waitDelete = kwargs["pair"]
            for pair in self.card_linked_pairLi:
                if pair.card_id == waitDelete.card_id:
                    self.card_linked_pairLi.remove(pair)
                    break
        elif "pairLi" in kwargs:
            for pair in kwargs["pairLi"]:
                self.pairLi_pair_remove(pair=pair)
        return self

    def pairLi_pair_append(self, **kwargs):
        """从pair中提取html格式的JSON,操作card_linked_pairLi,接受两种参数:pair或pairLi"""
        if "pair" in kwargs:
            self.script_el_select().HTMLdata_load().card_linked_pairLi.append(kwargs["pair"])
        elif "pairLi" in kwargs:
            self.script_el_select().HTMLdata_load().card_linked_pairLi += kwargs["pairLi"]
        return self

    # @debugWatcher
    def HTMLdata_save(self, scriptId=""):
        """小功能给他做成单个函数,保存到self.script_el.string,把JSON数据保存到字段中"""
        s_e_dict = self.script_el_dict
        data_dict = {self.linkdata_scriptId: list(map(lambda x: x.__dict__, self.card_linked_pairLi)),
                     self.carddata_scriptId: self.card_selfdata_dict
                     }
        self.script_el_select()  # 如果不存在应该换新
        scriptId = scriptId if scriptId != "" else self.linkdata_scriptId
        for k, v in s_e_dict.items():
            v.string = k + "=" + json.dumps(data_dict[k], ensure_ascii=False)
        console("self.script_el.string:" + self.script_el_dict.__str__()).log.end()
        return self


    def _anchor_container_el_select(self, new=True) -> element:
        """寻找锚点的容器,如果找不到,而且new为True时,就重做一个,否则保持空,返回容器元素"""
        anchor_container: element = self.domRoot.select(f"#{self.container_L0_Id}")
        if not anchor_container:
            if new:
                anchor_container = self.domRoot.new_tag(name="div")
                anchor_container.attrs["id"] = self.container_L0_Id
                self.domRoot.insert(1, anchor_container)
            else:
                return None
        else:
            anchor_container = anchor_container[0]
        return anchor_container

    def HTMLButton_selfdata_make(self, fielddata, **args):
        """制作按钮,anchor是总体锚点,container是容器,accordion是折叠主题"""

        self.card_linked_pairLi = fielddata.card_linked_pairLi  # 卡片链接的列表
        self.card_selfdata_dict = fielddata.card_selfdata_dict  # 卡片链接的结构
        self.cardinfo_dict = fielddata.cardinfo_dict  #

        if len(self.card_linked_pairLi) > 0:
            cfg = self.config
            anchor_header_L1 = self.domRoot.new_tag(name="div")
            anchor_header_L1.attrs["class"] = self.container_header_L1_class
            anchor_header_L1.string = self.consolerName

            container_body_L1 = self.domRoot.new_tag(name="div")
            container_body_L1.attrs["class"] = self.container_body_L1_class

            for info in self.card_selfdata_dict["menuli"]:
                if info["type"] == "cardinfo":
                    pair = self.cardinfo_dict[info["card_id"]]
                    button_L2 = \
                        self.domRoot.new_tag(name="button", card_id=pair.card_id, dir=pair.dir,
                                             onclick=f"""javascript:pycmd('{self.idPrefix}'+'{pair.card_id}');""",
                                             style=f"""margin:12px;displaystyle:inline;font-size:inherit;{cfg.linkStyle};""", )
                    button_L2.string = pair.dir + pair.desc
                elif info["type"] == "groupinfo":
                    pairli = [self.cardinfo_dict[id_] for id_ in
                              self.card_selfdata_dict["groupinfo"][info["groupname"]]]
                    button_L2 = self.HTMLAccordion_pairli_make(pairli, info["groupname"], container_body_L1)
                container_body_L1.append(button_L2)

            anchor_container_L0 = self._anchor_container_el_select()
            anchor_container_L0.append(anchor_header_L1)
            anchor_container_L0.append(container_body_L1)
            style = self.domRoot.new_tag(name="style")
            style.string = self.containerDivCSS.format(
                container_L0=self.container_L0_Id,
                container_body_L1=self.container_body_L1_class,
                container_header_L1=self.container_header_L1_class,
                accordion_L2=self.accordion_L2_class,
                accordion_checkbox_L3=self.accordion_checkbox_L3_Id,
                accordion_header_L3=self.accordion_header_L3_class,
                accordion_body_L3=self.accordion_body_L3_class
            )
            self.domRoot.insert(1, style)
        else:
            pass
            # showInfo("card_pairLi==0!")
        return self

    def HTMLAccordion_pairli_make(self, pairli: List[Pair], groupname, container_body_L1):
        """制造手风琴需要的pair"""

        cfg = self.config
        accordion_L2 = self.domRoot \
            .new_tag(name="div", attrs={
            "class": self.accordion_L2_class,
            "id": f"{self.baseInfo.consolerName}{groupname}"
        })
        console("container_body_L1的值為" + container_body_L1.__str__()).log.end()

        console("Accordion_L2的值為" + accordion_L2.__str__()).log.end()
        checkboxid = self.accordion_checkbox_L3_Id + groupname
        checkboxclass = self.accordion_checkbox_L3_Id
        accordion_header_L3 = self.domRoot.new_tag(name="label", attrs={"class": self.accordion_header_L3_class,
                                                                        "for": checkboxid})
        accordion_checkbox_L3 = self.domRoot.new_tag(name="input", attrs={"id": checkboxid,
                                                                          "class": checkboxclass,
                                                                          "type": "checkbox"})
        accordion_header_L3.string = groupname
        accordion_body_L3 = self.domRoot.new_tag(name="div", attrs={"class": self.accordion_body_L3_class})
        accordion_L2.append(accordion_header_L3)
        accordion_L2.append(accordion_checkbox_L3)
        accordion_L2.append(accordion_body_L3)
        for pair in pairli:
            button_L2 = \
                self.domRoot.new_tag(name="button", card_id=pair.card_id, dir=pair.dir,
                                     onclick=f"""javascript:pycmd('{self.idPrefix}'+'{pair.card_id}');""",
                                     style=f"""margin:12px;display:inline;font-size:inherit;{cfg.linkStyle};""", )
            button_L2.string = pair.dir + pair.desc
            accordion_body_L3.append(button_L2)
        return accordion_L2

    # @debugWatcher
    def HTMLdata_load(self):
        """从HTML中读取json,保存到 self.card_linked_pairLi 和 self.card_selfdata_dict"""
        self.script_el_select(if_not_exist_then_new=False)
        if self.script_el_dict != {}:
            linkdata = self.script_el_dict[self.linkdata_scriptId]  # 链接的数据
            selfdata = self.script_el_dict[self.carddata_scriptId]  # 自身的结构数据
            if linkdata.string:
                linkdata_str = re.sub(rf"{self.linkdata_scriptId}=", "", linkdata.string.__str__())
            else:
                linkdata_str = "[]"
            if selfdata.string:
                selfdata_str = re.sub(rf"{self.carddata_scriptId}=", "", selfdata.string.__str__())
            else:
                selfdata_str = "{}"
            console("report:script_str" + linkdata_str).log.end()
            self.card_linked_pairLi: List[Pair] = list(map(lambda x: Pair(**x), json.loads(linkdata_str)))
            self.card_selfdata_dict = json.loads(selfdata_str)
            for pair in self.card_linked_pairLi:
                self.cardinfo_dict[pair.card_id] = pair
            if "menuli" not in self.card_selfdata_dict:
                self.card_selfdata_dict["menuli"] = []
                self.card_selfdata_dict["groupinfo"] = {}
            if len(self.card_linked_pairLi) == 0:
                self.card_selfdata_dict["menuli"] = []
            self.exist_pairli = []
            menuli = self.card_selfdata_dict["menuli"]
            groupinfo = self.card_selfdata_dict["groupinfo"]
            cardinfo = self.cardinfo_dict
            needremove = []
            for info in menuli:
                if info["type"] == "cardinfo":
                    if info["card_id"] not in cardinfo:
                        needremove.append(info)
                        continue
                    else:
                        self.exist_pairli.append(info["card_id"])
                elif info["type"] == "groupinfo":
                    groupneedremove = []
                    for card_id in groupinfo[info["groupname"]]:
                        if card_id not in cardinfo:
                            groupneedremove.append(card_id)
                        else:
                            self.exist_pairli.append(card_id)
                    for card_id in groupneedremove:
                        groupinfo[info["groupname"]].remove(card_id)
            for info in needremove:
                menuli.remove(info)
            for k in cardinfo.keys():
                if k not in self.exist_pairli:
                    menuli.append(dict(card_id=k, type="cardinfo"))

        return self





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