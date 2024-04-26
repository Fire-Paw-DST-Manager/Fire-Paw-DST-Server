# -*- coding: utf-8 -*-
from collections import namedtuple
from itertools import product, chain
from savedata import SaveData


savedata = SaveData('../../../src/saved_data/0000020657')
map_data = savedata.map.tiles
width = savedata.map.width
height = savedata.map.height

tile = tuple(map_data[i * height: (i + 1) * height] for i in range(width))

# 要铺的地皮类型
tile_codes = [*range(35, 42), 78]

# 铺的结果是 一个大区域，分为若干行，每行有若干个不同的地皮矩形

# 每块地皮矩形的边长
size = 20
# 起始点
start_point = namedtuple('start_point', ['x', 'y'])
start_point.x = 20
start_point.y = 20
# 大矩形中，每行有几种地皮
num_per_line = 8
# 一共有多少行
_ = len(tile_codes) // num_per_line + 1

for i, code in enumerate(tile_codes):
    col, row = divmod(i, num_per_line)
    # 行的范围
    rr = range(start_point.y + col * size, start_point.y + (col + 1) * size)
    # 列的范围
    cr = range(start_point.x + row * size, start_point.x + (row + 1) * size)
    for r, c in product(rr, cr):
        tile[r][c] = code

from struct import pack
tile = b''.join([pack('<H', i) for i in chain.from_iterable(tile)])

from base64 import b64encode
tile = b64encode(b'VRSN\x00\x01\x00\x00\x00' + tile)
tile = tile.decode('ascii')


def save():
    with open(savedata._file.name, 'w+', encoding='utf-8') as savad:
        data = savad.read()
        tile_encode = savedata.all_data['map']['tiles']
        data = data.replace(tile_encode, tile)
        savad.seek(0)
        savad.write(data)

