# -*- coding: utf-8 -*-

from configparser import ConfigParser, DEFAULTSECT
from enum import Enum
from os import PathLike
from typing import Iterable, Mapping, Any


def mybool(value: str) -> bool:
    if not value:
        raise ValueError("Invalid boolean value: %s", value)
    if value.lower() == 'true':
        return True
    return False


class ValueType(Enum):
    bool = 1
    float = 2
    int = 3
    str = 4


class IniReader:
    _VALUE_TYPES: dict | None = None

    def __init__(self) -> None:
        self._configparser: ConfigParser | None = None
        self.data = {}

    @staticmethod
    def _get_configparser() -> ConfigParser:
        return ConfigParser(converters={'boolean': mybool})

    def _read(self, method: str, *args, strict: bool = False, **kwargs) -> None:
        """

        :param method: 需要调用的 configparser.ConfigParser 的方法名
        :param args: 参数
        :param strict: 是否是严格模式。如果是，将会舍弃 self._VALUE_TYPES 中不包含的项
        :param kwargs: 键值对参数
        :return: None
        """
        self._configparser = self._get_configparser()
        getattr(self._configparser, method)(*args, **kwargs)
        self._parse(strict)

    def read(self, filenames: str | bytes | PathLike[str] | PathLike[bytes] | Iterable[
            str | bytes | PathLike[str] | PathLike[bytes]], encoding: str = 'utf-8', strict: bool = False) -> None:
        self._read(method='read', filenames=filenames, encoding=encoding, strict=strict)

    def read_str(self, string: str, strict: bool = False) -> None:
        self._read(method='read_string', string=string, strict=strict)

    def read_dict(self, dictionary: Mapping[str, Mapping[str, Any]], strict: bool = False) -> None:
        self._read(method='read_dict', dictionary=dictionary, strict=strict)

    def _parse(self, strict: bool = False) -> None:
        if self._VALUE_TYPES is None:
            # 由于不能确定原始数据中是否有 DEFAULTSECT，所以不尝试忽略
            for section_name, section in self._configparser.items():
                if section_name not in self.data:
                    self.data[section_name] = dict(section)
                    continue
                self.data[section_name] |= dict(section)
            return

        for section_name, section in self._configparser.items():
            section_name = section_name.upper()
            if strict:
                if section_name not in self._VALUE_TYPES:
                    continue
            else:
                if section_name == DEFAULTSECT and section_name not in self._VALUE_TYPES:
                    # ConfigParser 实例默认带有 DEFAULT section，这里在尽量保留未知 section 的前提下，忽略额外引入的 DEFAULT
                    continue

            value_types = self._VALUE_TYPES.get(section_name, {})

            if section_name in self.data:
                sec = self.data[section_name]
            else:
                self.data[section_name] = (sec := {})

            for key in section:
                if strict:
                    if key not in value_types:
                        continue
                try:
                    match value_types.get(key):
                        case ValueType.bool:
                            sec[key] = section.getboolean(key)
                        case ValueType.float:
                            sec[key] = section.getfloat(key)
                        case ValueType.int:
                            sec[key] = section.getint(key)
                        case ValueType.str:
                            sec[key] = section.get(key)
                        case _:
                            sec[key] = section.get(key)
                except ValueError:
                    # 原数据不合规，忽略掉
                    pass
