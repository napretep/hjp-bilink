from . import compatible_import as compatible
currentLang = compatible.Anki.Lang.currentLang

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
        "打开卡片元信息": "open card meta info",
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
        "保存当前搜索条件为群组复习条件":"restore current search for group review",
        "保存成功":"successfully restored",
        "群组复习操作":"group review operation",
        "重建群组复习数据库":"rebuild group review database",
        "配置表操作":"operations for config file",
        "重置配置表":"reset config file",
        "创建为视图":"create a new view",
        "视图名":"name of view",
        "视图名不能为空":"name of view cannot be empty",
        "视图名必须是JSON合法的字符串":"must be a valid JSON string",
        "打开于视图":"in view of",
        "直接打开":"just open",
        "删除边":"delete edge",
        "隐藏边":"hide edge",
        "Anki搜索":"Anki_search",
        "本视图已被删除,确定退出?":"this view has been deleted, continue?",
        "视图名不能有空白字符,不能有连续4个':',即'::::'非法":"The view name cannot have blank characters, "
                                          "and there cannot be 4 consecutive':', that is,'::::' is illegal",
        "视图名已存在":"name exists",
        "Anki视图":"Anki_view",
        "打开视图管理器":"open view manager",
        "自动更新描述":"auto update desc",
        "上次复习":"last review",
        "下次复习":"next review",
        "可复习":"reviewable",
        "未到期":"not now",
        "学习":"review",
        "请选择卡片":"please select card",
        "复习相关":"review",
        "链接相关":"linking",
        "快捷键":"shortcuts",
        "同步与备份":"sync & backup",
        "关于":"about",
        "已冻结":"review freezed",
        "已解冻":"review recovered",
        "你复习得太快了,你确定你记住了吗?":"review too fast, are you sure you really recall the card?",
        "要开始群组复习了, 你确定吗?":"The automatic review is about to start, please confirm",
        "查看数据库最近更新时间":"lateset update time",
        "手风琴式":"accordion style",
        "直铺式":"straight laying",
        "请点击叶结点":"please choose the leaf nodes",
        "重命名":"rename",
        "删除":"delete",
        "视图":"graph view",
        "群组复习视图":"group_review graph view",
        "含于视图":"Included in view",
        "新建视图":"create view",
        "插入到已有视图":"insert into existing view",
        "链接池视图":"as linkpool view",
        "粘贴卡片":"paste cards",
        "插入到已打开视图":"insert into opened view",
        "修改描述":"edit card description",
        "时间到":"time up",
        "请选择后续操作":"please choose next action",
        "取消":"cancel",
        "重新计时":"retime",
        "默认操作":"default action",
        "秒":"seconds",
        "插入pdf链接":"insert pdf link",
        "临时视图":"temp graph for outext link",
        "即将开始群组复习,点是确认执行,点否仅复习当前卡片":'To start the group review, tap Yes to confirm the execution, or No to review only the current card.',
        "保存当前视图为群组复习条件":"regist view as group review condition",
        "下次到期":"next due",
        "提前复习": "review in advance",
        "开始复习": "click to review",
        "另存视图":"save as new view",
            "描述已修改,但是你不会看到修改结果,因为这张卡保持着描述与字段同步":"The description has been modified, but you will not see the result of the modification because the card keeps the description synchronized with the field"
            ,"打开复习队列":"open due queue"
    }
    ZHdict = {
        "gview_admin_default_display":"视图管理器默认显示",
        "gview_popup_when_review":"复习时视图自动弹出",
        "gview_popup_type":"自动弹出的视图种类",
        "last_backup_time":"上次备份时间",
        "group_review_just_due_card":"仅群组复习到期卡片",
        "group_review_global_condition": "群组复习的全局条件",
        "auto_backup_interval":"自动备份间隔",
        "auto_backup_path":"自动备份路径",
        "auto_backup": "自动备份",
        "auto_sync":"自动同步",
        "group_review_search_string":"群组复习的卡片筛选条件",
        "freeze_review": "开启冻结复习",
        "freeze_review_interval":"冻结复习的最小间隔",
        "too_fast_warn_interval":"提示复习过快的最小间隔",
        "too_fast_warn":"提示复习过快",
        "too_fast_warn_everycard":"连续几张卡片复习过快才提示",
        "group_review":"开启群组复习",
        "group_review_comfirm_dialog":"开启群组复习提示框",
        "length_of_desc":"链接描述自动提取时的限制长度",
        "desc_sync":"链接描述与卡片内容全局同步",
        "new_card_default_desc_sync":"新卡片默认启用链接描述同步",
        "delete_intext_link_when_extract_desc":"提取链接描述时,删去文内链接",
        "add_link_tag":"链接后加时间戳标签",
        "open_browser_after_link":"链接后在浏览界面中展示链接卡片",
        "default_link_mode":"默认链接模式",
        "default_unlink_mode":"默认取消链接模式",
        "default_insert_mode":"默认插入链接池的模式",
        "default_copylink_mode":"默认复制链接的模式",
        "shortcut_for_link":"链接快捷键",
        "shortcut_for_unlink":"取消链接快捷键",
        "shortcut_for_insert":"插入链接池快捷键",
        "shortcut_for_copylink":"复制链接快捷键",
        "shortcut_for_openlinkpool":"打开链接池快捷键",
        "PDFUrlLink_style":"链接样式",
        "PDFUrlLink_cmd":"调用命令",
        "PDFUrlLink_page_num_str":"pdf页码名称",
        "PDFUrlLink_default_show_pagenum":"pdf默认显示页码",

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
    打开anchor:str  = rosetta("打开卡片元信息")
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
    保存当前搜索条件为群组复习条件:str=rosetta("保存当前搜索条件为群组复习条件")
    保存成功:str=rosetta("保存成功")
    群组复习操作:str=rosetta("群组复习操作")
    重建群组复习数据库:str=rosetta("重建群组复习数据库")
    配置表操作:str=rosetta("配置表操作")
    重置配置表:str=rosetta("重置配置表")
    创建为视图:str=rosetta("创建为视图")
    视图名:str=rosetta("视图名")
    视图命名规则:str=rosetta("视图名不能有空白字符,不能有连续4个':',即'::::'非法")
    视图名必须是JSON合法的字符串:str=rosetta("视图名必须是JSON合法的字符串")
    打开于视图:str=rosetta("打开于视图")
    直接打开:str=rosetta("临时视图")
    删除边:str=rosetta("删除边")
    隐藏边:str=rosetta("隐藏边")
    Anki搜索:str=rosetta("Anki搜索")
    本视图已被删除_确定退出么:str=rosetta("本视图已被删除_确定退出么")
    视图名已存在:str=rosetta("视图名已存在")
    视图名不能为空:str=rosetta("视图名不能为空")
    Anki视图:str=rosetta("Anki视图")
    打开视图管理器:str=rosetta("打开视图管理器")
    已复制到剪贴板:str=rosetta("已复制到剪贴板")
    未选择卡片:str=rosetta("未选择卡片")
    自动更新描述:str=rosetta("自动更新描述")
    上次复习:str=rosetta("上次复习")
    下次复习:str=rosetta("下次复习")
    可复习:str=rosetta("可复习")
    未到期:str=rosetta("未到期")
    学习:str=rosetta("学习")
    请选择卡片:str=rosetta("请选择卡片")
    复习相关:str=rosetta("复习相关")
    链接相关:str=rosetta("链接相关")
    快捷键:str=rosetta("快捷键")
    同步与备份:str=rosetta("同步与备份")
    关于:str=rosetta("关于")
    已冻结:str=rosetta("已冻结")
    已解冻:str=rosetta("已解冻")
    过快提示:str=rosetta("你复习得太快了,你确定你记住了吗?")
    群组复习提示:str=rosetta("即将开始群组复习,点是确认执行,点否仅复习当前卡片")
    查看数据库最近更新时间:str=rosetta("查看数据库最近更新时间")
    手风琴式:str=rosetta("手风琴式")
    直铺式:str=rosetta("直铺式")
    请点击叶结点:str=rosetta("请点击叶结点")
    重命名:str=rosetta("重命名")
    删除:str=rosetta("删除")
    视图:str=rosetta("视图")
    群组复习视图:str=rosetta("群组复习视图")
    反链视图:str=rosetta("含于视图")
    新建视图:str=rosetta("新建视图")
    插入视图:str=rosetta("插入到已有视图")
    粘贴卡片:str=rosetta("粘贴卡片")
    插入到已打开视图:str=rosetta("插入到已打开视图")
    修改描述:str=rosetta("修改描述")
    插入pdf链接:str=rosetta("插入pdf链接")
    pdf链接:str=rosetta("pdf链接")
    pdf路径:str=rosetta("pdf路径")
    pdf页码:str=rosetta("pdf页码")
    pdf名字:str=rosetta("pdf名字")
    确定:str=rosetta("确定")
    不操作:str=rosetta("不操作")
    忘记:str=rosetta("忘记")
    困难:str=rosetta("困难")
    良好:str=rosetta("良好")
    简单:str=rosetta("简单")
    延迟一天:str=rosetta("延迟一天")
    延迟三天: str = rosetta("延迟三天")
    延迟一周: str = rosetta("延迟一周")
    延迟一月: str = rosetta("延迟一月")
    自定义延迟: str = rosetta("自定义延迟")
    显示答案:str=rosetta("显示答案")
    取消:str=rosetta("取消")
    重新计时:str=rosetta("重新计时")
    默认操作:str=rosetta("默认操作")
    pdf默认显示页码:str=rosetta("pdf默认显示页码")
    pdf样式:str=rosetta("pdf样式")
    anki网络版:str=rosetta("anki网络版")
    本地版:str=rosetta("本地版")
    保存当前视图为群组复习条件:str=rosetta("保存当前视图为群组复习条件")
    下次到期:str=rosetta("下次到期")
    提前复习:str=rosetta("提前复习")
    开始复习:str=rosetta("开始复习")
    另存视图:str=rosetta("另存视图")
    描述已修改但是___ :str=rosetta("描述已修改,但是你不会看到修改结果,因为这张卡保持着描述与字段同步")
    打开复习队列:str = rosetta("打开复习队列")

if __name__ == "__main__":
    print(Translate.打开配置表)