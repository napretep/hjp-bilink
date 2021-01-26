"""
用来设计input对象,把一些常用属性绑定起来.
"""
import json
from copy import deepcopy
from functools import reduce

from anki.notes import Note
from aqt import mw
from aqt.main import AnkiQt

from .language import rosetta as say
from .utils import *


class Empty:
    """空对象"""


class Params:
    """参数对象"""

    def __init__(self,
                 card_id: str = None,
                 desc: str = None,
                 need: tuple = None,
                 parent=None,
                 menu=None,
                 inputObj=None
                 ):
        self.card_id = card_id
        self.desc = desc
        self.need = need
        self.parent = parent
        self.menu = menu
        self.input = inputObj


class Pair:
    """卡片ID和卡片描述的键值对的对象"""

    def __init__(self, **pair):
        self.card_id = pair["card_id"]
        self.desc = pair["desc"]


class Input(object):
    """集成input对象,满足增删查改需求"""

    def __init__(self,
                 inputFileDir: str = os.path.join(THIS_FOLDER, inputFileName),
                 configFileDir: str = os.path.join(THIS_FOLDER, configFileName),
                 helpDir: str = helpSite,
                 relyDir: str = RELY_FOLDER,
                 initDict: dict = inputSchema,
                 model: AnkiQt = mw
                 ):
        self.console = console(obj=self)
        self.model = model
        self.helpSite = helpDir
        self.initDict = initDict
        self.relyDir = relyDir
        self.inputDir = inputFileDir
        self.configDir = configFileDir
        self.config = json.load(open(configFileDir, "r", encoding="UTF-8", ))
        self.insertPosi = self.config["appendNoteFieldPosition"]
        self.linkstyle = self.config["linkStyle"]
        self.seRegx = self.config["DEFAULT"]["regexForDescContent"] if self.config["regexForDescContent"] == 0 else \
            self.config["regexForDescContent"]
        try:
            self.data: json = json.load(open(inputFileDir, "r", encoding="UTF-8", ))
            self.tag = self.data["addTag"]
        except:
            self.tag = self.dataReset.dataSave.data["addTag"]

    @property
    def dataLoad(self):
        """数据读取"""
        self.data: json = json.load(open(self.inputDir, "r", encoding="utf-8"))
        return self

    @property
    def dataObj(self):
        """将数据转换为对象,方便访问"""
        return [[Pair(**pair) for pair in group] for group in self.data["IdDescPairs"]]

    @property
    def dataReset(self):
        """数据重设"""
        self.data = deepcopy(self.initDict)
        return self

    @property
    def dataSave(self):
        """数据保存"""
        try:
            json.dump(self.data, open(self.inputDir, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        except:
            return self.dataReset.dataSave
        return self

    @property
    def dataflat(self):
        """将东西扁平化"""
        return list(reduce(lambda x, y: x + y, self.dataObj, []))

    def configOpen(self):
        """打开配置文件"""
        configUrl = QUrl.fromLocalFile(self.configDir)
        QDesktopServices.openUrl(configUrl)
        return self

    def helpSiteOpen(self):
        """打开帮助页面"""
        helpUrl = QUrl(self.helpSite)
        QDesktopServices.openUrl(helpUrl)

    def pairExtract(self, cardLi: List[str] = None) -> List[Pair]:
        """从卡片列表中读取卡片ID和desc. 为了统一我们都处理成Pair,输出时再改回普通的."""
        descLi: List[str] = list(map(lambda x: self.descExtract(x), cardLi))
        return list(map(lambda x, y: Pair(card_id=x, desc=y), cardLi, descLi))

    def descExtract(self, c: str = ""):
        """读取卡片的描述"""
        cid = int(c)
        cfg: dict = self.config
        note = self.model.col.getCard(cid).note()
        content = note.fields[cfg["readDescFieldPosition"]]
        seRegx = cfg["DEFAULT"]["regexForDescContent"] if cfg["regexForDescContent"] == 0 \
            else cfg["regexForDescContent"]
        try:
            desc = re.search(seRegx, content)[0]
        except:
            console(say("正则读取描述字符失败!")).showInfo.talk()
            return
        desc = desc[0:cfg['descMaxLength'] if len(desc) > cfg['descMaxLength'] != 0 else len(desc)]
        return desc

    def noteAddTagAll(self):
        """给所有的note加上tag"""
        tag = self.tag
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        tagbase = self.config["addTagRoot"] + "::"
        tagtail = tag if tag is not None else timestamp
        groupLi = self.dataObj
        tag = tagbase + tagtail
        for group in groupLi:
            list(map(lambda x: self.noteAddTag(tag, x.card_id), group))
        return self

    def noteAddTag(self, tag: str = "", pair: Pair = None):
        """一个加tag的子函数"""
        note = self.noteLoadFromId(pair)
        note.addTag(tag)
        note.flush()
        return self

    def noteInsertedByPair(self, pairA: Pair, pairB: Pair, dirposi: str = "→", diffInsert=True):
        """往pairA的note里加pairB,默认不给自己加pair"""
        self.console.log()
        if diffInsert and pairA.card_id == pairB.card_id:
            self.console._("""if diffInsert and pairA.card_id == pairB.card_id:return self""").log()
            return self
        note = self.noteLoadFromId(pairA)
        self.console._("""note = self.noteLoadFromId(pairA)""").log()
        if re.search(pairB.card_id, note.fields[self.insertPosi]) is None:
            cfg = Empty()
            cfg.__dict__ = self.config
            dirMap = {"→": cfg.linkToSymbol, '←': cfg.linkFromSymbol}
            direction = dirMap[dirposi]
            Id = pairB.card_id
            try:
                desc = pairB.desc if len(pairB.desc) > 0 else re.search(self.seRegx, note[self.insertPosi])[0]
            except:
                self.console._(say("正则读取描述字符失败!")).showInfo.talk()
                return self
            note.fields[
                self.insertPosi] += f"""<button card_id='{Id}' dir = '{dirposi}'""" \
                                    + f""" style='font-size:inherit;{cfg.linkStyle}'>""" \
                                    + f"""{direction}{desc} {cfg.cidPrefix}{Id}</button>"""
            note.flush()

        return self

    def IdLiFromLinkedCard(self, pair: Pair = None):
        """读取那些被连接的笔记中的卡片ID"""
        pass

    def AnchorDelete(self, pairA: Pair, pairB: Pair):
        """A中删除B的id"""
        pass

    def noteLoadFromId(self, pair: Pair = None) -> Note:
        """从卡片的ID获取note"""
        console("").log()
        li = int(pair.card_id)
        return self.model.col.getCard(li).note()

    def __setattr__(self, name, value):
        if name == "data" \
                and (type(value) == list and len(value) > 0) \
                and (type(value[0]) == list and len(value[0]) > 0) \
                and isinstance(value[0][0], Pair):
            v = [list(map(lambda x: x.__dict__, group)) for group in value]
            self.__dict__[name]["IdDescPairs"] = v
        else:
            self.__dict__[name] = value
