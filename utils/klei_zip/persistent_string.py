# -*- coding: utf-8 -*-

from base64 import b64decode, b64encode
from zlib import compress, decompress


def decode_unzip(string: str) -> str:
    if string.startswith('KLEI     1D'):
        string = string[11:]
    if string.startswith('AQAAABAA'):  # AQAAABAA -> \x01\x00\x00\x00\x10\x00
        data_full = b64decode(string)
        data_zip = data_full[16:]
        str_encode = decompress(data_zip)
        string = str_encode.decode('utf-8')
    return string


def zip_encode(string: str, encode: bool = True) -> str:
    """
    通过 zlib 对原始字符串进行压缩，在添加数据信息后，返回经过 base64 编码后的新字符串
    """
    # 在 c 中 \x00 作为结束符，为了与饥荒保持同样的输出，应该截断字符串
    if (flag := string.find('\x00')) != -1:
        string = string[:flag]

    if encode:
        str_encode = string.encode('utf-8')

        # klei 使用 1.2.3 版本（2005）的 zlib，压缩等级是 9
        data_zip = compress(str_encode, 9)

        len_str = len(str_encode).to_bytes(4, byteorder='little')
        len_zip = len(data_zip).to_bytes(4, byteorder='little')
        # klei 的做法是：分配内存，前十六字节存放自定义数据，之后存放压缩后数据
        # 自定义数据：前八字节放 0x1000000001i64，后八字节放长度信息（低四：原字符串长度，高四：压缩后字符串长度）
        # '' -> \x01\x00\x00\x00\x10\x00\x00\x00 + \x00\x00\x00\x00 \x08\x00\x00\x00 + \x78\xda\x03\x00\x00\x00\x00\x01
        # 前缀(8) + 压缩前字符长度(4) + 压缩后字符长度(4) + 压缩后数据
        data_full = 0x1000000001.to_bytes(8, byteorder='little') + len_str + len_zip + data_zip

        data_b64 = b64encode(data_full)
        str_new = data_b64.decode('ascii')
        result = 'KLEI     1D' + str_new
    else:
        result = 'KLEI     1 ' + string
    return result


def verify_algorithm():
    from persistent_example import var
    succ, fail = [], []
    for i in var:
        if zip_encode(i) == var[i]:
            succ.append(i)
            continue
        fail.append(i)
    print(f'验证结果：\n\t结果一致：{len(succ)}\n\t结果不一致：{fail}')


if __name__ == "__main__":
    raw = 'KLEI     1DAQAAABAAAAAVBAAA/wAAAHjazdPNasMwDADgd/E5GMuy/vIqoxRvc0cgXSEJPaz03ecMVtYwxhJ2mE42xuKzJD9c3NQdi2sjQ/BI0TAocOPGfC775zxl117coQxT13dvZXBtaFw37h/70+nYvb649pD7sTQfWeopJg+ICCGIkVDj+nIufU3fuCFP5bYYn3Jfd3S9Nv9MEELAKJIYthMEPc8BEIOtJAT1NocYsGwnWPTRTEkEDflGwE8C3BF4SRAyFRahJeHrpR8FydSn2gdjrp3QbwV371kSWNECCUTdXAWK5HU2aEBZWQP5izYoJU/MlJSAAFYT6jCCmiRLmwnzZ/BaDYIE8TeTsHsH1HA+Cg=='
    # raw = open(r"C:\Users\suke\Documents\Klei\DoNotStarveTogether\446835953\Cluster_1\Master\save\mod_config_data\modconfiguration_workshop-2189004162_CLIENT", 'r').read()
    # open(r"C:\Users\suke\Desktop\server__decode", "w+", encoding='utf-8').write(decode_unzip(raw))
    # print([decode_unzip(raw)])
    # stri = '1\x001'
    # str2 = zip_encode('\x00')
    # print(str2)
    # print([decode_unzip(str2)])
    # verify_algorithm()
