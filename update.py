#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

def update():
    fp = open("memes.txt", "w+")
    
    for mp3 in os.scandir(r"./mp3"):
        file_name = os.path.splitext(os.path.basename(mp3))[0]

        fp.write(file_name + "\n") 
