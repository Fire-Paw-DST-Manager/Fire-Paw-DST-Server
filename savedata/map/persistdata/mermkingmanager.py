# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Mermkingmanager(BaseModel):

    # 存在多个鱼人王座时的 GUID
    # {index: GUID, ...}
    thrones: dict[int, int] = None

    # 只有一个王座时的 GUID
    throne: int = None

    # 鱼人王的 GUID
    king: int = None

    # 鱼人王候选鱼的 GUID
    candidate_transforming: int = None
