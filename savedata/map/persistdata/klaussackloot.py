# -*- coding: utf-8 -*-
from typing import Union
from pydantic import BaseModel


_StackPrefab = dict[int, Union[str, int]]


class Klaussackloot(BaseModel):

    # {index: {index: prefab_name, ...}, ...}
    # 赃物袋内的物品
    loot: dict[int, dict[int, str]]

    # 冬季盛宴活动期间的额外物品
    wintersfeast_loot: dict[int, dict[int, Union[str, _StackPrefab]]]
