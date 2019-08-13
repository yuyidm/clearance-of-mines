from time import sleep
from sys import platform
from random import sample
from threading import Thread

import tkinter as tk
import tkinter.ttk as ttk

import page_parts1_lump
import page_parts2_menu
import page_parts3_gameover
import page_parts4_menusetting
from mines_file import setinfo_load, recordinfo_write, historical_records


class GameInfo:
    def __init__(self, win: tk.Tk):
        self.top = win  # 游戏主窗口
        self.timer = 0  # 游戏计时器
        self.timer_switch = True  # 游戏计时器状态
        self.lv = None  # 游戏难度
        self.w = None  # 游戏 lump_grid x轴 的数量
        self.h = None  # 游戏 lump_grid y轴 的数量
        self.m = None  # 游戏 lump_grid 中雷的数量
        self.lumps = {}  # 游戏中所有 lump_grid 的索引
        self.top_len_x = None  # 游戏主窗口 宽
        self.top_len_y = None  # 游戏主窗口 长
        self.boom_list = []  # 储存雷的坐标
        self.ing = None  # 记录游戏是否在进行
        self.Timer_obj = None  # 计时器对象

        # 开始游戏
        self.start_game()

    def _start_timer(self):
        """开启计时器线程"""

        def thread(name):
            while self.timer_switch:
                sleep(1)
                self.timer += 1
                # print("游戏时间：", self.timer)

        Thread(target=thread, args=("开始计时", ), daemon=True).start()

    def _stop_timer(self):
        """停止计时器"""
        self.timer_switch = False

    def _get_info(self):
        """初始化 游戏元素"""

        # 读取设置信息
        setinfo = setinfo_load()

        # 配置游戏信息
        self.lv = setinfo["var_l"]  # 游戏难度
        self.w = setinfo["var_w"]  # 游戏 lump_grid 在x轴的数量
        self.h = setinfo["var_h"]  # 游戏 lump_grid 在y轴的数量
        self.m = setinfo["var_m"]  # 游戏 lump_grid 中雷的数量

        # 创建游戏所有 lump_grid 索引
        for x in range(1, self.w+1):
            for y in range(1, self.h+1):
                self.lumps.update({(x, y): None})

        # 配置游戏主窗口大小
        self.top_len_x = 30 + 25 * self.w + 30  # 游戏主窗口 宽
        self.top_len_y = 60 + 25 * self.h + 30  # 游戏主窗口 长
        self.top.geometry(str(self.top_len_x) + "x" + str(self.top_len_y))

        # 生成雷的随机坐标
        total = self.w * self.h
        boom_list_bak = sample(list(range(1, total + 1)), self.m)
        for num in boom_list_bak:
            self.boom_list.append(((num - 1) % self.w + 1, (num - 1) // self.w + 1))

    def start_game(self):
        """开始游戏"""
        self.ing = True  # 游戏标记为开始
        self._get_info()  # 初始化游戏数据
        self._start_timer()  # 开始计时器
        recordinfo_write(self.lv)

        # 创建 lump 矩阵
        for lump_grid in self.lumps:
            Lump(lump_grid, self)

        # 创建 计时器
        self.Timer_obj = Timer(self)

    def stop_game(self):
        """停止游戏"""
        self._stop_timer()  # 停止计时器
        self.ing = False  # 游戏标记为结束

        # 结束游戏
        for lump_grid in self.lumps:
            lump_obj = self.lumps[lump_grid]
            if lump_obj.essence == "b9":
                lump_obj.change_laber_status(lump_obj.essence)
            else:
                lump_obj.change_laber_status(lump_obj.status)

    def init_game(self):

        # 清空 lump 矩阵
        for lump_grid in self.lumps:
            lump_obj = self.lumps[lump_grid]
            lump_obj.destroy()

        # 清除 计时器对象
        self.Timer_obj.destroy()

        # 游戏信息初始化
        self.timer = 0  # 游戏计时器
        self.timer_switch = True  # 游戏计时器状态
        self.lv = None  # 游戏难度
        self.w = None  # 游戏 lump_grid x轴 的数量
        self.h = None  # 游戏 lump_grid y轴 的数量
        self.m = None  # 游戏 lump_grid 中雷的数量

        self.lumps = {}  # 游戏中所有 lump_grid 的索引

        self.top_len_x = None  # 游戏主窗口 宽
        self.top_len_y = None  # 游戏主窗口 长

        self.boom_list = []  # 储存雷的坐标


class Lump:
    def __init__(self, grid: tuple, gameInfo: GameInfo):
        self.grid = grid  # lump_grid 的坐标
        self.gameinfo = gameInfo  # 当局 游戏信息
        self.gameinfo.lumps[self.grid] = self  # 在游戏对象中注册 lump_grid 对象
        self.essence = None  # lump_grid 的本质信息
        self._get_essence()  # 获取 lump_grid 的本质信息
        self.valid_grid_list = []  # lump_grid 周围有效 lump_grid 坐标列表
        self._valid_grid()  # 获取 lump_grid 周围有效 lump_grid 坐标列表

        self.label = tk.Label(self.gameinfo.top)  # 创建 lump_grid 的 Label 部件
        self.status = None  # Label 部件当前所处的状态
        self.is_trigger = None  # Label 部件是否被触发
        self.change_laber_status("a1")  # 设置 Label 部件的初始状态
        self.associated_events()

    def _get_essence(self):
        boom_list = self.gameinfo.boom_list
        if self.grid in boom_list:
            self.essence = "b9"
        else:
            x = self.grid[0]
            y = self.grid[1]
            content = ((x - 1, y - 1) in boom_list) + ((x, y - 1) in boom_list) + ((x + 1, y - 1) in boom_list) + \
                      ((x - 1, y) in boom_list) + ((x + 1, y) in boom_list) + \
                      ((x - 1, y + 1) in boom_list) + ((x, y + 1) in boom_list) + ((x + 1, y + 1) in boom_list)
            self.essence = "b" + str(content)

    def _valid_grid(self):
        """周围有效 lump_grid 坐标列表"""
        x = self.grid[0]
        y = self.grid[1]
        if (x - 1, y - 1) in self.gameinfo.lumps:
            self.valid_grid_list.append((x - 1, y - 1))
        if (x, y - 1) in self.gameinfo.lumps:
            self.valid_grid_list.append((x, y - 1))
        if (x + 1, y - 1) in self.gameinfo.lumps:
            self.valid_grid_list.append((x + 1, y - 1))
        if (x - 1, y) in self.gameinfo.lumps:
            self.valid_grid_list.append((x - 1, y))
        if (x + 1, y) in self.gameinfo.lumps:
            self.valid_grid_list.append((x + 1, y))
        if (x - 1, y + 1) in self.gameinfo.lumps:
            self.valid_grid_list.append((x - 1, y + 1))
        if (x, y + 1) in self.gameinfo.lumps:
            self.valid_grid_list.append((x, y + 1))
        if (x + 1, y + 1) in self.gameinfo.lumps:
            self.valid_grid_list.append((x + 1, y + 1))

    def essence_is_b0(self, grid):
        """对传入的坐标进行迭代点击"""
        lump_obj = self.gameinfo.lumps[grid]

        # 周围有标记错误 游戏结束
        if self.make_error(grid):
            self.gameinfo.stop_game()
            GameOver(self.gameinfo)
            return
        # 如果被点击直接退出
        elif lump_obj.is_trigger:
            return
        # 如果本质不为 b0
        elif lump_obj.essence != "b0":
            lump_obj.change_laber_status(lump_obj.essence)
            lump_obj.associated_events()
            return
        else:
            lump_obj.change_laber_status(lump_obj.essence)
            lump_obj.associated_events()
            for grid in lump_obj.valid_grid_list:
                self.essence_is_b0(grid)

    def make_error(self, grid):
        """查看当前 lump_grid 周围的有效 lump_grid 是否有标旗错误"""
        lump_obj = self.gameinfo.lumps[grid]

        flag_error = False
        for grid_ in lump_obj.valid_grid_list:
            lump_obj_ = self.gameinfo.lumps[grid_]
            if lump_obj_.status == "a2" and lump_obj_.essence != "b9":
                lump_obj_.change_laber_status("ax")
                flag_error = True
        return flag_error

    def change_laber_status(self, statusCode):
        """改变当前 Label 部件的形态"""

        # 获取 Label 部件的状态
        self.status = statusCode
        if statusCode == "a1" or statusCode == "a2" or statusCode == "a3":
            self.is_trigger = False
        else:
            self.is_trigger = True

        # 销毁旧 Lable，创建新 Lable
        self.label.destroy()
        self.label = tk.Label(self.gameinfo.top)
        self.label.place(x=5 + 25 * self.grid[0], y=35 + 25 * self.grid[1], height=25, width=25)
        page_parts1_lump.change_status(statusCode, self.label)

    def associated_events(self):
        # 为 Lable 关联事件
        self.label.bind("<Button-1>", self._events_button_1())
        self.label.bind("<Button-2>", self._events_button_2())
        self.label.bind("<Control-Button-1>", self._events_button_2())
        self.label.bind("<Control-Button-2>", self._events_button_2())
        self.label.bind("<Button-3>", self._events_button_3())

    def _events_button_1(self):

        def bind(event):
            # 如果 lump_grid 被触发，则无法左键点击
            if self.is_trigger:
                return

            # 点击 到雷 游戏结束
            if self.essence == "b9":
                self.gameinfo.stop_game()
                GameOver(self.gameinfo)
                return

            elif self.essence == "b0":
                self.essence_is_b0(self.grid)
            else:
                self.change_laber_status(self.essence)
                self.associated_events()

            # 统计剩余未点击的 lump 数量
            nums = 0
            for lump in self.gameinfo.lumps:
                lump_obj = self.gameinfo.lumps[lump]
                if not lump_obj.is_trigger:
                    nums += 1
            # 如果未点击数量 == 雷的数量 游戏胜利
            if nums == self.gameinfo.m:
                self.gameinfo.stop_game()
                GameOver(self.gameinfo, is_lose=False)

        return bind

    def _events_button_2(self):

        def change_colour(grid):
            lump_obj = self.gameinfo.lumps[grid]

            # 如果 lump_grid 被触发，则无变化
            if lump_obj.is_trigger:
                return

            def t(name):
                lump_obj.label.configure(background="#f0f0f0")
                sleep(0.2)
                lump_obj.label.configure(background="#898989")

            Thread(target=t, args=("闪", )).start()

        def census():
            """统计周围的有效 lump_grid 中标旗数量对应的状态和未标旗的坐标"""
            flag_nums = 0  # 标旗数量
            trigger_grid = []  # 周围未被点击 且未被标记

            for grid in self.valid_grid_list:
                lump_obj = self.gameinfo.lumps[grid]
                if lump_obj.status == "a2":
                    flag_nums += 1
                elif not lump_obj.is_trigger:
                    trigger_grid.append(grid)
            return flag_nums, trigger_grid

        def bind(event):
            # 如果 lump_grid 未被触发，则无变化
            if not self.is_trigger:
                return
            # 查看有无标记错误
            elif self.make_error(self.grid):
                self.gameinfo.stop_game()
                GameOver(self.gameinfo)
                return
            else:
                censu = census()
                # 标记数量 < 实际周围雷数
                if censu[0] != int(self.essence[-1]):
                    for grid in censu[1]:
                        change_colour(grid)
                else:
                    for grid in censu[1]:
                        if self.gameinfo.lumps[grid].essence == "b0":
                            self.essence_is_b0(grid)
                        else:
                            self.gameinfo.lumps[grid].change_laber_status(self.gameinfo.lumps[grid].essence)
                            self.gameinfo.lumps[grid].associated_events()
                    # 统计剩余未点击的 lump 数量
                    nums = 0
                    for lump in self.gameinfo.lumps:
                        lump_obj = self.gameinfo.lumps[lump]
                        if not lump_obj.is_trigger:
                            nums += 1
                    # 如果未点击数量 == 雷的数量 游戏胜利
                    if nums == self.gameinfo.m:
                        self.gameinfo.stop_game()
                        GameOver(self.gameinfo, is_lose=False)
        return bind

    def _events_button_3(self):

        def bind_button_3(event):
            if self.status == "a1":
                self.change_laber_status("a2")
                self.associated_events()
            elif self.status == "a2":
                self.change_laber_status("a3")
                self.associated_events()
            elif self.status == "a3":
                self.change_laber_status("a1")
                self.associated_events()

        return bind_button_3

    def destroy(self):
        self.label.destroy()


class Timer:
    def __init__(self, gameInfo: GameInfo):

        top = gameInfo.top
        w = gameInfo.w
        m = gameInfo.m

        font1 = "-family {Microsoft YaHei UI} -size 23 -weight bold -slant roman -underline 0 -overstrike 0"
        font2 = "-family {Microsoft YaHei UI} -size 24 -weight bold -slant roman -underline 0 -overstrike 0"

        self.Label_1 = tk.Label(top)
        self.Label_1.place(x=60, y=10, height=40, width=100)
        self.Label_1.configure(background="#898989")
        self.Label_1.configure(borderwidth="3")
        self.Label_1.configure(disabledforeground="#a3a3a3")
        self.Label_1.configure(font=font2)
        self.Label_1.configure(foreground="#ffffff")
        self.Label_1.configure(relief='sunken')
        self.Label_1.configure(text=0)
        self.Label_1.configure(width=100)

        self.Label_2 = tk.Label(top)
        self.Label_2.place(x=(25 * w - 100), y=10, height=40, width=100)
        self.Label_2.configure(activebackground="#f9f9f9")
        self.Label_2.configure(activeforeground="black")
        self.Label_2.configure(background="#898989")
        self.Label_2.configure(borderwidth="3")
        self.Label_2.configure(disabledforeground="#a3a3a3")
        self.Label_2.configure(font=font1)
        self.Label_2.configure(foreground="#ffffff")
        self.Label_2.configure(highlightbackground="#d9d9d9")
        self.Label_2.configure(highlightcolor="black")
        self.Label_2.configure(relief='sunken')
        self.Label_2.configure(text=m)

        def thread_timer(name):
            times = gameInfo.timer
            while gameInfo.ing:
                sleep(0.1)
                if times != gameInfo.timer:
                    times = gameInfo.timer
                    try:
                        self.Label_1.configure(text=times)
                    except tk.TclError:
                        pass

        Thread(target=thread_timer, args=("计时",), daemon=True).start()

        def thread_m(name):

            def count_num():
                try:
                    num = 0
                    for lump in gameInfo.lumps:
                        lump_obj = gameInfo.lumps[lump]
                        if lump_obj.status == "a2":
                            num += 1
                    return num
                except AttributeError:
                    return 0

            num = count_num()
            while gameInfo.ing:
                sleep(0.1)
                num0 = count_num()
                if num != num0:
                    num = num0
                    self.Label_2.configure(text=m - num)

        Thread(target=thread_m, args=("计雷",), daemon=True).start()

    def destroy(self):
        self.Label_1.destroy()
        self.Label_2.destroy()


class Menu:
    def __init__(self, gameInfo: GameInfo):
        page_parts2_menu.init(gameInfo)

        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        top = gameInfo.top

        self.menubar = tk.Menu(top, font="TkMenuFont", bg=_bgcolor, fg=_fgcolor)
        top.configure(menu=self.menubar)

        self.sub_menu = tk.Menu(top, tearoff=0)
        self.menubar.add_cascade(menu=self.sub_menu,
                                 activebackground="#ececec",
                                 activeforeground="#000000",
                                 background="#d9d9d9",
                                 font="TkMenuFont",
                                 foreground="#000000",
                                 label="游戏")
        self.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            command=page_parts2_menu.command_new,
            font="TkMenuFont",
            foreground="#000000",
            label="新游戏")
        self.sub_menu.add_separator(
            background="#d9d9d9")
        self.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            command=page_parts2_menu.command_sum,
            font="TkMenuFont",
            foreground="#000000",
            label="统计信息")
        self.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            command=page_parts2_menu.command_setting,
            font="TkMenuFont",
            foreground="#000000",
            label="选项")
        self.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            command=page_parts2_menu.command_appearance,
            font="TkMenuFont",
            foreground="#000000",
            label="更改外观")
        self.sub_menu.add_separator(
            background="#d9d9d9")
        self.sub_menu.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            command=page_parts2_menu.command_exit,
            font="TkMenuFont",
            foreground="#000000",
            label="退出")
        self.sub_menu1 = tk.Menu(top, tearoff=0)
        self.menubar.add_cascade(menu=self.sub_menu1,
                                 activebackground="#ececec",
                                 activeforeground="#000000",
                                 background="#d9d9d9",
                                 font="TkMenuFont",
                                 foreground="#000000",
                                 label="帮助")
        self.sub_menu1.add_command(
            activebackground="#ececec",
            activeforeground="#000000",
            background="#d9d9d9",
            command=page_parts2_menu.command_about,
            font="TkMenuFont",
            foreground="#000000",
            label="关于游戏")


class GameOver:
    def __init__(self, gameInfo: GameInfo, is_lose=True):

        if is_lose:
            text1 = "游戏失败"
            text2 = '''不好意思，您输了。下次走运！'''
        else:
            text1 = "游戏胜利"
            text2 = '''恭喜恭喜，您赢了。再接再厉！'''
            recordinfo_write(gameInfo.lv, is_winning=True)
            historical_records(gameInfo.lv, gameInfo.timer)

        top = tk.Toplevel(gameInfo.top)
        page_parts3_gameover.init(gameInfo, top)
        page_parts3_gameover.set_Tk_var()

        top.geometry("466x248+586+125")
        top.title(text1)
        top.configure(background="#d9d9d9")

        self.Button_1 = tk.Button(top)
        self.Button_1.place(relx=0.15, rely=0.766, height=28, width=99)
        self.Button_1.configure(activebackground="#ececec")
        self.Button_1.configure(activeforeground="#000000")
        self.Button_1.configure(background="#d9d9d9")
        self.Button_1.configure(command=page_parts3_gameover.command_quit)
        self.Button_1.configure(disabledforeground="#a3a3a3")
        self.Button_1.configure(foreground="#000000")
        self.Button_1.configure(highlightbackground="#d9d9d9")
        self.Button_1.configure(highlightcolor="black")
        self.Button_1.configure(pady="0")
        self.Button_1.configure(text='''退出''')
        self.Button_1.configure(width=99)

        self.Button_2 = tk.Button(top)
        self.Button_2.place(relx=0.644, rely=0.766, height=28, width=99)
        self.Button_2.configure(activebackground="#ececec")
        self.Button_2.configure(activeforeground="#000000")
        self.Button_2.configure(background="#d9d9d9")
        self.Button_2.configure(command=page_parts3_gameover.command_newgame)
        self.Button_2.configure(disabledforeground="#a3a3a3")
        self.Button_2.configure(foreground="#000000")
        self.Button_2.configure(highlightbackground="#d9d9d9")
        self.Button_2.configure(highlightcolor="black")
        self.Button_2.configure(pady="0")
        self.Button_2.configure(text='''再玩一局''')

        self.Label_1 = tk.Label(top)
        self.Label_1.place(relx=0.258, rely=0.081, height=23, width=227)
        self.Label_1.configure(background="#d9d9d9")
        self.Label_1.configure(disabledforeground="#a3a3a3")
        self.Label_1.configure(foreground="#000000")
        self.Label_1.configure(text=text2)
        self.Label_1.configure(width=227)

        self.Label_2 = tk.Label(top)
        self.Label_2.place(relx=0.322, rely=0.363, height=23, width=66)
        self.Label_2.configure(background="#d9d9d9")
        self.Label_2.configure(disabledforeground="#a3a3a3")
        self.Label_2.configure(foreground="#000000")
        self.Label_2.configure(text='''游戏难度：''')

        self.Label_3 = tk.Label(top)
        self.Label_3.place(relx=0.322, rely=0.444, height=23, width=66)
        self.Label_3.configure(activebackground="#f9f9f9")
        self.Label_3.configure(activeforeground="black")
        self.Label_3.configure(background="#d9d9d9")
        self.Label_3.configure(disabledforeground="#a3a3a3")
        self.Label_3.configure(foreground="#000000")
        self.Label_3.configure(highlightbackground="#d9d9d9")
        self.Label_3.configure(highlightcolor="black")
        self.Label_3.configure(text='''已玩游戏：''')

        self.Label_4 = tk.Label(top)
        self.Label_4.place(relx=0.322, rely=0.524, height=23, width=66)
        self.Label_4.configure(activebackground="#f9f9f9")
        self.Label_4.configure(activeforeground="black")
        self.Label_4.configure(background="#d9d9d9")
        self.Label_4.configure(disabledforeground="#a3a3a3")
        self.Label_4.configure(foreground="#000000")
        self.Label_4.configure(highlightbackground="#d9d9d9")
        self.Label_4.configure(highlightcolor="black")
        self.Label_4.configure(text='''游戏胜率：''')

        self.Label_2_1 = tk.Label(top)
        self.Label_2_1.place(relx=0.472, rely=0.363, height=23, width=60)
        self.Label_2_1.configure(anchor='nw')
        self.Label_2_1.configure(background="#d9d9d9")
        self.Label_2_1.configure(disabledforeground="#a3a3a3")
        self.Label_2_1.configure(foreground="#000000")
        self.Label_2_1.configure(textvariable=page_parts3_gameover.nan_du)

        self.Label_3_1 = tk.Label(top)
        self.Label_3_1.place(relx=0.472, rely=0.444, height=23, width=60)
        self.Label_3_1.configure(activebackground="#f9f9f9")
        self.Label_3_1.configure(activeforeground="black")
        self.Label_3_1.configure(anchor='nw')
        self.Label_3_1.configure(background="#d9d9d9")
        self.Label_3_1.configure(disabledforeground="#a3a3a3")
        self.Label_3_1.configure(foreground="#000000")
        self.Label_3_1.configure(highlightbackground="#d9d9d9")
        self.Label_3_1.configure(highlightcolor="black")
        self.Label_3_1.configure(textvariable=page_parts3_gameover.ju_shu)

        self.Label_4_1 = tk.Label(top)
        self.Label_4_1.place(relx=0.472, rely=0.524, height=23, width=60)
        self.Label_4_1.configure(activebackground="#f9f9f9")
        self.Label_4_1.configure(activeforeground="black")
        self.Label_4_1.configure(anchor='nw')
        self.Label_4_1.configure(background="#d9d9d9")
        self.Label_4_1.configure(disabledforeground="#a3a3a3")
        self.Label_4_1.configure(foreground="#000000")
        self.Label_4_1.configure(highlightbackground="#d9d9d9")
        self.Label_4_1.configure(highlightcolor="black")
        self.Label_4_1.configure(textvariable=page_parts3_gameover.sheng_lv)

        tk.Label(top).bind("<Destroy>", page_parts3_gameover.band_newgame)


class MenuSetting:
    def __init__(self, gameInfo: GameInfo):
        top = tk.Toplevel(gameInfo.top)

        page_parts4_menusetting.init(gameInfo, top)
        page_parts4_menusetting.set_Tk_var()

        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9'  # X11 color: 'gray85'
        _ana1color = '#d9d9d9'  # X11 color: 'gray85'
        _ana2color = '#ececec'  # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.', background=_bgcolor)
        self.style.configure('.', foreground=_fgcolor)
        self.style.configure('.', font="TkDefaultFont")
        self.style.map('.', background=[('selected', _compcolor), ('active', _ana2color)])

        top.geometry("460x370")
        top.title("设置")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        self.menubar = tk.Menu(top, font="TkMenuFont", bg=_bgcolor, fg=_fgcolor)
        top.configure(menu=self.menubar)

        self.TLabelframe_ld = ttk.Labelframe(top)
        self.TLabelframe_ld.place(relx=0.043, rely=0.054, relheight=0.716, relwidth=0.891)
        self.TLabelframe_ld.configure(relief='groove')
        self.TLabelframe_ld.configure(text='''难度''')
        self.TLabelframe_ld.configure(relief='groove')
        self.TLabelframe_ld.configure(width=410)

        self.TFrame_1 = ttk.Frame(self.TLabelframe_ld)
        self.TFrame_1.place(relx=0.073, rely=0.075, relheight=0.283, relwidth=0.378, bordermode='ignore')
        self.TFrame_1.configure(relief='ridge')
        self.TFrame_1.configure(borderwidth="2")
        self.TFrame_1.configure(relief='ridge')
        self.TFrame_1.configure(width=155)

        self.style.map('TRadiobutton', background=[('selected', _bgcolor), ('active', _ana2color)])
        self.TRadiobutton_1 = ttk.Radiobutton(self.TFrame_1)
        self.TRadiobutton_1.place(relx=0.065, rely=0.267, relwidth=0.148, relheight=0.0, height=23)
        self.TRadiobutton_1.configure(variable=page_parts4_menusetting.var)
        self.TRadiobutton_1.configure(takefocus="")

        self.Label_11 = tk.Label(self.TFrame_1)
        self.Label_11.place(relx=0.194, rely=0.133, height=13, width=30)
        self.Label_11.configure(activebackground="#f9f9f9")
        self.Label_11.configure(activeforeground="black")
        self.Label_11.configure(background="#d9d9d9")
        self.Label_11.configure(disabledforeground="#a3a3a3")
        self.Label_11.configure(foreground="#000000")
        self.Label_11.configure(highlightbackground="#d9d9d9")
        self.Label_11.configure(highlightcolor="black")
        self.Label_11.configure(text='''初级''')

        self.Label_12 = tk.Label(self.TFrame_1)
        self.Label_12.place(relx=0.194, rely=0.4, height=13, width=50)
        self.Label_12.configure(activebackground="#f9f9f9")
        self.Label_12.configure(activeforeground="black")
        self.Label_12.configure(background="#d9d9d9")
        self.Label_12.configure(disabledforeground="#a3a3a3")
        self.Label_12.configure(foreground="#000000")
        self.Label_12.configure(highlightbackground="#d9d9d9")
        self.Label_12.configure(highlightcolor="black")
        self.Label_12.configure(text='''10 个雷''')

        self.Label_13 = tk.Label(self.TFrame_1)
        self.Label_13.place(relx=0.194, rely=0.667, height=13, width=90)
        self.Label_13.configure(activebackground="#f9f9f9")
        self.Label_13.configure(activeforeground="black")
        self.Label_13.configure(background="#d9d9d9")
        self.Label_13.configure(disabledforeground="#a3a3a3")
        self.Label_13.configure(foreground="#000000")
        self.Label_13.configure(highlightbackground="#d9d9d9")
        self.Label_13.configure(highlightcolor="black")
        self.Label_13.configure(text='''9 x 9 平铺网格''')

        self.TFrame_2 = ttk.Frame(self.TLabelframe_ld)
        self.TFrame_2.place(relx=0.073, rely=0.377, relheight=0.283, relwidth=0.378, bordermode='ignore')
        self.TFrame_2.configure(relief='ridge')
        self.TFrame_2.configure(borderwidth="2")
        self.TFrame_2.configure(relief='ridge')
        self.TFrame_2.configure(width=155)

        self.TRadiobutton_2 = ttk.Radiobutton(self.TFrame_2)
        self.TRadiobutton_2.place(relx=0.065, rely=0.267, relwidth=0.148, relheight=0.0, height=23)
        self.TRadiobutton_2.configure(variable=page_parts4_menusetting.var)
        self.TRadiobutton_2.configure(value="2")
        self.TRadiobutton_2.configure(takefocus="")

        self.Label_21 = tk.Label(self.TFrame_2)
        self.Label_21.place(relx=0.194, rely=0.133, height=13, width=30)
        self.Label_21.configure(activebackground="#f9f9f9")
        self.Label_21.configure(activeforeground="black")
        self.Label_21.configure(background="#d9d9d9")
        self.Label_21.configure(disabledforeground="#a3a3a3")
        self.Label_21.configure(foreground="#000000")
        self.Label_21.configure(highlightbackground="#d9d9d9")
        self.Label_21.configure(highlightcolor="black")
        self.Label_21.configure(text='''中级''')

        self.Label_22 = tk.Label(self.TFrame_2)
        self.Label_22.place(relx=0.194, rely=0.4, height=13, width=50)
        self.Label_22.configure(activebackground="#f9f9f9")
        self.Label_22.configure(activeforeground="black")
        self.Label_22.configure(background="#d9d9d9")
        self.Label_22.configure(disabledforeground="#a3a3a3")
        self.Label_22.configure(foreground="#000000")
        self.Label_22.configure(highlightbackground="#d9d9d9")
        self.Label_22.configure(highlightcolor="black")
        self.Label_22.configure(text='''40 个雷''')

        self.Label_23 = tk.Label(self.TFrame_2)
        self.Label_23.place(relx=0.194, rely=0.667, height=13, width=100)
        self.Label_23.configure(activebackground="#f9f9f9")
        self.Label_23.configure(activeforeground="black")
        self.Label_23.configure(background="#d9d9d9")
        self.Label_23.configure(disabledforeground="#a3a3a3")
        self.Label_23.configure(foreground="#000000")
        self.Label_23.configure(highlightbackground="#d9d9d9")
        self.Label_23.configure(highlightcolor="black")
        self.Label_23.configure(text='''16 x 16 平铺网格''')

        self.TFrame_3 = ttk.Frame(self.TLabelframe_ld)
        self.TFrame_3.place(relx=0.073, rely=0.679, relheight=0.283, relwidth=0.378, bordermode='ignore')
        self.TFrame_3.configure(relief='ridge')
        self.TFrame_3.configure(borderwidth="2")
        self.TFrame_3.configure(relief='ridge')
        self.TFrame_3.configure(width=155)

        self.TRadiobutton_3 = ttk.Radiobutton(self.TFrame_3)
        self.TRadiobutton_3.place(relx=0.065, rely=0.267, relwidth=0.148, relheight=0.0, height=23)
        self.TRadiobutton_3.configure(variable=page_parts4_menusetting.var)
        self.TRadiobutton_3.configure(value="3")
        self.TRadiobutton_3.configure(takefocus="")

        self.Label_31 = tk.Label(self.TFrame_3)
        self.Label_31.place(relx=0.194, rely=0.133, height=13, width=30)
        self.Label_31.configure(activebackground="#f9f9f9")
        self.Label_31.configure(activeforeground="black")
        self.Label_31.configure(background="#d9d9d9")
        self.Label_31.configure(disabledforeground="#a3a3a3")
        self.Label_31.configure(foreground="#000000")
        self.Label_31.configure(highlightbackground="#d9d9d9")
        self.Label_31.configure(highlightcolor="black")
        self.Label_31.configure(text='''高级''')

        self.Label_32 = tk.Label(self.TFrame_3)
        self.Label_32.place(relx=0.194, rely=0.333, height=13, width=50)
        self.Label_32.configure(activebackground="#f9f9f9")
        self.Label_32.configure(activeforeground="black")
        self.Label_32.configure(background="#d9d9d9")
        self.Label_32.configure(disabledforeground="#a3a3a3")
        self.Label_32.configure(foreground="#000000")
        self.Label_32.configure(highlightbackground="#d9d9d9")
        self.Label_32.configure(highlightcolor="black")
        self.Label_32.configure(text='''99个雷''')

        self.Label_33 = tk.Label(self.TFrame_3)
        self.Label_33.place(relx=0.194, rely=0.6, height=13, width=100)
        self.Label_33.configure(activebackground="#f9f9f9")
        self.Label_33.configure(activeforeground="black")
        self.Label_33.configure(background="#d9d9d9")
        self.Label_33.configure(disabledforeground="#a3a3a3")
        self.Label_33.configure(foreground="#000000")
        self.Label_33.configure(highlightbackground="#d9d9d9")
        self.Label_33.configure(highlightcolor="black")
        self.Label_33.configure(text='''16 x 30 平铺网格''')

        self.TFrame_0 = ttk.Frame(self.TLabelframe_ld)
        self.TFrame_0.place(relx=0.537, rely=0.075, relheight=0.434, relwidth=0.427, bordermode='ignore')
        self.TFrame_0.configure(relief='ridge')
        self.TFrame_0.configure(borderwidth="2")
        self.TFrame_0.configure(relief='ridge')
        self.TFrame_0.configure(width=175)

        self.TRadiobutton_0 = ttk.Radiobutton(self.TFrame_0)
        self.TRadiobutton_0.place(relx=0.057, rely=0.043, relwidth=0.131, relheight=0.0, height=23)
        self.TRadiobutton_0.configure(variable=page_parts4_menusetting.var)
        self.TRadiobutton_0.configure(value="0")
        self.TRadiobutton_0.configure(takefocus="")

        self.Label_01 = tk.Label(self.TFrame_0)
        self.Label_01.place(relx=0.171, rely=0.087, height=13, width=40)
        self.Label_01.configure(activebackground="#f9f9f9")
        self.Label_01.configure(activeforeground="black")
        self.Label_01.configure(background="#d9d9d9")
        self.Label_01.configure(disabledforeground="#a3a3a3")
        self.Label_01.configure(foreground="#000000")
        self.Label_01.configure(highlightbackground="#d9d9d9")
        self.Label_01.configure(highlightcolor="black")
        self.Label_01.configure(text='''自定义''')

        self.Label_02 = tk.Label(self.TFrame_0)
        self.Label_02.place(relx=0.114, rely=0.261, height=23, width=67)
        self.Label_02.configure(activebackground="#f9f9f9")
        self.Label_02.configure(activeforeground="black")
        self.Label_02.configure(background="#d9d9d9")
        self.Label_02.configure(disabledforeground="#a3a3a3")
        self.Label_02.configure(foreground="#000000")
        self.Label_02.configure(highlightbackground="#d9d9d9")
        self.Label_02.configure(highlightcolor="black")
        self.Label_02.configure(text='''高度(9-24):''')

        self.Label_03 = tk.Label(self.TFrame_0)
        self.Label_03.place(relx=0.114, rely=0.435, height=23, width=67)
        self.Label_03.configure(activebackground="#f9f9f9")
        self.Label_03.configure(activeforeground="black")
        self.Label_03.configure(background="#d9d9d9")
        self.Label_03.configure(disabledforeground="#a3a3a3")
        self.Label_03.configure(foreground="#000000")
        self.Label_03.configure(highlightbackground="#d9d9d9")
        self.Label_03.configure(highlightcolor="black")
        self.Label_03.configure(text='''宽度(9-30):''')

        self.Entry_01 = tk.Entry(self.TFrame_0)
        self.Entry_01.place(relx=0.629, rely=0.261, height=17, relwidth=0.309)
        self.Entry_01.configure(background="white")
        self.Entry_01.configure(disabledforeground="#a3a3a3")
        self.Entry_01.configure(font="TkFixedFont")
        self.Entry_01.configure(foreground="#000000")
        self.Entry_01.configure(highlightbackground="#d9d9d9")
        self.Entry_01.configure(highlightcolor="black")
        self.Entry_01.configure(insertbackground="black")
        self.Entry_01.configure(selectbackground="#c4c4c4")
        self.Entry_01.configure(selectforeground="black")
        self.Entry_01.configure(textvariable=page_parts4_menusetting.var_h)
        self.Entry_01.bind("<FocusOut>", page_parts4_menusetting.bind_FocusOut_Entry_01)

        self.Entry_02 = tk.Entry(self.TFrame_0)
        self.Entry_02.place(relx=0.629, rely=0.478, height=17, relwidth=0.309)
        self.Entry_02.configure(background="white")
        self.Entry_02.configure(disabledforeground="#a3a3a3")
        self.Entry_02.configure(font="TkFixedFont")
        self.Entry_02.configure(foreground="#000000")
        self.Entry_02.configure(highlightbackground="#d9d9d9")
        self.Entry_02.configure(highlightcolor="black")
        self.Entry_02.configure(insertbackground="black")
        self.Entry_02.configure(selectbackground="#c4c4c4")
        self.Entry_02.configure(selectforeground="black")
        self.Entry_02.configure(textvariable=page_parts4_menusetting.var_w)
        self.Entry_02.bind("<FocusOut>", page_parts4_menusetting.bind_FocusOut_Entry_02)

        self.Entry_03 = tk.Entry(self.TFrame_0)
        self.Entry_03.place(relx=0.629, rely=0.696, height=17, relwidth=0.309)
        self.Entry_03.configure(background="white")
        self.Entry_03.configure(disabledforeground="#a3a3a3")
        self.Entry_03.configure(font="TkFixedFont")
        self.Entry_03.configure(foreground="#000000")
        self.Entry_03.configure(highlightbackground="#d9d9d9")
        self.Entry_03.configure(highlightcolor="black")
        self.Entry_03.configure(insertbackground="black")
        self.Entry_03.configure(selectbackground="#c4c4c4")
        self.Entry_03.configure(selectforeground="black")
        self.Entry_03.configure(textvariable=page_parts4_menusetting.var_m)
        self.Entry_03.bind("<FocusOut>", page_parts4_menusetting.bind_FocusOut_Entry_03)

        self.Label_04 = tk.Label(self.TFrame_0)
        self.Label_04.place(relx=0.057, rely=0.652, height=23, width=77)
        self.Label_04.configure(activebackground="#f9f9f9")
        self.Label_04.configure(activeforeground="black")
        self.Label_04.configure(background="#d9d9d9")
        self.Label_04.configure(disabledforeground="#a3a3a3")
        self.Label_04.configure(foreground="#000000")
        self.Label_04.configure(highlightbackground="#d9d9d9")
        self.Label_04.configure(highlightcolor="black")
        self.Label_04.configure(text='''雷数(10-90%):''')
        self.Label_04.configure(width=77)

        self.TFrame_dl = ttk.Frame(top)
        self.TFrame_dl.place(relx=0.043, rely=0.811, relheight=0.095, relwidth=0.989)
        self.TFrame_dl.configure(relief='flat')
        self.TFrame_dl.configure(borderwidth="2")
        self.TFrame_dl.configure(relief='flat')
        self.TFrame_dl.configure(width=455)

        self.Button_qx = tk.Button(self.TFrame_dl)
        self.Button_qx.place(relx=0.593, rely=0.0, height=28, width=55)
        self.Button_qx.configure(activebackground="#ececec")
        self.Button_qx.configure(activeforeground="#000000")
        self.Button_qx.configure(background="#d9d9d9")
        self.Button_qx.configure(command=page_parts4_menusetting.command_Button_qx)
        self.Button_qx.configure(disabledforeground="#a3a3a3")
        self.Button_qx.configure(foreground="#000000")
        self.Button_qx.configure(highlightbackground="#d9d9d9")
        self.Button_qx.configure(highlightcolor="black")
        self.Button_qx.configure(pady="0")
        self.Button_qx.configure(text='''取消''')

        self.Button_bc = tk.Button(self.TFrame_dl)
        self.Button_bc.place(relx=0.736, rely=0.0, height=28, width=55)
        self.Button_bc.configure(activebackground="#ececec")
        self.Button_bc.configure(activeforeground="#000000")
        self.Button_bc.configure(background="#d9d9d9")
        self.Button_bc.configure(command=page_parts4_menusetting.command_Button_bc)
        self.Button_bc.configure(disabledforeground="#a3a3a3")
        self.Button_bc.configure(foreground="#000000")
        self.Button_bc.configure(highlightbackground="#d9d9d9")
        self.Button_bc.configure(highlightcolor="black")
        self.Button_bc.configure(pady="0")
        self.Button_bc.configure(text='''保存''')
