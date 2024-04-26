# -*- coding: utf-8 -*-

from pydantic import BaseModel


class _Info(BaseModel):

    # 还有多久尝试再生
    regrowtime: float

    # 虽然会存，但始终都是空值，可能是以前用现在不用了吧
    density: None = None


class Desolationspawner(BaseModel):

    # {node_index: {prefab: Info}
    areas: dict[int, dict[str, _Info]]
