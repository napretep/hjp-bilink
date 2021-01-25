"""
用来设计input对象,把一些常用属性绑定起来.
"""
import json

from .utils import *


class Input:
    """集成input对象,满足增删查改需求"""

    def __init__(self,
                 inputFileDir: str = os.path.join(THIS_FOLDER, inputFileName),
                 configFileDir: str = os.path.join(THIS_FOLDER, configFileName),
                 helpDir: str = helpSite,
                 relyDir: str = RELY_FOLDER,
                 initDict: dict = inputSchema,
                 ):
        self.helpSite = helpDir
        self.data: json = json.load(open(inputFileDir, "r", encoding="UTF-8"))
        self.config: json = json.load(open(configFileDir, "r", encoding="UTF-8", ))
        self.relyDir = relyDir
        self.inputDir = inputFileDir
        self.configDir = configFileDir
        self.initDict = initDict

    @property
    def dataReset(self):
        """数据重设"""
        self.data = self.initDict
        return self

    @property
    def dataSave(self):
        """数据保存"""
        json.dump(self.data, open(self.inputDir, "w", encoding="UTF-8"))
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
