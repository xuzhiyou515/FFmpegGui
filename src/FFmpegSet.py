import subprocess
import requests
import zipfile
import os, sys, stat,ctypes
from contextlib import closing

class FFmpeg(object):

    def checkFFmpeg(self,reporthook):
        try:
            p = subprocess.run('ffmpeg -h')
            # showinfo(message="FFmpeg可正常使用！")
            reporthook("FFmpeg可正常使用！")
        except FileNotFoundError as e:
            # showerror(message="环境变量中不存在FFmpeg！")
            reporthook("环境变量中不存在FFmpeg！")

    def setFFmpeg(self,reporthook):
        try:
            subprocess.run('ffmpeg -h')
            NotWork = 0
        except FileNotFoundError as e:
            NotWork = 1
        if NotWork:
            # self.setInfo.set('FFmpeg不在环境变量中，开始配置工作....')
            # self.master.update()
            reporthook('FFmpeg不在环境变量中，开始配置工作....')
            url = 'https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-4.0.2-win64-static.zip'
            if os.path.exists("c:\\tool"):
                os.chmod("c:\\tool", stat.S_IWGRP)
            else:
                os.mkdir("C:\\tool", stat.S_IWGRP)
            with closing(requests.get(url, stream=True)) as response:
                chunk_size = 1024
                content_size = int(response.headers['content-length'])
                print('content_size', content_size, response.status_code, )
                with open('c:\\tool\\ffmpeg.zip', "wb") as file:
                    count = 0
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        count += len(data)
                        # self.setInfo.set('正在下载FFmpeg... {}/{}'.format(count, content_size))
                        # self.master.update()
                        reporthook('正在下载FFmpeg... {}/{}'.format(count, content_size))
                # self.setInfo.set('下载完成')
                # self.master.update()
                reporthook('下载完成')
            zfile = zipfile.ZipFile('c:\\tool\\ffmpeg.zip', 'r')
            # self.setInfo.set('正在解压中...')
            # self.master.update()
            reporthook('正在解压中...')
            zfile.extractall("c:\\tool")
            # self.setInfo.set('正在将FFmpeg写入环境变量中...')
            # self.master.update()
            reporthook('正在将FFmpeg写入环境变量中...')
            environ_value = dict(os.environ)
            path = environ_value.get('PATH')
            self.setEnviron()
            reporthook("配置已完成，请检测是否成功")
            os.putenv('PATH', path + ";C:\\tool\\ffmpeg-4.0.2-win64-static\\bin")
            # sign = self.checkFFmpeg()
            # if sign:
                # self.setInfo.set("FFmpeg环境已成功配置！")
                # self.master.update()
                # print('success')
            # else:
                # self.setInfo.set('!!!配置失败')
                # self.master.update()
                # print('fail')
        else:
            # self.setInfo.set('FFmpeg可正常使用！')
            # self.master.update()
            # print('enable')
            reporthook('FFmpeg可正常使用！')

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def setEnviron(self):
        environ_value = dict(os.environ)
        path=environ_value.get('PATH')
        # print(path)
        # print(__file__)

        if self.is_admin():
            # 将要运行的代码加到这里
            cmd='setx -m path "{};C:\\tool\\ffmpeg-4.0.2-win64-static\\bin"'.format(path)
            print(cmd)
            subprocess.run(cmd)

        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

if __name__=='__main__':
    setFFmpeg=FFmpeg()
    setFFmpeg.setEnviron()