# -*- coding: utf-8 -*-
"""
配置项根据必要程度，可以分为 可选、主世界必选、所有世界都必选。但是由于官方说明并不详细，因此很难准确归类各项，所以不做区分，每个世界都使用相同的包含全部信息的配置文件
"""
from typing import Union

from pydantic import BaseModel, Field, model_serializer

from ..sections import (
    Gameplay,
    Network,
    Misc,
    Steam,
    Shard
)

from .shard_setting import ShardSetting as World


class ClusterSetting(BaseModel):
    # cluster/cluster.ini

    GAMEPLAY: Gameplay = Field(default_factory=Gameplay)

    NETWORK: Network = Field(default_factory=Network)

    MISC: Misc = Field(default_factory=Misc)

    STEAM: Steam = Field(default_factory=Steam)

    SHARD: Shard = Field(default_factory=Shard)

    SERVERS: dict[int, World] = Field(default_factory=dict)

    def test_server(self, data):
        """
        检测
        端口是否重复
        主世界是否冲突
        世界id是否重复

        """
        ...

    @model_serializer
    def _(self) -> dict[str, Union[Gameplay, Misc, Steam, Shard]]:
        result = {}
        allow_key = ['GAMEPLAY', 'NETWORK', 'MISC', 'STEAM', 'SHARD']

        for key, value in self:
            if key in allow_key:
                result[key] = value

        return result
