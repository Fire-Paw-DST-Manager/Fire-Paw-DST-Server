# -*- coding: utf-8 -*-
from typing import Literal
from pydantic import BaseModel


class Lunarriftmutationsmanager(BaseModel):

    # 该轮循环已被击败的突变生物的索引
    # {"mutatedwarg": 1, "mutatedbearger": 2, "mutateddeerclops": 3}
    # {index: mutation_index}
    defeated_mutations: dict[int, int] = None

    # 是否已经打败过首轮三个突变生物
    task_completed: Literal[True] = None
