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




class Input(object, metaclass=MetaClass_loger):
    """集成input对象,满足增删查改需求
    当你保存dataobj到data的时候会自动类型转换
    """

    def __init__(self,
                 inputFileDir: str = os.path.join(THIS_FOLDER, inputFileName),
                 configFileDir: str = os.path.join(THIS_FOLDER, configFileName),
                 helpDir: str = helpSite,
                 relyDir: str = RELY_FOLDER,
                 initDict: dict = inputSchema,
                 model: AnkiQt = mw,
                 ):
        self.valueStack = []
        self.console = console(obj=self)
        self.dataflat_ = None
        self.model = model
        self.helpSite = helpDir
        self.initDict = initDict
        self.relyDir = relyDir
        self.inputDir = inputFileDir
        self.configDir = configFileDir
        self.config = json.load(open(configFileDir, "r", encoding="UTF-8", ))
        self.insertPosi = self.config["appendNoteFieldPosition"]
        self.regexDescPosi = self.config["readDescFieldPosition"]
        self.linkstyle = self.config["linkStyle"]
        self.seRegx = self.config["DEFAULT"]["regexForDescContent"] if self.config["regexForDescContent"] == 0 else \
            self.config["regexForDescContent"]
        self.HTMLmanage = HTML_converter()
        try:
            self.data: json = json.load(open(inputFileDir, "r", encoding="UTF-8", ))
            self.dataObj_ = self.dataObj.val
            self.tag = self.data["addTag"]
        except:
            self.tag = self.dataReset.dataSave.dataload.data["addTag"]

    @property
    def dataLoad(self):
        """数据读取, 修改self.data,tag,objdata"""
        self.data: json = json.load(open(self.inputDir, "r", encoding="utf-8"))
        self.tag = self.data["addTag"]
        self.dataObj_ = self.dataObj.val
        return self

    @property
    def dataObj(self):
        """将数据转换为对象,方便访问,修改 self.objdata """
        v = [[Pair(**pair) for pair in group] for group in self.data["IdDescPairs"]]
        self.dataObj_ = v
        return self

    @property
    def dataReset(self):
        """数据重设,修改 self.data """
        self.data = deepcopy(self.initDict)
        return self

    @property
    def dataSave(self):
        """数据保存,尝试json.dump,否则self.dataReset.dataSave"""
        try:
            json.dump(self.data, open(self.inputDir, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        except:
            return self.dataReset.dataSave
        return self

    @property
    def dataFlat(self):
        """去掉数据的组别,修改self.dataflat_"""
        self.dataflat_ = list(reduce(lambda x, y: x + y, self.dataObj_, []))
        return self

    @property
    def val(self):
        """取回上一次求解的内容"""
        return self.valueStack.pop()

    @property
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
        """从卡片列表中读取卡片ID和desc. 为了统一我们都处理成Pair,输出时再改回普通的."""
        descLi: List[str] = list(map(lambda x: self.desc_extract(x), cardLi))
        return list(map(lambda x, y: Pair(card_id=x, desc=y), cardLi, descLi))

    def desc_extract(self, c=None):
        """读取卡片的描述"""
        if isinstance(c, Pair): cid = c.int_card_id
        if isinstance(c, str): cid = int(c)
        cfg: dict = self.config
        note = self.model.col.getCard(cid).note()
        content = note.fields[self.regexDescPosi]
        desc = self.HTMLmanage.feed(content).node_remove().text_get().text
        desc = re.sub(r"\n+", "", desc)
        desc = desc[0:cfg['descMaxLength'] if len(desc) > cfg['descMaxLength'] != 0 else len(desc)]
        return desc

    def note_addTagAll(self):
        """给所有的note加上tag"""
        tag = self.tag
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        tagbase = self.config["addTagRoot"] + "::"
        tagtail = tag if tag != "" else timestamp
        pairLi = self.dataObj.dataFlat.dataUnique.val
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

    def note_insertPair(self, pairA: Pair, pairB: Pair, dirposi: str = "→", diffInsert=True):
        """往A note 加 pairB,默认不给自己加pair"""
        if diffInsert and pairA.card_id == pairB.card_id:
            return self
        note = self.note_loadFromId(pairA)
        if self.Id_noFoundInNote(pairB, pairA):
            Id, desc = pairB.card_id, pairB.desc if pairB.desc != "" else self.desc_extract()
            cfg = Empty()
            cfg.__dict__ = self.config
            dirMap = {"→": cfg.linkToSymbol, '←': cfg.linkFromSymbol}
            direction = dirMap[dirposi]
            fieldcontent = note.fields[self.insertPosi]
            fieldcontent = self.HTMLmanage.feed(fieldcontent).button_make(Id=Id,
                                                                          desc=desc,
                                                                          direction=direction,
                                                                          prefix=cfg.cidPrefix,
                                                                          linkStyle=cfg.linkStyle).HTML_get().HTML_text
            note.fields[self.insertPosi] = fieldcontent
            note.flush()
        return self

    def Id_noFoundInNote(self, pairA: Pair = None, pairB: Pair = None) -> bool:
        """判断A id是否在B Note中,如果不在,返回真"""
        console(
            f"""card_id={pairA.card_id},fieldcontent={self.note_loadFromId(pairB).fields[self.insertPosi]}""").log.end()
        return re.search(pairA.card_id, self.note_loadFromId(pairB).fields[self.insertPosi]) is None

    def IdLi_FromLinkedCard(self, pair: Pair = None):
        """读取那些被链接的笔记中的卡片ID"""
        pass

    def anchor_unbind(self, pairA: Pair, pairB: Pair):
        """两张卡片若有链接则会相互解除绑定,用于reduce函数"""
        console(f"""pairA={pairA.desc},pairB={pairB.desc}""").log.end()
        self.anchor_delete(pairA, pairB).anchor_delete(pairB, pairA)
        return pairB

    def anchor_updateVersion(self):
        """升级旧版锚点注入规则 TODO"""
        pass

    def anchor_delete(self, pairA: Pair, pairB: Pair):
        """A中删除B的id,返回自己"""
        note = self.note_loadFromId(pairA)
        field = note.fields[self.insertPosi]
        field = self.HTMLmanage.feed(field).node_remove(card_id=pairB.card_id).HTML_get().HTML_text
        note.fields[self.insertPosi] = field
        note.flush()
        return self

    def note_loadFromId(self, pair: Pair = None) -> Note:
        """从卡片的ID获取note"""
        console(self.__class__.__name__ + " argument: pair=" + pair.__str__()).log.end()
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
        console(f"""{self.__class__.__name__}.{name}={value}""").log.end()
        if name == "data":
            if (type(value) == list and len(value) > 0) \
                    and (type(value[0]) == list and len(value[0]) > 0) \
                    and isinstance(value[0][0], Pair):
                v = [list(map(lambda x: x.__dict__, group)) for group in value]
                self.__dict__[name]["IdDescPairs"] = v
            if type(value) == dict:
                self.__dict__[name] = value
            self.dataObj
            self.valueStack.append(value)
        else:
            if name == "tag": self.__dict__["data"]["addTag"] = value
            self.__dict__[name] = value
            if len(self.valueStack) > 100:
                del self.valueStack
                self.valueStack = []
            if name != "valueStack":
                self.valueStack.append(value)

    # def __getattribute__(self, name):
    #     console(f"遇到调用属性名:{self.__class__.__name__}.{name}")
