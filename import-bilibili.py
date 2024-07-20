import bilibili
print(dir(bilibili))
# bilibili.RegularforVideoInfo="" #打开就有报错，因为修改此选项后无法正常匹配。
bilibili.start()
print(dir(bilibili))
print(bilibili.__name__)
videoUrl=bilibili.urlparse("https://www.baidu.com/aa")
videoUrl=bilibili.urlunparse(videoUrl._replace(path=videoUrl.path if videoUrl.path.endswith('/') else videoUrl.path + '/', params='', query='', fragment=''))
print(videoUrl)
with open(input("含json数据的html文件路径> "),"r",encoding="utf-8") as f:
    print(bilibili.getInfoJson(htmlPage=f.read(),path=bilibili.os.path.join(bilibili.savePath,"testJSON.json")))