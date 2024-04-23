# -*- coding: utf-8 -*-
import logging

from ipaddress import IPv4Address, AddressValueError
from random import randint, choices
from re import findall
from string import ascii_uppercase
from typing import Any, TypeAlias

from pydantic import BaseModel, Field
from pydantic.functional_serializers import model_serializer
from pydantic.functional_validators import field_validator, model_validator, AfterValidator
from pydantic_core.core_schema import FieldValidationInfo
from typing_extensions import Annotated

log = logging.getLogger(__name__)


def non_negative_integer(value: int, info: FieldValidationInfo) -> int:
    if value < 0:
        field_name = info.field_name
        default = info.context.model_fields.get(field_name).default
        log.warning('%s 不能小于 0，将设置为默认值：%s', field_name, default)
        return default
    return value


non_neg_int: TypeAlias = Annotated[int, AfterValidator(non_negative_integer)]


class _IniSection(BaseModel, validate_assignment=True):
    """
    当前场景下，值的类型只有 list, int, bool, str, IPv4Address
    由于开启了 validate_assignment，为属性赋值时会进行验证，所以在 after validator 类 函数内修改属性时务必注意，避免 赋值-验证-赋值 循环
    """

    # noinspection PyMethodParameters, PyMissingConstructor
    def __init__(__pydantic_self__, **data) -> None:
        # 将 context 设置为自己，用于获取字段的默认值
        __pydantic_self__.__pydantic_validator__.validate_python(
            data,
            self_instance=__pydantic_self__,
            context=__pydantic_self__,
        )

    @model_serializer
    def ini_section(self) -> dict[str, str]:
        result = {}
        for key, value in self:
            # if value != '':
            result[key] = self._convert_type(value)
        return result

    @staticmethod
    def _convert_type(value: Any) -> str:
        if isinstance(value, list):
            return ','.join(str(i) for i in value)
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, int):
            return str(value)
        if isinstance(value, IPv4Address):
            return str(value)
        raise TypeError(f'{value} is {type(value)}')


class DefaultGameplay(_IniSection):
    # 游戏模式：生存/survival、无尽/endless、荒野/wilderness、熔炉/lavaarena、暴食/quagmire
    # 默认 survival
    game_mode: str = 'survival'

    # 服务器人数上限
    # 默认 16
    max_players: non_neg_int = 16

    # 是否开启PVP
    # 默认 false
    pvp: bool = False

    # 无人时是否暂停
    # 默认 false
    pause_when_empty: bool = False

    # 是否开启投票。踢人、回档、重置世界
    # 默认 true
    vote_enabled: bool = True

    # noinspection PyNestedDecorators
    @field_validator('max_players')
    @classmethod
    def validate_max_players(cls, value: int) -> int:
        if value > 64:
            log.warning('max_players 的值不应该大于 64，当前值：%s', value)
        return value


class DefaultNetwork(_IniSection):
    # 服务器名称
    # 默认 [Host]'s World
    cluster_name: str = "[Host]'s World"

    # 服务器描述
    # 默认 ''
    cluster_description: str = ''

    # 已弃用
    # 游戏风格：社交/social、合作/cooperative、竞争/competitive、疯狂/madness
    # 默认 随模式变化 survival/cooperative, endless/social, wilderness/competitive, lavaarena/madness, quagmire/madness
    # cluster_intention: str = 'cooperative'

    # 服务器密码。无密码留空
    # 默认 无
    cluster_password: str = ''

    # 游戏内语言
    # 默认 en
    cluster_language: str = 'en'

    # 客户端尝试连接服务器的超时时间，超出后仍未成功将会被服务器断开连接
    # 默认 8000  （毫秒）
    connection_timeout: str = 8000

    # 是否在一天结束时自动存档
    # 默认 true
    autosaver_enabled: bool = True

    # 连接超时时间，单位/秒。客户端无操作超过该时间后将被断开连接
    # 默认 1800  （秒）
    idle_timeout: non_neg_int = 1800

    # 是否为局域网联机模式。联机分互联网联机与局域网联机
    # 默认 false
    lan_only_cluster: bool = False

    # 是否为离线模式。没有在线功能如皮肤等，但局域网仍可加入
    # 默认 false
    offline_cluster: bool = False

    # 每秒通信次数：15、30、60 可被60整除的值。次数多，游戏体验好，服务器压力大
    # 默认 15
    tick_rate: non_neg_int = 15

    # 为白名单玩家保留的位置数量  实际保留栏位 并不等于 设置的保留栏位 ，而是 设置保留栏位 与 白名单中ID数量 两者中较小的那个值。
    # 默认 0
    # TODO 在加载白名单后，处理白名单数量与该项
    whitelist_slots: non_neg_int = 0

    # 指定DNS。linux不适用，其它平台不清楚  8.8.8.8,8.8.4.4
    override_dns: list[IPv4Address] = []

    # 是否广播服务器信息，比如注册到klei房间大厅
    # 关闭后依然可通过直连进入，但主世界不会与从世界连接，导致只能游玩单个世界
    # 默认 True
    internet_broadcasting_enabled: bool = True

    # 存档保存为 steam 云存档时，其对应的 cloudid。（客户端开房间时，可选的云存档功能。专用服务器应该不适用？
    cluster_cloud_id: str = ''

    # 不知道干嘛的
    # cached_ping_size

    # noinspection PyNestedDecorators
    @field_validator('cluster_name')
    @classmethod
    def validate_cluster_name(cls, value: str, info: FieldValidationInfo) -> str:
        if not value:
            value = cls.model_fields.get(info.field_name).default
        return value

    # noinspection PyNestedDecorators
    @field_validator('cluster_language')
    @classmethod
    def validate_cluster_language(cls, value: str, info: FieldValidationInfo) -> str:
        language_dict = {
            'zh': '汉语 简体',
            'zht': '汉语 繁体',
            'en': '英语',
            'fr': '法语',
            'es': '西班牙语',
            'de': '德语',
            'it': '意大利语',
            'pt': '葡萄牙语',
            'pl': '波兰语',
            'ru': '俄语',
            'ko': '韩语',
        }
        language_list = list(language_dict)
        value = value.lower()
        if value not in language_list:
            log.warning('不合规的 cluster_language，应为 %s 其中之一', language_list)
            value = cls.model_fields.get(info.field_name).default
        return value

    # noinspection PyNestedDecorators
    @field_validator('tick_rate')
    @classmethod
    def validate_tick_rate(cls, value: int) -> int:
        if value < 10:
            log.warning('tick_rate 过低会影响客户端流畅度，建议设置为 15 及以上')
        if value <= 30:
            quotient, remainder = divmod(60, value)
            if remainder != 0:
                log.warning('tick_rate 应该是可被 60 整除的整数。当前值：%s', value)
        else:
            log.warning('tick_rate 不建议超过 30，因为游戏只有 30 帧，该项超过 30 意义不大')
        return value

    # noinspection PyNestedDecorators
    @field_validator('override_dns', mode='before')
    @classmethod
    def validate_override_dns(cls, value: str) -> list[IPv4Address]:
        if not isinstance(value, str):
            raise ValueError('override_dns 需要输入字符串，如 8.8.8.8,8.8.4.4')
        ipv4_str_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        ipv4_str_list = findall(ipv4_str_pattern, value)
        ipv4_list = []
        for item in ipv4_str_list:
            try:
                ipv4_list.append(IPv4Address(item))
            except AddressValueError:
                pass
        return ipv4_list


class DefaultMisc(_IniSection):
    # 是否开启控制台
    # 默认 true
    console_enabled: bool = True

    # 最大快照数量。决定可回滚天数
    # 默认 6
    max_snapshots: non_neg_int = 6

    # 不知道具体作用，使用备用的 gc？
    # use_alternate_gc: bool = false

    # debug_random_data  # 离线模式下会用到？
    # encoded_user_cache


class DefaultSteam(_IniSection):
    # 是否将群组管理员设为游戏管理员
    # 默认 false
    steam_group_admins: bool = False

    # steam群组编号
    # 默认 0
    steam_group_id: non_neg_int = 0

    # 是否仅允许steam群组成员加入
    # 默认 false
    steam_group_only: bool = False

    # noinspection PyNestedDecorators
    @field_validator('steam_group_id')
    @classmethod
    def validate_steam_group_id(cls, value: int, info: FieldValidationInfo) -> int:
        # 32 位，不能超出
        if value > ((1 << 32) - 1):
            default = cls.model_fields.get(info.field_name).default
            value = default
            log.warning('steam 群组 ID 无效，将设置为默认值：%s', default)
        return value


class DefaultShard(_IniSection):
    # 以下设置项中，服务器指饥荒服务器（一个服务器运行着一个世界，主世界对应主服务器，其他为从服务器）；计算机指电脑、云服务器等

    # 多服务器模式，非单一世界时必须开启（地上地下是两个世界，需要两个服务器运行）
    # 默认 false
    shard_enabled: bool = False

    # 以下选项都可以在sever.ini中重写(多计算机开服相关，***正常无需修改***）

    # 只需要为主服务器设置此项
    # 从服务器的IP，主服务器监听此IP并与其连接。主从服务器都在同一计算机上时，填127.0.0.1（表示本机）；否则填0.0.0.0（表示所有IP）
    # 默认 127.0.0.1
    bind_ip: IPv4Address = IPv4Address('127.0.0.1')

    # 只需要为从服务器设置此项
    # 主服务器的IP，从服务器请求此IP并与其连接。主从服务器都在同一计算机上时，填127.0.0.1；否则填主服务器IP
    # 默认 无
    master_ip: IPv4Address = None

    # 主服务器将监听/从服务器请求与主服务器连接 的UDP端口。主从服务器应设为相同值
    # 默认 10888
    master_port: int = 10888

    # 多服务器开服时，服务器间的验证密码
    # 默认 无
    cluster_key: str = ''

    # noinspection PyNestedDecorators
    @field_validator('bind_ip', 'master_ip', mode='before')
    @classmethod
    def validate_ip(cls, value: str, info: FieldValidationInfo) -> IPv4Address:
        default = cls.model_fields.get(info.field_name).default
        if not value:
            return default
        try:
            value = IPv4Address(value)
        except AddressValueError:
            value = default
        return value

    # noinspection PyNestedDecorators
    @field_validator('cluster_key')
    @classmethod
    def validate_cluster_key(cls, value: str, info: FieldValidationInfo) -> str:
        if info.data['shard_enabled'] and value == '':
            default = cls.model_fields.get(info.field_name).default
            value = default
            log.warning('cluster_key 不能为空，将重置为默认值 %s', default)
        return value


class DefaultNetworkForShard(_IniSection):
    # 当前世界监听的端口 由于局域网连接只会扫描 10998-11018，最好在该范围内
    # 默认 10999
    server_port: int = 10999


class DefaultSteamForShard(_IniSection):
    master_server_port: int = 27016

    authentication_port: int = 8766


class DefaultShardForShard(_IniSection):
    # 该小节取值若不符合要求，世界依然可以正常开启，但会影响到其作为世界分片的能力

    # 是否是主世界
    # 没有默认值
    # 未设置的情况下，世界可以开启且游玩，但是不具有作为世界分片的能力，比如与其他世界连接
    is_master: bool = True

    # 世界名称  主世界强制为 [SHDMASTER]
    # 未设置也可以正常开启游玩
    name: str = '[SHDMASTER]'

    # 世界id，很重要，是用于区分世界的标识  主世界强制为 1
    # 默认 随机正整数
    id: non_neg_int = Field(gt=0, default=1)

    # 只需要为主服务器设置此项
    # 从服务器的IP，主服务器监听此IP并与其连接。主从服务器都在同一计算机上时，填127.0.0.1（表示本机）；否则填0.0.0.0（表示所有IP）
    # 默认 127.0.0.1
    # bind_ip: IPv4Address = IPv4Address('127.0.0.1')

    # 只需要为从服务器设置此项
    # 主服务器的IP，从服务器请求此IP并与其连接。主从服务器都在同一计算机上时，填127.0.0.1；否则填主服务器IP
    # 默认 无
    # master_ip: IPv4Address = IPv4Address('127.0.0.1')

    # 主服务器将监听/从服务器请求与主服务器连接 的UDP端口。主从服务器应设为相同值
    # 默认 10888
    # master_port: int = 10888

    # 多服务器开服时，服务器间的验证密码
    # 默认 defaultPass
    # cluster_key: str = 'defaultPass'

    @model_validator(mode='after')
    def _(self):
        print('vvvvv')
        if self.is_master:
            if self.name != '[SHDMASTER]':
                self.name = '[SHDMASTER]'
            if self.id != 1:
                self.id = 1
        else:
            if self.name == '[SHDMASTER]':
                self.name = ''.join(choices(ascii_uppercase, k=10))
            if self.id == 1:
                self.id = randint(1 << 20, 1 << 24)
        return self


class DefaultAccountForShard(_IniSection):
    # 玩家存档文件夹名是否编码  未编码情况下，为玩家 KUid，包含符号与大小写，某些系统可能不适用  编码后，只包含 0-9、A-V
    encode_user_path: bool = False
