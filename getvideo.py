#!/usr/bin/env python
# -*- coding: utf-8 -*-

#https://spapas.github.io/2018/03/06/easy-youtube-mp3-downloading/

import sys
from youtube_dl import YoutubeDL

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ydl_opts = {
            "format":"bestaudio/best",
            "outtmpl": "temp/%(title)s-%(id)s.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                }],
            }
        ydl = YoutubeDL(ydl_opts)
        ydl.download(sys.argv[1:])
    else:
        print("Enter list of urls to download")
        exit(0)
