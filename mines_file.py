#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from pickle import dump, load


def setinfo_load():
    try:
        with open("conf/set.mines", "rb") as fp:
            set_info = load(fp)
    except FileNotFoundError:
        with open("conf/set.mines", "wb") as fp:
            set_info = {
                "var_l": 3,
                "var_w": 30,
                "var_h": 16,
                "var_m": 99,
            }
            dump(set_info, fp)
    return set_info


def setinfo_write(var_l, var_w=None, var_h=None, var_m=None):
    set_info = setinfo_load()
    if var_l == 3:
        set_info["var_l"] = 3
        set_info["var_w"] = 30
        set_info["var_h"] = 16
        set_info["var_m"] = 99
    elif var_l == 2:
        set_info["var_l"] = 2
        set_info["var_w"] = 16
        set_info["var_h"] = 16
        set_info["var_m"] = 40
    elif var_l == 1:
        set_info["var_l"] = 1
        set_info["var_w"] = 10
        set_info["var_h"] = 10
        set_info["var_m"] = 9
    elif var_l == 0:
        set_info["var_l"] = 0
        set_info["var_w"] = var_w
        set_info["var_h"] = var_h
        set_info["var_m"] = var_m
    else:
        raise Exception("难度不存在！")

    with open("conf/set.Mines", "wb") as fp:
        dump(set_info, fp)


def recordinfo_load():
    try:
        with open("conf/record.mines", "rb") as fp:
            record_info = load(fp)
    except FileNotFoundError:
        with open("conf/record.mines", "wb") as fp:
            record_info = {
                1: ["初级", 0, 0, "无记录"],
                2: ["中级", 0, 0, "无记录"],
                3: ["高级", 0, 0, "无记录"],
                0: ["自定义", 0, 0, "无记录"],
            }
            dump(record_info, fp)
    return record_info


def recordinfo_write(var_l, is_winning=False):
    record_info = recordinfo_load()
    record = record_info[var_l]

    if is_winning:
        record[2] += 1
    else:
        record[1] += 1

    with open("conf/record.mines", "wb") as fp:
        dump(record_info, fp)


def historical_records(var_l, nums: int):
    record_info = recordinfo_load()
    histor = record_info[var_l][3]
    if histor == "无记录":
        histor = 100000000
    if nums < histor:
        record_info[var_l][3] = str(nums) + "秒"

    with open("conf/record.mines", "wb") as fp:
        dump(record_info, fp)
