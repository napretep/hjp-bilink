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
        "默认连接": "default",
        "完全图连接": "complete map",
        "组到组连接": "group by group",
        "按结点取消连接": "unlink by node",
        "按路径取消连接": "unlink by path",
        "由于这里无法读取card_id, 连接菜单不在这显示": "Since card_id cannot be read here, the  menu is not displayed here",
        "清除后选中卡片插入": "clear input Before insert selected",
        "将选中卡片插入": "insert selected",
        "将选中卡片编组插入": "insert as group",
        "调整config": "configuration",
        "查看版本": "version",
        "打开插件页面": "open webSite",
        "连接": "link",
        "清空input": "clear input",
        "打开input": "open input",
        "插入": "Insert",
        "先清除再插入": "clear input before insert",
        "直接插入": "directly insert",
        "插入上一个组": "insert to last group",
        "选中文字更新标签": "update tag by selected string",
        "标签": "tag",
        "已经更新到": "updated to",
        "已经被插入到": "inserted to",
        "张卡被加入到": "cardsInserted to",
        "没有选中任何卡片!": "selected nothing!",
        "正则读取描述字符失败!": "load Desc by Regex failed",
        '初始化完毕': "initialized",
        "操作完成": "operation finished",
        "链接失败,组连接至少需要两个组!": "linkFailed,group by group Link need at least 2 groups",
        "input中没有数据！": "no data in input, abort",
        '全部展开/折叠': "Expand/Collapse All",
        '选中删除': "deleteSelected",
        "选中连接": "linkSelected"
    }
    translateFuncs = {
        "en":En,
        "en-GB": En,
        "zh-CN":Zh,
        "zh-TW":Zh,
    }
    text = translateFuncs[lang](text)
    return text
