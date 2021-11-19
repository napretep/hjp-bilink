from anki.lang import *


def rosetta(text: str = ""):
    """# return text"""
    lang = currentLang

    surrport = ["zh-CN", "zh_TW", "en", "en-GB"]

    def En(text):
        if text in Endict:
            return Endict[text]
        else:
            return text

    def Zh(text):
        if text in ZHdict:
            return ZHdict[text]
        return text

    if not (lang in surrport):
        lang = "en"
    Endict = {
        "未知错误": "unknown error",
        "错误信息": "Error info",
        "链接列表渲染失败": "failed in render link list",
        "默认链接": "default",
        "完全图链接": "complete map",
        "组到组链接": "group to group",
        "按结点取消链接": "unlink by node",
        "按路径取消链接": "unlink by path",
        "由于这里无法读取card_id, 链接菜单不在这显示": "Since card_id cannot be read here, the  menu is not displayed here",
        "清除后选中卡片插入": "clear input Before insert selected",
        "将选中卡片插入": "insert selected",
        "将选中卡片编组插入": "insert as group",
        "调整config": "configuration",
        "查看版本和新特性": "version and what's new",
        "打开插件页面": "open code repository",
        "链接": "link",
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
        "链接失败,组链接至少需要两个组!": "linkFailed,group by group Link need at least 2 groups",
        "input中没有数据！": "no data in input, abort",
        '全部展开/折叠': "Expand/Collapse All",
        '选中删除': "deleteSelected",
        "选中链接": "linkSelected",
        "升级旧版(小于等于0.6的版本)锚点": "old version(<=0.6) linked anchors update",
        "错误:字段中的HTML无法读取": "error:can't read HTML in card.field",
        "联系作者": "contact author",
        "支持作者": "support author",
        "其他": "other",
        "未选择卡片": "please select card",
        "张卡片重复插入, 已去重": " cards already inserted before, skip",
        "卡片已经存在,跳过": "the card already inserted before, skip",
        "所选卡片早已插入,跳过任务": "these cards already inserted before, skip",
        "张卡片已插入": "cards has been inserted",
        "刚插入的标签为:": "inserted tag:",
        "成功插入{卡片-描述}对:": "successfully insert the pair of card_id and desc",
        "已按路径取消链接": "unlinked given path",
        "已按结点取消链接": "unlinked given node",
        "已按组到组完成链接": "linked, method: group to group",
        "已按完全图完成链接": "linked, method: complete map",
        "已删除选中卡片": "selected card deleted",
        "input 已清空": "input cleared",
        "重置config": "config reset",
        "打开anchor": "open anchor",
        "多选模式": "in multi-select mode",
        "普通模式": "in default mode",
        "同名组已合并": "the group with the same name has been merged",
        "空组已移除": "the empty group has been removed",
        "新建组": "create new group",
        "抱歉,组名中暂时不能用空格与标点符号,否则会报错": "the name of group cannot contain non-word character",
        "已更新": "updated",
        "选中插入": "selected insert to input",
        "anchor数据为空": "the anchor data is empty",
        "请多多转发支持!": "Please let more people know hjp-bilink! ",
        "开启": "enabled",
        "关闭": "disabled",
        "sqlite数据库存储": "sqlite3 DB",
        "卡片字段存储": "card field",
        "JSON文件存储": "JSON File",
        "清空后插入": "clean and insert",
        "编组插入": "insert as a group",
        "选择文件": "choose a file",
        "数据覆盖": "overwrite data",
        "数据合并": "merge data",
        "已删除反链": "back reference deleted",
        "已复制到剪贴板": "links copied to clipboard",
        "已建立反链": "back reference created",
        "复制为文内链接": "copy as in-text link",
        "链接数据迁移对话框": "migrate storage location",
        "链接数据迁移": "migrate the data storage location",
        "执行": "execute",
        "从": "from",
        "转移到": "migrate to",
        "写入模式": "write mode",
        "转移卡片到卡组": "change deck",
        "移除标签": "remove tag",
        "添加标签": "add tag",
        "请先到配置表中设置根卡组": "set root deck in config table first",
        "请先到配置表中设置根标签": "set root tag in config table first",
        "根卡组不存在": "root deck don't exist",
        "根标签不存在": "root tag don't exist",
        "打开链接信息保存目录": "open storage directory",
        "注意1:当数据从A转移到B，会删除A中的数据记录": "hint1:migrate data from A to B, the data in A will be deleted",
        "注意2:先把想要转移的卡片插入到input": "hint2:put the card you want into the Input before execute",
        "打开配置表":"open configuration file",
        "文内链接":"in-text link",
        "html链接":"html link",
        "markdown链接":"markdown link",
        "orgmode链接":"orgmode link",
        "复制为":"copy card as",
        "复制当前搜索栏为":"copy current search result as",
        "文外链接操作":"out-text link operation",
        "打开链接池":"open link pool",
        "清空链接池":"clear link pool",
        "完全图绑定":"complete map binding",
        "组到组绑定":"group by group binding",
        "按结点解绑":"unbind by node",
        "按路径解绑":"unbind by path",
        "选中直接操作":"operations of selected cards",
        "卡片插入池":"insert card to the link pool",
        "池中卡片操作":"operations in the link pool",
        "改变牌组":"change the deck of the card",
        "操作标签":"modify the tags of the card",
        "发现未注册自定义url协议,现已自动注册,若出现反复注册,请以管理员身份运行anki":
            "detect the url scheme of Anki is not registered, now has been automatically registered\n"
            "if this information repeated occurs, please run anki in administrator",
        "打开clipper":"open clipper",
        "在clipper中打开卡片":"open card in clipper",
        "在grapher中打开卡片":"open card in grapher",
        "添加同步复习标签":"add sync review tag",
        "保存当前搜索条件为自动复习条件":"restore current search for auto review",
        "保存成功":"successfully restored",
        "自动复习操作":"auto review operation",
        "重建数据库":"rebuild auto review database",
        "配置表操作":"operations for config file",
        "重置配置表":"reset config file",
        "创建为视图":"create view",
        "视图名":"name of view",
        "视图名不能为空":"name of view cannot be empty",
        "视图名必须是JSON合法的字符串":"must be a valid JSON string",
        "打开于视图:":"open in view of:",
        "直接打开":"just open",
        "删除边":"delete edge",
        "隐藏边":"hide edge"
    }
    ZHdict = {
        "defaultLinkMode": "默认链接方式(用于快捷键)",
        "defaultUnlinkMode": "默认取消链接方式(用于快捷键)",
        "defaultInsertMode": "默认插入input方式(用于快捷键)",
        "addTagEnable": "开启链接自动加标签的功能",
        "appendNoteFieldPosition": "数据存于卡片字段的位置（对应模式开启有效）",
        "readDescFieldPosition": "描述读取于卡片字段的位置",
        "linkInfoStorageLocation": "链接数据保存的模式",
        "descMaxLength": "自动读取描述的最大长度",
        "addTagRoot": "自动加的标签其根部名称",
        "button_appendTo_AnchorId": "添加按钮锚点的HTML元素 ID（不懂可不管）",
        "shortcut_inputDialog_open": "打开input的快捷键(全局)",
        "shortcut_browserTableSelected_link": "链接快捷键(browser下)",
        "shortcut_browserTableSelected_unlink": "取消链接快捷键(browser下)",
        "shortcut_browserTableSelected_insert": "插入input快捷键(browser下)",
        "shortcut_inputFile_clear": "input清空快捷键(全局)",
        "anchorCSSFileName": "按钮锚点的CSS样式文件（不懂可不管）",
        "shortcut_copylink": "文内链接快捷键（browser下）"
    }
    translateFuncs = {
        "en": En,
        "en-GB": En,
        "zh-CN": Zh,
        "zh-TW": Zh,
    }

    return translateFuncs[lang](text)


# noinspection NonAsciiCharacters
class Translate:
    lang = currentLang
    surrport = ["zh-CN", "zh_TW", "en", "en-GB"]
    打开配置表:str = rosetta("打开配置表")
    打开anchor:str  = rosetta("打开anchor")
    文内链接:str = rosetta("文内链接")
    html链接:str = rosetta("html链接")
    markdown链接:str = rosetta("markdown链接")
    orgmode链接:str = rosetta("orgmode链接")
    复制为:str=rosetta("复制为")
    复制当前搜索栏为:str = rosetta("复制当前搜索栏为")
    文外链接操作:str=rosetta("文外链接操作")
    打开链接池:str=rosetta("打开链接池")
    清空链接池:str=rosetta("清空链接池")
    完全图绑定:str=rosetta("完全图绑定")
    组到组绑定:str=rosetta("组到组绑定")
    按结点解绑:str=rosetta("按结点解绑")
    按路径解绑:str=rosetta("按路径解绑")
    选中直接操作:str=rosetta("选中直接操作")
    清空后插入:str=rosetta("清空后插入")
    直接插入:str=rosetta("直接插入")
    编组插入:str=rosetta("编组插入")
    卡片插入池:str=rosetta("卡片插入池")
    池中卡片操作:str=rosetta("池中卡片操作")
    改变牌组:str=rosetta("改变牌组")
    操作标签:str=rosetta("操作标签")
    其他:str=rosetta("其他")
    联系作者:str=rosetta("联系作者")
    支持作者:str=rosetta("支持作者")
    打开链接数据保存目录:str=rosetta("打开链接数据保存目录")
    打开代码仓库:str=rosetta("打开代码仓库")
    查看更新与文档:str=rosetta("查看更新与文档")
    发现未注册自定义url协议_现已自动注册_若出现反复注册_请以管理员身份运行anki:str=rosetta("发现未注册自定义url协议,现已自动注册,若出现反复注册,请以管理员身份运行anki")
    打开clipper:str=rosetta("打开clipper")
    在clipper中打开卡片:str=rosetta("在clipper中打开卡片")
    在grapher中打开卡片:str=rosetta("在grapher中打开卡片")
    添加同步复习标签:str=rosetta("添加同步复习标签")
    保存当前搜索条件为自动复习条件:str=rosetta("保存当前搜索条件为自动复习条件")
    保存成功:str=rosetta("保存成功")
    自动复习操作:str=rosetta("自动复习操作")
    重建数据库:str=rosetta("重建数据库")
    配置表操作:str=rosetta("配置表操作")
    重置配置表:str=rosetta("重置配置表")
    创建为视图:str=rosetta("创建为视图")
    视图名:str=rosetta("视图名")
    视图名不能为空:str=rosetta("视图名不能为空")
    视图名必须是JSON合法的字符串:str=rosetta("视图名必须是JSON合法的字符串")
    打开于视图:str=rosetta("打开于视图")
    直接打开:str=rosetta("直接打开")
    删除边:str=rosetta("删除边")
    隐藏边:str=rosetta("隐藏边")

if __name__ == "__main__":
    print(Translate.打开配置表)