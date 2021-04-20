# 注意:修改完配置刷新或重开一下
    
    
## V0.7新增
    
### anchorCSSFileName:
- 这是一个控制锚点样式的代码,如果user_files里不存在这个文件,那么程序会读取根目录下的anchorCSS.txt内的样式
- 如果你想修改CSS样式,请从hjp-bilink的根目录复制一个anchorCSS.txt,到user_files目录下粘贴,然后再根据文件内的要求,修改其中的css代码.
- 改完后再将文件更改成自己需要的名字,也就是这里anchorCSSFileName所指定的名字
### button_appendTo_AnchorId:
- 程序会在最终卡片的HTML渲染中,搜索id等于这个字段值的元素,并把链接按钮作为他的子元素插入,你可以在卡片模板中添加一个以这个字段值为id 的div， 他就会加到这里去。
- 如果找不到,那么程序就会创建一个div,id等于这个字段值,并插入到卡片最开始的位置。

---
### 默认操作模式编号
  0-完全图,1-组到组,2-按结点取消,3-按路径取消,4-直接插入,5-清空后插入,6-编组插入
### defaultLinkMode:
用来定义默认的链接模式, 0 代表 完全图链接, 1,代表组到组链接,他会影响 
### shortcut_browserTableSelected_link,
对应的快捷键所执行的操作
### defaultUnlinkMode:
用来定义默认的取消链接模式, 其中的数字2,代表按节点取消链接, 3,代表按路径取消链接, 
### defaultInsertMode:
用来定义插入input的模式,其中的数字 4代表直接插入input, 5代表清空后再插入input, 6代表编组插入

---
## 杂项
### appendNoteFieldPosition:
用来定义在卡片的第几个字段插入链接按钮. 默认为0 ,也就是第一个字段.
### readDescFieldPosition：
用来定义在卡片的第几个字段读取卡片描述. 默认为0, 
### descMaxLength:
用来限制读取的卡片描述字符最大长度, 如果为0, 表示不限制, 默认是32, 表示32个字.
### linkFromSymbol,linkToSymbol
是一对标记, 分别表示链过来的卡片和链过去的卡片, 默认是向左向右箭头, 
### linkStyle
在其中可填写CSS代码,用来控制按钮的样式, 默认为空, 如果你会CSS,可以自定义样式.
### addTagEnable
表示是否开启 在一次链接操作中,给所有卡片加标签的功能, 默认为1, 表示开启, 其他表示关闭.
### addTagRoot
表示多级标签中, 根标签的名字, 默认是插件名.

---
## 快捷键(此参数已经遗弃)
### shortcut_browserTableSelected_link
定义了默认链接快捷键
### shortcut_browserTableSelected_unlink
定义了默认取消链接快捷键
### shortcut_browserTableSelected_insert
定义了默认插入快捷键
### shortcut_inputFile_clear
定义了默认清空input的快捷键
### shortcut_inputDialog_open
定义了默认打开 input 的快捷键