



 `V0.7`新增
 
"button_appendTo_AnchorId":"hjp_bilink_button",程序会在最终卡片的HTML渲染中,搜索id等于这个字符串的元素,并把链接按钮作为他的子元素插入, 如果找不到,那么就会把按钮插入到卡片HTML文字的头部.

VERSION:"0.7", 用来标记配置表版本是否落后,从而从 config_template.json加载新的配置项.

---

0-完全图,1-组到组,
2-按结点取消,3-按路径取消,
4-直接插入,5-清空后插入,6-编组插入



"defaultLinkMode": 1, 用来定义默认的链接模式,  0 代表 完全图链接, 1,代表组到组链接,他会影响 shortcut browser Table Selected link, 对应的快捷键所执行的操作

"defaultUnlinkMode": 2, 用来定义默认的取消链接模式, 其中的数字2,代表按节点取消链接, 3,代表按路径取消链接, 

"defaultInsertMode": 4, 用来定义插入input的模式,其中的数字 4代表直接插入input, 5代表清空后再插入input, 6代表编组插入

"appendNoteFieldPosition": 0,用来定义在卡片的第几个字段插入链接按钮. 默认为0 ,也就是第一个字段.

"readDescFieldPosition": 0,用来定义在卡片的第几个字段读取卡片描述. 默认为0, 

"descMaxLength": 0,用来限制读取的卡片描述字符最大长度, 默认为0, 表示不限制.

"linkFromSymbol": "←",是一对标记, 分别表示链过来的卡片和链过去的卡片, 默认是向左向右箭头, 

"linkToSymbol": "→",是一对标记, 分别表示链过来的卡片和链过去的卡片, 默认是向左向右箭头, 

"linkStyle": "",在其中可填写CSS代码,用来控制按钮的样式, 默认为空, 如果你会CSS,可以自定义样式.

"addTagEnable": 1,表示是否开启 在一次链接操作中,给所有卡片加标签的功能, 默认为1, 表示开启, 其他表示关闭.

"addTagRoot": "hjp-bilink",表示多级标签中, 根标签的名字, 默认是插件名.

"shortcut_browserTableSelected_link": "Alt+1", 定义了链接快捷键

"shortcut_browserTableSelected_unlink": "Alt+2",定义了取消链接快捷键

"shortcut_browserTableSelected_insert": "Alt+3",定义了插入快捷键

"shortcut_inputFile_clear": "Alt+4",定义了清空input的快捷键

"shortcut_inputDialog_open": "Alt+`"定义了打开 input 的快捷键