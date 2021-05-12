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
        "请安装插件1423933177,否则将无法点击链接预览卡片": "please install the addon 1423933177, otherwise you can't click the link and open preivew window",
        "请安装插件564851917,否则将无法折叠标签,我们每次链接都会产生标签": "please install the addon 1423933177,otherwise you won't have hierarchical tag system, it's useful for collapse/expand the tag produced by hjp-bilink",
        "config重置成功": "config reseted",
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
        "开启":"enabled",
        "关闭":"disabled",
        "sqlite数据库存储":"sqlite3 DB",
        "卡片字段存储":"card field",
        "JSON文件存储":"JSON File",
        "清空后插入":"clean and insert",
        "编组插入":"insert as a group",
        "选择文件":"choose a file",
        "数据覆盖":"overwrite data",
        "数据合并":"merge data",
        "已删除反链":"back reference deleted",
        "已复制到剪贴板":"links copied to clipboard",
        "已建立反链":"back reference created",
        "复制为文内链接":"copy as in text link",
        "链接数据迁移对话框":"switch storage location",
        "链接数据迁移":"switch the data storage location",
        "执行":"execute",
        "从":"from",
        "转移到":"switch to",
        "写入模式":"write mode",
        "注意1:当数据从A转移到B，会删除A中的数据记录":"hint1:switch data from A to B, the data in A will be deleted",
        "注意2:先把想要转移的卡片插入到input":"hint2:put the card you want into the Input before execute",
        "defaultLinkMode": "default link mode (for shortcut)",
        "defaultUnlinkMode": "default unlink mode (for shortcut)",
        "defaultInsertMode": "default insert mode(for shortcut)",
        "addTagEnable": "auto add tag when linking",
        "appendNoteFieldPosition": "note field to store data (work in specified mode)",
        "readDescFieldPosition": "note field to read the description",
        "linkInfoStorageLocation": "link data storage location",
        "descMaxLength": "auto read desc max length",
        "addTagRoot": "the root tag name of auto add tag ",
        "button_appendTo_AnchorId": "the HTML id of anchor (if you know)",
        "shortcut_inputDialog_open": "shortcut:open input(global)",
        "shortcut_browserTableSelected_link": "shortcut:link(browser)",
        "shortcut_browserTableSelected_unlink": "shortcut:unlink(browser)",
        "shortcut_browserTableSelected_insert": "shortcut:insert to input(browser)",
        "shortcut_inputFile_clear": "shortcut:clear input(global)",
        "anchorCSSFileName": "anchor CSS file name (if you know)",
        "shortcut_copylink": "shortcut:copy link (browser)"
    }
    ZHdict = {
        "defaultLinkMode":"默认链接方式(用于快捷键)",
        "defaultUnlinkMode":"默认取消链接方式(用于快捷键)",
        "defaultInsertMode":"默认插入input方式(用于快捷键)",
        "addTagEnable":"开启链接自动加标签的功能",
        "appendNoteFieldPosition":"数据存于卡片字段的位置（对应模式开启有效）",
        "readDescFieldPosition":"描述读取于卡片字段的位置",
        "linkInfoStorageLocation":"链接数据保存的模式",
        "descMaxLength":"自动读取描述的最大长度",
        "addTagRoot":"自动加的标签其根部名称",
        "button_appendTo_AnchorId":"添加按钮锚点的HTML元素 ID（不懂可不管）",
        "shortcut_inputDialog_open":"打开input的快捷键(全局)",
        "shortcut_browserTableSelected_link":"链接快捷键(browser下)",
        "shortcut_browserTableSelected_unlink":"取消链接快捷键(browser下)",
        "shortcut_browserTableSelected_insert":"插入input快捷键(browser下)",
        "shortcut_inputFile_clear":"input清空快捷键(全局)",
        "anchorCSSFileName":"按钮锚点的CSS样式文件（不懂可不管）",
        "shortcut_copylink":"文内链接快捷键（browser下）"
    }
    translateFuncs = {
        "en": En,
        "en-GB": En,
        "zh-CN": Zh,
        "zh-TW": Zh,
    }

    return translateFuncs[lang](text)
