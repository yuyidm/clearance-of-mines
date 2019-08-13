#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from threading import Thread
import tkinter.messagebox

game = None


def init(gameInfo):
    global game
    game = gameInfo


def command_exit():
    game.top.destroy()


def command_about():
    info = """
    版本 1.0.2
    
    作者：pcheng
    时间：2019.8.12"""
    tkinter.messagebox.showinfo(title='关于游戏', message=info)


def command_appearance():
    tkinter.messagebox.showinfo(title='提示', message='功能即将开放！')


def command_new():
    game.stop_game()

    def new_game(name):
        game.init_game()
        game.start_game()

    Thread(target=new_game, args=("new_game", )).start()


def command_setting():
    from mines_parts import MenuSetting
    MenuSetting(game)


def command_sum():
    tkinter.messagebox.showinfo(title='提示', message='功能即将开放！')

