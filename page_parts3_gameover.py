#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
from mines_file import recordinfo_load


def init(gameInfo, top_obj):
    global game
    game = gameInfo
    global top
    top = top_obj
    global recordinfo
    recordinfo = recordinfo_load()


nan_du = None
ju_shu = None
sheng_lv = None


def set_Tk_var():
    global nan_du
    nan_du = tk.StringVar()
    nan_du.set(recordinfo[game.lv][0])
    global ju_shu
    ju_shu = tk.StringVar()
    ju_shu.set("%d 局" % recordinfo[game.lv][1])
    global sheng_lv
    sheng_lv = tk.StringVar()
    var_a = (recordinfo[game.lv][2] / recordinfo[game.lv][1]) * 100
    sheng_lv.set("%.2f %%" % var_a)


def band_newgame(e):
    game.init_game()
    game.start_game()


def command_newgame():
    top.destroy()


def command_quit():
    game.top.destroy()


