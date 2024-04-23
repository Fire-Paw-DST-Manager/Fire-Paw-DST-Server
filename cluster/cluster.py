# -*- coding: utf-8 -*-
from os import PathLike
from pathlib import Path
from typing import Literal, TypeAlias

from pydantic import BaseModel

WORLD_TYPE: TypeAlias = Literal["master", "cave"]


class ClusterStatus(BaseModel):
    ...


class WorldStatus(BaseModel):
    type: Literal['local', 'remote'] = 'local'

    is_running: bool = False


class Cluster:
    def __init__(self, dir_path: PathLike):
        self.status: ClusterStatus | None = None
        self.world_status: WorldStatus | None = None
        self.worlds = {}
        self.path: PathLike = Path(dir_path)
        ...

    def add_world(self, world_type: WORLD_TYPE, worldinfo: PathLike | str | dict) -> bool:
        ...

