"""
klei 使用的图片压缩算法主要是基于 DXT1 与 DXT5 算法（有损纹理压缩算法 S3TC 的变体）修改的，主要添加了 ktex 格式的各种私有信息，
核心算法没有改变，提取出文件中图像部分的数据之后，可通过对应算法解码

                                     (r+g+b(+a))*16    (r+g+b)*2+2*16   a*2+3*16
DXT1 用于 RGB 图像的压缩，压缩比为 6:1    (8+8+8)*16    ->  (5+6+5)*2+2*16               384->64  6:1
DXT5 用于 RGBA 图像的压缩，压缩比为 4:1   (8+8+8+8)*16  ->  (5+6+5)*2+2*16 + 8*2+3*16    512->128 4:1
这里压缩是指在显存中的情况，存储在硬盘时，由于 png 会对数据再次压缩，所以 ktex 的占用空间会比 png 大

DXT1 用于地皮的贴图与噪点文件等
DXT3 未见使用
DXT5 用于一般图像
RGBA 无压缩 未见使用
RGB  无压缩 用于 colour_cubes 图像  滤镜？

S3TC / DXTn / BCn
    https://en.wikipedia.org/wiki/S3_Texture_Compression
    https://registry.khronos.org/OpenGL/extensions/EXT/EXT_texture_compression_s3tc.txt
    https://learn.microsoft.com/zh-cn/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression

    https://github.com/Cavewhere/squish
    https://github.com/svn2github/libsquish
    https://github.com/Benjamin-Dobell/s3tc-dxt-decompression
    https://github.com/leamsii/Python-DXT-Decompress
    https://github.com/python-pillow/Pillow/blob/main/docs/example/DdsImagePlugin.py

ktex
    https://github.com/kleientertainment/ds_mod_tools
    https://gitlab.com/Zarklord/ztools
    https://github.com/nsimplex/ktools
    https://github.com/oblivioncth/Stexatlaser

PremultiplyAlpha
    https://codebrowser.dev/qt5/qtbase/src/gui/painting/qrgb.h.html#_Z12qPremultiplyj
    https://codebrowser.dev/qt5/qtbase/src/gui/image/qimage.cpp.html#_ZNK6QImage22convertToFormat_helperENS_6FormatE6QFlagsIN2Qt19ImageConversionFlagEE
    https://codebrowser.dev/qt5/qtbase/src/gui/painting/qdrawhelper_p.h.html#_ZL26qt_convertARGB32ToARGB32PMPjPKji

2023.09
    通过游戏将png转为tex后，rgb值是经过不透明度预乘的。
    但测试发现，游戏一些贴图中的rgb值是大于alpha的，说明未经过预乘  (918 err / 2696 all)
    但其它转换工具如 ktools、stex 都是默认预乘的，暂时也这么做
"""

from enum import IntEnum
from io import BytesIO
from math import log2
from struct import pack, unpack
from typing import Union

import png


class Ktex:
    class _PixelFormat(IntEnum):
        DXT1 = 0b00000
        DXT3 = 0b00001
        DXT5 = 0b00010
        RGBA = 0b00100
        RGB = 0b00101

    class _Platform(IntEnum):
        PC = 0b1100
        XBOX360 = 0b1011
        PS3 = 0b1010
        DEFAULT = 0b0000

    class _TextureType(IntEnum):
        D1 = 0b0000
        D2 = 0b0001
        D3 = 0b0010
        CUBEMAP = 0b0011

    _FLAGS = 0b11
    _REMAINDER = 0b111111111111

    class _HeaderDataLen(IntEnum):
        platform = 4
        pixel_format = 5
        texture_type = 4
        mipmaps = 5
        flags = 2
        remainder = 12

    def __init__(self, file_path: str = None, file_type: str = None):
        self.file_path: str = ''
        self.file_type: str = ''
        self.header: dict[str, Union[int, str]] = {
            'platform': '',
            'pixel_format': '',
            'texture_type': '',
            'mipmaps': 0,
            'flags': 0,
            'remainder': 0
        }

        self.width = 0
        self.height = 0
        self.pitch = 0
        self.data_size = 0

        self._img_data: bytes = b''
        self._tex_data: bytes = b''

        # 默认预乘开启
        self.premultiply = True

        if file_path:
            self.load_file(file_path, file_type)

    def load_file(self, file_path: str = None, file_type: str = None):
        if file_path is None:
            if self.file_path is None:
                raise ValueError('文件路径为空')
            file_path = self.file_path
        else:
            self.file_path = file_path

        if file_type == 'tex' or file_path.endswith('.tex'):
            self.file_type = 'tex'
        elif file_type == 'png' or file_path.endswith('.png'):
            self.file_type = 'png'
        else:
            raise TypeError('文件后缀名不为 tex 或 png，且未显式传递类型参数')

        if self.file_type == 'tex':
            with open(self.file_path, 'rb') as ktex:
                self._tex_data = ktex.read()

            self._parse_header()
            self._decode()
            return

        img = png.Reader(file_path)
        img.preamble()
        if img.alpha:
            mode = 'RGBA'
            self.width, self.height, rows, info = img.asRGBA8()
        else:
            mode = 'RGB'
            self.width, self.height, rows, info = img.asRGB8()

        self.pitch = self._cal_pitch(mode)
        self.data_size = self._cal_data_size(mode)
        self._set_header(mode)

        self._img_data = bytearray(b''.join(reversed(tuple(rows))))
        if self.premultiply and mode == 'RGBA':
            self._premultiply_alpha()

        self._build_tex()

    def _cal_pitch(self, mode):
        match mode:
            case 'DXT5':
                bytes_per_block = 16
                return ((self.width + 3) // 4) * bytes_per_block
            case 'RGB1':
                bytes_per_block = 8
                return ((self.width + 3) // 4) * bytes_per_block
            case 'RGBA':
                return self.width * 4
            case 'RGB':
                return self.width * 3
            case _:
                raise

    def _cal_data_size(self, mode):
        match mode:
            case 'DXT5':
                pass
            case 'DXT1':
                pass
            case 'RGBA':
                return self.width * self.height * 4
            case 'RGB':
                return self.width * self.height * 3
            case _:
                raise

    def _set_header(self, img_mode: str):
        self.header = {
            'platform': self._Platform.DEFAULT,
            'pixel_format': self._PixelFormat[img_mode],
            'texture_type': self._TextureType.D2,
            'mipmaps': 1,
            'flags': self._FLAGS,
            'remainder': self._REMAINDER,
        }

    def _parse_header(self):
        ktex = self._tex_data[:4]
        if ktex != b'KTEX':
            raise TypeError('文件类型错误，文件不以 KTEX 开头')
        header, self.width, self.height, self.pitch, self.data_size = unpack('<I3HI', self._tex_data[4:18])

        # header: 000000000000 00    00000   0000         00000        0000
        #         remainder    flags mipmaps texture_type pixel_format platform'
        offset = 0
        len_tmp = self._HeaderDataLen
        self.header['platform'] = self._Platform((header >> offset) & ((1 << len_tmp.platform) - 1)).name

        offset += len_tmp.platform
        self.header['pixel_format'] = self._PixelFormat((header >> offset) & ((1 << len_tmp.pixel_format) - 1)).name

        offset += len_tmp.pixel_format
        self.header['texture_type'] = self._TextureType((header >> offset) & ((1 << len_tmp.texture_type) - 1)).name

        offset += len_tmp.texture_type
        self.header['mipmaps'] = (header >> offset) & ((1 << len_tmp.mipmaps) - 1)

        offset += len_tmp.mipmaps
        self.header['flags'] = (header >> offset) & ((1 << len_tmp.flags) - 1)

        offset += len_tmp.flags
        self.header['remainder'] = (header >> 20) & ((1 << len_tmp.remainder) - 1)

        # if int(log2(self.width)) != log2(self.width) or int(log2(self.height)) != log2(self.height):
        # if self.header['pixel_format'] == 'DXT5' and self.header['mipmaps'] != int(max(log2(self.width), log2(self.height))) + 1:
        print(self.file_path)
        print(f'{self.header}\n{self.pitch=} {self.data_size=}\n{self.width} x {self.height}')

        self._tex_data = self._tex_data[4 + 4 + self.header['mipmaps'] * 10:]

    def _build_tex(self):
        """以未压缩的格式保存为 tex 文件，优点是不会因为压缩造成质量的少量降低，缺点是内存占用是 DXT5 格式文件的四倍。
        嗯主要是压缩不好写，python 实现估计也会很慢很慢"""
        ktex = b'KTEX'
        self._tex_data = ktex

        offset, header = 0, 0
        for dataname, datalen in self._HeaderDataLen.__members__.items():
            header |= self.header[dataname] << offset
            offset += datalen

        self._tex_data += pack('<I3HI', header, self.width, self.height, self.pitch, self.data_size)

        mipmaps_len = self.header['mipmaps'] * 10 - 10
        self._tex_data += pack(f'<{mipmaps_len}B', *(0 for _ in range(mipmaps_len)))

        self._tex_data += self._img_data

    def _decode(self) -> None:
        dxt = Dxt(self.width, self.height)
        self._img_data = dxt.decompress(self._tex_data, self.header['pixel_format'])
        if self.premultiply:
            self._unpremultiply_alpha()

    def _encode(self, img_data: bytes, img_width: int, img_height: int) -> None:
        # 放弃
        if not img_width or not img_height:
            raise ValueError('图片宽或高不能为零')
        if max(img_width, img_height) > 2048:
            raise TypeError('图片尺寸最大为 2048。否则可能导致游戏崩溃')
        log2_w, log2_h = log2(img_width), log2(img_height)
        if int(log2_w) != log2_w or int(log2_h) != log2_h:
            raise TypeError(f'图片宽或高都需要是 2 的幂。当前图片尺寸：{img_width} x {img_height}')

        self._img_data = img_data

    def save(self, save_path: str = None) -> None:
        if not save_path:
            save_path = self.file_path

        save_path = save_path.removesuffix('.tex').removesuffix('.png')
        if self.file_type == 'tex':
            self._save_png(f'{save_path}.png')
        elif self.file_type == 'png':
            self._save_tex(f'{save_path}.tex')

    def _save_tex(self, save_path):
        with open(save_path, 'wb') as tex_file:
            tex_file.write(self._tex_data)

    def _save_png(self, save_path):
        if self.header['pixel_format'] == 'RGB':
            mode = 'RGB'
            pixel_size = 3
        else:
            mode = 'RGBA'
            pixel_size = 4

        # use pillow
        # from PIL import Image
        # img = Image.frombuffer(mode, (self.width, self.height), self.img_data, 'raw', mode, 0, 1)  # 0 1 | 0 -1  数据首行是图片第一行还是最后一行

        # use pypng
        img_array = (self._img_data[i * self.width * pixel_size:(i + 1) * self.width * pixel_size] for i in
                     range(self.height))
        img = png.from_array(img_array, mode=mode, info={'height': self.height, 'width': self.width})

        # save
        img.save(save_path)

    def _premultiply_alpha(self):
        tmp_all = [[round(i * j / 255) for j in range(256)] for i in range(256)]
        for i in range(0, len(self._img_data), 4):
            tmp = tmp_all[self._img_data[i + 3]]
            self._img_data[i: i + 3] = tmp[self._img_data[i]], tmp[self._img_data[i + 1]], tmp[self._img_data[i + 2]]

    def _unpremultiply_alpha(self):
        tmp_cal_all = [[0] * 256, *([min(255, round(n * 255 / a)) for n in range(256)] for a in range(1, 256))]
        tmp = bytearray(self._img_data)
        for i in range(0, len(self._img_data), 4):
            a = tmp[i + 3]
            if a == 0 or a == 255:
                continue
            tmp_cal = tmp_cal_all[a]
            tmp[i: i + 3] = tmp_cal[tmp[i]], tmp_cal[tmp[i + 1]], tmp_cal[tmp[i + 2]]

        self._img_data = tmp


class Dxt:
    def __init__(self, width: int = None, height: int = None):
        self.width = width
        self.height = height

    def decompress(self, tex_data: Union[bytes, BytesIO], compress_type: str, width: int = None,
                   height: int = None) -> bytes:
        if width is None or height is None:
            if self.width is None or self.height is None:
                raise ValueError('未输入图片长度或宽度')
            width = self.width
            height = self.height

        if compress_type == 'DXT5':
            return self._dxt5_decompress(tex_data, width, height)
        elif compress_type == 'DXT1':
            return self._dxt1_decompress(tex_data, width, height)
        elif compress_type == 'RGBA':
            return b''.join(
                reversed([tex_data[i * width * 4: (i + 1) * width * 4] for i in range(len(tex_data) // width)]))
            # return b''.join([tex_data[i * width * 4: (i + 1) * width * 4] for i in range(len(tex_data) // width)][::-1])
        elif compress_type == 'RGB':
            return b''.join(
                reversed([tex_data[i * width * 3: (i + 1) * width * 3] for i in range(len(tex_data) // width)]))
            # return b''.join([tex_data[i * width * 3: (i + 1) * width * 3] for i in range(len(tex_data) // width)][::-1])
        else:
            raise ValueError(f'不能处理的格式：{compress_type}')

    def _dxt5_decompress(self, data: Union[bytes, BytesIO], width: int, height: int) -> bytes:
        buffer = BytesIO(data) if isinstance(data, bytes) else data

        ret = memoryview(bytearray(4 * width * height))

        for y in range(0, height, 4):
            for x in range(0, width, 4):
                a0, a1, ac0, ac1, c0, c1, code = unpack("<2BHI2HI", buffer.read(16))

                ac = ac1 << 16 | ac0  # ac1(4*8) + ac0(2*8) = a(16*3)   拼凑回六个字节，48位，十六份alpha数据
                r0, g0, b0 = self._decode565(c0)
                r1, g1, b1 = self._decode565(c1)
                rgb2 = self._c2a(r0, r1), self._c2a(g0, g1), self._c2a(b0, b1)
                rgb3 = self._c3(r0, r1), self._c3(g0, g1), self._c3(b0, b1)
                rgbs = (r0, g0, b0), (r1, g1, b1), rgb2, rgb3

                for j in range(4):
                    for i in range(4):
                        ai = 3 * (4 * j + i)
                        alpha = self._dxtc_alpha(a0, a1, ac, ai)

                        cc = (code >> (2 * (4 * j + i))) & 0b11
                        r, g, b = rgbs[cc]

                        idx = 4 * (((height - 1) - (y + j)) * width + x + i)

                        # 根据转换后的rgb值推断，编码过程对图像进行了 不透明度的预乘
                        # (64, 64, 64, 127) --- pre-multiplied rgb*a/255 --> (32, 32, 32, 127)
                        # 像这样，rgb值均变为了一半，直接按照字面值转换的话，像素点会偏暗，需要转换回去
                        # 一个特征是，所有的rgb值都不会大于a  可以根据这个来判断，很小概率会把非预乘图判为预乘图  (n<=255  ->  n*a/255<=a)
                        # 有的图，rgb大于a，说明是非预乘图，ds_mod_tools 也确实有非预乘的选项
                        # 但是其它转换的工具都是按预乘算的，溢出部分直接舍去了 ds_mod_tools 也只有压缩没有解压的代码
                        # 暂时按其他工具写吧
                        # if self.premultiply:
                        #     r_, g_, b_, a_ = self._unpremultiply(r, g, b, alpha)
                        # else:
                        #     r_, g_, b_, a_ = r, g, b, alpha

                        # ret[idx: idx + 4] = pack("4B", r_, g_, b_, a_)
                        ret[idx: idx + 4] = pack("4B", r, g, b, alpha)
        return ret.tobytes()

    def _dxt1_decompress(self, data: Union[bytes, BytesIO], width: int, height: int) -> bytes:

        buffer = BytesIO(data) if isinstance(data, bytes) else data

        ret = memoryview(bytearray(4 * width * height))
        for y in range(0, height, 4):
            for x in range(0, width, 4):
                color0, color1, bits = unpack("<HHI", buffer.read(8))

                r0, g0, b0 = self._decode565(color0)
                r1, g1, b1 = self._decode565(color1)

                for j in range(4):
                    for i in range(4):
                        control = bits & 0b11
                        bits >>= 2
                        if control == 0:
                            r, g, b = r0, g0, b0
                        elif control == 1:
                            r, g, b = r1, g1, b1
                        elif control == 2:
                            if color0 > color1:
                                r, g, b = self._c2a(r0, r1), self._c2a(g0, g1), self._c2a(b0, b1)
                            else:
                                r, g, b = self._c2b(r0, r1), self._c2b(g0, g1), self._c2b(b0, b1)
                        else:  # control == 3
                            if color0 > color1:
                                r, g, b = self._c3(r0, r1), self._c3(g0, g1), self._c3(b0, b1)
                            else:
                                r, g, b = 0, 0, 0

                        idx = 4 * (((height - 1) - (y + j)) * width + x + i)
                        ret[idx: idx + 4] = pack("4B", r, g, b, 255)

        return ret.tobytes()

    @staticmethod
    def _decode565(bits):
        r = (bits >> 11) & 0b11111
        g = (bits >> 5) & 0b111111
        b = (bits >> 0) & 0b11111
        r = (r << 3) | (r >> 2)
        g = (g << 2) | (g >> 4)
        b = (b << 3) | (b >> 2)
        return r, g, b

    @staticmethod
    def _c2a(a, b):
        return (2 * a + b) // 3

    @staticmethod
    def _c2b(a, b):
        return (a + b) // 2

    @staticmethod
    def _c3(a, b):
        return (2 * b + a) // 3

    @staticmethod
    def _dxtc_alpha(a0, a1, ac, ai):
        ac = (ac >> ai) & 0b111

        if ac == 0:
            alpha = a0
        elif ac == 1:
            alpha = a1
        elif a0 > a1:
            alpha = ((8 - ac) * a0 + (ac - 1) * a1) // 7
        elif ac == 6:
            alpha = 0
        elif ac == 7:
            alpha = 0xFF
        else:
            alpha = ((6 - ac) * a0 + (ac - 1) * a1) // 5

        return alpha


if __name__ == "__main__":
    def test():
        tex_path = r'C:\Users\suke\Desktop\test'
        # tex_path = r"C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data"

        from pathlib import Path
        from time import perf_counter

        s = perf_counter()
        tex = Ktex()
        for xx in Path(tex_path).glob(
                # '**/'
                '*'
                # '*'
                '.tex'
                # '.png'
        ):
            print(f'convert {xx}')
            tex.load_file(str(xx))

            tex.save()

        print(perf_counter() - s)


    test()
