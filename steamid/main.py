# -*- coding: utf-8 -*-

# https://github.com/xPaw/SteamID.php
# https://steam.readthedocs.io/en/stable/api/steam.steamid.html
# https://github.com/SteamRE/SteamKit/blob/master/SteamKit2/SteamKit2/Types/SteamID.cs

from .enums import (
    BitLenght,
    Instances,
    Masks,
    MaxValue,
    Patterns,
    TypeChars,
    TypeCharsToInstances,
    Types,
    Universes,
)


class SteamID:
    def __init__(self,
                 steam_id: str | int = None,
                 *,
                 universe: int = None,
                 type_: int = None,
                 instance: int = None,
                 account_id: int = None
                 ) -> None:

        self._universe: Universes = Universes.invalid
        self._type: Types = Types.invalid
        self._instance: Instances = Instances.all
        self._account_id: int = 0

        if steam_id is not None:
            self.set_steam_id(steam_id)

        if universe is not None:
            self.set_universe(universe)
        if type_ is not None:
            self.set_type(type_)
        if instance is not None:
            self.set_instance(instance)
        if account_id is not None:
            self.set_account_id(account_id)

    def set_universe(self, universe: int) -> None:
        """单独设置实例的 universe"""
        if universe not in Universes:
            raise ValueError(f'无效的 universe')
        self._universe = universe

    def set_type(self, type_: int) -> None:
        """设置实例的 type，若 instance 为 0，将会根据 type 为其设置对应的值"""
        if type_ not in Types:
            raise ValueError(f'无效的 type')
        self._type = type_
        if not self._instance:
            self._instance = TypeCharsToInstances[TypeChars(type_).name]

    def set_instance(self, instance: int) -> None:
        """单独设置实例的 instance"""
        if not (0 <= instance <= MaxValue.instance):
            raise ValueError(f'instance 超出有效范围：0~{MaxValue.instance}')
        self._instance = instance

    def set_account_id(self, account_id: int) -> None:
        """单独设置实例的 account_id"""
        if not (0 <= account_id <= MaxValue.account_id):
            raise ValueError(f'account_id 超出有效范围：0~{MaxValue.account_id}')
        self._account_id = account_id

    def set_steam_id(self, steam_id: str | int) -> None:
        """通过解析有效的 steamID 设置所需属性"""
        steam_id = str(steam_id)
        if result := Patterns.steamID64.value.match(steam_id):
            self._parse_steamID64(result.string)
        elif Patterns.steamID32.value.match(steam_id):
            self._parse_steamID32(steam_id)
        elif Patterns.steamID3.value.match(steam_id):
            self._parse_steamID3(steam_id)

    @staticmethod
    def _divide_account_id(account_id: int) -> tuple[int, int]:
        return account_id >> BitLenght.account_suf, account_id & Masks.account_suf

    @staticmethod
    def _combine_account_id(account_pre: int, account_suf: int) -> int:
        if account_pre > MaxValue.account_pre:
            raise ValueError(f'account_pre 超出有效范围：0~{MaxValue.account_pre}')
        if account_suf > MaxValue.account_suf:
            raise ValueError(f'account_suf 超出有效范围：0~{MaxValue.account_suf}')
        return (account_pre << BitLenght.account_suf) | account_suf

    @staticmethod
    def _shift_right_read(num: int, length: int) -> tuple[int, int]:
        mask = (1 << length) - 1
        result = num & mask
        num >>= length
        return result, num

    def _parse_steamID64(self, steam_id64: str | int) -> None:
        steam_id64 = int(steam_id64)
        if steam_id64 > MaxValue.steam_id:
            raise ValueError(f'传入数据不是有效的 steamID')
        num = steam_id64
        self._account_id, num = self._shift_right_read(num, BitLenght.account_id)
        self._instance, num = self._shift_right_read(num, BitLenght.instance)
        self._type, num = self._shift_right_read(num, BitLenght.type)
        self._universe, num = self._shift_right_read(num, BitLenght.universe)

    def _parse_steamID32(self, steam_id: str) -> None:
        result = Patterns.steamID32.value.match(steam_id)

        account_pre = int(result.group('account_pre'))
        account_suf = int(result.group('account_suf'))
        account_id = self._combine_account_id(account_pre, account_suf)
        if account_id > MaxValue.account_id:
            raise ValueError(f'account_id 超出有效范围：0~{MaxValue.account_id}')
        self._account_id = account_id

        universe = int(result.group('universe'))
        # 由于某些错误，在一些旧的游戏中获取 id 时，universe 显示为 0，实际上应该是 1
        if universe == Universes.invalid:
            universe = Universes.public
        self._universe = universe

        self._instance = Instances.desktop
        self._type = Types.individual

    def _parse_steamID3(self, steam_id: str) -> None:
        result = Patterns.steamID3.value.match(steam_id)

        account_id = int(result.group('account_id'))
        if account_id > MaxValue.account_id:
            raise ValueError(f'account_id 超出有效范围：0~{MaxValue.account_id}')
        self._account_id = account_id

        type_ = result.group('type')
        self._type = Types(TypeChars[type_]).name

        universe = result.group('universe')
        self._universe = universe

        instance = result.group('instance')
        if instance is None or self._type == Types.chat:
            instance = TypeCharsToInstances[type_]
        self._instance = instance

    @property
    def steam_id64(self) -> str:
        shift_dis_account_id = 0
        shift_dis_instance = shift_dis_account_id + BitLenght.account_id
        shift_dis_type = shift_dis_instance + BitLenght.instance
        shift_dis_universe = shift_dis_type + BitLenght.type
        return str(
            (self._universe << shift_dis_universe) |
            (self._type << shift_dis_type) |
            (self._instance << shift_dis_instance) |
            (self._account_id << shift_dis_account_id)
        )

    @property
    def steam_id(self) -> str:
        return self.steam_id64

    @property
    def steam_id32(self) -> str:
        account, auth_server = self._divide_account_id(self._account_id)
        return f'STEAM_{self._universe}:{auth_server}:{account}'

    @property
    def steam_id2(self) -> str:
        return self.steam_id32

    @property
    def steam_id3(self) -> str:
        extra = ''
        if self._type == Types.multiseat or (self._type == Types.individual and self._instance != Instances.desktop):
            extra = f':{self._instance}'
        return f'[{TypeChars(self._type).name}:{self._universe}:{self._account_id}{extra}]'

    @property
    def is_valid(self) -> bool:
        if self._universe == Universes.invalid or self._universe not in Universes:
            return False
        if self._type == Types.invalid or self._type not in Types:
            return False
        if self._type == Types.individual and (
                self._account_id == 0 or self._instance not in Instances):
            return False
        if self._type == Types.clan and (
                self._account_id == 0 or self._instance != 0):
            return False
        if self._type == Types.game_server and self._account_id == 0:
            return False

        return True

    @property
    def is_valid_user(self) -> bool:
        if self._universe == Universes.invalid or self._universe not in Universes:
            return False
        if ((self._type == Types.individual or self._type == Types.console_user)
                and self._account_id != 0 and self._instance in Instances):
            return True
        return False

    def __repr__(self):
        return (f'<{self.__class__} '
                f'universe={self._universe} '
                f'type={self._type} '
                f'instance={self._instance} '
                f'account_id={self._account_id} '
                f'>')
