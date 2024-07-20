# 一、简介

一个可以让你轻松下载bilibili上视频的项目，你只需要在窗口内输入链接（还有cookie），就可以下载高清视频。

你也可以将文件当作库导入到你的项目里，调用函数就能进行处理。你还可以定制步骤，自定义参数，将流程掌握在自己手中。

供遇到视频失效等需要缓存视频的朋友

不要做坏事，**不欢迎盗视频的人**！不能拿去赚钱。搬运**请附上作者名和[链接](https://github.com/MCIOXZ/getBilibili/)**！**盗视频没母亲**

## 二、文件解释

| 文件名                | 文件作用                     |
| --------------------- | ---------------------------- |
| bilibili.py           | 主程序                       |
| bilibili_setCookie.py | 处理cookie中的特殊字符       |
| import-example.py     | 演示文件，基本囊括了可用选项 |
| import-bilibili.py    | 简陋的测试文件               |

## 三 使用方法

### 普通使用

1.下载[本项目](https://github.com/MCIOXZ/getBilibili/)

2.检查依赖（见**四**）

3.(可选) 修改`bilibili.py`文件内的配置

4.运行`bilibili.py` _(python bilibili.py)_ 程序，根据指引操作。

### 当作库导入

1.[下载](https://github.com/MCIOXZ/getBilibili/)本项目

2.检查依赖（见**四**）

3.在你的项目中写入

```python
import bilibili             #导入库
```

4.(可选)使用`bilibili.{配置}=xxx`来更改配置，可更改的配置见`bilibili.py`文件头部

5.配置更改完后执行

```python
bilibili.start()            #初始化库
```

6.你可以调用`bilibili.py`内的函数来处理链接与文件了，函数列表见**五**

## 四、依赖

ps:大部分为python基础库

| 库名                   | 作用                                   |
| ---------------------- | -------------------------------------- |
| requests               | 请求页面，下载文件                     |
| re                     | 使用正则表达式匹配html文件内的json内容 |
| json                   | 将json字符串转为python字典             |
| sys                    | 获取运行路径                           |
| os                     | 处理文件与路径                         |
| random                 | 输出日志前生成随机session              |
| atexit                 | 退出时关闭日志文件                     |
| datetime               | 获取日期与时间                         |
| urllib.parse           | 去除url跟踪参数，补全请求路径          |
| html.parser            | 解析html文件，读取视频标题             |
| subprocess(可选)       | 运行ffmpeg合并音视频                   |
| emoji(可选)            | 去除视频标题中的emoji                  |
| tqdm(在普通使用时导入) | 输出下载进度条                         |

## 五、函数/类列表

| 函数/类名                           | 参数/继承                                                                                                                                                                                                                                          | 作用                  |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- |
| start                               | -                                                                                                                                                                                                                                                  | 初始化库              |
| printlog(类)                        | -                                                                                                                                                                                                                                                  | **管理**日志          |
| printlog>\__init_ \_                | `self`:无,`filename`:日志文件名,`Header`:日志格式                                                                                                                                                                                                  | 初始化日志            |
| printlog>log                        | `self`:无,`word`:日志内容,`header`:日志格式(默认为self.Header),`endv`:日志结束换行符(默认为\n)                                                                                                                                                     | **输出**日志          |
| printlog>delog                      | `self`:无,`ycontinue`:是否确认(!**这个选项为"y"时这个函数才会工作**)                                                                                                                                                                               | **删除**日志文件      |
| printlog>closeLogFile               | `self`:无                                                                                                                                                                                                                                          | 关闭日志文件          |
| printlog>close                      | `self`:无                                                                                                                                                                                                                                          | 本次运行不再记录日志  |
| HTMLDomTree(类)                     | HTMLParser                                                                                                                                                                                                                                         | 从html中寻找title标签 |
| fullwidth_to_halfwidth              | `s`:需要转换的字符串                                                                                                                                                                                                                               | 全角字符串转半角      |
| removeEmoji                         | `text`:需要移除emoji的文字 (!**需要安装emoji库**)                                                                                                                                                                                                  | 移除字符串中的emoji   |
| downloadHtml                        | `url`:需要下载的页面的链接,`path`:html文件保存路径,`headers`:http请求头                                                                                                                                                                            | 下载html页面          |
| getInfoJson                         | `htmlPage`:html页面字符串,`path`:解析出的json文件保存路径                                                                                                                                                                                          | 获取json地址信息      |
| getInfoTitle                        | `htmlPage`:html页面字符串                                                                                                                                                                                                                          | 提取视频标题          |
| getClarityList                      | `videoInfo`:json格式的视频地址信息,`way`:获取的方法，有效值"1","2"                                                                                                                                                                                 | 从json中提取分辨率    |
| getAudioInfo                        | `data`:json格式的视频地址信息                                                                                                                                                                                                                      | 获取音频链接          |
| runcodeNoneClass(类)                | -                                                                                                                                                                                                                                                  | 在下载时插入代码运行  |
| runcodeNoneClass>\__init_ \_        | `self`:无                                                                                                                                                                                                                                          | -                     |
| runcodeNoneClass>AfterOpenFile      | **1.**`self`:无,**2.**`localsA`:一个字典，格式{"变量/object名":"值"}。                                                                                                                                                                             | 打开文件后运行的代码  |
| runcodeNoneClass>AfterCreateConnect | `接上条`有调用时父函数内所有变量(等)的值，包括循环内的变量，只读,                                                                                                                                                                                  | 创建连接后运行的代码  |
| runcodeNoneClass>beforeDownloadFile | `接上条`**3.**`changeStorage`:在函数内有名为storage的字典，                                                                                                                                                                                        | 在下载前运行的代码    |
| runcodeNoneClass>onDownloadingFiles | `接上条`调用此函数修改字典，格式changeStorage(键，值)。                                                                                                                                                                                            | 下载时循环运行的代码  |
| runcodeNoneClass>onEnd              | `接上条`是（也是唯一的）存储 调用此类中函数时产生的临时数据 的地方。                                                                                                                                                                               | 下载结束后运行的代码  |
| downloadFile                        | **1.**`fileType`:文件类型,video,audio,**2.**`Url`:下载地址,**3.**`path`:保存路径,**4.**`saveName`:保存的文件名(前面path也要加),**5.**`headers`:http请求头(默认为变量headers),**6.**`runcodeObj`:下载时插入的代码,**7.**`downSize`:一次性下载的字节 | 下载音视频            |
| mergeAudioAndVideo                  | **1.**`videoFilePath`:视频路径,**2.**`audioFilePath`:音频路径,**3.**`outputFilePath`:输出路径,**4.**`ffmpegRunFile`:ffmpeg可执行文件路径(默认为ffmpegPath),**5.**`otherOptions`其他参数(默认为""),**6.**`encoding`:终端命令编码方式(默认为'utf-8') | 合并音视频            |
| debugMode                           | -                                                                                                                                                                                                                                                  | debug模式             |

#### 开源协议

Mozilla Public License 2.0

[made by klpyx(github:MCIOXZ)](https://github.com/MCIOXZ/getBilibili/)
