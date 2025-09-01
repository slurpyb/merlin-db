from enum import Enum, StrEnum


class ColumnType(Enum):
    TYPE_BOOLEAN = 1
    TYPE_INT8 = 2
    TYPE_INT16 = 3
    TYPE_INT32 = 4
    TYPE_MONEY = 5
    TYPE_FLOAT32 = 6
    TYPE_FLOAT64 = 7
    TYPE_DATETIME = 8
    TYPE_BINARY = 9
    TYPE_TEXT = 10
    TYPE_OLE = 11
    TYPE_MEMO = 12
    TYPE_GUID = 15
    TYPE_96_bit_17_BYTES = 16
    TYPE_COMPLEX = 18


class GenisysObjectType(StrEnum):
    CEILING_FAN = "Fan"
    EXHAUST_FAN = "ExhaustFan"
    CURTAIN = "Curtain"
    HEATER = "GeneralSwitch"

    @classmethod
    def get(cls, value: str) -> str | None:
        return cls(value).name.lower() if value in cls else None


class DeviceTypeEnum(str, Enum):
    light = "light"
    curtain = "curtain"
    fan = "fan"
    fan_ceiling = "fan_ceiling"
    fan_exhaust = "fan_exhaust"
    heater = "heater"


class ObjectTypeEnum(Enum):
    curtain = "Curtain"
    light = "Light"
    fan = "Fan"
    exhaust_fan = "ExhaustFan"
    general_switch = "GeneralSwitch"
    unknown = "unknown"
