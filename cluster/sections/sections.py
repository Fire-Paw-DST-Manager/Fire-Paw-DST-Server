# -*- coding: utf-8 -*-
from ipaddress import IPv4Address
from time import time

from utils import get_new_cluster_name
from .default_sections import (
    DefaultGameplay,
    DefaultNetwork,
    DefaultMisc,
    DefaultSteam,
    DefaultShard,
    DefaultNetworkForShard,
    DefaultShardForShard,
    DefaultSteamForShard,
    DefaultAccountForShard
)


class Gameplay(DefaultGameplay):
    max_players: int = 8

    pause_when_empty: bool = True


class Network(DefaultNetwork):
    cluster_name: str = get_new_cluster_name()

    cluster_description: str = '我要开饥！'

    cluster_language: str = 'zh'


class Misc(DefaultMisc):
    pass


class Steam(DefaultSteam):
    pass


class Shard(DefaultShard):
    master_ip: IPv4Address = IPv4Address('127.0.0.1')

    cluster_key: str = f'FirePaw{int(time())}'


class NetworkForShard(DefaultNetworkForShard):
    pass


class ShardForShard(DefaultShardForShard):
    pass


class AccountForShard(DefaultAccountForShard):
    encode_user_path: bool = True


class SteamForShard(DefaultSteamForShard):
    pass
