from tkinter.scrolledtext import *
from tkinter.messagebox import *
from tkinter.ttk import *
from tkinter.filedialog import *
import time
import threading

from Track import *
from FFmpegSet import *


class App(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.mediainfos = []
        self.MediaInfoPath = StringVar(self.master)
        self.ExtractStreamPath = StringVar(self.master)
        self.PackageStreamPath = StringVar(self.master)

        # self.TotalTasks=0
        # self.DoneTasks=0
        self.TaskProgessStr = StringVar(self.master)
        self.TaskProgessStr.set('暂无任务')

        # self.MediaReadProgessStr = StringVar(self.master)
        # self.MediaReadProgessStr.set('暂无任务')
        #
        # self.ExtractReadProgessStr = StringVar(self.master)
        # self.ExtractReadProgessStr.set('暂无任务')

        self.MediaInfos = MediaInfos(self.MediaInfoPath.get())
        self.ExtractStreams = Extract(self.ExtractStreamPath.get())
        self.PackageStreams=Package(self.PackageStreamPath.get())
        self.FFmpeg=FFmpeg()

        # self.window_width = self.master.winfo_screenwidth()
        # self.window_height = self.master.winfo_screenheight()
        self.master.title("MediaTools v0.0  by XZY")
        # self.master.geometry("{}x{}+{}+{}".format(int(0.6 * self.window_width), int(0.8 * self.window_height),int(0.2 * self.window_width), int(0.1 * self.window_height)))
        self.master.geometry("960x600+200+72")
        self.master.resizable(False, False)
        self.pack()
        # 主tab
        self.notebooks = Notebook()
        self.notebooks.pack(expand=1, fill=BOTH)

        # 介绍页
        self.Introduce = Frame(self.notebooks)
        self.Introduce.pack()

        self.TitleFrame = Frame(self.Introduce)
        self.TitleFrame.pack(in_=self.Introduce)
        self.MainLable = Label(self.TitleFrame, text='MediaTools v0.0', font=("仿宋", 24, "normal"))
        self.MainLable.pack(in_=self.TitleFrame, pady=10)

        self.FFmpegCheckFrame = Frame(self.Introduce)
        self.FFmpegCheckFrame.pack(in_=self.Introduce, expand=1, fill=X)
        self.CheckFFmpegLabel = Label(self.FFmpegCheckFrame, text='检测是否存在FFmpeg环境变量')
        self.CheckFFmpegLabel.pack(in_=self.FFmpegCheckFrame, side=LEFT, expand=1, fill=X)
        self.CheckFFmpegButton = Button(self.FFmpegCheckFrame, text='检测', command=self.checkFFmpeg)
        self.CheckFFmpegButton.pack(in_=self.FFmpegCheckFrame, side=LEFT, expand=1)
        self.SetFFmpegButton = Button(self.FFmpegCheckFrame, text="配置FFmpeg环境", command=self.setFFmpeg)
        self.SetFFmpegButton.pack(in_=self.FFmpegCheckFrame, side=LEFT, expand=1, padx=10)
        self.setInfo = StringVar()
        # self.setInfo.set('')
        # self.setInfoFrame = Frame(self.Introduce)
        # self.setInfoFrame.pack(in_=self.Introduce)
        self.SetDetailLabel = Label(self.Introduce, textvariable=self.setInfo)
        self.SetDetailLabel.pack(in_=self.Introduce, expand=1, fill=X)

        self.IntroduceDetailFrame = Frame(self.Introduce)
        self.IntroduceDetailFrame.pack(in_=self.Introduce, expand=1, fill=BOTH, padx=20, pady=5)
        self.InfoScrollArea = ScrolledText(self.IntroduceDetailFrame, font=("隶书", 15), wrap=WORD)
        self.setIntroduceInfo()
        self.InfoScrollArea.pack(in_=self.IntroduceDetailFrame, expand=1, fill=BOTH)

        # 媒体信息页
        self.MediaInfo = Frame(self.notebooks)
        self.MediaInfo.pack()

        self.MediaInfosPathFrame = Frame(self.MediaInfo)
        self.MediaInfosPathFrame.pack(in_=self.MediaInfo, fill=X, padx=10, pady=20)
        self.MediaInfosPathLabel = Label(self.MediaInfosPathFrame, text="目标路径:")
        self.MediaInfosPathLabel.pack(in_=self.MediaInfosPathFrame, side=LEFT)
        self.MediaInfosPathEntry = Entry(self.MediaInfosPathFrame, textvariable=self.MediaInfoPath, state='readonly')
        self.MediaInfosPathEntry.pack(in_=self.MediaInfosPathFrame, side=LEFT, fill=X, expand=1)
        self.MediaInfosPathChooseValue = StringVar()
        self.MediaInfosPathChooseValue.set('路径选择')
        self.MediaInfosPathCombobox = Combobox(self.MediaInfosPathFrame, textvariable=self.MediaInfosPathChooseValue,
                                               state='readonly')
        self.MediaInfosPathCombobox['values'] = ('打开文件', '打开文件夹', '打开文件（追加）', '打开文件夹（追加）')
        self.MediaInfosPathCombobox.bind("<<ComboboxSelected>>", self.chooseMediaInfosPath)
        self.MediaInfosPathCombobox.pack(in_=self.MediaInfosPathFrame, side=LEFT)

        self.SetMediaInfoTreeviewFrame = Frame(self.MediaInfo)
        self.SetMediaInfoTreeviewFrame.pack(in_=self.MediaInfo, side=BOTTOM)
        self.MediaInfosClearButton = Button(self.SetMediaInfoTreeviewFrame, text="清空内容", command=self.clearMediaInfos)
        self.MediaInfosClearButton.pack(in_=self.SetMediaInfoTreeviewFrame, side=RIGHT, padx=10)
        self.MediaInfosDeleteButton = Button(self.SetMediaInfoTreeviewFrame, text="删除所选项",
                                             command=self.deleteMediaInfos)
        self.MediaInfosDeleteButton.pack(in_=self.SetMediaInfoTreeviewFrame, side=RIGHT, padx=10)
        self.MediaInfoLabel = Label(text='视频信息', font=('仿宋', 12))
        self.MediaInfoLabel.place(x=1, y=50, in_=self.MediaInfo)
        self.MediaInfoTreeview = Treeview(self.MediaInfo, selectmode='extended')
        self.MediaInfoTreeview.pack(in_=self.MediaInfo, expand=1, fill=BOTH, padx=30, pady=10)

        self.MediaInfoVScrollbar = Scrollbar(self.MediaInfoTreeview)
        self.MediaInfoVScrollbar.config(command=self.MediaInfoTreeview.yview)
        self.MediaInfoTreeview.config(yscroll=self.MediaInfoVScrollbar.set)
        self.MediaInfoVScrollbar.pack(in_=self.MediaInfoTreeview, fill=Y, side=RIGHT)

        # 提取页
        self.Extract = Frame()
        self.Extract.pack()

        self.ExtractPathFrame = Frame(self.Extract)
        self.ExtractPathFrame.pack(in_=self.Extract, fill=X, padx=10, pady=10)
        self.ExtractPathEntry = Entry(self.ExtractPathFrame, textvariable=self.ExtractStreamPath, state='readonly')
        self.ExtractPathEntry.pack(in_=self.ExtractPathFrame, side=LEFT, fill=X, expand=1, padx=10)
        self.ExtractPathChooseValue = StringVar()
        self.ExtractPathChooseValue.set('路径选择')
        self.ExtractPathCombobox = Combobox(self.ExtractPathFrame, textvariable=self.ExtractPathChooseValue,
                                            state='readonly')
        self.ExtractPathCombobox['values'] = ('打开文件', '打开文件夹', '打开文件（追加）', '打开文件夹（追加）')
        self.ExtractPathCombobox.bind("<<ComboboxSelected>>", self.chooseExtractStreamPath)
        self.ExtractPathCombobox.pack(in_=self.ExtractPathFrame, side=LEFT)

        self.SetExtractStreamTreeviewFrame = Frame(self.Extract)
        self.SetExtractStreamTreeviewFrame.pack(in_=self.Extract, expand=1, fill=BOTH, pady=10)

        self.ExtractStreamDetailFrame = Frame(self.SetExtractStreamTreeviewFrame)
        self.ExtractStreamDetailFrame.pack(in_=self.SetExtractStreamTreeviewFrame, expand=1, fill=BOTH, side=LEFT,
                                           padx=16)
        self.ExtractStreamVScrollbar = Scrollbar(self.ExtractStreamDetailFrame)
        self.ExtractStreamVScrollbar.pack(in_=self.ExtractStreamDetailFrame, side=RIGHT, fill=Y)
        # self.ExtractStreamVScrollbar.grid(row=0, column=1, sticky='ns')
        # self.ExtractStreamHScrollbar = Scrollbar(self.ExtractStreamDetailFrame, orient='horizontal')
        # self.ExtractStreamHScrollbar.pack(in_=self.ExtractStreamDetailFrame, side=BOTTOM, fill=X)
        # self.ExtractStreamHScrollbar.grid(row=1, column=0, sticky='ew')
        # self.ExtractStreamListBox=Listbox(self.ExtractStreamDetailFrame,selectmode='EXPANDED',xscrollcommand=self.ExtractStreamHScrollbar.set,yscrollcommand=self.ExtractStreamVScrollbar.set)
        self.ExtractStreamTreeview = Treeview(self.ExtractStreamDetailFrame, selectmode='extended',
                                              yscrollcommand=self.ExtractStreamVScrollbar.set)
        self.ExtractStreamTreeview.pack(in_=self.ExtractStreamDetailFrame, expand=1, fill=BOTH)
        # self.ExtractStreamListBox.grid(row=0, column=0, sticky='NSEW')
        self.ExtractStreamVScrollbar.config(command=self.ExtractStreamTreeview.yview)
        # self.ExtractStreamHScrollbar.config(command=self.ExtractStreamListBox.xview)
        # self.getExtractStreamTreeview()

        self.ExtractChooseFrame = Frame(self.SetExtractStreamTreeviewFrame)
        self.ExtractChooseFrame.pack(in_=self.SetExtractStreamTreeviewFrame, side=LEFT, fill=Y, ipadx=10)

        self.MediaInfosImportButton = Button(self.ExtractChooseFrame, text='从Mediainfo\n导入',
                                             command=self.extractImportMediaInfos)
        self.MediaInfosImportButton.pack(in_=self.ExtractChooseFrame, pady=10)
        self.ExtractStreamsDeleteButton = Button(self.ExtractChooseFrame, text="删除所选项",
                                                 command=self.deleteExtractStreams)
        self.ExtractStreamsDeleteButton.pack(in_=self.ExtractChooseFrame, pady=10)
        self.ChoosedApplyToAllButton = Button(self.ExtractChooseFrame, text="将选择应用\n到所有媒体",
                                              command=self.applyToAllChoose)
        self.ChoosedApplyToAllButton.pack(in_=self.ExtractChooseFrame, pady=10)

        self.TaskProgressFrame = Frame(self.Extract)
        self.TaskProgressFrame.pack(in_=self.Extract, side=LEFT, padx=20, fill=X)
        # self.TotalProgressFrame=Frame(self.TaskProgressFrame)
        # self.TotalProgressFrame.pack(in_=self.TaskProgressFrame,side=BOTTOM,fill=Y)
        self.TotalProgressbar = Progressbar(self.TaskProgressFrame, orient='horizontal', length=300)
        self.TotalProgressbar.pack(in_=self.TaskProgressFrame, side=LEFT, padx=20, fill=Y)
        self.TotalProgressLabel = Label(self.TaskProgressFrame, textvariable=self.TaskProgessStr)
        self.TotalProgressLabel.pack(in_=self.TaskProgressFrame, side=RIGHT, fill=Y)

        self.ExtractFunctionFrame = Frame(self.Extract)
        self.ExtractFunctionFrame.pack(in_=self.Extract, side=LEFT, fill=Y, padx=20)
        self.ExtractChoosedItemsButton = Button(self.ExtractFunctionFrame, text='提取所选项',
                                                command=self.tryExtractChoosedItems)
        self.ExtractChoosedItemsButton.pack(in_=self.ExtractFunctionFrame, side=LEFT, padx=10)
        self.ExtractAllSubsButton = Button(self.ExtractFunctionFrame, text='提取所有字幕',
                                           command=self.extractAllSubtitles)
        self.ExtractAllSubsButton.pack(in_=self.ExtractFunctionFrame, side=LEFT, padx=10)
        self.ExtractAllAudiosButton = Button(self.ExtractFunctionFrame, text='提取所有音频',
                                             command=self.extractAllAudios)
        self.ExtractAllAudiosButton.pack(in_=self.ExtractFunctionFrame, side=LEFT, padx=10)

        # 封装页
        self.Package = Frame()
        self.Package.pack()

        self.PackagePathFrame = Frame(self.Package)
        self.PackagePathFrame.pack(in_=self.Package, fill=X, padx=10, pady=10)
        self.PackagePathEntry = Entry(self.PackagePathFrame, textvariable=self.PackageStreamPath, state='readonly')
        self.PackagePathEntry.pack(in_=self.PackagePathFrame, side=LEFT, fill=X, expand=1, padx=10)
        self.PackagePathChooseValue = StringVar()
        self.PackagePathChooseValue.set('路径选择')
        self.PackagePathCombobox = Combobox(self.PackagePathFrame, textvariable=self.PackagePathChooseValue,
                                            state='readonly')
        self.PackagePathCombobox['values'] = ('打开文件', '打开文件夹', '打开文件（追加）', '打开文件夹（追加）')
        self.PackagePathCombobox.bind("<<ComboboxSelected>>", self.choosePackageStreamPath)
        self.PackagePathCombobox.pack(in_=self.PackagePathFrame, side=LEFT)

        self.SetPackageStreamTreeviewFrame = Frame(self.Package)
        self.SetPackageStreamTreeviewFrame.pack(in_=self.Package, expand=1, fill=BOTH, pady=10)

        self.PackageStreamDetailFrame = Frame(self.SetPackageStreamTreeviewFrame)
        self.PackageStreamDetailFrame.pack(in_=self.SetPackageStreamTreeviewFrame, expand=1, fill=BOTH, side=LEFT,
                                           padx=16)
        self.PackageStreamVScrollbar = Scrollbar(self.PackageStreamDetailFrame)
        self.PackageStreamVScrollbar.pack(in_=self.PackageStreamDetailFrame, side=RIGHT, fill=Y)
        self.PackageStreamTreeview = Treeview(self.PackageStreamDetailFrame, selectmode='extended',
                                            yscrollcommand=self.PackageStreamVScrollbar.set)
        self.PackageStreamTreeview.pack(in_=self.PackageStreamDetailFrame, expand=1, fill=BOTH)
        self.PackageStreamVScrollbar.config(command=self.PackageStreamTreeview.yview)

        self.PackageChooseFrame = Frame(self.SetPackageStreamTreeviewFrame)
        self.PackageChooseFrame.pack(in_=self.SetPackageStreamTreeviewFrame, side=LEFT, fill=Y, ipadx=10)

        self.MediaInfosImportButton = Button(self.PackageChooseFrame, text='从Mediainfo\n导入',
                                             command=self.PackageImportMediaInfos)
        self.MediaInfosImportButton.pack(in_=self.PackageChooseFrame, pady=10)
        self.PackageStreamsDeleteButton = Button(self.PackageChooseFrame, text="删除所选项",
                                                 command=self.deletePackageStreams)
        self.PackageStreamsDeleteButton.pack(in_=self.PackageChooseFrame, pady=10)

        self.PackageFunctionFrame = Frame(self.Package)
        self.PackageFunctionFrame.pack(in_=self.Package, side=LEFT, fill=Y, padx=20)
        self.PackageChoosedItemsButton = Button(self.PackageFunctionFrame, text='封装所选项',
                                                command=self.tryPackageChoosedItems)
        self.PackageChoosedItemsButton.pack(in_=self.PackageFunctionFrame, side=LEFT, padx=10)
        self.ChoosedApplyToAllButton = Button(self.PackageFunctionFrame, text="将所有流封装为一个文件",
                                              command=self.packageAllStreams)
        self.ChoosedApplyToAllButton.pack(in_=self.PackageFunctionFrame, padx=10)

        self.notebooks.add(self.Introduce, text='Introduce')
        self.notebooks.add(self.MediaInfo, text='MediaInfo')
        self.notebooks.add(self.Extract, text='Extract')
        self.notebooks.add(self.Package, text='Package')

        # 检查FFmpeg

    def checkFFmpeg(self, sign=0, env=None):
        thread=threading.Thread(target=self.FFmpeg.checkFFmpeg,args=(self.showFFmpegInfo,))
        thread.start()

    def showFFmpegInfo(self,info,ev=None):
        showinfo(message=info)

        # 配置FFmpeg
    def updateFFmpegInfo(self,info,ev=None):
        self.setInfo.set(info)

    def setFFmpeg(self, env=None):
        thread=threading.Thread(target=self.FFmpeg.setFFmpeg,args=(self.updateFFmpegInfo,))
        thread.start()
        # import subprocess
        # try:
        #     subprocess.run('ffmpeg -h')
        #     NotWork = 0
        # except FileNotFoundError as e:
        #     NotWork = 1
        # if NotWork:
        #     self.setInfo.set('FFmpeg不在环境变量中，开始配置工作....')
        #     self.master.update()
        #     import requests
        #     import zipfile
        #     import os, sys, stat
        #     import subprocess
        #     from contextlib import closing
        #     url = 'https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-4.0.2-win64-static.zip'
        #     if os.path.exists("c:\\tool"):
        #         os.chmod("c:\\tool", stat.S_IWGRP)
        #     else:
        #         os.mkdir("C:\\tool", stat.S_IWGRP)
        #     with closing(requests.get(url, stream=True)) as response:
        #         chunk_size = 1024
        #         content_size = int(response.headers['content-length'])
        #         print('content_size', content_size, response.status_code, )
        #         with open('c:\\tool\\ffmpeg.zip', "wb") as file:
        #             count = 0
        #             for data in response.iter_content(chunk_size=chunk_size):
        #                 file.write(data)
        #                 count += len(data)
        #                 self.setInfo.set('正在下载FFmpeg... {}/{}'.format(count, content_size))
        #                 self.master.update()
        #         self.setInfo.set('下载完成')
        #         self.master.update()
        #     zfile = zipfile.ZipFile('c:\\tool\\ffmpeg.zip', 'r')
        #     self.setInfo.set('正在解压中...')
        #     self.master.update()
        #     zfile.extractall("c:\\tool")
        #     self.setInfo.set('正在将FFmpeg写入环境变量中...')
        #     self.master.update()
        #     environ_value = dict(os.environ)
        #     path = environ_value.get('PATH')
        #     import getRoot
        #     os.putenv('PATH', path + ";C:\\tool\\ffmpeg-4.0.2-win64-static\\bin")
        #     sign = self.checkFFmpeg()
        #     if sign:
        #         self.setInfo.set("FFmpeg环境已成功配置！")
        #         self.master.update()
        #     else:
        #         self.setInfo.set('!!!配置失败')
        #         self.master.update()
        # else:
        #     self.setInfo.set('FFmpeg可正常使用！')
        #     self.master.update()
        # import time
        # time.sleep(2)
        # self.setInfo.set('')


        # 设置Introduce的内容

    def setIntroduceInfo(self, ev=None):
        # for i in range(30):
            # self.InfoScrollArea.insert(END, 'haha\n')
        with open('Introduce.txt','r',encoding='utf-8') as file:
            # line = 'hello'
            # while line:
            #     line=file.readline()
            #     # print(line)
            #     self.InfoScrollArea.insert(END,line)
            self.InfoScrollArea.insert(END,file.read())
        self.InfoScrollArea.config(state=DISABLED)

        # 对self.MediaInfos的处理

    def addMediaInfos(self, ev=None):
        thread = threading.Thread(target=self.MediaInfos.add_mediainfo,
                                  args=(self.MediaInfoPath.get(), self.addMediaInfoTreeview))
        thread.start()
        # return add_mediainfos

    def clearMediaInfos(self, ev=None):
        self.MediaInfos.mediainfos = []
        self.clearMediaInfoTreeview()

    def updateMediaInfos(self, ev=None):
        self.clearMediaInfos()
        self.addMediaInfos()
        # thread = threading.Thread(target=self.MediaInfos.set_mediainfo,
        # args=(self.MediaInfoPath.get(), self.addMediaInfoTreeview))
        # thread.start()

    def deleteMediaInfos(self, ev=None):
        # items=[]
        items = list(self.MediaInfoTreeview.selection())
        # for item in item_tuple:
        #     items.append(item)
        # items=list(item_tuple)
        # print(type(items))
        while items:
            item = items[0]
            if self.MediaInfoTreeview.parent(item) == '':
                media_name = self.MediaInfoTreeview.item(item)['text']
                for media_info in self.MediaInfos.mediainfos:
                    if media_info['media_name'] == media_name:
                        self.MediaInfos.mediainfos.remove(media_info)
                        break
                self.MediaInfoTreeview.delete(item)
                items = list(self.MediaInfoTreeview.selection())
            else:
                items.remove(item)

        # 根据选择的目录对MediaInfos更新

    def chooseMediaInfosPath(self, env=None):
        value = self.MediaInfosPathCombobox.get()
        if value == '打开文件':
            path = askopenfilename()
            self.MediaInfoPath.set(path)
            self.updateMediaInfos()
            # self.getMediaInfoTreeview()
        elif value == '打开文件（追加）':
            path = askopenfilename()
            self.MediaInfoPath.set(path)
            self.addMediaInfos()
            # self.addMediaInfoTreeview(mediainfos)
        elif value == '打开文件夹':
            path = askdirectory()
            self.MediaInfoPath.set(path)
            self.updateMediaInfos()
            # self.getMediaInfoTreeview()
        else:
            path = askdirectory()
            self.MediaInfoPath.set(path)
            self.addMediaInfos()
            # self.addMediaInfoTreeview(mediainfos)


        # def getMediaInfoTreeview(self, ev=None):
        #     self.clearMediaInfoTreeview()
        #     for mediainfo in self.MediaInfos.mediainfos:
        #         self.addMediaInfoTreeview(mediainfo)

    # 处理self.MediaInfoTreeview内容
    def addMediaInfoTreeview(self, mediainfo, ev=None):
        # for mediainfo in mediainfos:
        treeOne = self.MediaInfoTreeview.insert('', 'end', text=mediainfo['media_name'])
        treeSecondvideos = self.MediaInfoTreeview.insert(treeOne, 'end', text="视频流")
        treeSecondaudios = self.MediaInfoTreeview.insert(treeOne, 'end', text="音频流")
        treeSecondsubtitles = self.MediaInfoTreeview.insert(treeOne, 'end', text="字幕流")
        treeSecondothers = self.MediaInfoTreeview.insert(treeOne, 'end', text="其他流")
        n = 1
        video_tracks = mediainfo['video_tracks']
        for videotrack in video_tracks:
            treeThreevideos = self.MediaInfoTreeview.insert(treeSecondvideos, 'end', text='视频#{}'.format(n))
            n = n + 1
            for (k, v) in videotrack.items():
                self.MediaInfoTreeview.insert(treeThreevideos, 'end', text=("%s:" % k, v))
        n = 1
        audio_tracks = mediainfo['audio_tracks']
        for audiotrack in audio_tracks:
            treeThreeaudios = self.MediaInfoTreeview.insert(treeSecondaudios, 'end', text='音频#{}'.format(n))
            n = n + 1
            for (k, v) in audiotrack.items():
                self.MediaInfoTreeview.insert(treeThreeaudios, 'end', text=("%s:" % k, v))
        n = 1
        subtitle_tracks = mediainfo['subtitle_tracks']
        for subtitletrack in subtitle_tracks:
            treeThreesubtitles = self.MediaInfoTreeview.insert(treeSecondsubtitles, 'end', text='字幕#{}'.format(n))
            n = n + 1
            for (k, v) in subtitletrack.items():
                self.MediaInfoTreeview.insert(treeThreesubtitles, 'end', text=("%s:" % k, v))
        n = 1
        other_tracks = mediainfo['other_tracks']
        for othertrack in other_tracks:
            treeThreeothers = self.MediaInfoTreeview.insert(treeSecondothers, 'end', text='其他#{}'.format(n))
            n = n + 1
            for (k, v) in othertrack.items():
                self.MediaInfoTreeview.insert(treeThreeothers, 'end', text=("%s:" % k, v))

    def clearMediaInfoTreeview(self, ev=None):
        items = self.MediaInfoTreeview.get_children()
        [self.MediaInfoTreeview.delete(item) for item in items]


        # 对self.ExtractStreams的处理


    def extractImportMediaInfos(self, ev=None):
        media_paths = []
        for mediainfo in self.MediaInfos.mediainfos:
            media_paths.append(mediainfo['media_path'])
        self.ExtractStreams.add_mediainfo(media_paths, self.addExtractStreamTreeview)
        # self.addExtractStreamTreeview(add_mediainfos)

    def clearExtractStreams(self, ev=None):
        self.ExtractStreams.mediainfos = []
        self.clearExtractStreamTreeview()

    def addExtractStreams(self, ev=None):
        # add_mediainfos = self.ExtractStreams.add_mediainfo(self.ExtractStreamPath.get())
        # return add_mediainfos
        thread = threading.Thread(target=self.ExtractStreams.add_mediainfo,
                                  args=(self.ExtractStreamPath.get(), self.addExtractStreamTreeview))
        thread.start()

    def updateExtractStreams(self, ev=None):
        self.clearExtractStreams()
        self.addExtractStreams()
        # self.ExtractStreams = Extract(self.ExtractStreamPath.get())
        # thread = threading.Thread(target=self.ExtractStreams.set_mediainfo,
        #                           args=(self.ExtractStreamPath.get(), self.addExtractStreamTreeview))
        # thread.start()

    def deleteExtractStreams(self, ev=None):
        items = list(self.ExtractStreamTreeview.selection())
        print(items)
        while items:
            item = items[0]
            if self.ExtractStreamTreeview.parent(item) == '':
                media_name = self.ExtractStreamTreeview.item(item)['text']
                for media_info in self.ExtractStreams.mediainfos:
                    if media_info['media_name'] == media_name:
                        self.ExtractStreams.mediainfos.remove(media_info)
                        break
                self.ExtractStreamTreeview.delete(item)
                items = list(self.ExtractStreamTreeview.selection())
            else:
                items.remove(item)

        # 根据选择的目录对ExtractStreams更新

    def chooseExtractStreamPath(self, env=None):
        value = self.ExtractPathCombobox.get()
        if value == '打开文件':
            path = askopenfilename()
            self.ExtractStreamPath.set(path)
            self.updateExtractStreams()
            # self.getExtractStreamTreeview()
        elif value == '打开文件（追加）':
            path = askopenfilename()
            self.ExtractStreamPath.set(path)
            self.addExtractStreams()
            # self.addExtractStreamTreeview(mediainfos)
        elif value == '打开文件夹':
            path = askdirectory()
            self.ExtractStreamPath.set(path)
            self.updateExtractStreams()
            # self.getExtractStreamTreeview()
        else:
            path = askdirectory()
            self.ExtractStreamPath.set(path)
            self.addExtractStreams()
            # self.addExtractStreamTreeview(mediainfos)

        # 处理self.ExtractStreamTreeview内容

    def getExtractStreamTreeview(self, ev=None):
        self.clearExtractStreamTreeview()
        self.addExtractStreamTreeview(self.ExtractStreams.mediainfos)

    def addExtractStreamTreeview(self, mediainfo, ev=None):
        # for mediainfo in mediainfos:

        treeOne = self.ExtractStreamTreeview.insert('', 'end', text=mediainfo['media_name'])
        title = 'TAG:title'
        lang = 'TAG:language'
        sign = 1
        num = len(mediainfo['media_name'].split('.')[-1]) + 1
        name = mediainfo['media_name'][0:-num]
        # name=mediainfo['media_name']
        # values = ['{}'.format(videotrack['media_path']), '{}'.format(videotrack['index'])]
        treeSecondvideos = self.ExtractStreamTreeview.insert(treeOne, 'end', text="视频流")
        treeSecondaudios = self.ExtractStreamTreeview.insert(treeOne, 'end', text="音频流")
        treeSecondsubtitles = self.ExtractStreamTreeview.insert(treeOne, 'end', text="字幕流")
        # treeSecondothers = self.ExtractStreamTreeview.insert(treeOne, 'end', text="其他流")
        n = 1
        video_tracks = mediainfo['video_tracks']
        for videotrack in video_tracks:
            # values = {'path':'{}'.format(mediainfo['media_path']),'type':'video','index': '{}'.format(videotrack['index'])}
            values = ['{}'.format(mediainfo['media_path']), 'video', '{}'.format(str(videotrack['index']))]
            if title in videotrack.keys():
                sign = 0
                name = name + '-' + videotrack[title]
            if lang in videotrack.keys():
                name = name + '-' + videotrack[lang]
            if sign:
                self.ExtractStreamTreeview.insert(treeSecondvideos, 'end',
                                                  text='视频--{}'.format(name + '-' + videotrack['index']),
                                                  value=values)
            else:
                self.ExtractStreamTreeview.insert(treeSecondvideos, 'end', text='视频--{}'.format(name), value=values)
            n = n + 1

        n = 1
        audio_tracks = mediainfo['audio_tracks']
        for audiotrack in audio_tracks:
            # values = {'path': '{}'.format(mediainfo['media_path']), 'type': 'audio', 'index': '{}'.format(audiotrack['index'])}
            values = ['{}'.format(mediainfo['media_path']), 'audio', '{}'.format(str(audiotrack['index']))]
            if title in audiotrack.keys():
                sign = 0
                name = name + '-' + audiotrack[title]
            if lang in audiotrack.keys():
                name = name + '-' + audiotrack[lang]
            if sign:
                self.ExtractStreamTreeview.insert(treeSecondaudios, 'end',
                                                  text='音频--{}'.format(name + '-' + audiotrack['index']),
                                                  value=values)
            else:
                self.ExtractStreamTreeview.insert(treeSecondaudios, 'end',
                                                  text='音频--{}'.format(name),
                                                  value=values)
            n = n + 1

        n = 1
        subtitle_tracks = mediainfo['subtitle_tracks']
        for subtitletrack in subtitle_tracks:
            # values = {'path': '{}'.format(mediainfo['media_path']), 'type': 'subtitle', 'index': '{}'.format(subtitletrack['index'])}
            values = ['{}'.format(mediainfo['media_path']), 'subtitle', '{}'.format(str(subtitletrack['index']))]
            if title in subtitletrack.keys():
                sign = 0
                name = name + '-' + subtitletrack[title]
            if lang in subtitletrack.keys():
                name = name + '-' + subtitletrack[lang]
            if sign:
                self.ExtractStreamTreeview.insert(treeSecondsubtitles, 'end',
                                                  text='字幕--{}'.format(name + '-' + subtitletrack['index']),
                                                  value=values)
            else:
                self.ExtractStreamTreeview.insert(treeSecondsubtitles, 'end',
                                                  text='字幕--{}'.format(name),
                                                  value=values)
            n = n + 1

    def clearExtractStreamTreeview(self, ev=None):
        items = self.ExtractStreamTreeview.get_children()
        [self.ExtractStreamTreeview.delete(item) for item in items]

    def applyToAllChoose(self, ev=None):
        items = self.ExtractStreamTreeview.selection()
        item = items[0]
        root_item = ''
        while (item):
            root_item = item
            item = self.ExtractStreamTreeview.parent(root_item)
        gaps = []
        for item in items:
            gaps.append(int(item[1:], 16) - int(root_item[1:], 16))
        # print(gaps)
        root_items = self.ExtractStreamTreeview.get_children()
        print(root_items)
        all_items = []
        for root_item in root_items:
            for gap in gaps:
                item = hex(int(root_item[1:], 16) + gap)[2:]
                count = 3 - len(item)
                if count:
                    for i in range(count):
                        item = '0' + item
                item = 'i' + item
                all_items.append(item.upper())
        # for item in all_items:
        print(all_items)
        self.ExtractStreamTreeview.selection_set(all_items)

    def tryExtractChoosedItems(self, ev=None):
        thread = threading.Thread(target=self.extractChoosedItems, args=(self.updateTasks,))
        thread.start()

    def extractChoosedItems(self, reporthook=None, ev=None):
        # items=[]
        items = self.ExtractStreamTreeview.selection()
        item_infos = []
        for item in items:
            children = self.ExtractStreamTreeview.item(item)
            item_infos.append(children['values'])
        print(item_infos)
        DoneTasks = 0
        TotalTasks = len(item_infos)
        reporthook(DoneTasks, TotalTasks)
        for item_info in item_infos:
            path = item_info[0]
            types = item_info[1]
            index = str(item_info[2])
            print(type(index))
            if types == 'video':
                self.ExtractStreams.extract_video(path, index)
            elif types == 'audio':
                self.ExtractStreams.extract_one_audio(path, index)
            else:
                self.ExtractStreams.extract_one_subtitle(path, index)
            DoneTasks = DoneTasks + 1
            reporthook(DoneTasks, TotalTasks)

    def extractAllSubtitles(self, ev=None):
        extract = threading.Thread(target=self.ExtractStreams.extract_all_subtitles, args=(self.updateTasks,))
        extract.start()

    def extractAllAudios(self, ev=None):
        extractAudios = threading.Thread(target=self.ExtractStreams.extract_all_audios, args=(self.updateTasks,))
        extractAudios.start()

    def updateTasks(self, DoneTasks, TotalTasks, ev=None):
        self.TotalProgressbar.config(value=DoneTasks, maximum=TotalTasks)
        self.TaskProgessStr.set('进度：{}/{}'.format(DoneTasks, TotalTasks))
        self.master.update()
        if DoneTasks == TotalTasks:
            time.sleep(2)
            self.TaskProgessStr.set('所有任务都完成了！'.format(DoneTasks, TotalTasks))


    def addPackageStreams(self,ev=None):
        thread = threading.Thread(target=self.PackageStreams.add_mediainfo,args=(self.PackageStreamPath.get(), self.addPackageStreamTreeview))
        thread.start()

    def clearPackageStreams(self,ev=None):
        self.PackageStreams.mediainfos=[]
        self.clearPackageStreamTreeview()

    def updatePackageStreams(self,ev=None):
        self.clearPackageStreams()
        self.addPackageStreams()

    def deletePackageStreams(self,ev=None):
        items = self.PackageStreamTreeview.selection()
        for item in items:
            self.PackageStreamTreeview.delete(item)
    #     是否对self.PackageStreams 进行处理？
    def PackageImportMediaInfos(self,ev=None):
        media_paths = []
        for mediainfo in self.MediaInfos.mediainfos:
            media_paths.append(mediainfo['media_path'])
        for mediainfo in self.MediaInfos.single_mediainfos:
            media_paths.append(mediainfo['media_path'])
        self.ExtractStreams.add_mediainfo(media_paths, self.addPackageStreamTreeview)

    def choosePackageStreamPath(self,value,ev=None):
        value = self.PackagePathCombobox.get()
        if value == '打开文件':
            path = askopenfilename()
            self.PackageStreamPath.set(path)
            self.updatePackageStreams()
        elif value == '打开文件（追加）':
            path = askopenfilename()
            self.PackageStreamPath.set(path)
            self.addPackageStreams()
        elif value == '打开文件夹':
            path = askdirectory()
            self.PackageStreamPath.set(path)
            self.updatePackageStreams(0)
        else:
            path = askdirectory()
            self.PackageStreamPath.set(path)
            self.addPackageStreams()


    def clearPackageStreamTreeview(self, ev=None):
        items = self.PackageStreamTreeview.get_children()
        [self.PackageStreamTreeview.delete(item) for item in items]

    def addPackageStreamTreeview(self,mediainfo,ev=None):
        if mediainfo['isSingle']:
            info=[mediainfo['media_path'],mediainfo['index'],mediainfo['type'],mediainfo['isSingle']]
            self.PackageStreamTreeview.insert('','end',text=mediainfo['media_name'],value=info)
        else:
            media_name=mediainfo['media_name']
            media_path=mediainfo['media_path']
            self.PackageStreamTreeview.insert('','end',text=media_name)
            video_tracks=mediainfo['video_tracks']
            audio_tracks=mediainfo['audio_tracks']
            sub_tracks=mediainfo['subtitle_tracks']
            for video_track in video_tracks:
                info=[media_path,video_track['index'],'video',0]
                self.PackageStreamTreeview.insert('','end',text=media_name+'-video'+'#{}'.format(video_track['index']),value=info)
            for audio_track in audio_tracks:
                info = [media_path, audio_track['index'], 'audio', 0]
                self.PackageStreamTreeview.insert('', 'end',text=media_name + '-audio' + '#{}'.format(audio_track['index']),value=info)
            for sub_track in sub_tracks:
                info = [media_path, sub_track['index'], 'subtitle', 0]
                self.PackageStreamTreeview.insert('', 'end',text=media_name + '-sub' + '#{}'.format(sub_track['index']),value=info)
            self.PackageStreamTreeview.insert('','end',text='-----------------------------------------------------------------------')

    def tryPackageChoosedItems(self,ev=None):
        thread = threading.Thread(target=self.packageChoosedItems)
        thread.start()
    def packageAllStreams(self,ev=None):
        thread=threading.Thread(target=self.packageChoosedItems,args=(0,))
        thread.start()

    def packageChoosedItems(self,isChoosed=1,ev=None):
        if isChoosed:
            items = self.PackageStreamTreeview.selection()
        else:
            items=self.PackageStreamTreeview.get_children()
        print(items)
        item_infos = []
        for item in items:
            children = self.PackageStreamTreeview.item(item)
            item_infos.append(children['values'])
        print(item_infos)
        paths=[]
        indexs=[]
        types=[]
        isSingles=[]
        for item_info in item_infos:
            paths.append(item_info[0])
            indexs.append(str(item_info[1]))
            types.append(item_info[2])
            isSingles.append(item_info[3])
        # print(paths)
        if paths:
            self.PackageStreams.get_packaged(paths,indexs,types,isSingles)

app = App()

app.mainloop()
