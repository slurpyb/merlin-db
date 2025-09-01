import datetime as dt

from pydantic import BaseModel


class GenisysTableBase(BaseModel):
    pass


class AVManufacturerBase(GenisysTableBase):
    AVManufacturer_ID: int
    Manufacturer: str | None


class AVManufacturer(AVManufacturerBase):
    AVManufacturer_ID: int | None


class AVModelBase(GenisysTableBase):
    AVModel_ID: int
    AVManufacturer_ID: int | None
    Model: str | None


class AVModel(AVModelBase):
    AVModel_ID: int | None


class ButtonMultiStateBase(GenisysTableBase):
    ButtonMultiState_ID: int
    ButtonIndex: int | None
    ButtonLabel: str | None
    Macro_ID: int | None
    Area: int | None
    Preset: int | None
    CustomCode_ID: int | None
    Colour: int | None


class ButtonMultiState(ButtonMultiStateBase):
    ButtonMultiState_ID: int | None


class CommsBase(GenisysTableBase):
    comms: int
    Comport1: bool
    baud1: str | None
    databits1: str | None
    parity1: str | None
    stopbits1: str | None
    Comport2: bool
    baud2: str | None
    databits2: str | None
    parity2: str | None
    stopbits2: str | None
    ComPort3: bool
    baud3: str | None
    databits3: str | None
    parity3: str | None
    stopbits3: str | None
    ComPort4: bool
    baud4: str | None
    databits4: str | None
    parity4: str | None
    stopbits4: str | None
    UseTCP: bool
    hostname: str | None


class Comms(CommsBase):
    pass


class ConfigBase(GenisysTableBase):
    Config_ID: int
    AreaNames: int | None
    LightLevels: int | None
    Events: int | None
    Scheduler: int | None
    Email: int | None
    CustomCode: int | None
    InfraRed: int | None
    DMXCommands: int | None
    DDEAbility: int | None
    DigiLin: int | None
    RollCall: int | None
    Macros: int | None
    DirectControl: int | None
    Plan: int | None
    Monitor: int | None
    SensorLog: int | None
    MacrosRunning: int | None
    MacroDynalite: int | None
    MacroWAVFiles: int | None
    MacroCustomCodes: int | None
    MacroEmail: int | None
    MacroRunMacros: int | None
    MacroCancelMacros: int | None
    MacroReports: int | None
    MacroIRControl: int | None
    MacroDMXControl: int | None
    MacroDigiLin: int | None
    MacroRollCall: int | None
    MacroDynaliteChannels: int | None
    Buttonversion: int | None
    Editbuttons: int | None
    EnableMonitorLog: bool
    MonitorLogMaxRecords: int | None
    LoadFromMonitorLog: int | None
    EnableSensorLog: bool
    SensorLogMaxRecords: int | None
    EnableEnergyUsage: bool
    Counter: int | None
    Latitude: float | None
    Longitude: float | None
    Timezone: float | None
    DaylightSaving: bool
    UserCanSaveLightingPresets: bool
    UserCanSeekChannels: bool
    ReleaseRate: int | None
    DoNotallowShutdown: bool


class Config(ConfigBase):
    Config_ID: int | None


class CurtainOpenStatusBase(GenisysTableBase):
    CurtainOpenStatus_ID: int
    CurtainArea: int | None
    CurtainOpenStatus: bool


class CurtainOpenStatus(CurtainOpenStatusBase):
    CurtainOpenStatus_ID: int | None


class CustomCodesBase(GenisysTableBase):
    CustomCode_ID: int
    CustomCodeName: str | None
    CustomCode: str | None
    CustomCodeRS232: str | None


class CustomCodes(CustomCodesBase):
    CustomCode_ID: int | None


class DeviceTypesBase(GenisysTableBase):
    Device_ID: int
    Device: str | None
    DeviceOpCode: str | None


class DeviceTypes(DeviceTypesBase):
    Device_ID: int | None


class DevicesInstalledBase(GenisysTableBase):
    DevicesInstalled_ID: int
    Device_ID: int | None
    BoxNumber: int | None
    Description: str | None


class DevicesInstalled(DevicesInstalledBase):
    DevicesInstalled_ID: int | None


class DigiLinLightBoxBase(GenisysTableBase):
    DigiLinLightBox_ID: int
    DigiLinBoxNumber: int | None
    Area: int | None
    Channel: int | None
    ChannelDesc: str | None


class DigiLinLightBox(DigiLinLightBoxBase):
    DigiLinLightBox_ID: int | None


class DynaliteBase(GenisysTableBase):
    Dynalite_ID: int
    Area: int | None
    Preset: int | None
    Fade: float | None
    DynaliteRS232: str | None
    Channel: int | None
    Level: int | None


class Dynalite(DynaliteBase):
    Dynalite_ID: int | None


class EmailsBase(GenisysTableBase):
    Email_ID: int
    EmailName: str | None
    Recipients: str | None
    Subject: str | None
    Message: str | None


class Emails(EmailsBase):
    Email_ID: int | None


class FactorySet6SeriesBase(GenisysTableBase):
    ID: int
    DataString: str | None
    Keyword: str | None
    Comments: str | None


class FactorySet6Series(FactorySet6SeriesBase):
    ID: int | None


class GeniSysObjectsBase(GenisysTableBase):
    Object_ID: int
    Object: str | None
    Area_ID: int | None


class GeniSysObjects(GeniSysObjectsBase):
    Object_ID: int | None


class GenisysAirCondMasterMotorBase(GenisysTableBase):
    AirCondMasterMotor_ID: int
    GenisysObject_ID: int | None


class GenisysAirCondMasterMotor(GenisysAirCondMasterMotorBase):
    AirCondMasterMotor_ID: int | None


class GenisysBacklightingBase(GenisysTableBase):
    Backlighting_ID: int
    MorningTime: dt.datetime | None
    MorningBacklightLevel: int | None
    MorningIndicatorLevel: int | None
    EveningTime: dt.datetime | None
    EveningBacklightLevel: int | None
    EveningIndicatorLevel: int | None


class GenisysBacklighting(GenisysBacklightingBase):
    Backlighting_ID: int | None


class GenisysOtherObjectsBase(GenisysTableBase):
    OtherObjects_ID: int
    OtherObject: str | None
    Area_ID: int | None
    HeightAboveFloorLevel: str | None
    Comments: str | None


class GenisysOtherObjects(GenisysOtherObjectsBase):
    OtherObjects_ID: int | None


class GenisysSensorChannelsBase(GenisysTableBase):
    GenisysSensorChannels_ID: int
    GenisysSensorObject_ID: int | None
    Areachannel_ID: int | None
    DisableifOperatedbySwitch: bool
    Level: int | None


class GenisysSensorChannels(GenisysSensorChannelsBase):
    GenisysSensorChannels_ID: int | None


class GenisysSensorObjectBase(GenisysTableBase):
    GenisysSensorObject_ID: int
    GenisysSensor: str | None
    Area_ID: int | None
    AreaNumbertoListenOn: int | None
    PresetnumbertoListenTo: int | None
    ActiveTimeStart: dt.datetime | None
    ActiveTimeEnd: dt.datetime | None
    Disabled: bool
    FadeOnTime: int | None
    FadeOffTime: int | None
    TimeOut: int | None


class GenisysSensorObject(GenisysSensorObjectBase):
    GenisysSensorObject_ID: int | None


class GenisysUserPresetsBase(GenisysTableBase):
    GenisysUserPresets_ID: int
    Preset_ID: int | None
    Channel: int | None
    Level: int | None


class GenisysUserPresets(GenisysUserPresetsBase):
    GenisysUserPresets_ID: int | None


class GenisysZonesBase(GenisysTableBase):
    Zone_ID: int
    Zone: str | None


class GenisysZones(GenisysZonesBase):
    Zone_ID: int | None


class GreenTrimTimesBase(GenisysTableBase):
    GreenTrim_ID: int
    TrimTime1: str | None
    TrimTime2: str | None


class GreenTrimTimes(GreenTrimTimesBase):
    GreenTrim_ID: int | None


class IRCommandsBase(GenisysTableBase):
    IRCommand_ID: int
    AVModel_ID: int | None
    CommandName: str | None
    IRCode: str | None


class IRCommands(IRCommandsBase):
    IRCommand_ID: int | None


class LampFittingsBase(GenisysTableBase):
    LampFitting_ID: int
    LampDescription: str | None
    RatedWattage: int | None
    Losses: int | None


class LampFittings(LampFittingsBase):
    LampFitting_ID: int | None


class LoadControllersBase(GenisysTableBase):
    Dimmer_ID: int
    Zone_ID: int | None
    LoadController: str | None
    Boxnumber: int | None
    Module: str | None
    PhysicalChannel: int | None
    AreaChannel_ID: int | None
    Locked: bool


class LoadControllers(LoadControllersBase):
    Dimmer_ID: int | None


class MacrosBase(GenisysTableBase):
    Macro_ID: int
    Macro: str | None
    Enabled: bool


class Macros(MacrosBase):
    Macro_ID: int | None


class PasswordBase(GenisysTableBase):
    Password: str | None


class Password(PasswordBase):
    pass


class Phys_DimmersBase(GenisysTableBase):
    Dimmer_ID: int
    Zone_ID: int | None
    LoadController: str | None
    BoxNumber: int | None


class Phys_Dimmers(Phys_DimmersBase):
    Dimmer_ID: int | None


class PlanIndicatorsBase(GenisysTableBase):
    PlanIndicator_ID: int
    Index: int | None
    IndicatorLEFT: float | None
    IndicatorTOP: float | None
    Area: int | None
    WMFFile_ID: int | None


class PlanIndicators(PlanIndicatorsBase):
    PlanIndicator_ID: int | None


class ProjectNameBase(GenisysTableBase):
    ProjectName_ID: int
    ProjectName: str | None


class ProjectName(ProjectNameBase):
    ProjectName_ID: int | None


class RollCallBase(GenisysTableBase):
    Rollcall_ID: int
    RollCallName: str | None
    Device_ID: int | None
    Boxnumber: int | None


class RollCall(RollCallBase):
    Rollcall_ID: int | None


class RollCallActionsBase(GenisysTableBase):
    RollCallAction_ID: int
    RollCall: str | None
    emailRecipients: str | None
    MacrotoRun: str | None


class RollCallActions(RollCallActionsBase):
    RollCallAction_ID: int | None


class ScheduleWorkspaceBase(GenisysTableBase):
    ScheduleWorkspace_ID: int
    Scheduler_ID: int | None
    StartDateTime: dt.datetime | None
    Macro: str | None


class ScheduleWorkspace(ScheduleWorkspaceBase):
    ScheduleWorkspace_ID: int | None


class SchedulerBase(GenisysTableBase):
    Scheduler_ID: int
    StartTime: dt.datetime | None
    Startdate: dt.datetime | None
    Hours: dt.datetime | str | None
    Before: bool
    Sunset: bool
    Macro_ID: int | None
    RecurringDaily: bool
    D1_EveryXdays: int | None
    D2_EveryWeekDay: bool
    D3_EveryWeekEndDay: bool
    RecurringWeekly: bool
    W_EveryXweeks: int | None
    W_Mon: bool
    W_Tues: bool
    W_Wed: bool
    W_Thurs: bool
    W_Fri: bool
    W_Sat: bool
    W_Sun: bool
    RecurringMonthly: bool
    M1_EveryWhatDay: int | None
    M1_OfEveryXmonths: int | None
    M2_TheWhatDay: str | None
    M2_OfEveryWhatDay: str | None
    M2_OfEveryXmonths: str | None
    RecurringYearly: bool
    Y1_EverywhatDay: int | None
    Y1_OfEveryNameofMonth: str | None
    Y2_TheFirstSecondThirdFourthLast: str | None
    Y2_DayOfWeek: str | None
    Y2_OfEveryNameofMonth: str | None
    Disabled: bool


class Scheduler(SchedulerBase):
    Scheduler_ID: int | None


class SensorIntervalBase(GenisysTableBase):
    SensorInterval: int | None


class SensorInterval(SensorIntervalBase):
    pass


class SensorsBase(GenisysTableBase):
    SensorBoxNum: int | None
    SensorDesc: str | None
    Calibration: str | None
    Lastcalibrated: dt.datetime | None
    LogthisSensor: bool


class Sensors(SensorsBase):
    pass


class StereoInputsBase(GenisysTableBase):
    StereoInput_ID: int
    StereoInput: int | None
    Area_ID: int | None


class StereoInputs(StereoInputsBase):
    StereoInput_ID: int | None


class TreeViewBase(GenisysTableBase):
    TreeView_ID: int
    Label: str | None
    ChildOf: int | None
    WMFFile: str | None
    IconSize: int | None
    Left: float | None
    Width: float | None
    Top: float | None
    Height: float | None


class TreeView(TreeViewBase):
    TreeView_ID: int | None


class VersionBase(GenisysTableBase):
    Version_ID: int
    Version: float | None
    Build: int | None


class Version(VersionBase):
    Version_ID: int | None


class WAVfilesBase(GenisysTableBase):
    WAVfile_ID: int
    WAVFile: str | None


class WAVfiles(WAVfilesBase):
    WAVfile_ID: int | None


class WMFFilesBase(GenisysTableBase):
    WMFFile_ID: int
    WMFFile: str | None


class WMFFiles(WMFFilesBase):
    WMFFile_ID: int | None


class WeatherAreasBase(GenisysTableBase):
    WeatherAreas_ID: int
    Weather: int | None
    AirQuality: int | None
    WindSpeed: int | None
    WindDirection: int | None
    RateofTemp: int | None
    DirectionofTemp: int | None


class WeatherAreas(WeatherAreasBase):
    WeatherAreas_ID: int | None


class WeatherConditionsBase(GenisysTableBase):
    WeatherConditions_ID: int
    Weather: int | None
    WeatherTime: str | None
    Airquality: int | None
    AirQualityTime: str | None
    WindSpeed: int | None
    WindSpeedTime: str | None
    WindDirection: int | None
    WindDirectionTime: str | None
    RateofTemp: int | None
    RateofTempTime: str | None
    DirectionofTemp: int | None
    DirectionofTempTime: str | None


class WeatherConditions(WeatherConditionsBase):
    WeatherConditions_ID: int | None


class WeatherSchedulesBase(GenisysTableBase):
    WeatherSchedule_ID: int
    Day: str | None
    Active: int | None
    Macro_ID: int | None
    TimetoExecute: str | None
    DisableWP: int | None
    EnableWP: int | None


class WeatherSchedules(WeatherSchedulesBase):
    WeatherSchedule_ID: int | None


class heroBase(GenisysTableBase):
    id: int
    name: str | None
    secret_name: str | None
    age: int | None


class hero(heroBase):
    pass


class AreaNamesBase(GenisysTableBase):
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


class AreaNames(AreaNamesBase):
    Area_ID: int | None


class ButtonsBase(GenisysTableBase):
    Button_ID: int
    ButtonIndex: int | None
    Buttonlabel: str | None
    Macro_ID: int | None


class Buttons(ButtonsBase):
    Button_ID: int | None


class DigiLinChannelLevelsBase(GenisysTableBase):
    DigiLinChannelLevel_ID: int
    DigiLinLightBox_ID: int | None
    ChannelLevel: int | None
    ChannelLevelDesc: str | None
    DigiLinRS232: str | None


class DigiLinChannelLevels(DigiLinChannelLevelsBase):
    DigiLinChannelLevel_ID: int | None


class EventsBase(GenisysTableBase):
    Event_ID: int
    EventName: str | None
    Area: int | None
    Preset: int | None
    CustomCode_ID: int | None
    Macro_ID: int | None


class Events(EventsBase):
    Event_ID: int | None


class LampFittingsonChannelBase(GenisysTableBase):
    LampFittingsonChannel_ID: int
    LampFitting_ID: int | None
    Number: int | None
    Area: int | None
    Channel: int | None


class LampFittingsonChannel(LampFittingsonChannelBase):
    LampFittingsonChannel_ID: int | None


class LampInterpolationsBase(GenisysTableBase):
    LampInterpolations_ID: int
    Lampfitting_ID: int | None
    InterpolatedPercentage: int | None
    InterpolatedLevel: float | None


class LampInterpolations(LampInterpolationsBase):
    LampInterpolations_ID: int | None


class LampPropertiesBase(GenisysTableBase):
    LampCharacteristic_ID: int
    LampFitting_ID: int | None
    PowerPercentage: int | None
    Load: float | None


class LampProperties(LampPropertiesBase):
    LampCharacteristic_ID: int | None


class Phys_ModulesBase(GenisysTableBase):
    Module_ID: int
    Dimmer_ID: int | None
    Module: str | None
    Slot: int | None


class Phys_Modules(Phys_ModulesBase):
    Module_ID: int | None


class PlanAreaColoursBase(GenisysTableBase):
    PlanAreaColour_ID: int
    Area: int | None
    WMFFile_ID: int | None
    DefaultColour: int | None


class PlanAreaColours(PlanAreaColoursBase):
    PlanAreaColour_ID: int | None


class SchedulesBase(GenisysTableBase):
    Schedule_ID: int
    RecurringDay: str | None
    RecurringTime: dt.datetime | None
    SpecificDate: dt.datetime | None
    Hours: dt.datetime | None
    Before: bool
    Sunrise: bool
    Macro_ID: int | None
    LasttimeExecuted: dt.datetime | None


class Schedules(SchedulesBase):
    Schedule_ID: int | None


class AreaChannelsBase(GenisysTableBase):
    AreaChannels_ID: int
    Area: int | None
    Channel: int | None
    Channelname: str | None
    GenisysObject_ID: int | None


class AreaChannels(AreaChannelsBase):
    AreaChannels_ID: int | None


class GeniSysPanelsBase(GenisysTableBase):
    Panel_ID: int
    Panel: str | None
    Area_ID: int | None
    BoxNumber: int | None
    NumberofButtons: int | None
    AnyButtonTurnOn: bool
    PanelType: str | None
    PanelConfig: str | None
    DeviceCode: str | None
    Version: str | None


class GeniSysPanels(GeniSysPanelsBase):
    Panel_ID: int | None


class MacrosDetailsBase(GenisysTableBase):
    MacroDetails_ID: int
    Macro_ID: int | None
    WAVfile_ID: int | None
    Email_ID: int | None
    Dynalite_ID: int | None
    CustomCode_ID: int | None
    DigiLinChannelLevel_ID: int | None
    SubMacro: str | None
    CancelMacro: str | None
    EnableMacro: str | None
    DisableMacro: str | None
    Rollcall: str | None
    Delay: float | None
    TreeView_ID: int | None


class MacrosDetails(MacrosDetailsBase):
    MacroDetails_ID: int | None


class Phys_ChannelAllocBase(GenisysTableBase):
    Phys_Channel_ID: int
    Module_ID: int | None
    PhysicalChannel: int | None
    AreaChannel_ID: int | None
    Locked: bool


class Phys_ChannelAlloc(Phys_ChannelAllocBase):
    Phys_Channel_ID: int | None


class PlanPresetColoursBase(GenisysTableBase):
    PlanPresetColour_ID: int
    PlanAreaColour_ID: int | None
    Preset: int | None
    Colour: int | None
    Icon: str | None


class PlanPresetColours(PlanPresetColoursBase):
    PlanPresetColour_ID: int | None


class PresetNamesBase(GenisysTableBase):
    Preset_ID: int
    Preset: int | None
    PresetName: str | None
    Area: int | None


class PresetNames(PresetNamesBase):
    Preset_ID: int | None


class ScheduleExceptionsBase(GenisysTableBase):
    ExceptionDates_ID: int
    Date: dt.datetime | None
    Schedule_ID: int | None


class ScheduleExceptions(ScheduleExceptionsBase):
    ExceptionDates_ID: int | None


class AreaChannelLoadsBase(GenisysTableBase):
    AreaChannelLoad_ID: int
    AreaChannels_ID: int | None
    Dimming: bool
    Lessthan: bool
    Wattage: int | None
    Fluoro: bool
    dsi: bool


class AreaChannelLoads(AreaChannelLoadsBase):
    AreaChannelLoad_ID: int | None


class GeniSysButtonFunctionsBase(GenisysTableBase):
    GeniSysButtonFunctions_ID: int
    Panel_ID: int | None
    Button: int | None
    Function: str | None
    Area: int | None
    Channel: int | None
    Macro_ID: int | None
    Macro1_ID: int | None
    FadeTime: float | None
    LeaveLEDOn: bool
    HideButton: bool
    IRButton: bool
    Engraving: str | None


class GeniSysButtonFunctions(GeniSysButtonFunctionsBase):
    GeniSysButtonFunctions_ID: int | None


model_map = {
    "AVManufacturer": AVManufacturer,
    "AVModel": AVModel,
    "ButtonMultiState": ButtonMultiState,
    "Comms": Comms,
    "Config": Config,
    "CurtainOpenStatus": CurtainOpenStatus,
    "CustomCodes": CustomCodes,
    "DeviceTypes": DeviceTypes,
    "DevicesInstalled": DevicesInstalled,
    "DigiLinLightBox": DigiLinLightBox,
    "Dynalite": Dynalite,
    "Emails": Emails,
    "FactorySet6Series": FactorySet6Series,
    "GeniSysObjects": GeniSysObjects,
    "GenisysAirCondMasterMotor": GenisysAirCondMasterMotor,
    "GenisysBacklighting": GenisysBacklighting,
    "GenisysOtherObjects": GenisysOtherObjects,
    "GenisysSensorChannels": GenisysSensorChannels,
    "GenisysSensorObject": GenisysSensorObject,
    "GenisysUserPresets": GenisysUserPresets,
    "GenisysZones": GenisysZones,
    "GreenTrimTimes": GreenTrimTimes,
    "IRCommands": IRCommands,
    "LampFittings": LampFittings,
    "LoadControllers": LoadControllers,
    "Macros": Macros,
    "Password": Password,
    "Phys_Dimmers": Phys_Dimmers,
    "PlanIndicators": PlanIndicators,
    "ProjectName": ProjectName,
    "RollCall": RollCall,
    "RollCallActions": RollCallActions,
    "ScheduleWorkspace": ScheduleWorkspace,
    "Scheduler": Scheduler,
    "SensorInterval": SensorInterval,
    "Sensors": Sensors,
    "StereoInputs": StereoInputs,
    "TreeView": TreeView,
    "Version": Version,
    "WAVfiles": WAVfiles,
    "WMFFiles": WMFFiles,
    "WeatherAreas": WeatherAreas,
    "WeatherConditions": WeatherConditions,
    "WeatherSchedules": WeatherSchedules,
    "hero": hero,
    "AreaNames": AreaNames,
    "Buttons": Buttons,
    "DigiLinChannelLevels": DigiLinChannelLevels,
    "Events": Events,
    "LampFittingsonChannel": LampFittingsonChannel,
    "LampInterpolations": LampInterpolations,
    "LampProperties": LampProperties,
    "Phys_Modules": Phys_Modules,
    "PlanAreaColours": PlanAreaColours,
    "Schedules": Schedules,
    "AreaChannels": AreaChannels,
    "GeniSysPanels": GeniSysPanels,
    "MacrosDetails": MacrosDetails,
    "Phys_ChannelAlloc": Phys_ChannelAlloc,
    "PlanPresetColours": PlanPresetColours,
    "PresetNames": PresetNames,
    "ScheduleExceptions": ScheduleExceptions,
    "AreaChannelLoads": AreaChannelLoads,
    "GeniSysButtonFunctions": GeniSysButtonFunctions,
}
