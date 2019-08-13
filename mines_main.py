#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
@author:pengcheng(wx012357@gmail.com)
@Version:1.0.2
Update on 2019.08.13
"""

import tkinter as tk
from mines_parts import GameInfo, Menu

if __name__ == '__main__':
    top = tk.Tk()
    top.title("扫雷")
    game = GameInfo(top)
    Menu(game)
    top.mainloop()
