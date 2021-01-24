from anki.lang import *
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
        "清除后选中卡片插入":"clearInputBeforeInsert",
        "将选中卡片插入":"insertSelected",
        "将选中卡片编组插入":"insertAsGroup",
        "调整config":"configuration",
        "查看版本":"version",
        "打开插件页面":"openWebSite",
        "连接":"link",
        "清空input":"clearInput",
        "打开input":"openInput",
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
    text = translateFuncs[lang](text)
    return text
