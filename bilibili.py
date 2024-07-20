# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
'''
爬取bilibili视频
made by klpyx
open-source license:MP2.0(Mozilla Public License)
'''
import requests #请求页面，下载文件
import re #正则表达式匹配json内容
import json #json字符串转字典
import sys #获取运行的路径
import time #在下载文件后延迟等待
import os #拼接目录
import random #输出日志时生成ssession id
import atexit #用于在退出时关闭日志文件
import datetime #获取日期，时间
from urllib.parse import urlparse, urlunparse #解析url（去除追踪参数，在路径后添加/）
from html.parser import HTMLParser #解析html文件，读取title

#自定义请求头请在调用需要请求头（headers）的函数时传入
#更改以下配置以自定义设置


self_defaultHeader="[{time} |{session}|] {things}{endv}" #日志格式 不建议修改此项
openLog=True #是否开启日志，默认为True。所有printlog类初始化的对象的默认值。
RegularforVideoInfo=r"(?<=>window.__playinfo__=).*?(?=<\/script>)" #从html中过滤出视频信息的正则表达式 不建议修改
downSpeed=1024*1024*5 #用于设置downloadFile函数下载文件的速度。默认5MB(40mbps),视频下载速度为这个速度*2，1024是1KB,1024*1024是1MB,默认为5MB。
ffmpegPath="" #若使用到ffmpeg,请在此处填入ffmpeg可执行文件的完整路径 包括文件名后缀。
createMainDir=True #是否自动创建savePath指明的文件路径
mergeAudioVideo=False #是否需要合并音视频，若要合并请设置为True并安装ffmpeg。
#在当作库导入和普通运行时生效
#------------------------------------------------------------------
#仅在普通运行时生效（因为在当作库导入时没有像普通运行时配置参数，以下参数均可在函数调用时调整）
savePath=os.path.join(sys.path[0],"bilibiliP") #产生的文件的路径(文件夹)
localHtmlPath=os.path.join(savePath,'bilibili_localhtml.html') #从本地读取html文件的路径
htmlSavePath=os.path.join(savePath,"bilibili_html.html") #html文件保存的路径
jsonSavePath=os.path.join(savePath,"bilibili_js.json") #json文件保存的路径
downFileSavePath=os.path.join(savePath,"download") #下载的音视频文件保存路径
removeEmojis=False #如果你的文件系统不支持Emoji，请设置为True并安装emoji库。
# m4sTOmp43=False #是否自动将m4s转换为mp4/3，若要转换请设置为True并安装ffmpeg和对应的python库。
#请在下面放上你登录bilibili后的cookie
bCookie=""

#设置请求头
headers={
    "Cookie": bCookie,
    'Origin': 'https://www.bilibili.com',
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/121.0.0.0",
    'Accept': '*/*',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    "referer": "https://message.bilibili.com/",
    'Accept-Encoding': 'identity',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

#下面非专业不建议修改

def start(): #初始 化 文件
    global savePath,FLog,closeLogFile,bCookie,headers,random,atexit,subprocess
    # if openLog:
    if mergeAudioVideo:
        import subprocess #引用运行shell代码的库
    #创建文件夹
    if createMainDir:
        if not os.path.exists(savePath):
            os.mkdir(savePath)
    #注册日志类
    FLog=printlog("bilibili.log",self_defaultHeader)
    @atexit.register #装饰器函数会在程序结束时运行
    def closeLogFile():
        if FLog.openLog:
            FLog.closeLogFile()
            print(f'日志保存在{os.path.join(savePath,"bilibili.log")}，下载bilibili库 by klpyx.')



class printlog(): #输出日志
    def __init__(self,filename,Header):
        RandomList="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.@~-,:*?!_#/=+&^;%$<>'`´\""
        self.path=os.path.join(savePath,filename)
        self.Header=Header
        #检查存放目录
        if not os.path.exists(savePath):
            FLog.log("Error printlog(class->__init__): 存放日志文件的目录不存在！请将createMainDir设为True或手动创建文件夹。关闭日志请将openLog设为False。")
            print("Error printlog(class->__init__): 存放日志文件的目录不存在！请将createMainDir设为True或手动创建文件夹。关闭日志请将openLog设为False。")
        self.openLog=openLog
        #创建文件
        if not os.path.exists(self.path):
            self.logFile=open(self.path,"w",encoding='utf-8')
            self.logFile.close()
        self.logFile=open(self.path,"a+",encoding='utf-8')
        #随机生成session id
        self.SessionId=''.join(random.choices(RandomList, k=16))
    def log(self,word,header=None,endv="\n"): #记录日志
        if self.openLog:
            Realheader=self.Header if header==None else header
            self.logFile.write(Realheader.format(time=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()),session=self.SessionId,things=word,endv=endv))
    def delog(self,ycontinue): #删除日志
        if ycontinue!="y":
            FLog.log("class:printlog.delog异常：调用self.delog()时需传入'y'以确定删除")
            print("class:printlog.delog异常：调用self.delog()时需传入'y'以确定删除")
            return
        os.remove(self.path)
        self.close()
    def closeLogFile(self): #关闭日志文件
        self.logFile.close()
        self.close()
    def close(self):
        self.openLog=False

class HTMLDomTree(HTMLParser): #从html文件中解析内容 (ai写的，赞美gpt)
  def __init__(self):
    super().__init__()
    self.in_title = False
    self.title = ""
  def handle_starttag(self, tag, attrs):
    if tag == "title":
      self.in_title = True
  def handle_endtag(self, tag):
    if tag == "title":
      self.in_title = False
  def handle_data(self, data):
    if self.in_title:
      self.title += data

def fullwidth_to_halfwidth(s): #字符串中所有全角字符转换成半角字符（也是ai写的）
    result = []
    for char in s:
        code_point = ord(char)
        # Convert fullwidth characters to halfwidth
        if 0xFF01 <= code_point <= 0xFF5E:
            result.append(chr(code_point - 0xFEE0))
        # Convert fullwidth space to halfwidth space
        elif code_point == 0x3000:
            result.append(chr(0x0020))
        else:
            result.append(char)
    return ''.join(result)

def removeEmoji(text): #移除字符串中所有emoji
    try:
        import emoji # type: ignore 此注释让vscode忽略本行Warning
        return emoji.replace_emoji(text, replace='')
    except ImportError:
        FLog.log("Error: emoji module is not installed. Try install it or set removeEmojis to False")
        print("Error: emoji module is not installed. Try install it or set removeEmojis to False")
        return text

# def login(): #画大饼：密码登录和扫码登录，网页操作界面，批量下载

def downloadHtml(url,path,headers=headers): #下载html页面
    requestToGetHtml=requests.get(url,headers=headers) #请求页面
    htmlPage=requestToGetHtml.text #处理页面
    if path!="" or path!=None:
        with open(path,"w",encoding='utf-8') as f2: #保存html页面
            f2.write(htmlPage)
    return htmlPage

def getInfoJson(htmlPage,path): #获取视频信息，从html文件中筛选
    videoInfoStr=re.findall(RegularforVideoInfo,htmlPage)[0]
    if path!="" or path!=None:
        with open(path,"w",encoding='utf-8') as f2:
            f2.write(str(videoInfoStr))
    videoInfo=json.loads(videoInfoStr) #字符串转json
    return videoInfo

def getInfoTitle(htmlPage): #提取视频标题，从html页面中
    parser = HTMLDomTree() #创建树
    parser.feed(htmlPage)  #加载html文件
    if parser.title: #找到/没找到
        return parser.title.replace("_哔哩哔哩_bilibili","") #返回标题
    else:
        #返回e.g. (404,"20991230013027-未找到title标签")
        return str((404,f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-未找到title标签"))

def getClarityList(videoInfo,way): #选择视频分辨率
  if way=="1": #从data/dash/video读取
    sourceUrlList=videoInfo["data"]["dash"]["video"] #所有清晰度的列表
    clarityList={} #视频分辨率对应url列表
    #筛选分辨率
    for sourceClarityList in sourceUrlList:
        widthAndHeight=str(sourceClarityList["height"])+"P"
        #处理重复的值
        if widthAndHeight in list(clarityList.values()):
            widthAndHeight+=f"({str(clarityList.count(widthAndHeight))})" #count: 元素在列表中出现的次数
        clarityList[widthAndHeight]=sourceClarityList["baseUrl"]
  elif way=="2": #从data/support_formats读取支持的分辨率并拼接url 已失效
    clarityList={} #视频分辨率对应url列表
    clarityIdList={}
    原视频后缀=".m4s"
    sourceClarityList=videoInfo["data"]["support_formats"] #视频支持的清晰度的列表
    baseUrl=videoInfo["data"]["dash"]["video"][0]["baseUrl"] #用来拼接的url
    #处理链接
    baseUrlSplit=baseUrl.split(原视频后缀)
    if len(baseUrlSplit) !=2:
      FLog.log(f"Error getClarityList:原视频链接中不存在'{原视频后缀}'后缀或存在'{原视频后缀}'的数量大于1")
      print(f"Error getClarityList:原视频链接中不存在'{原视频后缀}'后缀或存在'{原视频后缀}'的数量大于1")
      exit(1)
    baseUrlSplit[0]=baseUrlSplit[0][0:-3]
    #处理支持的分辨率
    for sourceClarityEvery in sourceClarityList: #sourceClarityEvery是每种分辨率的object
      clarityIdList[sourceClarityEvery["display_desc"]]=str(sourceClarityEvery["quality"])
      #补位
      if len(clarityIdList[sourceClarityEvery["display_desc"]])<3:
        clarityIdList[sourceClarityEvery["display_desc"]]="0"*(3-len(clarityIdList[sourceClarityEvery["display_desc"]]))+clarityIdList[sourceClarityEvery["display_desc"]]
    #处理id对应的链接
    for sourceClarityKeyEvery in clarityIdList.keys(): #sourceClarityKeyEvery是筛选过的每种分辨率的object的键
      clarityUrlIdEvery=clarityIdList[sourceClarityKeyEvery] #每个分辨率的id
      clarityUrlEvery="".join((baseUrlSplit[0],str(clarityUrlIdEvery),原视频后缀,baseUrlSplit[1])) #每个分辨率的链接
      clarityList[sourceClarityKeyEvery]=clarityUrlEvery
    #done
  else:
    FLog.log("Error getClarityList:未知选项。")
    print("Error getClarityList:未知选项。")
    exit(1)
  return clarityList

def getAudioInfo(data): #获取音频下载地址
    AudioList=data["data"]["dash"]["audio"]
    AudioLink={}
    for temp in AudioList:
       AudioLink[temp["bandwidth"]]=temp["baseUrl"]
    return AudioLink #返回音频带宽对应下载链接的object

class runcodeNoneClass: #空类，是downloadFile函数参数runcodeObj的默认值，用于在函数运行时插入代码运行，支持五个位置。
    def __init__(self): #不需要填
        return
    def AfterOpenFile(self,localsA,changeStorage): #必接收3个选项 1.self:调用runcodeObj()时用。 
        return
    def AfterCreateConnect(self,localsA,changeStorage): #2.localsA:一个字典，格式{"变量/object名":"值"}。调用时父函数内所有变量(等)的值，包括循环内的变量，只读。
        return
    def beforeDownloadFile(self,localsA,changeStorage): #3.changeStorage:在函数内有名为storage的字典，调用此函数修改字典，格式changeStorage(键，值)。是（也是唯一的）存储 调用此类中函数时产生的临时数据 的地方。
        return
    def onDownloadingFiles(self,localsA,changeStorage):
        return
    def onEnd(self,localsA,changeStorage):
        return

def downloadFile(fileType,Url,path,saveName,headers=headers,runcodeObj=runcodeNoneClass,downSize=downSpeed):#下载视频 downSize是一次性下载多少字节(就是downSpeed)
    #通过传入带有自定义功能的runcodeObj类实现print和进度条
    #你也可以直接将此文件导入成库来调用现成的函数，不会有任何print的文字干扰你程序的运行(除了报错)。(虽然根本没适配就是了)
    storage={} #runcodeObj类存储的地方（也是唯一的），提供了changeStorage函数供修改
    def changeStorage(key,value): #修改storage的内容
       nonlocal storage
       storage[key]=value
    FileA=open(path,"wb") #打开文件
    runcodeObj().AfterOpenFile(locals(),changeStorage) #执行插入代码
    Res=requests.get(url=Url,headers=headers,stream=True) #建立连接,stream=True是以流式下载
    runcodeObj().AfterCreateConnect(locals(),changeStorage)
    FileSize=int(Res.headers["content-length"]) #文件大小
    runcodeObj().beforeDownloadFile(locals(),changeStorage)
    #下载文件
    for data in Res.iter_content(chunk_size=downSize):
        FileA.write(data) #分段保存
        runcodeObj().onDownloadingFiles(locals(),changeStorage)
    time.sleep(0.5)
    runcodeObj().onEnd(locals(),changeStorage)
    FileA.close() #关闭文件
    Res.close() #关闭连接
    time.sleep(1)
    return {"type":"OK","fileType":fileType,"states":Res.status_code,"url":Url,"path":path}

def mergeAudioAndVideo(videoFilePath,audioFilePath,outputFilePath,ffmpegRunFile=ffmpegPath,otherOptions="",encoding='utf-8'): #合并音视频，输出文件名后缀必须是ffmpeg支持的（例如mp4）,encoding是与终端交互用的编码，建议utf-8
    if not mergeAudioVideo:
        FLog.log("Error mergeAudioAndVideo:在调用mergeAudioAndVideo函数前请先设置mergeAudioVideo为True")
        print("Error mergeAudioAndVideo:在调用mergeAudioAndVideo函数前请先设置mergeAudioVideo为True")
        return
    Command=f"{ffmpegRunFile} -i {videoFilePath} -i {audioFilePath} {otherOptions} -acodec copy -vcodec copy {outputFilePath}" #组成命令
    runCommmand=subprocess.run(Command,shell=True,stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,text=True,encoding=encoding) # type: ignore #使vscode忽略
    printCommand=str(runCommmand.stdout)+str(runCommmand.stderr) #提取输出
    FLog.log({"ffmpegPrint":printCommand,"path":outputFilePath})
    if runCommmand.returncode==0: #subprocess.run的returncode==0代表正常结束
        return {"type":"OK","ffmpegPrint":printCommand,"path":outputFilePath}
    else:
        return {"type":"Error","returncode":runCommmand.returncode,"ffmpegPrint":printCommand,"path":outputFilePath}

def debugMode(): #debug模式）
  print("DEBUGING")
  NOEND=True
  while NOEND:
      NOEND=True
      De=input("> ")
      if "python:" in De:
          DCom=De.split(":")
          if DCom[0] == "python":
              DECom=":"
              DECom=DECom.join((DCom[1:]))
              print("python命令:  ",DECom)
              try:
                  exec(DECom)
              except Exception as Err:
                  print("此语句发生了以下错误: \n",str(sys.exc_info()[0]).split("'")[1],": ",Err)
      else:
          NOEND=False

#仅在普通运行时运行以下代码（用户交互）
if __name__=="__main__":
    import tqdm
    openLog=True #若要修改参数请在调用start函数前修改
    start() #初始化，若引用 请先调用此函数
    FLog.log(headers)
    if input("是否手动输入cookie[Y/other]. ")=="Y":
        bCookie=input("cookie:\n")
        headers["Cookie"]=bCookie
    print("提示:若获取高清视频，cookie中必须包含SESSDATA字段。在控制台使用document.cookie输出的cookie不完整，请在控制台网络页面手动捕获cookie！！！")
    print("请设置cookie内容！") if bCookie=="" or bCookie==None else fullwidth_to_halfwidth("made by klpyx！【】；‘’”“，。《》😀？")
    print("一般m4s文件都可以用视频播放器打开，改成mp4后缀也是没问题的。")
    #询问url
    videoUrl=input("输入视频URL ")
    #处理url
    videoUrl=urlparse(videoUrl)
    videoUrl=urlunparse(videoUrl._replace(path=videoUrl.path if videoUrl.path.endswith('/') else videoUrl.path + '/', params='', query='', fragment=''))
    #是否从本地读取
    getInfoForInputFile=True if input("是否从本地输入html文件并解析[Y/other]. ")=="Y" else False
    addText=",从本地读取 建议选此项" if getInfoForInputFile else ""
    if getInfoForInputFile:
        print("读取本地Html文件...")
        print(f"将要读取:{localHtmlPath}")
        input("请在准备好后按下回车 ")
        with open(localHtmlPath,"r",encoding='utf-8') as f2:
            htmlPage=f2.read()
    else:
        htmlPage=downloadHtml(videoUrl,htmlSavePath,headers)
        print(f"html页面保存在 {htmlSavePath}")
    print(f"视频信息保存在 {jsonSavePath}")
    print(f"视频标题：{getInfoTitle(htmlPage)}")
    #询问保存的文件名
    saveName=input("下载后的文件名(需输入后缀，留空为使用标题做文件名) ")
    if saveName=="":
       saveName=getInfoTitle(htmlPage)
    #全角转成半角
    saveName = fullwidth_to_halfwidth(saveName)
    #删除某些敏感肌文件系统和程序不支持的符号和emoji
    if removeEmojis:
       saveName=removeEmoji(saveName)
    saveName = re.sub('[\'!"#$%&\'()*+,-/:;<=>?@ ，。?★、…【】《》？“”‘\'！[\\]^_`{|}~\\s]+', "", saveName)
    saveName = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', saveName)
    #检查后缀是否存在
    if len(saveName.split(".")) <= 1:
       saveName+=".m4s"
    audioSaveName="au"
    videoSaveName="vi"
    #获取视频信息
    videoInfo=getInfoJson(htmlPage,jsonSavePath)
    #询问如何获取分辨率
    wayToGetClarity=input(f"获取分辨率的方法\n 1.保守(可能获取不全{addText})\n 2.激进(随时可能失效,目前已失效)\n ")
    #获取分辨率列表
    clarityList=getClarityList(videoInfo,wayToGetClarity)
    FLog.log(clarityList)
    #输出分辨率列表
    #forCount=0 #for计数器
    for clarity in clarityList.keys():
      print("".join((str(list(clarityList.keys()).index(clarity)+1),". ",clarity)))
    #选择分辨率
    selete=input("输入序号选择分辨率: ")
    #获取视频对应链接
    videoUrl=clarityList[list(clarityList.keys())[int(selete)-1]]
    FLog.log("vURL: "+videoUrl)
    #获取音频对应链接
    audioUrl=getAudioInfo(videoInfo)[max(getAudioInfo(videoInfo).keys())]
    #检查目录/文件是否存在
    if not os.path.exists(downFileSavePath):
        os.mkdir(downFileSavePath)
    if os.path.exists(os.path.join(downFileSavePath,videoSaveName+saveName)):
       os.remove(os.path.join(downFileSavePath,videoSaveName+saveName))
    if os.path.exists(os.path.join(downFileSavePath,audioSaveName+saveName)):
       os.remove(os.path.join(downFileSavePath,audioSaveName+saveName))
    #定义在下载文件时插入代码的类
    class runcodeOnDownloadFile:    
        def __init__(self):#不需要填
            return
        def AfterOpenFile(self,localsA,changeStorage):
            return
        def AfterCreateConnect(self,localsA,changeStorage):
            Res=localsA['Res']
            print(f"连接：{Res}")
        def beforeDownloadFile(self,localsA,changeStorage):
            FileSize=localsA['FileSize']
            print(f"文件大小: {str(FileSize)}bytes")
            #初始化tqdm进度条
            saveName=localsA['saveName']
            FileSize=localsA['FileSize']
            changeStorage("pBar",tqdm.tqdm(unit="B",unit_scale=True,unit_divisor=1024,miniters=1,desc=f"正在下载： {str(saveName)[0:6]}...{os.path.splitext(str(saveName))[0][-6:len(str(saveName))]}",total=FileSize) )
        def onDownloadingFiles(self,localsA,changeStorage):
            storage=localsA['storage'] #需要实时（假实时）读取
            data=localsA['data']
            pBarCopy=storage['pBar']#这里一定要复制一遍再更新否则会变成bool值
            pBarCopy.update(len(data))
            changeStorage("pBar",pBarCopy)
        def onEnd(self,localsA,changeStorage):
            storage=localsA['storage']
            pBarCopy=storage['pBar']
            pBarCopy.close()
            changeStorage("pBar",pBarCopy)
    #下载视频
    downloadFile(fileType="video",Url=videoUrl,path=os.path.join(downFileSavePath,videoSaveName+saveName),saveName=videoSaveName+saveName,headers=headers,runcodeObj=runcodeOnDownloadFile,downSize=downSpeed*2)
    print("视频文件下载完成,文件在"+os.path.join(downFileSavePath,videoSaveName+saveName))
    #下载音频
    downloadFile(fileType="audio",Url=audioUrl,path=os.path.join(downFileSavePath,audioSaveName+saveName),saveName=audioSaveName+saveName,headers=headers,runcodeObj=runcodeOnDownloadFile,downSize=downSpeed)
    print("音频文件下载完成,文件在"+os.path.join(downFileSavePath,audioSaveName+saveName))
    # if m4sTOmp43:
    #    a=1
    # else:
    #    print("m4sTOmp43=False,不进行m4s转mp4。")
    if mergeAudioVideo:
        ffmpegLog=mergeAudioAndVideo(ffmpegRunFile=ffmpegPath,videoFilePath=os.path.join(downFileSavePath,videoSaveName+saveName),audioFilePath=os.path.join(downFileSavePath,audioSaveName+saveName),outputFilePath=os.path.join(downFileSavePath,"merge_"+saveName)+".mp4")
        FLog.log(ffmpegLog)
        if ffmpegLog['type']=="OK":
            print(f"ffmpeg合并成功！文件在{os.path.join(downFileSavePath,'merge_'+saveName)}")
        else:
            print("ffmpeg出了一些问题，详见日志miao~")
    else:
        print("mergeAudioVideo=False,不进行音视频合并。")
    #debugMode()