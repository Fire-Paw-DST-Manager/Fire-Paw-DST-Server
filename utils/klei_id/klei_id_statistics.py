# -*- coding: utf-8 -*-
"""
数据来源
kuids               2021.02 - 2021.07  steam  in game
kuids_steam_lobby   2023.08.24         steam  from lobby


kuids 除去共同的前三位，观察剩余字符，可以发现  前五位一致的情况出现的次数异常的多，其中第六位则仅有少量一致
说明并不是随机生成，否则前两、三位一致的肯定会比前五位一致出现的次数多非常多
同时首字符从0(0)至_(63)均有出现

可变的有八位，每一位可以表示6bit，一共48bit    1 << (48 - 1) = 140,737,488,355,328
都转为bit来观察应该可以得到一些信息，比如前n位一致次数异常  看不了，二进制里都要看出2了


KU 是一起生成的，还是生成八位后补的呢

生成规则会与外源因素有关吗  时间？ip？平台？

"""

from itertools import chain
from pathlib import Path
from pydantic import BaseModel
from random import randint
from re import findall

path_ids = r'C:\Users\suke\Documents\python\dstserver\temp'
alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'


class IDs(BaseModel):
    kuids: list[str]
    kuids_lobby_steam: list[str]
    kuids_split: dict[str, list[str]]
    dirnames: list[str]


with open('klei_ids.json', 'r', encoding='utf-8') as f_:
    ids = IDs.model_validate_json(f_.read())


def collect_ids():
    ids_ = []
    for i in Path(path_ids).glob('*'):
        with i.open('r', encoding='utf-8') as f:
            ids_.extend(findall('KU_[0-9a-zA-Z-_]{8}', f.read()))
    ids_ = list(set(ids_ + ids.kuids_lobby_steam))

    rule = {j: i for i, j in enumerate(alphabet)}
    ids_.sort(key=lambda x: sum(rule[k] << ((7 - j) * 6) for j, k in enumerate(x[3:])))

    kuids_lobby_steam = ids_
    print(kuids_lobby_steam)
    print(len(kuids_lobby_steam))


def split_ids():
    result = {}
    for i in chain(ids.kuids, ids.kuids_lobby_steam):
        pre, suf = i[3:8], i[8:]
        if pre in result:
            result[pre].append(suf)
        else:
            result[pre] = [suf]

    rules = {j: i for i, j in enumerate(alphabet)}
    for j in result.values():
        j.sort(key=lambda x: rules[x[0]] << 12 | rules[x[1]] << 6 | rules[x[2]])
    kuids_split = result
    print(kuids_split)
    print(len(kuids_split))


def test():
    # 筛选出具有共同前缀的id们的前缀
    special = [i for i, j in ids.kuids_split.items() if len(j) > 1]
    # print(special)
    # print(special[randint(0, len(special))])
    print(ids.kuids_split[special[randint(0, len(special))]])
    print(f'共 {len(ids.kuids_lobby_steam + ids.kuids)} 个id， {len(ids.kuids_split)} 个键，其中 {len(special)} 个包含多个子项')

    # 统计id中KU_后首字母的分布情况
    first_char = [i[0] for i in ids.kuids_split]
    rr = {x: first_char.count(x) for x in alphabet}
    # print(rr)
    print(rr.values())

    bb = []
    for i in ids.kuids:
        bits = (alphabet.index(j) for j in i.removeprefix('KU_'))
        asd = ''.join(f'{j:0>6b}' for j in bits)
        bb.append(asd)
    print('\n'.join(bb))


def update():
    with open('klei_ids.json', 'w+', encoding='utf-8') as f:
        f.write(ids.model_dump_json())


if __name__ == "__main__":
    collect_ids()
    split_ids()
    # update()
    test()
