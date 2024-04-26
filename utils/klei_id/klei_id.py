# -*- coding: utf-8 -*-
"""
klei 的编码规则
    kleiID  base64 | bitlen(char) = 6 | len(str) = 10 | KUXXXXXXXX    # KU后的下划线属于格式要求，计算时忽略
    dirname base32 | bitlen(char) = 5 | len(str) = 12 | A7XXXXXXXXXX  # 由于kleiID的KU是固定的，所以正常情况这里前两位也必是A7

    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
"""
import json
from enum import IntEnum, StrEnum
from typing import Literal

alphabet64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
alphabet32 = alphabet64[:32]


class IDType(StrEnum):
    kleiID = 'kleiID'
    dirname = 'dirname'
    unknown = 'unknown'


arg_id_type = Literal[IDType.kleiID, IDType.dirname, IDType.unknown]


class KleiID(IntEnum):
    char_bitlen = 6
    idlen = 10


class DirName(IntEnum):
    char_bitlen = 5
    idlen = 12


class Unknown(IntEnum):
    char_bitlen = 8


def _convert(char_bits: iter, old_bitlen: int, new_bitlen: int) -> bytearray:
    """
    将待处理的char_bits按照old_bitlen补全后拼接，再按new_bitlen重新截断分配
    eg. dirname -> kuid
            old_bit_len: 5 -> new_bit_len: 6
            01010 00111 10000 00110 00001 11110 11110 00100 01001 01101 01001 01101 ->
            010100 011110 000001 100000 111110 111100 010001 001011 010100 101101
    """

    tmp, tmp_bitlen, result = 0, 0, bytearray()
    for char_bit in char_bits:
        # 更新tmp当前位数
        tmp_bitlen += old_bitlen
        # 将char_bit拼接在tmp的右端
        tmp = (tmp << old_bitlen) | char_bit

        while tmp_bitlen >= new_bitlen:
            # 缓存值右移至只有new_bitlen位，添加至结果
            result.append(tmp >> (tmp_bitlen - new_bitlen))
            # 更新tmp当前位数
            tmp_bitlen -= new_bitlen
            # 舍去已经添加到结果中的部分
            tmp &= (1 << tmp_bitlen) - 1
    if tmp_bitlen:
        # 如果tmp中还有值，左移至new_bitlen位，添加到结果中
        result.append(tmp << (new_bitlen - tmp_bitlen))
    # print(' '.join((f'{i:b}'.zfill(old_bitlen) for i in char_bits)), '->')
    # print(' '.join((f'{i:b}'.zfill(new_bitlen) for i in result)))
    return result


def d2k(text: str) -> str:
    """将 玩家存档文件夹名 转换为对应的 kleiID"""

    # underline  kleiID 中第三位是否为'_'
    # base64     是否使用 base64 字母表
    underline, base64 = True, True
    if text.startswith('__'):
        underline, base64 = False, False
        text = text.removeprefix('__')
    elif text.startswith('_'):
        underline = False
        text = text.removeprefix('_')

    char_bits = [alphabet32.find(i) for i in text]
    if -1 in char_bits:
        raise ValueError(f"{text} 中包含非法字符，所有字符都应在该字母表内：{alphabet32}")
    if base64:
        # result = ''.join(convert(char_bits, DirName.char_bitlen, KleiID.char_bitlen).decode('ascii').translate(alphabet64))
        result = ''.join(alphabet64[i] for i in _convert(char_bits, DirName.char_bitlen, KleiID.char_bitlen))
    else:
        result = _convert(char_bits, Unknown.char_bitlen, KleiID.char_bitlen).decode('utf-8')
    if underline:
        result = result.replace('KU', 'KU_', 1)
    return result


def k2d(text: str) -> str:
    """将 kleiID 转换为对应的 玩家存档文件夹名"""

    if any(i not in alphabet64 for i in text):
        # 如果包含不在字母表中的字符，进行特殊处理，可能是兼容性处理吧
        old_bitlen = Unknown.char_bitlen
        pre = '__'
        char_bits = text.encode('utf-8')
    else:
        old_bitlen = KleiID.char_bitlen
        pre = ''
        if len(text) > 2:
            if text[2] == '_':
                # 这里是正常处理，处理规范的kleiID时都会走这里
                text = text[:2] + text[3:]
            else:
                pre = '_'
        char_bits = (alphabet64.index(i) for i in text)
    result = ''.join((alphabet64[i] for i in _convert(char_bits, old_bitlen, DirName.char_bitlen)))
    return f'{pre}{result}'


def convert(text: str, id_type: arg_id_type = IDType.unknown) -> str:
    match id_type:
        case IDType.unknown:
            if text.startswith('KU'):
                return k2d(text)
            return d2k(text)
        case IDType.kleiID:
            return k2d(text)
        case IDType.dirname:
            return d2k(text)
        case _:
            raise ValueError(f'id_type 应为 {list(IDType)} 之一或留空')


def test():
    from pydantic import BaseModel

    class IDs(BaseModel):
        kuids: list[str]
        kuids_lobby_steam: list[str]
        kuids_split: dict[str, list[str]]
        dirnames: list[str]

    print('读取数据')
    with open('klei_ids.json', 'r') as f:
        ids = IDs.model_validate_json(f.read())

    print('测试开始')
    for i, j in enumerate(ids.dirnames):
        if not convert(j) == ids.kuids[i]:
            print('error', j, ids.kuids[i])
    for i, j in enumerate(ids.kuids):
        if not convert(j) == ids.dirnames[i]:
            print('error', j, ids.dirnames[i])

    print('测试完毕')


if __name__ == "__main__":
    mix: dict[arg_id_type, list[str]] = {
        IDType.kleiID: ["KU_UnXyKKKK"],
        IDType.dirname: ["A7G2Q0NNBBBB", "A7GKKKKNMK3P", "A7G2Q0NMMMMJ", "_0GGC"],
        IDType.unknown: ["A7GASDFGHJKL", "KU_UnXyZZZZ"]
    }

    converted = {}
    for id_type_, id_list in mix.items():
        converted |= {id_: convert(id_, id_type_) for id_ in id_list}

    for raw, id_ in converted.items():
        print(f'{raw.ljust(12)} -> {id_.ljust(12)}')
    l1 = ["KU_0j0lUxtw", "KU_0vPtVA95", "KU_0vPtVQh8", "KU_0vPtVTa6", "KU_0vPtVotk", "KU_1W-yG3QG"]
    l2 = [_convert([alphabet64.index(j) for j in k.replace('_', '', 1)], 6, 8) for k in l1]
    l3 = [f'{int.from_bytes(i):064b}' for i in l2]
    for i in l3:
        print(i)
    # test()
    with open('klei_ids.json', 'r') as f:
        ids = json.loads(f.read())
    print(list(ids.get('kuids_split')))


"""
TheNet:SerializeUserSession(player.userid, data, isnewspawn == true, player.player_classified ~= nil and player.player_classified.entity or nil, metadataStr)
                        str: KU_XXXXXXXX   str   bool                player.player_classified.entity c userdata                                  str  .meta文件内容 角色的 predab
TheNet:EncodeUserPath('KU_iIl1iIl1')
"""
