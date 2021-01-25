"""
用来设计input对象,把一些常用属性绑定起来.
"""
import json
from copy import deepcopy

from aqt import mw
from aqt.main import AnkiQt

from .language import rosetta as say
from .utils import *


class Pair:
    """卡片ID和卡片描述的键值对的对象"""

    def __init__(self, card_id="", desc=""):
        self.card_id = card_id
        self.desc = desc

class Params:
    """集成装载"""

class Input:
    """集成input对象,满足增删查改需求"""

    def __init__(self,
                 inputFileDir: str = os.path.join(THIS_FOLDER, inputFileName),
                 configFileDir: str = os.path.join(THIS_FOLDER, configFileName),
                 helpDir: str = helpSite,
                 relyDir: str = RELY_FOLDER,
                 initDict: dict = inputSchema,
                 model: AnkiQt = mw
                 ):
        self.model = model
        self.helpSite = helpDir
        self.data: json = json.load(open(inputFileDir, "r", encoding="UTF-8", ))
        config = json.load(open(configFileDir, "r", encoding="UTF-8", ))
        self.config = config
        self.relyDir = relyDir
        self.inputDir = inputFileDir
        self.configDir = configFileDir
        self.initDict = initDict

    @property
    def dataLoad(self):
        """数据读取"""
        self.data: json = json.load(open(self.inputDir, "r", encoding="utf-8"))
        return self

    @property
    def dataReset(self):
        """数据重设"""
        self.data = deepcopy(self.initDict)
        return self

    @property
    def dataSave(self):
        """数据保存"""
        json.dump(self.data, open(self.inputDir, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        return self

    def configOpen(self):
        """打开配置文件"""
        configUrl = QUrl.fromLocalFile(self.configDir)
        QDesktopServices.openUrl(configUrl)
        return self

    def helpSiteOpen(self):
        """打开帮助页面"""
        helpUrl = QUrl(self.helpSite)
        QDesktopServices.openUrl(helpUrl)

    def idDescPairExtract(self, cardLi: List[str] = None) -> List[dict]:
        """从卡片列表中读取卡片ID和desc."""
        descLi: List[str] = list(map(lambda x: self.cardDescExtract(x), cardLi))
        return list(map(lambda x, y: Pair(x, y).__dict__, cardLi, descLi))

    def cardDescExtract(self, c: str = ""):
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
            console(say("正则读取描述字符失败!"), func=showInfo)
            return
        desc = desc[0:cfg['descMaxLength'] if len(desc) > cfg['descMaxLength'] != 0 else len(desc)]
        return desc
