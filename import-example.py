import bilibili
import os #你也可以引用bilibili.os
import sys #你也可以引用bilibili.sys
import tqdm

#修改配置,详见bilibili.py代码前说明
bilibili.ffmpegPath="F:\\projects\\ffmpeg\\ffmpeg.exe" #设置ffmpeg路径
bilibili.self_defaultHeader="[{time} testtest |{session}|] {things}{endv}" #设置日志格式
bilibili.downSpeed=1024*1024*10 #设置下载速度10MB
bilibili.mergeAudioVideo=True #设置需要合并音视频

bilibili.savePath=os.path.join(sys.path[0],"import_bilibili_example") #设置文件保存路径
downFileSavePath=os.path.join(bilibili.savePath,"download") #设置下载的音视频文件保存路径


#询问
bilibili.headers["Cookie"]=input("输入cookie:\n")
downloadLink=bilibili.urlparse(input("视频链接 "))
downloadLink=bilibili.urlunparse(downloadLink._replace(path=downloadLink.path if downloadLink.path.endswith('/') else downloadLink.path + '/', params='', query='', fragment='')) #处理链接

bilibili.start() #初始化

#检查下载目录是否存在
if not os.path.exists(downFileSavePath):
    os.mkdir(downFileSavePath)

bilibili.FLog.log("test111")

#下载html页面
page=bilibili.downloadHtml(url=downloadLink,headers=bilibili.headers,path=os.path.join(bilibili.savePath,"download.html"))

#获取视频标题
title=bilibili.getInfoTitle(page)
#处理标题(可选)
title=bilibili.re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', bilibili.re.sub('[\'!"#$%&\'()*+,-/:;<=>?@ ，。?★、…【】《》？“”‘\'！[\\]^`{|}~\\s]+', "", title))
#获取视频音频信息的JSON
infoJson=bilibili.getInfoJson(page,os.path.join(bilibili.savePath,"info.json"))

#提取视频分辨率
videoDict=bilibili.getClarityList(infoJson,"1")
#获取音频下载地址
audioDict=bilibili.getAudioInfo(infoJson)

#获取视频列表的第一个清晰度
videoClarityFirst=list(videoDict.keys())[0]
#获取视频列表的第一个链接
videoLink=videoDict[videoClarityFirst]
#获取音频的第一个下载链接
audioLink=audioDict[list(audioDict.keys())[0]]
print(f"已选择清晰度：{videoClarityFirst}")

#检查下载的文件是否存在
if os.path.exists(os.path.join(downFileSavePath,f'video_{title}')):
    os.remove(os.path.join(downFileSavePath,f'video_{title}'))
if os.path.exists(os.path.join(downFileSavePath,f'audio_{title}')):
    os.remove(os.path.join(downFileSavePath,f'audio_{title}'))

#定义下载时运行的代码(可选)
class doOnDownload:
    def __init__(self): #不需要填
        return
    def AfterOpenFile(self,localsA,changeStorage): #必接收3个选项,详见代码
        return
    def AfterCreateConnect(self,localsA,changeStorage):
        print(f"已创建连接：{localsA["Res"]}") #使用localsA["Res"]读取 调用此函数时Res变量的值
    def beforeDownloadFile(self,localsA,changeStorage):
        saveName=localsA['saveName']
        FileSize=localsA['FileSize']
        printText=f"正在下载:{saveName}..." 
        changeStorage("tqdmObj",tqdm.tqdm(desc=printText,
                                          total=FileSize,
                                          unit="B",
                                          unit_scale=True,
                                          unit_divisor=1024,miniters=1)) #初始化tqdm进度条(desc:描述词，total:预期迭代次数，unit:单位)
    def onDownloadingFiles(self,localsA,changeStorage):
        tqdmObj=localsA['storage']['tqdmObj'] #这里一定要复制一遍再更新否则会变成bool值
        tqdmObj.update(len(localsA['data']))
        changeStorage("tqdmObj",tqdmObj) #更新进度条
    def onEnd(self,localsA,changeStorage):
        changeStorage("tqdmObj",localsA['storage']['tqdmObj'].close())

#下载视频
bilibili.downloadFile(fileType="video",
                      Url=videoLink,
                      path=os.path.join(downFileSavePath,f'video_{title}.m4s'),
                      saveName=f"video_{title}.m4s",
                      headers=bilibili.headers,
                      runcodeObj=doOnDownload,
                      downSize=bilibili.downSpeed*2)
print(f"视频下载完成，在{os.path.join(downFileSavePath,f'video_{title}.m4s')}")
#下载音频
bilibili.downloadFile(fileType="audio",
                      Url=audioLink,
                      path=os.path.join(downFileSavePath,f'audio_{title}.m4s'),
                      saveName=f"audio_{title}.m4s",
                      headers=bilibili.headers,
                      runcodeObj=doOnDownload,
                      downSize=bilibili.downSpeed)
print(f"音频下载完成，在{os.path.join(downFileSavePath,f'audio_{title}.m4s')}")

#合并音视频,需要ffmpeg可执行文件
mergeResult=bilibili.mergeAudioAndVideo(videoFilePath=os.path.join(downFileSavePath,f"video_{title}.m4s"),
                                        audioFilePath=os.path.join(downFileSavePath,f"audio_{title}.m4s"),
                                        outputFilePath=os.path.join(downFileSavePath,f"merge_{title}.mp4"),
                                        ffmpegRunFile=bilibili.ffmpegPath,
                                        encoding="utf-8"
                                        ) #请确保输出文件的后缀是mp4等常见后缀，否则ffmpeg可能不支持！
if mergeResult["type"]=="OK":
    print(f"ffmpeg转换成功，文件在{mergeResult['path']}")
else:
    print(f"ffmpeg转换失败，文件在{mergeResult['path']}，详见日志。")


print("OK!")