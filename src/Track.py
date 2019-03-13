import subprocess
import os
import re


class MediaInfos(object):
    def __init__(self, media_path=''):
        # media_path=str(media_path)
        self.mediainfos = []
        self.single_mediainfos=[]
        # self.mediainfoIndex=0
        self.add_mediainfo(media_path)
    # def do_nothing(self, media_info):
    #     pass

    # def set_mediainfo(self, media_path, reporthook=None):
    #     self.mediainfos = []
    #     self.add_mediainfo(media_path, reporthook)

    def add_mediainfo(self, media_path, reporthook=None):
        audio_postfixs = ['aac', 'ogg', 'ac3', 'dts', 'mp3', 'flac', 'opus','wav']
        sub_postfixs = ['sup', 'ssa', 'ass', 'srt', 'vtt', 'pgs']
        video_postfixs=['mkv', 'mp4', 'rmvb', 'flv', 'mov', 'webm', 'm2ts', 'mpg', 'm4v', 'avi', 'wmv']
        single_postfixs=audio_postfixs+sub_postfixs
        media_paths_out = []
        single_media_paths=[]
        if isinstance(media_path, list):
            for path in media_path:
                if path.split('.')[-1] in video_postfixs:
                    media_paths_out.append(path)
                elif path.split('.')[-1] in single_postfixs:
                    single_media_paths.append(path)
        elif media_path == '':
            pass
        elif os.path.isfile(media_path):
            if media_path.split('.')[-1] in video_postfixs:
                media_paths_out.append(media_path)
            elif media_path.split('.')[-1] in single_postfixs:
                single_media_paths.append(media_path)
        else:
            files = []
            for dirpath, dirname, filename in os.walk(media_path):
                # print(dirpath,dirname,filename)
                if filename:
                    for file in filename:
                        files.append(dirpath + '/' + file)
            media_paths_out = [file for file in files if file.split('.')[-1] in video_postfixs]
            single_media_paths=[file for file in files if file.split('.')[-1] in single_postfixs]
        media_path_in = []
        single_path_in=[]
        for mediainfo in self.mediainfos:
            media_path_in.append(mediainfo['media_path'])
        for mediainfo in self.single_mediainfos:
            single_path_in.append(mediainfo['media_path'])
        # media_paths=media_path_in
        # print(media_path_in)
        # print(media_paths_out)
        # mediainfos=[]
        for media_path in media_paths_out:
            if media_path in media_path_in:
                # print(media_path)
                # print('in')
                continue
            # print(media_path)
            mediainfo = {}
            mediainfo['isSingle']=0
            indexslice = []
            mediainfo['media_path'] = media_path
            if len(media_path.split('\\')) == 1:
                mediainfo['media_name'] = media_path.split('/')[-1]
            else:
                mediainfo['media_name'] = media_path.split('\\')[-1]
            # print(mediainfo['media_name'])

            cmds = ['ffprobe', '-show_streams', media_path]
            info = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[
                0].decode().split('\n')
            tracks = []
            track = {}
            for line in info:
                if re.match('\[STREAM\]', line):
                    track = {}
                elif re.match(r'\[/STREAM\]', line):
                    tracks.append(track)
                    track = {}
                elif line == '':
                    pass
                else:
                    key, val = line.strip().split('=')
                    track[key] = val
            video_tracks = []
            audio_tracks = []
            subtitle_tracks = []
            other_tracks = []
            for track in tracks:
                if track['codec_type'] == 'video':
                    video_tracks.append(track)
                elif track['codec_type'] == 'audio':
                    audio_tracks.append(track)
                elif track['codec_type'] == 'subtitle':
                    subtitle_tracks.append(track)
                else:
                    other_tracks.append(track)
            mediainfo['video_tracks'] = video_tracks
            # indexslice.append(len(video_tracks)-1)
            mediainfo['audio_tracks'] = audio_tracks
            mediainfo['subtitle_tracks'] = subtitle_tracks
            mediainfo['other_tracks'] = other_tracks
            # mediainfos.append(mediainfo)
            if reporthook:
                reporthook(mediainfo)
            self.mediainfos.append(mediainfo)
            # self.mediainfoIndex=self.mediainfoIndex+1
        for media_path in single_media_paths:
            if media_path in single_path_in:
                continue
            postfix = media_path.split('.')[-1]
            mediainfo = {}
            mediainfo['isSingle'] = 1
            mediainfo['media_path'] = media_path
            mediainfo['index']='0'
            if len(media_path.split('\\')) == 1:
                mediainfo['media_name'] = media_path.split('/')[-1]
            else:
                mediainfo['media_name'] = media_path.split('\\')[-1]
            if postfix in audio_postfixs:
                mediainfo['type'] = 'audio'
                self.mediainfos.append(mediainfo)
            elif postfix in sub_postfixs:
                mediainfo['type'] = 'subtitle'
            # elif postfix in video_postfixs:
            # self.add_mediainfo(media_path)
            else:
                print("Unknown formats!!!")
            reporthook(mediainfo)
            self.single_mediainfos.append(mediainfo)
        # return mediainfos


class Extract(MediaInfos):
    def __init__(self, media_path=''):
        super(Extract, self).__init__(media_path)

    def import_mediainfos(self, mediainfos):
        self.mediainfos = mediainfos

    def extract_video(self, media_path, index):
        title = 'TAG:title'
        lang = 'TAG:language'
        media = {}
        for mediainfo in self.mediainfos:
            if mediainfo['media_path'] == media_path:
                media = mediainfo
                break
        if not media['video_tracks']:
            print('No videos!!!')
        else:
            for track in media['video_tracks']:
                if track['index'] == index:
                    num = len(media['media_path'].split('.')[-1]) + 1
                    name = media['media_path'][0:-num]
                    sign = 1
                    if track['codec_name'] in ['rv40', 'h264', 'hevc', 'vp8', 'vp9']:
                        postfix = '.mkv'
                        if title in track.keys():
                            sign = 0
                            name = name + '-' + track[title]
                        if lang in track.keys():
                            name = name + '-' + track[lang]
                        if len(name) > 249:
                            name = name[0:249] + '-{}'.format(track['index']) + postfix
                        else:
                            if sign:
                                name = name + '-{}'.format(track['index']) + postfix
                            else:
                                name = name + postfix
                        subprocess.run(
                            'ffmpeg -y -i {} -map 0:{} -vcodec copy {}'.format('"' + media['media_path'] + '"',
                                                                               track['index'],
                                                                               '"' + name + '"'))
                    else:
                        print('Unknown format!!!')
                    break

    def extract_one_audio(self, media_path, index):
        track = {}
        title = 'TAG:title'
        lang = 'TAG:language'
        media = {}
        print(self.mediainfos)
        for mediainfo in self.mediainfos:
            if mediainfo['media_path'] == media_path:
                media = mediainfo
                break
        print(media)
        for tracks in media['audio_tracks']:
            print(tracks['index'])
            print(tracks)
            if tracks['index'] == index:
                track = tracks
                break
        num = len(media['media_path'].split('.')[-1]) + 1
        name = media['media_path'][0:-num]
        sign = 1
        postfix = ''
        print(track)
        if 'aac' in track['codec_name']:
            postfix = '.aac'
        elif 'vorbis' in track['codec_name']:
            postfix = '.ogg'
        elif 'ac3' in track['codec_name']:
            postfix = '.ac3'
        elif 'dts' in track['codec_name']:
            postfix = '.dts'
        elif 'mp3' in track['codec_name']:
            postfix = '.mp3'
        elif 'flac' in track['codec_name']:
            postfix = '.flac'
        elif 'opus' in track['codec_name']:
            postfix = '.opus'
        if postfix == '':
            print('Unknown format!!!')
        else:
            if title in track.keys():
                sign = 0
                name = name + '-' + track[title]
            if lang in track.keys():
                name = name + '-' + track[lang]
            if len(name) > 249:
                name = name[0:249] + '-{}'.format(track['index']) + postfix
            else:
                if sign:
                    name = name + '-{}'.format(track['index']) + postfix
                else:
                    name = name + postfix
            subprocess.run(
                'ffmpeg -y -i {} -map 0:{} -acodec copy {}'.format('"' + media['media_path'] + '"', track['index'],
             '"' + name + '"'))
            # import fcntal
            # cmds='ffmpeg -y -i {} -map 0:{} -acodec copy {}'.format('"' + media['media_path'] + '"', track['index'],'"' + name + '"')
            # info = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            # print(type(info))
            # print(info)
            # for line in info.stdout.readlines():
            #     print(line)
            # flags = fcntal.fcntl(p.stdout, fcntal.F_GETFL)
            # flags |= os.O_NONBLOCK
            # fcntal.fcntl(p.stdout, fcntal.F_SETFL, flags)
            # line='aa'
            # while line!=b'':
            #     line=info.stdout.readline()
            #     print(line)
                # line=line.decode()

    def extract_all_audios(self, reporthook=None):
        title = 'TAG:title'
        lang = 'TAG:language'
        audio_tracks = []
        DoneTasks = 0
        TotalTasks = 0
        for mediainfo in self.mediainfos:
            track = {}
            track['media_path'] = mediainfo['media_path']
            track['audio_tracks'] = mediainfo['audio_tracks']
            TotalTasks = TotalTasks + len(mediainfo['audio_tracks'])
            audio_tracks.append(track)
        reporthook(DoneTasks, TotalTasks)
        if not audio_tracks:
            print('No audios!!!')
        else:
            for track in audio_tracks:
                num = len(track['media_path'].split('.')[-1]) + 1
                name = track['media_path'][0:-num]
                tracks = track['audio_tracks']
                for audio_track in tracks:
                    sign = 1
                    postfix = ''
                    if 'aac' in audio_track['codec_name']:
                        postfix = '.aac'
                    elif 'vorbis' in audio_track['codec_name']:
                        postfix = '.ogg'
                    elif 'ac3' in audio_track['codec_name']:
                        postfix = '.ac3'
                    elif 'dts' in audio_track['codec_name']:
                        postfix = '.dts'
                    elif 'mp3' in audio_track['codec_name']:
                        postfix = '.mp3'
                    elif 'flac' in audio_track['codec_name']:
                        postfix = '.flac'
                    if postfix == '':
                        print('Unknown format!!!')
                    else:
                        if title in audio_track.keys():
                            sign = 0
                            name = name + '-' + audio_track[title]
                        if lang in audio_track.keys():
                            name = name + '-' + audio_track[lang]
                        if len(name) > 249:
                            name = name[0:249] + '-{}'.format(audio_track['index']) + postfix
                        else:
                            if sign:
                                name = name + '-{}'.format(audio_track['index']) + postfix
                            else:
                                name = name + postfix
                        subprocess.run(
                            'ffmpeg -y -i {} -map 0:{} -acodec copy {}'.format('"' + track['media_path'] + '"',
                                                                               audio_track['index'],
                                                                               '"' + name + '"'))
                        DoneTasks = DoneTasks + 1
                        reporthook(DoneTasks, TotalTasks)

    def extract_one_subtitle(self, media_path, index):
        track = {}
        title = 'TAG:title'
        lang = 'TAG:language'
        media = {}
        for mediainfo in self.mediainfos:
            if mediainfo['media_path'] == media_path:
                media = mediainfo
                break
        for tracks in media['subtitle_tracks']:
            if tracks['index'] == index:
                track = tracks
                break
        num = len(media['media_path'].split('.')[-1]) + 1
        name = media['media_path'][0:-num]
        sign = 1
        postfix = ''
        if 'pgs' in track['codec_name']:
            postfix = '.sup'
        elif 'ass' in track['codec_name']:
            postfix = '.ass'
        elif 'subrip' in track['codec_name']:
            postfix = '.srt'

        if postfix == '':
            print('Unknown format!!!')
        else:
            if title in track.keys():
                sign = 0
                name = name + '-' + track[title]
            if lang in track.keys():
                name = name + '-' + track[lang]
            if len(name) > 249:
                name = name[0:249] + '-{}'.format(track['index']) + postfix
            else:
                if sign:
                    name = name + '-{}'.format(track['index']) + postfix
                else:
                    name = name + postfix

            subprocess.run(
                'ffmpeg -y -i {} -map 0:{} -scodec copy {}'.format('"' + media['media_path'] + '"', track['index'],
                                                                   '"' + name + '"'))
            # cmds='ffmpeg -y -i {} -map 0:{} -scodec copy {}'.format('"' + media['media_path'] + '"', track['index'],'"' + name + '"')
            # with subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,universal_newlines=True) as info: #.communicate()#[1].decode()
            # info=subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            # print(type(info))
            # print(info)
            # for line in info.stdout.readlines():
            #         print(line.decode())

    def extract_all_subtitles(self, reporthook=None):
        title = 'TAG:title'
        lang = 'TAG:language'
        subtitle_tracks = []
        DoneTasks = 0
        TotalTasks = 0
        for mediainfo in self.mediainfos:
            track = {}
            track['media_path'] = mediainfo['media_path']
            track['subtitle_tracks'] = mediainfo['subtitle_tracks']
            TotalTasks = TotalTasks + len(mediainfo['subtitle_tracks'])
            subtitle_tracks.append(track)
        # print(TotalTasks)
        reporthook(DoneTasks, TotalTasks)
        if not subtitle_tracks:
            print('No subtitles!!!')
        else:
            for track in subtitle_tracks:
                num = len(track['media_path'].split('.')[-1]) + 1
                name = track['media_path'][0:-num]
                tracks = track['subtitle_tracks']
                sign = 1
                postfix = ''
                for subtitle_track in tracks:
                    if 'pgs' in subtitle_track['codec_name']:
                        postfix = '.sup'
                    elif 'ass' in subtitle_track['codec_name']:
                        postfix = '.ass'
                    elif 'subrip' in subtitle_track['codec_name']:
                        postfix = '.srt'

                    if postfix == '':
                        print('Unknown format!!!')
                    else:
                        if title in subtitle_track.keys():
                            sign = 0
                            name = name + '-' + subtitle_track[title]
                        if lang in track.keys():
                            name = name + '-' + subtitle_track[lang]
                        if len(name) > 249:
                            name = name[0:249] + '-{}'.format(subtitle_track['index']) + postfix
                        else:
                            if sign:
                                name = name + '-{}'.format(subtitle_track['index']) + postfix
                            else:
                                name = name + postfix
                        subprocess.run(
                            'ffmpeg -y -i {} -map 0:{} -scodec copy {}'.format('"' + track['media_path'] + '"',
                                                                               subtitle_track['index'],
                                                                               '"' + name + '"'))
                        DoneTasks = DoneTasks + 1
                        reporthook(DoneTasks, TotalTasks)

    def extract_all(self):
        # self.extract_video()
        self.extract_all_audios()
        self.extract_all_subtitles()


# ffmpeg -i "Better Call Saul (2015) - S01E01 - Uno (1080p BluRay x265 RZeroX).mkv"
#        -i "Better Call Saul (2015) - S01E01 - Uno (1080p BluRay x265 RZeroX).ass"
#        -map 0:0 -map 0:1 -map 0:4 -map 0:5 -map 1 -c:v copy -c:a copy -c:s copy
#            test.mkv
class Package(MediaInfos):
    def __init__(self, media_path=''):
        super(Package, self).__init__(media_path)

    #
    # def add_single_media(self,media_path,reporthook=None):
    #     audio_postfixs = ['aac', 'ogg', 'ac3', 'dts', 'mp3', 'flac', 'opus']
    #     sub_postfixs = ['sup', 'ssa', 'ass', 'srt', 'vtt', 'pgs']
    #     all_single_postfixs=audio_postfixs+sub_postfixs
    #
    #     media_paths_out = []
    #     if isinstance(media_path, list):
    #         for path in media_path:
    #             media_paths_out.append(path)
    #     elif media_path == '':
    #         pass
    #     elif os.path.isfile(media_path):
    #         if media_path.split('.')[-1] in all_single_postfixs:
    #             media_paths_out.append(media_path)
    #     else:
    #         files = []
    #         for dirpath, dirname, filename in os.walk(media_path):
    #             # print(dirpath,dirname,filename)
    #             if filename:
    #                 for file in filename:
    #                     files.append(dirpath + '/' + file)
    #         media_paths_out = [file for file in files if
    #                            file.split('.')[-1] in all_single_postfixs]
    #     media_path_in = []
    #     for mediainfo in self.mediainfos:
    #         media_path_in.append(mediainfo['media_path'])
    #
    #     for media_path in media_paths_out:
    #         if media_path in media_path_in:
    #             # print(media_path)
    #             # print('in')
    #             continue
    #         # video_postfixs=['mkv', 'mp4', 'rmvb', 'flv', 'mov', 'webm', 'm2ts', 'mpg', 'm4v', 'avi', 'wmv']
    #         postfix=media_path.split('.')[-1]
    #         mediainfo={}
    #         mediainfo['mediainfoIndex']=self.mediainfoIndex
    #         mediainfo['isSingle']=1
    #         mediainfo['media_path']=media_path
    #         if len(media_path.split('\\')) == 1:
    #             mediainfo['media_name'] = media_path.split('/')[-1]
    #         else:
    #             mediainfo['media_name'] = media_path.split('\\')[-1]
    #         if postfix in audio_postfixs:
    #             mediainfo['type']='audio'
    #             self.mediainfos.append(mediainfo)
    #         elif postfix in sub_postfixs:
    #             mediainfo['type']='subtitle'
    #         # elif postfix in video_postfixs:
    #             # self.add_mediainfo(media_path)
    #         else:
    #             print("Unknown formats!!!")
    #         reporthook(mediainfo)
    #         self.mediainfos.append(mediainfo)
    #         self.mediainfoIndex=self.mediainfoIndex+1

    # def get_packaged(self,media_paths,indexs,types,isSingles):
    #     # media_paths=set(media_paths)
    #     infos={}
    #     cmds=[]
    #     video_sign=0
    #     audio_sign=0
    #     sub_sign=0
    #     for media_path in set(media_paths):
    #         cmd=' -i "{}"'.format(media_path)
    #         cmds.append(cmd)
    #     count=len(media_paths)
    #     j=0
    #     for i in range(count):
    #         if isSingles[i]:
    #             j=j+1
    #             cmd=' -map {}'.format(j)
    #         else:
    #             cmd=' -map {}:{}'.format(j,indexs[i])
    #         cmds.append(cmd)
    #     final_cmd='ffmpeg'
    #     for cmd in cmds:
    #         final_cmd=final_cmd+cmd
    #     type_set=set(types)
    #     if 'video' in type_set:
    #         final_cmd=final_cmd+' -c:v copy'
    #     if 'audio' in type_set:
    #         final_cmd=final_cmd+' -c:a copy'
    #     if 'subtitle' in type_set:
    #         final_cmd=final_cmd+' -c:s copy'
    #     path=os.path.dirname(media_paths[0])
    #     print(path)
    #     final_cmd=final_cmd+' "{}\\test.mkv"'.format(path)
    #     print(final_cmd)
    #     subprocess.run(final_cmd)
    def get_packaged(self,media_paths,indexs,types,isSingles):
        cmds=[]
        infos=[]
        for media_path in set(media_paths):
            info={}
            info['media_path']=media_path
            info_indexs=[]
            # info_types=[]
            info_isSingles=[]
            for i in range(len(media_paths)):
                if media_paths[i]==media_path:
                    info_indexs.append(indexs[i])
                    # info_types.append(types[i])
                    info_isSingles.append(isSingles[i])
            info['indexs']=info_indexs
            if len(info_isSingles)>1:
                info['isSingle']=0
            else:
                info['isSingle']=1
            # info['types']=info_types
            # info['isSingles']=info_isSingles
            infos.append(info)
        i=0
        cmd ='ffmpeg'
        cmd_maps=[]
        for info in infos:
            cmd=cmd+' -i "{}"'.format(info['media_path'])
            if info['isSingle']:
                cmd_maps.append(' -map {}'.format(i))
            else:
                for index in info['indexs']:
                    cmd_maps.append(' -map {}:{}'.format(i,index))
            i=i+1
        for cmd_map in cmd_maps:
            cmd=cmd+cmd_map
        type_set=set(types)
        if 'video' in type_set:
            cmd=cmd+' -c:v copy'
        if 'audio' in type_set:
            cmd=cmd+' -c:a copy'
        if 'subtitle' in type_set:
            cmd=cmd+' -c:s copy'
        path=os.path.dirname(media_paths[0])
        # print(path)
        if len(media_paths[0].split('\\')) == 1:
            media_name= media_paths[0].split('/')[-1]
        else:
            media_name = media_paths[0].split('\\')[-1]
        count=len(media_name.split('.')[-1])+1
        media_name=media_name[:-count]
        cmd=cmd+' "{}\\{}-Packaged.mkv"'.format(path,media_name)
        print(cmd)
        subprocess.run(cmd)
