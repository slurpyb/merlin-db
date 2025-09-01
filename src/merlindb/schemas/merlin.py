from pydantic import BaseModel, Field

from merlindb.consts import ObjectTypeEnum


class ReadZone(BaseModel):
    id: int = Field(alias="Zone_ID")
    name: str = Field(alias="Zone")


class ReadArea(BaseModel):
    area_id: int | None = Field(alias="Area_ID")
    id: int | None = Field(alias="Area")
    name: str | None = Field(alias="AreaName")
    zone_id: int | None = Field(alias="Zone_ID")
    object_id: int | None = Field(alias="GeniSysObject_ID")
    timeout: int | None = Field(alias="Timeout")
    next_press_preset_4_timeout: int | None = Field(alias="NextPressIsPreset4Timeout")
    disallow_preset_change_timeout: int | None = Field(alias="DisallowPresetChangeTimeout")
    trim_1: int | None = Field(alias="Trim1")
    trim_2: int | None = Field(alias="Trim2")


class ReadChannel(BaseModel):
    area_channels_id: int | None = Field(alias="AreaChannels_ID")
    id: int = Field(alias="Channel")
    area_id: int = Field(alias="Area")
    name: str = Field(alias="Channelname")
    object_id: int | None = Field(alias="GenisysObject_ID")


class ReadObjectType(BaseModel):
    area_id: int | None = Field(alias="Area_ID")
    object_type: ObjectTypeEnum | None = Field(alias="Object")
    object_id: int | None = Field(alias="Object_ID")

    class Config:
        use_enum_values = True


class ReadAreaChannelLoads(BaseModel):
    AreaChannelLoad_ID: int | None = Field(alias="AreaChannelLoad_ID")
    AreaChannels_ID: int | None = Field(alias="AreaChannels_ID")
    Dimming: bool | None = Field(alias="Dimming")
    Lessthan: bool | None = Field(alias="Lessthan")
    Wattage: int | None = Field(alias="Wattage")
    Fluoro: bool | None = Field(alias="Fluoro")
    dsi: bool | None = Field(alias="dsi")


class ReadPhysDimmers(BaseModel):
    dimmer_id: int | None = Field(alias="Dimmer_ID")
    zone_id: int | None = Field(alias="Zone_ID")
    name: str | None = Field(alias="LoadController")
    box_number: int | None = Field(alias="BoxNumber")


class ReadPhysModules(BaseModel):
    module_id: int | None = Field(alias="Module_ID")
    dimmer_id: int | None = Field(alias="Dimmer_ID")
    name: str | None = Field(alias="Module")
    slot: int | None = Field(alias="Slot")


class ReadPhysChannelAlloc(BaseModel):
    physical_channel_id: int | None = Field(alias="Phys_Channel_ID")
    module_id: int | None = Field(alias="Module_ID")
    number: int | None = Field(alias="PhysicalChannel")
    area_channel_id: int | None = Field(alias="AreaChannel_ID")
    locked: bool | None = Field(alias="Locked")
