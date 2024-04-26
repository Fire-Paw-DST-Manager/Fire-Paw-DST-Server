# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Chessunlocks(BaseModel):

    # 已解锁的棋子类型
    # {index: chess_name, ...}
    # pawn, bishop, rook, knight, muse, formal
    unlocks: dict[int, str]
