from pydantic import BaseModel


class AreaNamesBase(BaseModel):
    Area_ID: int
    Area: int | None
    AreaName: str | None
    Zone_ID: int | None
    GeniSysObject_ID: int | None
    Timeout: int | None
    NextPressIsPreset4Timeout: int | None
    DisallowPresetChangeTimeout: int | None
    Trim1: int | None
    Trim2: int | None
