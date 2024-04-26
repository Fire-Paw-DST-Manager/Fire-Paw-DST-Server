# -*- coding: utf-8 -*-

import os
import png
from itertools import compress, cycle

# tiles_path = r'C:\Users\suke\Desktop\tiles\ingame'
tiles_path = r'C:\Users\suke\Desktop\tiles\inmap'


def color(rows_, planes_):
    if planes_ == 3:
        fr, fg, fb = [1, 0, 0], [0, 1, 0], [0, 0, 1]
    else:
        fr, fg, fb = [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]
    r_ = g_ = b_ = 0
    for row in rows_:
        r_ += sum(compress(row, cycle(fr)))
        g_ += sum(compress(row, cycle(fg)))
        b_ += sum(compress(row, cycle(fb)))
    q = width * height
    return r_ // q, g_ // q, b_ // q


colors = {}
for file in os.listdir(tiles_path):
    if not file.endswith('.png') or not file.split('.')[0].isdigit():
        continue
    tile_path = os.path.join(tiles_path, file)
    pp = png.Reader(tile_path)
    width, height, rows, info = pp.read()
    planes = info['planes']
    bitdepth = info['bitdepth']
    if bitdepth != 8:
        raise TypeError('bitdepth 不是 8 位的')
    r, g, b = color(rows, planes)
    rgb = f'#{r:0>2X}{g:0>2X}{b:0>2X}'
    # rgb = hex(r * 16 ** 4 + g * 16 ** 2 + b).upper()[2:]
    tile_code = int(file.removesuffix(".png"))
    colors[tile_code] = rgb

    print(f'{tile_code}: "{rgb}",')

print({i: colors[i] for i in sorted(colors)})
result_ingame = {
    2: '#312E27',
    3: '#363F3E',
    4: '#585141',
    5: '#625339',
    6: '#26361E',
    7: '#181D0A',
    8: '#10121D',
    9: '#000000',
    10: '#32291D',
    11: '#323252',
    12: '#545C8B',
    13: '#7E7568',
    14: '#544956',
    15: '#3E421E',
    16: '#595755',
    17: '#493620',
    18: '#675A60',
    19: '#5B5957',
    20: '#59375A',
    21: '#43304B',
    22: '#512845',
    23: '#333231',
    24: '#64403F',
    25: '#435444',
    30: '#3D310B',
    31: '#554324',
    32: '#16120F',
    42: '#405251',
    43: '#336972',
    44: '#858093',
    45: '#664E42',
    46: '#404B4B',
    47: '#231E19',
    201: '#114048',
    202: '#114048',
    203: '#062D46',
    204: '#001F33',
    205: '#052B41',
    206: '#113E51',
    207: '#06161B',
    208: '#114047',
    256: '#A59165',
    257: '#382F1F',
    258: '#2B262C',
    259: '#391D2C',
    260: '#223040',
    261: '#180719',
}
result_inmap = {
    1: '#130F0D',
    2: '#D1AE6E',
    3: '#C2A163',
    4: '#F4CC80',
    5: '#DBA545',
    6: '#C7BD51',
    7: '#7D8146',
    8: '#836549',
    9: '#181310',
    10: '#AE894A',
    11: '#B57647',
    12: '#CE9E60',
    13: '#A48F63',
    14: '#57625F',
    15: '#8C863C',
    16: '#715E42',
    17: '#8B5F2F',
    18: '#77734F',
    19: '#787450',
    20: '#6C4643',
    21: '#6E4744',
    22: '#473A2F',
    23: '#6E4744',
    24: '#9A6647',
    25: '#69623A',
    30: '#A8784C',
    31: '#E1B863',
    32: '#5C4929',
    33: '#78270F',
    34: '#78270F',
    35: '#A0845A',
    36: '#A4754A',
    37: '#E7B879',
    38: '#8B853B',
    39: '#5A4429',
    41: '#DBB773',
    42: '#C0AD6B',
    43: '#8AA36D',
    44: '#C0AD6B',
    45: '#906137',
    46: '#59523A',
    47: '#554127',
    201: '#2E464E',
    202: '#2F464D',
    203: '#27354B',
    204: '#2B2838',
    205: '#3E6467',
    206: '#2F464D',
    207: '#1B181C',
    208: '#3A6165',
    256: '#BBA969',
    257: '#85664B',
    258: '#47362A',
    259: '#702D2E',
    260: '#46312D',
    261: '#34171E',
}
