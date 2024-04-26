# -*- coding: utf-8 -*-

from pydantic import BaseModel


class _Location(BaseModel):
    x: float
    z: float


class Deerherding(BaseModel):

    # 剩余游荡时间
    grazetimer: float

    # 鹿群初始位置
    herdhomelocation: _Location = None

    # 鹿群位置
    herdlocation: _Location

    # 当前是否是正常游荡状态
    isgrazing: bool
