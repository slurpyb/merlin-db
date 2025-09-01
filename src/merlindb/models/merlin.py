from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class MerlinBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    pk: ClassVar[str] = ""


class Dimmer(MerlinBaseModel):
    pk: ClassVar[str] = "dimmer_id"
    table_name: ClassVar[str] = "Phys_Dimmers"
    dimmer_id: int = Field(..., alias="Dimmer_ID")
    dimmer_type: str = Field(..., alias="LoadController")
    zone_id: int = Field(..., alias="Zone_ID")
    box_number: int = Field(..., alias="BoxNumber")


class Module(MerlinBaseModel):
    pk: ClassVar[str] = "module_id"
    table_name: ClassVar[str] = "Phys_Modules"
    module_id: int = Field(..., alias="Module_ID")
    module_type: str = Field(..., alias="Module")
    slot: int = Field(..., alias="Slot")
    dimmer_id: int = Field(..., alias="Dimmer_ID")


class PhysicalChannel(MerlinBaseModel):
    pk: ClassVar[str] = "channel_id"
    table_name: ClassVar[str] = "Phys_ChannelAlloc"
    channel_id: int = Field(..., alias="Phys_Channel_ID")
    number: int = Field(..., alias="PhysicalChannel")
    locked: bool = Field(..., alias="Locked")
    module_id: int = Field(..., alias="Module_ID")
    area_channels_id: int | None = Field(default=None, alias="AreaChannel_ID")


class LogicalChannel(MerlinBaseModel):
    pk: ClassVar[str] = "channel_id"
    table_name: ClassVar[str] = "AreaChannels"
    channel_id: int = Field(..., alias="AreaChannels_ID")
    number: int = Field(..., alias="Channel")
    name: str | None = Field(default="", alias="Channelname")
    area_id: int = Field(..., alias="Area")
    object_id: int | None = Field(default=None, alias="GenisysObject_ID")
    channel_type: str | None = Field(default=None)


class Zone(MerlinBaseModel):
    pk: ClassVar[str] = "zone_id"
    table_name: ClassVar[str] = "GenisysZones"
    zone_id: int = Field(..., alias="Zone_ID")
    name: str = Field(..., alias="Zone")


class Area(MerlinBaseModel):
    pk: ClassVar[str] = "area_id"
    table_name: ClassVar[str] = "AreaNames"
    area_id: int = Field(..., alias="Area")
    name: str | None = Field(default="", alias="AreaName")
    timeout: int | None = Field(default=0, alias="Timeout")
    zone_id: int | None = Field(default=None, alias="Zone_ID")
    object_id: int | None = Field(default=None, alias="GeniSysObject_ID")
    area_type: str | None = Field(default=None)


class Panel(MerlinBaseModel):
    pk: ClassVar[str] = "panel_id"
    table_name: ClassVar[str] = "GeniSysPanels"
    panel_id: int = Field(..., alias="Panel_ID")
    name: str = Field(..., alias="Panel")
    box_number: int = Field(..., alias="BoxNumber")
    any_button_on: bool = Field(..., alias="AnyButtonTurnOn")
    panel_type: str = Field(..., alias="PanelType")
    config_type: str | None = Field(default="", alias="PanelConfig")
    device_code: int = Field(..., alias="DeviceCode")


class Button(MerlinBaseModel):
    pk: ClassVar[str] = "number"
    table_name: ClassVar[str] = "GeniSysButtonFunctions"
    panel_id: int | None = Field(None, alias="Panel_ID")
    number: int | None = Field(None, alias="Button")
    name: str | None = Field(None, alias="Function")
    area_id: int | None = Field(None, alias="Area")
    channel_number: int | None = Field(None, alias="Channel")
    fade: int | None = Field(default=None, alias="FadeTime")
    engraving: str | None = Field(default=None, alias="Engraving")


class ObjectType(MerlinBaseModel):
    pk: ClassVar[str] = "object_id"
    table_name: ClassVar[str] = "GeniSysObjects"
    object_id: int | None = Field(default=None, alias="Object_ID")
    object_type: str | None = Field(default=None, alias="Object")
    area_id: int | None = Field(default=None, alias="Area_ID")


class Comms(MerlinBaseModel):
    table_name: ClassVar[str] = "Comms"
    pk: ClassVar[str] = "comms"
    comms: bool = Field(..., alias="comms")
    com_port_1: int = Field(..., alias="Comport1")
    baud_1: int = Field(..., alias="baud1")
    data_bits_1: int = Field(..., alias="databits1")
    parity_1: int | str | None = Field(default=None, alias="parity1")
    stop_bits_1: int = Field(..., alias="stopbits1")
    com_port_2: int = Field(..., alias="Comport2")
    baud_2: int = Field(..., alias="baud2")
    data_bits_2: int = Field(..., alias="databits2")
    parity_2: int | str | None = Field(default=None, alias="parity2")
    stop_bits_2: int = Field(..., alias="stopbits2")
    com_port_3: int = Field(..., alias="ComPort3")
    com_port_4: int = Field(..., alias="ComPort4")
    use_tcp: bool = Field(..., alias="UseTCP")
    hostname: str = Field(..., alias="hostname")


class AreaChannelLoad(MerlinBaseModel):
    pk: ClassVar[str] = "channel_id"
    table_name: ClassVar[str] = "AreaChannelLoads"
    channel_id: int = Field(alias="AreaChannels_ID")
    dimming: bool | None = Field(False, alias="Dimming")  # True=Dimming, False=Switching
    less_than: bool | None = Field(
        False, alias="Lessthan"
    )  # True=is less than the wattage below,   False=Greater than the wattage below
    wattage: int | None = Field(
        None, alias="Wattage"
    )  # The Wattage cut off we are interested in..   e.g. this channel is  Dimming < 300 watts.     True, True, 300
    fluoro: bool | None = Field(False, alias="Fluoro")
    dsi: bool | None = Field(False, alias="dimming")


class MerlinDbModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    dimmers: list[Dimmer] | None = Field(default=None, alias=Dimmer.table_name)
    modules: list[Module] | None = Field(default=None, alias=Module.table_name)
    physical_channels: list[PhysicalChannel] | None = Field(
        default=None, alias=PhysicalChannel.table_name
    )
    logical_channels: list[LogicalChannel] | None = Field(
        default=None, alias=LogicalChannel.table_name
    )
    zones: list[Zone] | None = Field(default=None, alias=Zone.table_name)
    areas: list[Area] | None = Field(default=None, alias=Area.table_name)
    panels: list[Panel] | None = Field(default=None, alias=Panel.table_name)
    buttons: list[Button] | None = Field(default=None, alias=Button.table_name)
    object_types: list[ObjectType] | None = Field(default=None, alias=ObjectType.table_name)
    comms: list[Comms] | None = Field(default=None, alias=Comms.table_name)
    area_channel_load: list[AreaChannelLoad] | None = Field(
        default=None, alias=AreaChannelLoad.table_name
    )


model_map = {
    "Dimmer": Dimmer,
    "Module": Module,
    "PhysicalChannel": PhysicalChannel,
    "LogicalChannel": LogicalChannel,
    "Comms": Comms,
    "Zone": Zone,
    "Button": Button,
    "Panel": Panel,
    "AreaChannelLoad": AreaChannelLoad,
    "ObjectType": ObjectType,
    "Area": Area,
}
