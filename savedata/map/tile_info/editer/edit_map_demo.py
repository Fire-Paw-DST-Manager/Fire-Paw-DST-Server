# -*- coding: utf-8 -*-
from json import loads
from itertools import product, chain
from decode_savedata import decode_tile, save_savadata

# data_path = r'./saved_data/savadata4.json'
data_path = r'C:\Users\suke\Desktop\0000000003'
savedata_path = './ssss'
save_savadata(data_path, savedata_path)
with open(savedata_path, 'r', encoding='utf-8') as savadata:
    data = loads(savadata.read())
    tile_encode = data['map']['tiles']
    print(len(tile_encode))
    width = data['map']['width']
    height = data['map']['height']
tile_decode = decode_tile(tile_encode)
tile = tuple(tile_decode[i * height: (i + 1) * height] for i in range(width))
tile_codes = list(range(35, 42)) + [78]
size = 20
start = 20, 20
rols = 7
cols = 8
for i, code in enumerate(tile_codes):
    col, row = divmod(i, cols)
    rr = range(start[1] + col * size, start[1] + (col + 1) * size)
    cr = range(start[0] + row * size, start[0] + (row + 1) * size)
    for r, c in product(rr, cr):
        tile[r][c] = code
# print(sum((len(i) for i in tile)))
from struct import pack
tile = b''.join([pack('<H', i) for i in chain.from_iterable(tile)])
print(len(tile))
from base64 import b64encode
tile = b64encode(b'VRSN\x00\x01\x00\x00\x00' + tile)
tile = tile.decode('ascii')
print(len(tile))

with open(data_path, 'r+', encoding='utf-8') as savadata:
    data = savadata.read()
    data = data.replace(tile_encode, tile)
    savadata.seek(0)
    savadata.write(data)
