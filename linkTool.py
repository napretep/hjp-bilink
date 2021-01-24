
class delog(object):
    """做到区分通知用户的一般消息和debug消息"""
    def __init__(self,t:str,logdir=os.path.join(THIS_FOLDER, logFileName),func=tooltip,dbg=False):#for debug
        self.message=t
        self.logDir=logdir
        self.needLog=True
        self.needDebug=True
        self.isDebuger=dbg
        self.func=func
        if not self.isDebuger:
            self.func(self.message)
        if self.isDebuger and self.needDebug:
            self.func(self.message)
            if self.needLog:
                self.toLogtxt()

    def toLogtxt(self):
        flog=open(self.logDir,"a",encoding="utf8")
        flog.write(datetime.datetime.now().strftime("%Y/%m/%d-%H:%M:%S")+f" {consolerName}:"+self.message+"\n")
        flog.flush()
        flog.close()

class __(object):
    """有必要时翻译成英语 zh-CN,zh_TW,en,en-GB """
def rosetta(text:str=""):
    # return text
    lang=currentLang

    surrport=["zh-CN","zh_TW","en","en-GB"]
    def En(text):
        return Endict[text]

    def Zh(text):
        return text
    if not (lang in surrport):
        lang="en"
    Endict ={
        "默认连接":"default",
        "完全图连接":"completeMap",
        "组到组连接":"groupBygroup",
        "按结点取消连接":"unlinkByNode",
        "按路径取消连接":"unlinkByPath",
        "由于这里无法读取card_id, 连接菜单不在这显示":"Since card_id cannot be read here, the  menu is not displayed here",
        "先清除再将选中卡片插入":"clearInputBeforeInsert",
        "将选中的卡片插入":"insertSelected",
        "将选中的卡片编组插入":"insertAsGroup",
        "调整config":"configuration",
        "查看版本":"version",
        "打开插件页面":"openWebSite",
        "连接":"link",
        "清空":"clear",
        "打开":"open",
        "插入":"Insert",
        "选中文字更新标签":"updateTagBySelectedString",
        "先清除再插入":"clearInputBefore",
        "直接":"directly",
        "标签":"tag",
        "已经更新到":"updatedTo",
        "已经被插入到":"insertedTo",
        "上一个组":"LastGroup",
        "张卡被加入到":"cardsInsertedTo",
        "没有选中任何卡片!":"selectedNothing!",
        "正则读取描述字符失败!":"loadDescByRegexFailed",
        '初始化完毕':"initialized",
        "操作完成":"operationFinished",
        "链接失败,组连接至少需要两个组!":"linkFailed,groupBygroup Link need at least 2 groups",
        "input中没有数据！":"no data in input",
        '全部展开/折叠':"Expand/Collapse All",
        '选中删除':"deleteSelected",
        "选中连接":"linkSelected"
    }
    translateFuncs = {
        "en":En,
        "en-GB": En,
        "zh-CN":Zh,
        "zh-TW":Zh,
    }
    delog(f"lang={lang}", dbg=True)
    text = translateFuncs[lang](text)
    return text

# def algdesc():
#     return list(map(lambda x:译(x),["默认连接","完全图连接","组到组连接","按结点取消连接","按路径取消连接"]))


hjp_bilink_VERSION=re.search("(?<=- # hjp-bilink V\")[\w\.]+(?=\")",open(os.path.join(THIS_FOLDER,helpFileName),"r", encoding="utf-8").read())[0]

# delog("linkTool.py运行完",dbg=True)
# delog(_translate("标签"))