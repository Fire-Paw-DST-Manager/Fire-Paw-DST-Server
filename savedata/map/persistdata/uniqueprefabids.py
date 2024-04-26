# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Uniqueprefabids(BaseModel):

    # 为某些类型的 prefab 提供累加不重复的 id，记录当前已给出的值
    topprefabids: dict[str, int]
