# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Frograin(BaseModel):

    # 青蛙雨中，玩家 50 单位范围内青蛙的数量上限
    frogcap: int
