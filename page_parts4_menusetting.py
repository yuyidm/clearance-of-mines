#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
from mines_file import setinfo_write, setinfo_load

window = None
game = None
var = None
var_h = None
var_w = None
var_m = None


def init(game_obj, top):
    global window, game
    game = game_obj
    window = top


def set_Tk_var():
    setinfo = setinfo_load()
    global var
    var = tk.StringVar()
    var.set(setinfo['var_l'])
    global var_h
    var_h = tk.StringVar()
    var_h.set(setinfo['var_h'])
    global var_w
    var_w = tk.StringVar()
    var_w.set(setinfo['var_w'])
    global var_m
    var_m = tk.StringVar()
    var_m.set(setinfo['var_m'])


def command_Button_qx():
    window.destroy()


def command_Button_bc():
    if var.get() == "1":
        setinfo_write(1)
    elif var.get() == "2":
        setinfo_write(2)
    elif var.get() == "3":
        setinfo_write(3)
    elif var.get() == "0":
        setinfo_write(0, int(var_w.get()), int(var_h.get()), int(var_m.get()))
    game.stop_game()
    game.init_game()
    window.destroy()
    game.start_game()


def bind_FocusOut_Entry_01(event):
    setinfo = setinfo_load()
    try:
        num_h = int(var_h.get())
        if num_h < 9:
            var_h.set(9)
        elif num_h > 24:
            var_h.set(24)
    except ValueError:
        var_h.set(setinfo['var_h'])


def bind_FocusOut_Entry_02(event):
    setinfo = setinfo_load()
    try:
        num_w = int(var_w.get())
        if num_w < 9:
            var_w.set(9)
        elif num_w > 30:
            var_w.set(30)
    except ValueError:
        var_w.set(setinfo['var_w'])


def bind_FocusOut_Entry_03(event):
    setinfo = setinfo_load()
    try:
        num_m = int(var_m.get())
        num_h = int(var_h.get())
        num_w = int(var_w.get())
        if num_m < 10:
            var_m.set(10)
        elif num_m > num_h * num_w * 9 // 10:
            var_m.set(num_h * num_w * 9 // 10)
    except ValueError:
        var_m.set(setinfo['var_m'])


if __name__ == '__main__':
    print(setinfo_load())