#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string

def token(): #load discord token
    with open("discord_token.txt", "r") as fp:
        token = fp.read()
    return token

def memes(): #load dictionary of memes
    with open("memes.txt", "r") as fp:
        dic = {new_list: [] for new_list in string.ascii_uppercase}
        loadDic(dic, fp)
    return dic

def stops(): #load list of stops
    with open("stop.txt", "r") as fp:
        ls = fp.read().splitlines()
    return ls

def loadDic(dic, fp):
    ls = fp.read().splitlines()

    for element in ls:
        dic[element[0]].append(element)
