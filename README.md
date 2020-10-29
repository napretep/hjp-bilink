[toc]
(本段上面有toc,不支持toc的markdown解析器请点下方链接跳转)
- [使用介绍](#1) |[更新记录](#2)|[未来计划](#3)|[安装教程](#4)|[配置教程](#5)

<a name="1"></a>
# hjp-bilink使用介绍
- ![0nlpjS.jpg](https://s1.ax1x.com/2020/09/30/0nlpjS.jpg)
- 本插件实现在anki上简易的手动双向绑定.
- 依赖的第三方插件代码 `1423933177`它提供了核心的卡片单向链接功能,
- 还有依赖插件`564851917(可选)` ,它提供了层级标签功能,这不是必须的,但有更好.
- 本插件将单向链接自动化实现链过去的同时又链回来,并且提供两种链接算法.
- 其他功能:修改连接样式,连接集体加tag,取消连接,可修改连接前缀,可定制连接描述
- 讨论QQ群:891730352
- 插件版本:0.2.1
- [插件地址](https://gitee.com/huangjipan/hjp-bilink)
- ## 提醒:
    - 本插件只适用于windows和桌面linux系统,不适用于mac系统,安卓手机,iphone,ipad等移动端

<a name="2"></a>
## 更新记录
### 0.3
- 新增
    - 新增集体加tag功能,你可以在`input.json>addTag`添加你喜欢的tag名,这样建立连接后,会给连接中的卡片集体添加`hjp-bilink::yourtagname`这样方便你从全局角度查看同一连接的全部成员.
    - [![B8c73n.gif](https://s1.ax1x.com/2020/10/29/B8c73n.gif)](https://imgchr.com/i/B8c73n)
    - 如果你没有输入tag名,那么插件会选择插入时间戳形式的tag:`hjp-bilink::YYYYMMDDHHMMSS`,
    - 这个tag默认是开启的,你可以在`config.json>addTagEnable`中关闭它(0关闭,1开启)
    - 没有提供取消tag功能,一是因为我还没想好合适的算法,二是因为批量取消tag的操作比较容易实现,不用插件也能做到,不排除将来会增加取消tag的功能.
    - 推荐安装层级标签插件`564851917`来管理标签,因为随着标签的增多如果不能层级折叠一定会越来越臃肿难看.
- 优化
    - 改进了菜单描述,现在`clear`菜单改名为`initInput`
### 0.2.2
- 优化
    - 现在`input.json`中的卡片ID可以统一处理,不再区分group或pair,每个pair都是单一的group,使用者不必在group或pair中反复横跳.
    - 现在`input.json`中的card_id在完全连接时是唯一的(尽管不唯一也不会造成重复).
    - 除非出现错误,大部分命令提示不再弹出窗口, 改为左下角静音提示.
- 新增
    - 增加style接口,你现在可以自定义链接的div样式.默认样式为空.
    - 退出时清空`input.json`
    - 增加可修改的链入和链出标记.

### 0.2.1
- 修复了一个愚蠢的错误

### 0.2
- 新增unlink取消链接，算法也是两种
- txt文本改为JSON数据,增加了易用性

### 0.1.1
- 修复了一些bug,比如重复插入卡片id

### 0.1
- 为了方便切换不同的链接模式,现在把两个模式直接拿到菜单中可点击了.
- 实现可修改前缀,网络化发布
<a name="3"></a>
## 未来计划
### 近期
- [ ] 增加提取tag内容和deck内容作为描述符的正则
- [ ] 实现各种方案转为tag(deck路径转tag,卡片内容转tag)
- [ ] 实现答题日志系统(点击显示答案后的任意一个按钮都会弹出是否记录日志的问号,选择是就会记录当前的文本到指定的位置.)
- [ ] 在复习,预览和编辑界面,显示右键添加到input.json(这个特别难)
### 长期
- [ ] 实现UI界面(抛弃丑陋的txt文本编辑,减少用户犯错几率)
- [ ] 利用sqlite3,实现链接信息的外部存储,方便维护,比如链接的同步更新,实时加载(可选)
    - 将来hjp-bilink会改为用外部存储anki卡片的链接关系,不会修改卡片内容,
    - 到时候是,打开一个卡片预览,会提供一个扩展按钮,点击后弹出linklist,
    - 连接关系独立出来做的好处是,将来修改link对应的desc可以同步更新到每一张被链接的卡片上.
### 已完成
- [x] 提供链接的html元素的样式修改接口
- [x] 实现input.json文件中card_id的唯一化.
- [x] 代码转移到gitee
- [x] 实现unlink功能(若选中的卡片存在link关系,则删除这个link)
- [x] 为了方便操作,将来会将卡片ID存储的txt文本改为json数据({id:,desc:})

<a name="4"></a>
## 插件的安装
### 依赖插件`link Cards`的安装
到`工具>附加组件>获取插件`输入`1423933177`,`564851917`  即可安装依赖插件

### `hjp-bilink`的安装
下载克隆这个插件仓库到本地,把文件夹`hjp-bilink`复制到anki的插件文件夹下,这个位置在windows上一般是`C:\Users\Administrator\AppData\Roaming\Anki2\addons21`
如果不知道插件文件夹在哪里,打开anki的`工具>附加组件>查看文件`也可以打开
装完以后记得重启anki

## 使用教程
目前这个工具用起来还是有一点繁琐的,将来会加入对话框功能,简化操作.
1. ### 打开`browser`
    - 就是在主界面点击`浏览/browse`弹出的那个窗口
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034448_bbf2a1fc_332584.png "屏幕截图.png")
2. ### 选取卡片记录插入`input.json`
    - 在`browser`窗口中选中几条你要双链的记录，在任何一条被选中的记录上点击鼠标右键，弹出上下文菜单，其中有
        - `hjpCopyCidAlltoInputJson`，
        - `hjpAsGroupCopytoInputJson`两个选项
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034558_0ef8a51b_332584.png "屏幕截图.png")
    - 根据模式不同,选择不同的选项
        1. 当你需要使用以下三种模式

            1 **`linkall`完全链接模式**, 

            2 **`unlinkNode`按结点取消链接模式** , 

            3 **`unlinkPath`按路径取消链接模式** 时

            - 选择`hjpCopyCidAlltoInputJson`,就能把你选的这几条记录的`card_id`插入到`input.json`中
            - 你可以反复执行这个过程,把所有需要的卡片ID都录入到`input.json`中
        2. 当你需要使用 **`linkGroupToGroup` 按组链接模式** 时
            - 选择`hjpAsGroupCopytoInputJson`,把所有选中的记录作为一个组录入到`input.json`中,
            - 注意 组链接至少需要两个组才能正常工作
            - 你执行`hjpAsGroupCopytoInputJson`就是把选中的卡片编一个组插入到`input.json`中,所以想要实现链接到其他组,还得插入另一个编组.
            - 实际上你也可以对非编组的ID使用`linkGroupToGroup`,目前新增功能可实现每个卡片默认是一个组.
3. ### (如果需要)打开`input.json`编辑卡片ID和描述desc,
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/035618_5e0cbe98_332584.png "屏幕截图.png")
    - 在你把想双链的卡的id都插入到这个`input.json`中后,你可以点击菜单栏上的`hjp_link>show`打开`input.json`
    - `input.json`里面都是你在第二步操作中输入的`card_id`还有程序默认提取的描述`desc`,你这时候可以修改默认的描述内容,你也可以不追加解释,走下一步操作.
    - ![0Rd6yj.png](https://s1.ax1x.com/2020/10/12/0Rd6yj.png)
4. ### 建立双向连接
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034730_38b2b795_332584.png "屏幕截图.png")
    - 选择`hjp_link>linkDefault`就会根据预先在`config.json>linkMode`中配置好的链接算法,自动建立双向连接
    - 不过,如果你想使用其他模式,也可以直接点击其他模式,因为我们会经常切换加链接的方式,所以我把这些模式单列了出来:
        - 选择`hjp_link>linkAll`调用完全图算法链接每个记录，将`input.json>IdDescPairs`中的每一张卡双向连接到每一张卡,比如输入ABC,那么A中有BC,B中有AC,C中有BA的ID链接.
        - 选择`hjp_link>linkGroupToGroup`调用组链接算法链接各个组的记录.在`input.json>IdDescGroups`中会分成几个组,前一个组的每一张卡双向连接到后一个组的每一张卡.比如ABC是一个组，DEF是一个组，那么组间链接就是第一组：A到DEF,B到DEF,C到DEF，第二组：D到ABC，E到ABC,F到ABC。
        - 选择`hjp_link>unlinkNode`调用取消结点链接算法,相当于将`input.json>IdDescPairs`中列出的每个节点孤立，比如`input.json>IdDescPairs`中有节点A，那么程序会查询A卡片，并发现A连接到BCD，那么就会解除到BCD的链接，并且反向解除BCD到A的链接。
        - 选择`hjp_link>unlinkPath`调用取消路径链接算法,相当于将`input.json>IdDescPairs`中的彼此相连的节点按顺序解除绑定，比如输入`input.json>IdDescPairs`中的ABCD是彼此有链接的节点，那么程序就会从A节点开始，从A到B解除链接，B到C解除链接以此类推，但是不会解除A到其他结点的链接,比如A连接到BCD,但是你输入`input.json>IdDescPairs`的顺序是ABCD,那么A只会解除从A到B的链接,A到CD的链接保持不动。
    
5. ### (如果需要)清除json中的记录
    - 选择`hjp_link`->`clear`就能删掉之前的全部记录.
    -  **如果不熟悉json的语法,千万别自己删json的结构,最好用clear清除记录,不容易破坏json结构,否则会频繁报错.** 
    - 如果你熟悉json的语法,以上操作也可以打开`input.json`手工完成录入.
    - ![输入图片说明](https://images.gitee.com/uploads/images/2020/1013/034926_1c9e8e3d_332584.png "屏幕截图.png")
<a name="5"></a>
## 配置指导
配置文件名为`config.json`,可以在ANKI插件页面做修改,也可以通过`hjp_link->config`打开,可修改的值有
1. ### `linkMode` (重点必看)
    - `linkMode`影响默认的链接多张卡片的算法,就是你点击`hjp_link>linkDefault`时会调用的算法,值为0或1,2,3,默认为0.
    - 0表示完全链接`linkAll`
    - 1表示按组链接`linkGroupToGroup`
    - 2表示按结点取消链接`unlinknode`
    - 3表示按路径取消链接`unlinkpath`
4. ### `cidPrefix`
    - 表示每个卡ID的默认前缀,用于让依赖的link插件识别这是可点的链接，默认是依赖插件的默认配置即`cidd`,可以清空,请注意标识符在txt中的含义必须是唯一确定的,不能在插入的正文中使用标识符.
5. ### `appendNoteFieldPosition`
    - 这个属性控制双链的标记插入到anki卡片的第几个字段,取值从0开始,所以第一个字段为0,默认为0,第一个字段通常是问题描述,也就是卡片的正面,那么双链就会插入到正面的末尾.
6. ### `readDescFieldPosition`
    - 这个属性控制程序默认从卡片的第几个字段提取卡片描述的字符，数据类型为number,默认为0,也就是提取问题描述中的前面10个非标点类字符.
7. ### `regexForDescContent`
    - 这个属性控制程序从卡片提取描述字符的方法，默认为0的话，会调用`DEFAULT>regexForDescContent`中的正则表达式来提取描述字符.如果你想按自己的正则表达式提取描述字符,可以改外层的`regexForDescContent`的值.
0. ### `regexForDescFromDeck`(未完成)
0. ### `descMaxLength`(未完成)
0. ### `linkFromSymbol`,`linkToSymbol`
    - 这两个属性,一个控制链入的符号,另一个控制链出的符号. 默认是`"←"`和`"→"`,如果不需要,可以设为`""`值
    - 效果比如这个图
    - 完全图算法全是链出符号,只有组链接算法有链入符号.
0. ### `linkStyle` 
    - 控制link所在的div元素的样式,默认是空字符串,即没有样式,你可以按照CSS的写法填入样式,不过注意JSON格式的回车换行问题.
0. ### `addTagEnable` ,`addTagRoot`**新增**
    - 前者控制是否开启集体加标签功能默认值是1,表示开启,可选0,表示关闭,后者给所有的标签增加一个根节点,
    - 比如你在`input.json`输入的tag 是`abc`,`addTagRoot`的值为`hjp-bilink`,那么真正插入anki的tag显示为`hjp-bilink::abc`
    - 如果你安装了前文推荐的层级tag,你还可以继续在自己的tag上输入`::def`实现层级折叠.
    
## 动画指导 
- 单向链接的使用
- ![0n1jQf.gif](https://s1.ax1x.com/2020/09/30/0n1jQf.gif)
- 双向链接的设置
- ![0n3JOO.gif](https://s1.ax1x.com/2020/09/30/0n3JOO.gif)


