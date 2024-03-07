# -*- coding: utf-8 -*-

from enum import Enum, IntEnum, IntFlag
from re import compile as re_compile
from typing import Pattern


class Universes(IntEnum):
    invalid  = 0
    public   = 1
    beta     = 2
    interval = 3
    dev      = 4
    # rc     = 5


class Types(IntEnum):
    invalid          = 0   # 不属于其他类别的机器人和帐号
    individual       = 1   # 单用户
    multiseat        = 2   # 多用户 如网吧
    game_server      = 3   # 游戏服务器
    anon_game_server = 4   # 匿名游戏服务器
    pending          = 5   # 单用户帐号在等待 steam 验证期间的临时状态
    content_server   = 6   # 内容服务器
    clan             = 7   # steam 群组
    chat             = 8   # 聊天，包含 多用户聊天T、群组聊天c、steam大厅聊天L
    console_user     = 9   # PS3 的本地帐号和 XBOX360 live 帐号等 使用的虚假帐号
    anon_user        = 10  # 匿名用户

    P2P_super_seeder = console_user


class TypeChars(IntEnum):
    I = Types.invalid.value
    U = Types.individual.value
    M = Types.multiseat.value
    G = Types.game_server.value
    A = Types.anon_game_server.value
    P = Types.pending.value
    C = Types.content_server.value
    g = Types.clan.value
    T = Types.chat.value      # 多用户聊天
    a = Types.anon_user.value

    i = I

    c = T                     # 群组聊天
    L = T                     # steam 大厅聊天


class Instances(IntEnum):
    all     = 0
    desktop = 1
    console = 2
    web     = 4


def _bit_fill_1(bit_length: int) -> int:
    """3 -> 0b111"""
    return (1 << bit_length) - 1


class BitLength(IntEnum):
    full        = 64

    universe    = 8
    type        = 4
    instance    = 20
    account_id  = 32

    account_pre = 31
    account_suf = 1

    auth_server = account_suf


class Masks(IntFlag):
    type        = _bit_fill_1(BitLength.type)
    universe    = _bit_fill_1(BitLength.universe)
    instance    = _bit_fill_1(BitLength.instance)
    account_pre = _bit_fill_1(BitLength.account_pre)
    account_suf = _bit_fill_1(BitLength.account_suf)


# 聊天使用的特殊 instance，使用前面的 bit
class InstanceFlags(IntFlag):
    chat_clan      = (Masks.instance + 1) >> 1
    chat_lobby     = (Masks.instance + 1) >> 2
    chat_MMS_lobby = (Masks.instance + 1) >> 3


class MaxValue(IntEnum):
    account_pre = _bit_fill_1(BitLength.account_pre)
    account_suf = _bit_fill_1(BitLength.account_suf)
    account_id  = _bit_fill_1(BitLength.account_id)
    instance    = _bit_fill_1(BitLength.instance)
    steam_id    = _bit_fill_1(BitLength.full)


# 除了 U, g, c, L, T，这几个（个人、群组、聊天），其他应该都是不准的
# 因为在不同的地方看到了不同的写法（一个是置0一个是置1）
# 而且使用匿名游戏服务器测试发现，instance 不是固定值，几个服务器的都不相同
class TypeCharsToInstances(IntEnum):
    I = Instances.all
    U = Instances.desktop
    M = Instances.all
    G = Instances.all
    A = Instances.all
    P = Instances.all
    C = Instances.all
    g = Instances.all
    T = Instances.all
    a = Instances.all

    i = I

    c = InstanceFlags.chat_clan
    L = InstanceFlags.chat_lobby


class Patterns(Enum):
    # \d{0, 20}
    steamID64: Pattern = re_compile('^[0-9]{0,20}$')  # f'^[0-9]{{0,{len(str(MaxValue.steam_id))}}}$'
    steamID: Pattern = steamID64

    # STEAM_X:Y:Z
    steamID32: Pattern = re_compile('^STEAM_(?P<universe>[0-5]):(?P<account_suf>[0-1]):(?P<account_pre>[0-9]{1,10})$')
    steamID2: Pattern = steamID32

    # [N:1:M[:O]]
    steamID3: Pattern = re_compile(
        '^\\[(?P<type>[AGMPCgcLTIUai]):(?P<universe>[0-4]):(?P<account_id>[0-9]{0,10})(?::(?P<instance>[0-9]+))?]$')
