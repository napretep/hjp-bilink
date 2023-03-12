from . import compatible_import as compatible
from . import baseClass
currentLang = compatible.Anki.Lang.currentLang

枚举 = baseClass.枚举命名

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
            "卡片":"card",
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
        "全局链接相关":"global linking",
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
            ,"打开复习队列":"open due queue",
            "双面展示":"both side",
            "开始漫游复习":"start roaming review",
            "由视图名搜索视图":"search graph by name",
            "视图配置与视图是两个独立的对象, 一个视图配置可以应用到多个视图上":"The view configuration and the view are two separate objects, and a view configuration can be applied to multiple views"
        ,
        "添加卡片":"append card",
        "添加视图":"append view",
        "新建":"create",
        "导入":"import"
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


def 翻译(zh="",en="",**kwargs):
    surrport = ["zh-CN", "zh-TW", "en", "en-GB"]
    if currentLang in ["zh-CN", "zh-TW"]:
        return zh
    elif currentLang in ["en", "en-GB"] and "en" in kwargs:
        return en
    else:
        return en

# noinspection NonAsciiCharacters
class Translate:

    例子_结点过滤=翻译("""例子:node_priority>0
表示当结点的优先级大于0时,才纳入漫游队列,
    ""","""Example: node_priority>0
means that when the priority of the node is greater than 0, it will be included in the roaming queue
    """)

    例子_多级排序=翻译("""例子:[[node_priority,descending],[node_visit_count,ascending]]
表示先比较两个结点的优先级,按降序排序, 若优先级相同, 则再比较两个结点的访问次数, 按升序排序
descending, ascending 是两个变量
""",
"""
Example: [[node_priority,descending],[node_visit_count,ascending]]
means first compare the priority of two nodes, sort by descending, if the priority is the same, then compare the visit count of two nodes, sort by ascending
descending, ascending are two variables
""")
    例子_加权排序=翻译("""例子: max(abs(node_last_visit-node_last_review)/86400,-node_role,node_out_degree+node_in_degree)
表示在以下三种结果中取最大的作为权重值:1结点上次访问与上次复习的差值比上1天的秒数,2结点角色在角色列表中所对应位置的负数, 3 结点出度与入度之和
最终结果默认按计算所得权重的降序排序
    ""","""Example: max(abs(node_last_visit - node_last_review)/86400,-node_role,node_out_degree+node_in_degree)
This means that the largest of the following three results is used as the weight value: 1 the number of seconds between the last visit and the last review of the node compared to the last day, 2 the negative number of the node's role in the role list, 3 the sum of the node's out-degree and in-degree.
The final result is sorted by default in descending order of the calculated weights
    """)

    可用变量与函数 = 翻译("可用变量,函数与模块","Available Variables, Functions and Modules")
    角色待选列表 = 翻译("角色待选列表","Role to be selected list")
    所有time开头的变量都是时间戳=翻译("所有以'time'开头的变量都是时间戳","All variables that start with 'time' are timestamps")
    说明_属性查看 = 翻译("当你没有选中东西,打开视图本身的属性,当你选中了一个东西,打开那个东西的属性","when you don't select node or edge, it will open the property of the view, else open the propery of the selected node or edge")
    边名=翻译("边名","edge name")
    删除结点 = 翻译("删除结点","delete node")
    移除= 翻译("移除(非删除卡片)","remove(not delete card)")
    视图上次访问 = 翻译("视图上次访问","view_last_visit")
    视图上次编辑 = 翻译("视图上次编辑","view_last_edit")
    视图上次复习 = 翻译("视图上次复习","view_last_review")
    视图访问次数 = 翻译("视图访问次数","view_visit_count")
    视图到期结点数 = 翻译("视图到期结点数","view_due_node_count")
    视图主要结点 = 翻译("视图主要结点","view_major_nodes")
    视图创建时间 = 翻译("视图创建时间","view_created_time")
    该项解释工作未完成= 翻译("该项解释工作未完成","the explanation was not completed")
    双击牌组即可修改卡片所属牌组=翻译("双击牌组即可选中","Double click on the deck to select")
    选择文外链接卡片加载 = 翻译("选择","select")
    加载全部文外链接卡片 = 翻译("全部","all")
    加载文外链接卡片 = 翻译("加载文外链接卡片","load out-link cards")
    无角色 = 翻译("无角色","no role")
    漫游起点 = 翻译("漫游起点","roaming start")
    说明_漫游起点 = 翻译("当你的漫游路线生成模式为图遍历排序模式, 而且视图配置中'roamingStart'项选择了自动模式时, 本程序会自动在结点集合中寻找首个'漫游起点'属性开启的结点作为图遍历的起点. 更多信息请查看视图配置中'roamingStart'项的解释.","When your roaming route generation mode is graph traversal sorting mode and automatic mode is selected for 'roamingStart' in the view configuration, the program will automatically find the first node in the node set with the 'roamingStart' attribute turned on as the starting point of the graph traversal. For more information, please see the explanation of 'roamingStart' item in the view configuration.")
    必须复习 = 翻译("必须复习","must review")
    说明_必须复习 = 翻译("当一个结点的'必须复习'属性被开启, 则无论是否满足漫游复习的过滤规则, 都会被选中复习","When the 'must review' attribute of a node is turned on, it will be selected for review regardless of whether the roaming review filter rule is satisfied")
    需要复习 = 翻译("需要复习","need review")
    说明_需要复习 = 翻译("当一个结点的'需要复习'属性被关闭, 则无论是否满足漫游复习的过滤规则, 都不会被选中复习","When the 'need to review' attribute of a node is turned off, it will not be selected for review, regardless of whether the roaming review filter rule is satisfied.")
    说明_结点优先级 = 翻译("结点优先级这个属性通常由于筛选和排序用于漫游复习的结点","The node priority property is usually used to filter and sort the nodes for roaming review due to")
    结点优先级 = 翻译("结点优先级","node priority")
    说明_主要结点 = 翻译("在展示视图概要信息时, 主要结点会作为这个视图的代表性结点用来简要展示","When presenting the view summary information, the major node is used as a representative node for this view for a brief presentation")
    主要结点 = 翻译("主要结点","major node")
    结点数据类型 = 翻译("结点类型","node  type")
    说明_结点数据类型 = 翻译("目前视图的结点有两种类型, 卡片类型和视图类型, 未来可能会增加更多的类型","Currently there are two types of view nodes, card type and view type, more types may be added in the future")
    说明_上次访问 = 翻译(zh="每当你在视图上双击打开一个结点时, 就会记录你这次访问的时间, 即所谓的上次访问时间, 同样上次访问时间也是依赖于特定视图的, 在不同视图中的相同卡片或视图结点有不同的上次访问时间",
                 en="Whenever you double-click on a view to open a node, the time of your visit is recorded, the so-called last visit time, which is also view-dependent, as the same card or view node in a different view has a different last visit time")
    上次访问 = 翻译(zh="上次访问时间",en="last view time")
    说明_上次编辑 = 翻译(zh="结点的上次编辑时间是指你最后一次编辑结点属性的时间, 他是与视图有关的属性, 也就是说, 同一个卡片或视图在不同的视图中作为结点时, 他们均有独立的上次编辑时间",
                 en="The last edit time of a node is the time when you last edited the properties of the node, which are view-related properties, that is, the same card or view has an independent last edit time when it is used as a node in different views")
    结点角色 = 翻译(zh="结点角色",en="node role")
    说明_结点角色 = 翻译(zh="每个结点都可以赋予一个角色属性, 角色的概念类似于标签, 用于对结点作进一步的分类, 结点的角色并不能随意赋予, 而是要根据视图配置中预定的角色列表来赋予, 视图配置预定的角色列表使用方法请直接看相关的选项.",
                 en="Each node can be assigned a role attribute, the concept of role is similar to tag, used to further classify the node, the role of the node can not be assigned arbitrarily, but according to the predefined list of roles in the view configuration, the use of the predefined list of roles in the view configuration, please see the relevant options directly")
    说明_到期结点 = 翻译(zh="对于卡片类型的结点来说, 结点到期即anki定义的到期, 对于视图类型的结点来说, 它总是处在到期状态",
                 en="For card type nodes, the due node is the due defined by anki, and for view type nodes, it is always in the due state")
    到期结点 = 翻译(zh="到期结点",en="is due node")
    说明_结点描述 = 翻译(zh="结点名称是与视图无关的属性, 你在任何地方修改结点名称都会导致所有视图中含有该对象的名称被同步改变,若结点类型为视图,则结点名称就是这个视图的名称, 若结点类型为卡片, 则结点名称是从卡片中提取的, 卡片结点的名称提取方法可以在全局设置中修改",
                 en="The node name is a view-independent property, where you change the node name anywhere, the name of the object in all views will be changed simultaneously, if the node type is a view, then the node name is the name of the view, if the node type is a card, then the node name is extracted from the card, the method of extracting the name of the card node can be changed in the global settings")
    结点描述 = 翻译(zh="结点名称",en="node name")
    结点上次复习 = 翻译(zh="结点上次复习",en="node last review")
    全局上次复习 = 翻译("全局上次复习","global last review")
    说明_结点上次复习=翻译("结点的上次复习时间与视图有关,在你的每次漫游复习中更新","The last review time of the node is related to the view, and is updated in each of your roaming reviews")
    说明_全局上次复习 = 翻译(zh="卡片的全局上次复习时间是与视图无关的,与anki自身的复习系统有关",
                 en="The global last review time of the card is not related to the view, but to anki's own review system")
    到达结点的边的数量 = 翻译(zh="到达结点的边的数量", en="Number of edges that reach the node")
    从结点出发的边的数量 = 翻译(zh="从结点出发的边的数量",en="Number of edges from the node")
    结点入度 = 翻译(zh="结点入度", en="node in-degree")
    结点出度 = 翻译(zh="结点出度",en="node out-degree")
    结点位置 = 翻译(zh="结点坐标",en="node coordinates")
    可执行字符串_返回的值必须是数值类型 = 翻译(
            zh="可执行字符串表达式的返回值必须是数值类型", en="The return value of codeString must be int or float type"
    )

    可执行字符串表达式的返回值必须是布尔类型= 翻译(
            zh="可执行字符串表达式的返回值必须是布尔类型", en="The return value of codeString must be a Boolean type"
    )
    可执行字符串表达式的返回值必须是列表类型 = 翻译(
            zh="可执行字符串表达式的返回值必须是列表类型", en="The return value of codeString must be a list type"
    )
    可执行字符串_必须是一个二元元组 = 翻译(
            zh="可执行字符串表达式的列表返回值的每个元素必须是一个二元元组", en="Each element of the list returned by codeString must be a binary tuple"
    )
    可执行字符串_二元组中的变量名必须是指定名称 = 翻译(
            zh="二元组中的变量名必须是指定名称", en="The variable name in the binary must be the specified name"
    )
    你将重置本视图的配置 = 翻译(zh="你将重置本视图的配置",en="You will reset the configuration of this view")
    过滤表达式 = 翻译(zh="过滤表达式",en="filter expression")
    多级排序依据=翻译(zh="排序依据",en="sorting bases")
    加权公式 = 翻译(zh="加权公式",en="weighted formula")
    选中 = 翻译(zh="选中",en="selected")
    你将删除这些结点 = 翻译(zh="你将删除这些结点", en="You will delete these nodes")
    深度优先遍历=翻译(zh="深度优先遍历",en="depth-first traversal ")
    广度优先遍历=翻译(zh="广度优先遍历",en="breadth-first traversal")
    说明_漫游路径算法选择=翻译(
            zh="""
漫游路径算法选择: roaming_path_mode
当我们打算在视图的结点网络中进行漫游复习时, 我们需要确定漫游经过的结点序列, 这个序列就是漫游的路线, 
这个路线需要两个不同的配置项确定, 当前配置项仅指定基本的漫游模式, 指定漫游的基本模式后, 就可以到这种模式同名的配置项中, 选择一种具体的排序算法来规划漫游路径,
基本模式有:random_sort(随机排序),cascading_sort(多级排序), weighted_sort(加权排序), graph_sort(图排序)三种.
其中 random_sort 模式是以随机的方式来确定漫游的路径, 无需进一步设置.
            """,
            en="""
Roaming path algorithm selection: roaming_path_mode
When we intend to roam a network of nodes in the view, we need to determine the sequence of nodes through which the roaming will take place, and this sequence is the roaming route, 
This route needs to be determined by two different configuration items, the current configuration item only specifies the basic roaming mode, after specifying the basic mode of roaming, you can go to the configuration item of the same name of this mode and choose a specific sorting algorithm to plan the roaming path,
The basic modes are:random_sort, cascading_sort, weighted_sort, and graph_sort.
The random_sort mode determines the roaming path in a random way, no further settings are needed.
            """
    )

    说明_总是显示边名 = 翻译(
            zh="""勾选本项后, 所有结点的边的名字总是会显示出来. 不勾选本项的话, 只有当你选中一个结点时, 才会显示从这个结点出发的边的名字.
""",
            en="""When this item is checked, the names of the edges of all nodes will always be displayed. If this item is not checked, the name of the edge from this node will be displayed only if you select it.
"""
    )

    说明_结点角色枚举 = 翻译(
            zh="""
你在文本框中输入python语法的字符串列表, 会被转换成 视图结点的 node_role属性中的 待选角色列表
示例: 
如果你在文本框中输入 ["apple","banana","orange"] 后, 那么视图中结点的node_role属性中就会有 apple, banana, orange 三个可选的角色.   
注意:
1. 必须严格遵守python的字符串列表类型格式, 否则无法被保存.

2. 元素的顺序是有意义的, 排在前面的权重更大, 用于加权计算.
            """,
en="""
The list of strings you enter in the text box in python syntax will be converted to a list of roles to be selected in the node_role property of the view node
Example: 

If you type ["apple", "banana", "orange"] in the textbox, then the node_role property of the view node will have apple, banana, orange as optional roles.   

Note: 1:
1. must strictly adhere to python's string list type format, otherwise it cannot be saved.

2. The order of the elements is meaningful, the first one has more weight, which is used for weighting calculation.

"""
    )

    说明_加权排序=翻译(
zh=f"""
加权排序:weighted_sort
如果你在roaming_path_mode中选择了weighted_sort模式,
那么在本程序执行生成漫游路径的操作时,会根据当前表格中选中的加权公式, 作为对每个结点评分的依据.最终会以这些结点的加权评分的降序排列结果作为漫游的路径.
如果没有选中任何加权公式, 那么会采用默认的公式来排序结点:  {baseClass.漫游预设.默认加权排序规则}
""",
en=f"""
Weighted sort: weighted_sort
If you select weighted_sort mode in roaming_path_mode,
Then when this program generates roaming paths, it will use the weighted formula selected in the current table as the basis for scoring each node. The final roaming path will be based on the descending order of the weighted scores of these nodes.
If no weighting formula is selected or the table is empty, then the default formula will be used to sort the nodes:{baseClass.漫游预设.默认加权排序规则}
"""
    )

    说明_多级排序 = 翻译(
            zh=f"""
多级排序:cascading_sort
如果你在roaming_path_mode中选择了cascading_sort模式, 则漫游路径会根据结点的各类属性排序结果生成.
在本配置项中, 如果你想添加一种多级排序规则, 则需要点击加号按钮, 在弹出的对话框中输入一个python语法风格的列表.
这个列表的每个元素是一个二元对,
在每个二元对中,第一个元素用于填写进行排序比较的变量, 第二元素用于填写升序还是降序排序, 
列表中的二元对放置顺序确定了多级排序比较所用变量的顺序, 排在前面的变量优先进行比较.

例如,当你填写:
[[node_priority,descending],[node_visit_count,ascending]]

则两个结点会先根据 node_priority 进行降序排序, 
如果两个结点的node_priority相同, 则再根据 node_visit_count 进行升序排序

注意:
升序和降序只能用"ascending","descending"来表示,
排序依据的变量只能是规定的可用变量

默认的多级排序规则:{baseClass.漫游预设.默认多级排序规则}
            """,
en=f"""
cascading sorting: cascading_sort
If you select cascading_sort mode in roaming_path_mode, the roaming path will be generated based on the sorting result of various attributes of the node.
In this configuration, if you want to add a multi-level sorting rule, you need to click the plus button and enter a python syntax style list in the popup dialog.
Each element of this list is a binary pair,
In each binary pair, the first element is used to fill in the variables to be sorted and compared, and the second element is used to fill in whether to sort ascending or descending, 
The order in which the binary pairs are placed in the list determines the order of the variables used in the multilevel sorting comparison, with the first variables being compared first.

For example, when you fill in:
[[node_priority,descending],[node_visit_count,ascending]]

then the two nodes will be sorted first in descending order according to node_priority, 
If both nodes have the same node_priority, then they are sorted ascending according to node_visit_count

Note:
Ascending and descending can only be represented by "ascending" and "descending",
The sorting variables can only be based on the available variables.

Default cascading sorting rule: {baseClass.漫游预设.默认多级排序规则}
"""
    )
    说明_图排序 = 翻译(
            zh="""
图排序:graph_sort,
如果你在roaming_path_mode中选择了graph_sort模式, 则漫游路径会根据结点的遍历结果生成.
图的排序算法有深度优先遍历和广度优先遍历两种.
如果你已经选中了一个结点, 则图排序会以你所选结点为遍历起点, 否则会在视图的结点中寻找首个 roaming_start=True的结点作为遍历的起点
""",
en="""
Graph sorting: graph_sort,
If you choose graph_sort mode in roaming_path_mode, the roaming path will be generated based on the node traversal result.
There are two sorting algorithms for graphs: depth-first traversal and breadth-first traversal.
If you have already selected a node, the graph sort will start the traversal with the node you selected, otherwise it will find the first node with roaming_start=True among the view nodes as the starting point of the traversal
"""
    )


    说明_漫游路径过滤 = 翻译(
        zh=f"""
漫游结点过滤:roaming_node_filter
本配置项将根据用户所设条件, 先将不满足条件的结点过滤剔除, 再在剩余满足条件的结点上执行漫游路径生成算法,

比如:
点击加号新建一行记录, 在弹出的文本框中输入 
node_priority > 50 and node_visit_count <30 and node_role_name in ["apple","banana"]
点击确定后, 在表中选中此行, 则程序会根据结点的优先级属性是否大于50, 访问次数属性是否小于30以及结点标签属性是否为apple或banana, 过滤掉不满足条件的结点, 在这个基础上再去执行路径生成算法.

注意:
条件必须是符合python语法的表达式,返回值只能是布尔类型.

默认的过滤规则: {baseClass.漫游预设.默认过滤规则}
        """,
en=f"""
Roaming node filtering: roaming_node_filter
This configuration item will filter out the nodes that do not meet the conditions according to the conditions set by the user, and then execute the roaming path generation algorithm on the remaining nodes that meet the conditions,

For example, Click the plus sign to create a new row in the pop-up text box, enter:
node_priority > 50 and node_visit_count < 30 and node_role in ["apple", "banana"] 
After clicking OK, select this row in the table, then the program will filter out nodes that do not meet the criteria based on their priority, visit count and node tag attributes, and then execute the path generation algorithm based on that.

Note:
The condition must be a python syntax expression, and the return value can only be a boolean.

Default filter rule:  {baseClass.漫游预设.默认过滤规则}
"""
    )

    导入 = 翻译(zh="导入到视图",en="insert into another view")
    不存在 = 翻译(zh="不存在",en="do not exist")
    在此处搜索=翻译(zh="输入关键词,敲击回车搜索", en="Enter something here, hit enter to search")
    说明_视图管理器的用法: str =翻译(zh="""
    这是视图管理器窗口, 用于管理视图, 目前提供的操作有: 打开视图, 重命名视图, 切换列表/树状显示, 搜索视图, 选中若干视图插入到另一个视图.
    打开视图:双击视图即可打开,点击底部栏的按钮也可以打开,
    重命名视图:选中一个视图, 点击底部对应按钮即可,
    切换显示方式: 点击底部对应按钮,
    将视图插入到另一个视图: 选中一个或多个视图, 点击右键选择当前打开的视图插入, 或者选择一个视图插入.
    搜索视图:可以搜视图的id, 视图的名字, 以及视图中卡片的描述. 
    注:为了实现搜索视图中卡片的描述, 这个程序会在关闭视图管理器时, 消耗一些时间去建立视图中卡片描述的缓存, 这可能使得关闭视图管理器时出现卡顿的现象, 如果不希望搜索视图中卡片的描述可以在设置中关闭.
    """,
    en="""This is the view manager window, used to manage views, currently provides the following actions: open a view, rename a view, switch the list/tree display, search for a view, select a number of views to insert into another view.
    Open view: Double click on a view to open it, or click on the button in the bottom bar to open it,
    Rename view: select a view and click on the corresponding button at the bottom,
    Switching the display: click the corresponding button at the bottom,
    Insert a view into another view: select one or more views, right-click and select the currently open view to insert, or select a view to insert.
    Search view: you can search the view id, the name of the view, and the description of the card in the view.
    Note: In order to search for card descriptions in the view, the program will spend some time to build a cache of card descriptions in the view when closing the view manager, which may cause a lag when closing the view manager, if you do not want to search for card descriptions in the view you can turn it off in the settings.
"""
                         )
    视图编号 = 翻译("视图编号","view id")

    视图名 = 翻译(zh="视图名",en="view name")
    说明_创建时间 = 翻译("结点的创建时间是不可修改的, 除非你删除这个结点, 并再次导入它","The creation time of a node cannot be modified unless you delete the node and import it again")
    创建时间 = 翻译(zh="创建时间", en="created time")
    上次访问时间=翻译(zh="上次访问时间", en="last visit time")
    上次编辑时间=翻译(zh="上次编辑时间", en="last edit time")
    上次复习时间=翻译(zh="上次复习时间", en="last review time")
    说明_访问数 = 翻译("每当你在视图上双击打开一个结点时, 结点访问次数属性就会增加1,  同样访问次数也是依赖于特定视图的, 在不同视图中的相同卡片或视图结点有不同的访问次数","Whenever you double-click on a view to open a node, the node visit count property is increased by 1. Again, the visit count is view-dependent, and the same card or view node in a different view has a different visit count")
    访问数 = 翻译(zh="访问数", en="visit count")
    结点数 = 翻译(zh="结点数", en="nodes count")
    边数 = 翻译(zh="边数", en="edges count")
    到期卡片数 = 翻译(zh="到期卡片数", en="due count")
    代表性结点 = 翻译(zh="代表性结点", en="major nodes")

    导入到视图 = 翻译(zh="导入到视图",en="Insert them to a view")
    选择一个视图 = 翻译(zh="选择一个视图",en="Select a view to insert")

    插入到已经打开的视图 = 翻译(zh="插入到已经打开的视图",en="Insert into an opened view")
    打开配置表:str = rosetta("打开配置表")
    打开anchor:str = rosetta("打开卡片元信息")
    文内链接:str = rosetta("文内链接")
    html链接:str = rosetta("html链接")
    markdown链接:str = rosetta("markdown链接")
    orgmode链接:str = rosetta("orgmode链接")
    复制为:str=rosetta("复制为")
    复制当前搜索栏为:str = rosetta("复制当前搜索栏为")
    文外链接操作:str=rosetta("文外链接操作")
    打开链接池:str=翻译("打开双链分组器","open bilink grouper")
    清空链接池:str=翻译("清空双链分组器","clear bilink grouper")

    完全图绑定:str=翻译("完全图绑定","complete graph binding")

    组到组绑定:str=翻译("完全多部图绑定","complete n-partite graph binding")
    按结点解绑:str=rosetta("按结点解绑")
    按路径解绑:str=rosetta("按路径解绑")
    选中直接操作:str=rosetta("选中直接操作")
    清空后插入:str=rosetta("清空后插入")
    直接插入:str=rosetta("直接插入")
    编组插入:str=rosetta("编组插入")
    卡片插入池:str=翻译("卡片插入分组器","insert card into grouper")
    池中卡片操作:str=翻译("分组器中卡片操作","operate in bilink grouper")
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
    在graph_view中打开卡片:str=翻译("在graph_view中打开卡片","open card in graph_view")
    添加同步复习标签:str=rosetta("添加同步复习标签")
    保存当前搜索条件为群组复习条件:str=rosetta("保存当前搜索条件为群组复习条件")
    保存成功:str=rosetta("保存成功")
    群组复习操作:str=rosetta("群组复习操作")
    重建群组复习数据库:str=rosetta("重建群组复习数据库")
    配置表操作:str=rosetta("配置表操作")
    重置配置表:str=rosetta("重置配置表")
    创建为视图:str=rosetta("创建为视图")

    视图命名规则:str=rosetta("视图名不能有空白字符,不能有连续4个':',即'::::'非法")
    视图名必须是JSON合法的字符串:str=rosetta("视图名必须是JSON合法的字符串")
    打开于视图:str=rosetta("打开于视图")
    图形化双链操作界面:str=翻译("图形化双链器","visual bilinker")
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
    卡片:str=rosetta("卡片")
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
    双面展示:str=rosetta("双面展示")
    开始漫游复习:str=rosetta("开始漫游复习")
    全部卡片:str=rosetta("全部卡片")
    到期卡片:str=翻译("到期卡片","node that is due")
    选中的卡片:str=rosetta("选中的卡片")
    选中卡片的连通集:str=rosetta("选中卡片的连通集")
    广度优先: str = rosetta("广度优先")
    深度优先: str = rosetta("深度优先")
    拓扑排序: str = rosetta("拓扑排序")
    随机排序: str = rosetta("随机排序")
    到期时间升序:str = rosetta("到期时间升序")
    到期时间降序: str = rosetta("到期时间降序")
    自动选择卡片开始:str=翻译("自动模式","Automatic mode")
    随机选择卡片开始:str=翻译("随机模式","Random mode")
    手动选择卡片开始:str = 翻译("手动模式","Manual mode")
    由视图名搜索视图:str = rosetta("由视图名搜索视图")
    更换本视图的配置:str = rosetta("更换本视图的配置")
    说明_视图配置与视图的区别:str = rosetta("视图配置表(设置表)与视图是两个独立的对象,两者的关系就像牌组设置与牌组本身, 视图配置可以控制视图的默认行为, 一个视图配置可以应用到多个视图上, 如果一个视图配置没有对应的视图, 则该视图配置会被删除")
    输入关键词并点击查询:str = rosetta("输入关键词并点击查询")
    搜索并选择配置:str = rosetta("搜索并选择配置")
    说明_同时搜索配置与视图的配置:str = rosetta("你输入的关键词会同时匹配视图名与配置名, 若你选择的是配置则直接加载这个配置, 若你选择的是视图则会加载这个视图对应的配置. 若你没有做出选择, 点击确认不会有反应")
    插件数据主动备份 =翻译("插件数据主动备份","addon data backup")
    新建配置:str = 翻译("新建配置","create new config")
    配置:str = rosetta("配置")
    添加卡片:str = rosetta("添加卡片")
    添加视图:str = rosetta("添加视图")
    新建:str = rosetta("新建")
    结点角色名= 翻译("结点角色名","node role name")
    说明_结点角色名=翻译(f"结点角色名无法在结点属性中修改,如果想更改角色名, 请到视图的配置表中修改{枚举.视图配置.结点角色表}",f"The node role name cannot be changed in the node properties, if you want to change the role name, please go to the configuration table of the view. {枚举.视图配置.结点角色表}")
    说明_新增卡片指定存放牌组=翻译("当你在视图中新增卡片时,在此处指定默认要存放的牌组,如果为空则根据anki默认的指定方式","When you add a card in this view, specify the default deck to be stored here, or if it is empty, specify it according to the anki default")
    打开默认视图 = 翻译("打开默认视图","open default view")
    打开默认漫游复习 = 翻译("打开默认漫游复习","open default roaming")
    说明_设定默认视图=翻译(f"设定mainwindow中 '{打开默认视图}' 和 '{打开默认漫游复习}' 这两个菜单所对应的视图",f"Set the view corresponding to the menus '{打开默认视图}' and '{打开默认漫游复习}' in mainwindow")
    请先设定默认视图=翻译(f"请先设定默认视图","Please set the default view first")
    设为默认视图 = 翻译("设为默认视图","set as default view")
    说明_漫游复习侧边栏收起 = 翻译("是否默认收起漫游复习的侧边栏","Whether to tuck away the sidebar for roaming review by default")
    双链分组器=翻译("双链分组器","bilink grouper")
    描述提取规则_标签=翻译("标签","tags")
    描述提取规则_牌组=翻译("牌组","deck")
    描述提取规则_正则=翻译("正则表达式","regex")
    描述提取规则_字段=翻译("字段","field")
    描述提取规则_同步=翻译("内容同步","content sync")
    描述提取规则_模板=翻译("卡片模板","card template")
    描述提取规则_长度=翻译("字符长度","text length")
    不选等于全选 = 翻译("你没有选择任何一项, 程序默认你选择了全部项","You have not selected any item, the program defaults to your selection of all items")
    不选角色等于不选 = 翻译("你没有选择任何一项, 程序默认你一项都不选","If you do not select any of them, the program defaults you to none of them")
    双击以选中项 = 翻译("双击以完成选中","double-click to select item")
    说明_多选框的用法 = 翻译("""右侧列表显示你可选的项,左侧列表为你已经选好的项,双击右侧列表的项或者点击右侧列表下面的确认按钮,即可将选中的项添加到左侧.
    在左侧列表中, 你选中一项或多项后, 点击左侧列表底下的删除按钮, 即可将选中的项从左侧窗口中移除. 当你点击关闭时自动会将所选的项保存下来.
    ""","""
    The right list shows the items you can choose, and the left list shows the items you have already chosen. 
    Double-click an item in the right list or click the confirm button below the right list to add the selected item to the left. 
    In the left list, after you select one or more items, click the delete button at the bottom of the left list to remove the selected items from the left window. 
    When you click close button, it will automatically save your selected items.
    """)
    已修改 = 翻译("已修改","edited")
    结点批量编辑 = 翻译("结点批量编辑","nodes batch editing")
    新版本介绍 = 翻译("hjp-linkmaster新版本介绍","Introduction of the new version of hjp-linkmaster")
    是否查看更新日志 = 翻译("是否查看更新日志? 你也可以稍后自己查看", "hjp-linkmaster has been updated, do you want to check the changelog? You can also check it yourself later")
    检测到同时启用了本地版与网络版插件 = 翻译("hjp_linkmaster:检测到同时启用了本地版与网络版插件,现在将取消启动本地版插件,如果你想启动本地版插件,请先禁用或卸载网络版插件","hjp_linkmaster:It is detected that both local and network versions of the addon are enabled, now the local version of the addon will be de-activated.If you want to start the local version of the plugin, please disable or uninstall the network version first ")
    你想打开链接吗 = 翻译("你输入的不是pdf文件,你想直接用默认程序打开文件吗?","What you type is not a pdf file, you want to open the file directly with the default program?")
    说明_描述提取规则=翻译("在本项设置中,你可以指定提取卡片描述的方式, 比如指定什么模板,提取哪个字段,长度多少,还可以写正则表达式, 双击单元格修改,加号按钮增加规则,减号去掉选中规则, ","")
    说明_漫游复习时分屏=翻译("漫游复习时,将屏幕分成两块","When roaming review, divide the screen into two pieces")
    说明_视图结点创建默认配置= 翻译("创建新的视图结点时,默认使用本配置作为新视图的配置","When creating a new view node, this configuration is used as the configuration of the new view by default")
    视图配置 = 翻译("视图配置","view config")
    视图配置选择 = 翻译("视图配置选择","select view config")
    说明_新建视图_配置选择 = 翻译("请选择一个存在的视图配置,若不选则默认新建一个配置.","Please select an existing view configuration. If not selected, a new configuration will be created by default")
    不选等于新建 = 翻译("你没有选择任何视图配置,因此将会新建配置","You have not selected any view configuration, so a new configuration will be created")
if __name__ == "__main__":
    print(Translate.打开配置表)