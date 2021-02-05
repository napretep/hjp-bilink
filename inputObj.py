"""
用来设计input对象,把一些常用属性绑定起来.
"""
import json
from copy import deepcopy
from functools import reduce

from anki.notes import Note
from aqt import mw
from aqt.main import AnkiQt

from .HTML_converter import HTML_converter
from .utils import *


class Input(BaseInfo,
            metaclass=MetaClass_loger
            ):
    """集成input对象,满足增删查改需求
    当你保存dataobj到data的时候会自动类型转换
    """

    # if ISDEBUG:
    #     __metaclass__ = MetaClass_loger

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = console(obj=self)
        self.dataflat_ = None
        self.insertPosi = self.config["appendNoteFieldPosition"]
        self.regexDescPosi = self.config["readDescFieldPosition"]
        self.linkstyle = self.config["linkStyle"]
        self.seRegx = self.config["DEFAULT_regexForDescContent"] if self.config["regexForDescContent"] == 0 else \
            self.config["regexForDescContent"]
        self.HTMLmanage = HTML_converter()
        try:
            self.data: dict = json.load(open(self.inputDir, "r", encoding="UTF-8", ))
            self.tag = self.data["addTag"]
        except:
            raise ValueError("读取input出现错误,请检查格式是否正确,或请点击'清空input'重置input文件")

    def dataLoad(self):
        """数据读取, 修改self.data,tag,objdata"""
        self.data: json = json.load(open(self.inputDir, "r", encoding="utf-8"))
        self.tag = self.data["addTag"]
        self.dataObj_ = self.dataObj().val()
        return self

    def dataObj(self):
        """将数据转换为对象,方便访问,修改 self.objdata """
        v = [[Pair(**pair) for pair in group] for group in self.data["IdDescPairs"]]
        self.dataObj_ = v
        return self

    def dataReset(self):
        """数据重设,修改 self.data """
        self.data = deepcopy(self.initDict)
        return self

    def dataSave(self):
        """数据保存,尝试json.dump,否则self.dataReset.dataSave"""
        try:
            json.dump(self.data, open(self.inputDir, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        except:
            return self.dataReset().dataSave()
        return self

    def dataFlat(self):
        """去掉数据的组别,传入self.dataObj_ 传出self.dataflat_"""
        self.dataflat_ = list(reduce(lambda x, y: x + y, self.dataObj_, []))
        return self

    def val(self):
        """取回上一次求解的内容"""
        return self.valueStack.pop()

    def dataUnique(self):
        """列表去重,默认对栈中上一个元素读取进行操作"""
        o, t = self.valueStack[-1], []
        if type(o) == list:
            [t.append(i) for i in o if i not in t]
            self.valueStack[-1] = t
        return self

    def config_open(self):
        """打开配置文件"""
        configUrl = QUrl.fromLocalFile(self.configDir)
        QDesktopServices.openUrl(configUrl)
        return self

    def helpSite_open(self):
        """打开帮助页面"""
        helpUrl = QUrl(self.helpSite)
        QDesktopServices.openUrl(helpUrl)

    def pairLi_extract(self, cardLi: List[str] = None) -> List[Pair]:
        """从卡片列表中读取卡片ID和desc. 为了统一我们都处理成listPair输出
        """
        descLi: List[str] = list(map(lambda x: self.desc_extract(x), cardLi))
        return list(map(lambda x, y: Pair(card_id=x, desc=y), cardLi, descLi))

    def desc_extract(self, c=None):
        """读取卡片的描述"""
        if isinstance(c, Pair):
            cid = c.int_card_id
        elif isinstance(c, str):
            cid = int(c)
        else:
            raise TypeError("参数类型不支持:" + c.__str__())
        cfg: dict = self.config
        note = self.model.col.getCard(cid).note()
        content = note.fields[self.regexDescPosi]
        desc = self.HTMLmanage.clear().feed(content).script_el_remove().text_get().text
        desc = re.sub(r"\n+", "", desc)
        desc = desc[0:cfg['descMaxLength'] if len(desc) > cfg['descMaxLength'] != 0 else len(desc)]
        return desc

    def card_remove(self, pair: Pair = None):

        [list(map(lambda x: group.remove(x) if x.card_id == pair.card_id else None, group)) for group in self.dataObj_]
        if [] in self.dataObj_: self.dataObj_.remove([])
        if len(self.dataObj_) > 0:
            self.data = self.dataObj_
        else:
            self.data["IdDescPairs"] = self.initDict["IdDescPairs"]
        return self

    def note_addTagAll(self):
        """给所有的note加上tag"""
        tag = self.tag
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        tagbase = self.config["addTagRoot"] + "::"
        tagtail = tag if tag != "" else timestamp
        pairLi = self.dataObj().dataFlat().dataUnique().val()
        tag = tagbase + tagtail
        self.tag = tag
        list(map(lambda pair: self.note_addTag(tag=tag, pair=pair), pairLi))
        return self

    def note_addTag(self, tag: str = "", pair: Pair = None):
        """一个加tag的子函数"""
        note = self.note_loadFromId(pair)
        note.addTag(tag)
        note.flush()
        return self

    @debugWatcher
    def note_insertPair(self, pairA: Pair, pairB: Pair, dirposi: str = "→", diffInsert=True):
        """往A note 加 pairB,默认不给自己加pair"""
        if diffInsert and pairA.card_id == pairB.card_id:
            return self
        note = self.note_loadFromId(pairA)
        self.HTMLmanage.clear().feed(note.fields[self.insertPosi])
        self.HTMLmanage.pairLi_loadFromHTML()
        if self.Id_noFoundInNote(pairB):
            pairB.desc = pairB.desc if pairB.desc != "" else self.desc_extract(pairB)
            cfg = Empty()
            cfg.__dict__ = self.config
            dirMap = {"→": cfg.linkToSymbol, '←': cfg.linkFromSymbol}
            pairB.dir = dirMap[dirposi]
            # fieldcontent = self.HTMLmanage.pairLi_appendPair(pair=pairB).HTML_savePairLi().HTML_get().HTML_text
            self.HTMLmanage.pairLi_appendPair(pair=pairB)
            self.HTMLmanage.HTML_savePairLi()
            self.HTMLmanage.HTML_get()
            fieldcontent = self.HTMLmanage.HTML_text
            console("最终要写入字段的内容:" + fieldcontent).log.end()
            note.fields[self.insertPosi] = fieldcontent
            note.flush()
        return self

    def Id_noFoundInNote(self, pairA: Pair = None) -> bool:
        """判断A id是否在B Note中,如果不在,返回真, 注意处理好pairLi的初始化"""
        for pairB in self.HTMLmanage.card_linked_pairLi:
            console(pairA.__dict__.__str__() + pairB.__dict__.__str__()).log.end()
            if pairA.card_id == pairB.card_id:
                return False
        return True

    def IdLi_FromLinkedCard(self, pair: Pair = None):
        """读取那些被链接的笔记中的卡片ID"""
        pass

    def anchor_unbind(self, pairA: Pair, pairB: Pair):
        """两张卡片若有链接则会相互解除绑定,用于reduce函数"""
        self.anchor_delete(pairA, pairB).anchor_delete(pairB, pairA)
        return pairB

    @debugWatcher
    @wrapper_browser_refresh
    def anchor_updateVersion(self):
        """升级旧版锚点注入规则 """
        for pair in self.dataflat_:
            note = self.note_loadFromId(pair)
            cardLi = []
            for i in range(len(note.fields)):  # 这一步是为了提取所有的卡片id
                # cardLi += self.HTMLmanage.clear().feed(note.fields[i]).pairLi_fromOldVer()
                self.HTMLmanage.clear().feed(note.fields[i])
                cardLi += self.HTMLmanage.pairLi_fromOldVer()
                note.fields[i] = self.HTMLmanage.HTML_get().HTML_text
                console("输入fields的HTML_text为" + self.HTMLmanage.HTML_get().HTML_text).log.end()
                note.flush()
            self.HTMLmanage.clear().feed(note.fields[self.insertPosi])
            self.HTMLmanage.card_linked_pairLi = cardLi
            self.HTMLmanage.HTML_savePairLi()
            console("看看root:" + self.HTMLmanage.domRoot.__str__()).log.end()
            note.fields[self.insertPosi] = self.HTMLmanage.domRoot.__str__()
            note.flush()  # 把卡片对保存成字段中的JSON数据
            for pairB in cardLi:
                self.note_insertPair(pair, pairB)
        console("升级完成,请检查,如失败请联系作者").talk.end()
        return self

    def anchor_delete(self, pairA: Pair, pairB: Pair):
        """A中删除B的id,返回自己"""
        note = self.note_loadFromId(pairA)
        self.HTMLmanage.clear().feed(note.fields[self.insertPosi]).pairLi_removePair(pair=pairB).HTML_savePairLi()
        note.fields[self.insertPosi] = self.HTMLmanage.HTML_get().HTML_text
        note.flush()
        return self

    def note_loadFromId(self, pair: Pair = None) -> Note:
        """从卡片的ID获取note"""
        li = pair.int_card_id
        return self.model.col.getCard(li).note()

    def group_bijectReducer(self, groupA: List[Pair] = None, groupB: List[Pair] = None):
        """A组的每个pair链接到B组的每个pair,还有一个反向回链,是个reduce使用的函数 """
        for pairA in groupA:
            for pairB in groupB:
                self.note_insertPair(pairA, pairB)
                self.note_insertPair(pairB, pairA, dirposi="←")
        return groupB

    def end(self):
        return self

    def __setattr__(self, name, value):
        """修改类型检查, 尽量不给这里添乱."""
        console(f"""{self.__class__.__name__}.{name}={value}""").log.end()

        def handle_list(name, value):
            """处理list"""

            def handle_list_list(name, value):
                """listlist"""
                handleAssignlistlist = {
                    Pair: handle_list_list_pair,
                    dict: handle_list_list_dict
                }
                if len(value[0]) > 0:
                    if type(value[0][0]) in (dict, Pair):
                        handleAssignlistlist[type(value[0][0])](name, value)
                    else:
                        raise TypeError("无法处理数据:" + value.__str__())
                else:
                    self.__dict__[name]["IdDescPairs"] = []

            def handle_list_list_dict(name, value):
                """listlistdict"""
                self.__dict__[name]["IdDescPairs"] = value

            def handle_list_list_pair(name, value):
                """listlistpair"""
                v = [list(map(lambda x: x.__dict__, group)) for group in value]
                self.__dict__[name]["IdDescPairs"] = v

            def handle_list_pair(name, value):
                """listpair"""
                self.__dict__[name]["IdDescPairs"] = list(map(lambda x: [x.__dict__], value))

            def handle_list_dict(name, value):
                """前面已经处理掉了空值的情况.listdict"""
                if "card_id" in value[0] and "desc" in value[0]:
                    self.__dict__[name]["IdDescPairs"] = list(map(lambda x: [x], value))
                else:
                    raise TypeError("无法处理数据:" + value.__str__())

            handleAssignlist = {
                list: handle_list_list,
                Pair: handle_list_pair,
                dict: handle_list_dict
            }

            if len(value) > 0:
                if type(value[0]) in (dict, Pair, list):
                    handleAssignlist[type(value[0])](name, value)
                else:
                    raise TypeError("无法处理数据:" + value.__str__())
            else:
                self.__dict__[name]["IdDescPairs"] = []

        def handle_dict(name, value):
            """dict"""
            if "IdDescPairs" in value and "addTag" in value:
                self.__dict__[name] = value
            else:
                raise TypeError("无法处理数据:" + value.__str__())

        if name == "data":
            handleAssign = {  # 兼容了五种类型: list[list[pair]],list[list[dict]],list[pair],list[dict],dict
                list: handle_list,
                dict: handle_dict
            }
            if type(value) in (list, dict):
                handleAssign[type(value)](name, value)
            else:
                raise TypeError("无法处理数据:" + value.__str__())
            self.dataObj().dataFlat().end()
        else:
            if name == "tag": self.__dict__["data"]["addTag"] = value
            self.__dict__[name] = value
            if len(self.valueStack) > 100:
                self.valueStack = []
            if name != "valueStack":
                self.valueStack.append(value)
