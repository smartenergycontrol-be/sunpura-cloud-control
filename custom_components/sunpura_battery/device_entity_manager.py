import logging
from typing import  Any


from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from .sensor import AeccSensor
from .switch import AeccSwitch
from .device_manager import DeviceManager

_LOGGER = logging.getLogger(__name__)


class DeviceEntityManager:
    """设备实体管理器，负责创建和管理不同类型的设备实体

        ### 通过HACS安装（推荐）

        1. 确保已安装[HACS](https://hacs.xyz/)
        2. 点击引入ha前端页面：
           [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?repository=https%3A%2F%2Fgithub.com%2Fyan1ib0%2Faecc_ha_dashboard&category=custom_panel&owner=yan1ib0)
        3. 在HACS中搜索"aecc"并安装

    """

    def __init__(self, hass: HomeAssistant, hub):
        self.hass = hass
        self.hub = hub
        self.dcm = DeviceManager(self.hass, self.hub)
        self.entities: dict[str, list[Entity]] = {"sensor": [], "switch": []}
        self.devices = []


    async def create_entities_from_data(self, data: dict) -> dict[str, list[Any]]:
        """根据API返回的数据创建设备实体"""
        
        _LOGGER.debug(f"植物数据键名: {list(data.keys())}")
        entities: dict[str, list[Any]] = {"sensor": [], "switch": []}
        # 处理负载设备列表
        if 'loadList' in data and data['loadList']:
            for load in data['loadList']:
                if load['iconType'] == 5:  # 插座类型
                    _LOGGER.debug(f"插座新建：{load}")
                    device = self.dcm.create_device(device_info=load)
                    self.devices.append(device)
                    entity = AeccSwitch(self.hass, self.hub, device, "switch", device.device_sn + "_socket_switch")
                    entities[entity.pf].append(entity)
                    #智能联动
                    # intervention = AeccSwitch(self.hass, self.hub, device, "intervention", device.device_sn + "_socket_intervention")
                    #目前未实现 禁用
                    # intervention.disable_entity()
                    # entities[entity.pf].append(intervention)
                    # AI预约用电
                    # ai_switch = AeccSwitch(self.hass, self.hub, device, "AI electricity reservation", device.device_sn + "_socket_ai")
                    # 目前未实现 禁用
                    # ai_switch.disable_entity()
                    # entities[entity.pf].append(ai_switch)
                    entities["sensor"].append(AeccSensor(self.hub, device, "device name",   device.device_sn+"_device_name", ""))
                    # _LOGGER.info(f"实体类型：{entity.pf}")
                    # "设备序列号": "NKPG1DDC40",
                    #  "Device sn": "NKPG1DDC40",
                    #                 "Rated power": "200.0W",
                    #                 "Current value": "0.0A",
                    #                 "Current power": "0.0W",
                    #                 "Current voltage": "232.4V",
                    #                 "Today electricity consumption": "0.0kWh",
                    #                 "Total power": "22.564kWh"
                    # "额定功率": "200.0W",
                    entities["sensor"].append(AeccSensor( self.hub, device, "rate power", device.device_sn + "_socket_rate", "W",field_name="Rated power"))
                    # "当前电流": "0.146A",
                    entities["sensor"].append(AeccSensor(self.hub, device, "current", device.device_sn + "_socket_cur", "A",field_name="Current value"))
                    # "当前功率": "16.1W",
                    entities["sensor"].append( AeccSensor(self.hub, device, "power", device.device_sn + "_socket_pow", "W",field_name="Current power"))
                    # "当前电压": "235.4V",
                    entities["sensor"].append( AeccSensor(self.hub, device, "vol", device.device_sn + "_socket_vol", "V",field_name="Current voltage"))
                    # "今日用电量": "0.0kWh",
                    entities["sensor"].append( AeccSensor(self.hub, device, "today energy", device.device_sn + "_socket_elec_day", "kWh",field_name="Today electricity consumption"))
                    # "总用电量": "6.206kWh"
                    entities["sensor"].append( AeccSensor(self.hub, device, "total energy", device.device_sn + "_socket_elec_total", "kWh",field_name="Total power"))

        # 处理充电桩设备列表
        if 'chargerList' in data and data['chargerList']:
            for charger in data['chargerList']:
                if charger['iconType'] == 6:  # 充电桩类型
                    _LOGGER.debug(f"充电桩新建：{charger}")
                    device = self.dcm.create_device(device_info=charger)
                    self.devices.append(device)
                    entity = AeccSwitch(self.hass, self.hub, device, "switch", device.device_sn + "_charger_switch")
                    entities[entity.pf].append(entity)
                    #智能联动
                    # intervention = AeccSwitch(self.hass, self.hub, device, "intervention", device.device_sn + "_socket_intervention")
                    #目前未实现 禁用
                    # intervention.disable_entity()
                    # entities[entity.pf].append(intervention)
                    # AI预约用电
                    # ai_switch = AeccSwitch(self.hass, self.hub, device, "AI electricity reservation", device.device_sn + "_socket_ai")
                    # 目前未实现 禁用
                    # "Charging Status": "Charger Plug Connected",
                    # "Charging and Discharging Voltage": "0.0V",
                    # "Charging and Discharging Current": "0.0A",
                    # "Charging and Discharging Power": "0.0kW",
                    # "Charger Plug Temperature": "0℃",
                    # "datalog sn": "SXDI78C594"
                    # ai_switch.disable_entity()
                    # entities[entity.pf].append(ai_switch)
                    entities["sensor"].append(  AeccSensor(self.hub, device, "device name",  device.device_sn + "_device_name", ""))
                    # _LOGGER.info(f"实体类型：{entity.pf}")
                    #"充电状态": "枪已连接",
                    entities["sensor"].append( AeccSensor(self.hub, device, "charger status", device.device_sn + "_charger_status", "",field_name="Charging Status"))
                    # "充放电电压": "0.0V",
                    entities["sensor"].append( AeccSensor(self.hub, device, "vol", device.device_sn + "_charger_vol", "V",field_name="Charging and Discharging Voltage"))
                    # "充放电电流": "0.0A",
                    entities["sensor"].append( AeccSensor(self.hub, device, "current", device.device_sn + "_charger_cur", "A",field_name="Charging and Discharging Current"))
                    # "充放电功率": "0.0kW",
                    entities["sensor"].append( AeccSensor(self.hub, device, "power", device.device_sn + "_charger_pow", "kW",field_name="Charging and Discharging Power"))
                    # "充电枪温度": "0℃",
                    entities["sensor"].append( AeccSensor(self.hub, device, "Temperature", device.device_sn + "_charger_temp", "℃",field_name="Charger Plug Temperature"))
                    # "采集器序列号": "SXDI78C594"
                    entities["sensor"].append( AeccSensor(self.hub, device, "charger sn", device.device_sn + "_charger_sn", "",field_name="datalog sn"))
        # 处理功率控制器列表
        if 'heatPumpList' in data and data['heatPumpList']:
            for heat in data['heatPumpList']:
                if heat['iconType'] == 9:  # 功率控制器
                    _LOGGER.debug(f"功率控制器新建：{heat}")
                    device = self.dcm.create_device(device_info=heat)
                    self.devices.append(device)
                    entity = AeccSwitch(self.hass, self.hub, device, "switch", device.device_sn + "__switch")
                    entities[entity.pf].append(entity)
        # 储能，电表，能管主控数据都在这里 数据是动态的
        # 电表
        if  data.get("emSn") is not None :
            res = await self.hub.fetch_device_info(data.get("emType"), data.get("emSn"))

            if res:
                _LOGGER.debug(f"电表新建：{res}")
                # em = self.dcm.create_device(device_info=res)
                em = self.dcm.create_device(device_info={
                    "deviceSn": data.get("emSn"),
                    "deviceName": data.get("emSn"),
                    "datalogSn": data.get("emSn"),
                    "iconType": 7,
                    "type":data.get("emType"),
                    "deviceCodeType": 0,
                    "status": 0,
                    "switchStatus": 0,
                })
                self.devices.append(em)
                _LOGGER.debug(f"电表displayMap:{res["displayMap"].items()}")
                for k,v in res["displayMap"].items():
                    entities["sensor"].append(AeccSensor(self.hub, em, k, em.device_sn+k, ""))

        # 处理电池设备 (检查不同的可能字段名)
        battery_sn = data.get("batSn") or data.get("batterySn") or data.get("storageSn")
        battery_type = data.get("batType") or data.get("batteryType") or data.get("storageType")
        
        if battery_sn is not None:
            res = await self.hub.fetch_device_info(battery_type, battery_sn)
            
            if res:
                _LOGGER.debug(f"电池新建：{res}")
                battery = self.dcm.create_device(device_info={
                    "deviceSn": battery_sn,
                    "deviceName": battery_sn,
                    "datalogSn": battery_sn,
                    "iconType": 2,
                    "type": battery_type,
                    "deviceCodeType": 0,
                    "status": 0,
                    "switchStatus": 0,
                })
                self.devices.append(battery)
                _LOGGER.debug(f"电池displayMap:{res["displayMap"].items()}")
                for k, v in res["displayMap"].items():
                    entities["sensor"].append(AeccSensor(self.hub, battery, k, battery.device_sn + k, ""))

        # 处理电池设备列表 (如果存在 batteryList)
        if 'batteryList' in data and data['batteryList']:
            for battery_info in data['batteryList']:
                if battery_info.get('iconType') == 2:  # 电池类型
                    _LOGGER.debug(f"电池列表新建：{battery_info}")
                    battery_device = self.dcm.create_device(device_info=battery_info)
                    self.devices.append(battery_device)
                    
                    # 获取详细的电池信息
                    res = await self.hub.fetch_device_info(battery_info.get('deviceType'), battery_info.get('datalogSn'))
                    if res and res.get("displayMap"):
                        _LOGGER.debug(f"电池列表displayMap:{res["displayMap"].items()}")
                        for k, v in res["displayMap"].items():
                            entities["sensor"].append(AeccSensor(self.hub, battery_device, k, battery_device.device_sn + k, ""))

        if  data.get("solarSn") is not None:
            res = await self.hub.fetch_device_info( data.get("solarType"),data.get("solarSn"))
            if res:
                _LOGGER.debug(f"储能新建：{res}")
                # em = self.dcm.create_device(device_info=res)
                bs = self.dcm.create_device(device_info={
                    "deviceSn": data.get("solarSn"),
                    "deviceName": data.get("solarSn"),
                    "datalogSn": data.get("solarSn"),
                    "iconType": 3,
                    "type": data.get("solarType"),
                    "deviceCodeType": 0,
                    "status": 0,
                    "switchStatus": 0,
                })
                self.devices.append(bs)
                _LOGGER.debug(f"储能displayMap:{res["displayMap"].items()}")
                for k, v in res["displayMap"].items():
                    entities["sensor"].append(AeccSensor(self.hub, bs, k, bs.device_sn + k, ""))
        if  data.get("deviceSn") is not None:
            master = self.dcm.create_device(device_info={
                        "deviceSn": data.get("deviceSn"),
                        "deviceName": data.get("deviceSn"),
                        "datalogSn": data.get("deviceSn"),
                        "iconType": 3,
                        "type":data.get("deviceType"),
                        "deviceCodeType": 0,
                        "status": 0,
                        "switchStatus": 0,
                    })
            self.devices.append(master)
            _LOGGER.error(f"创建主控entity   master：{master}")
            entities["sensor"].append(AeccSensor(self.hub, master, "plant_name", "plant_name", ""))
            entities["sensor"].append(AeccSensor(self.hub, master, "em_status", "emStatus", ""))
            entities["sensor"].append(AeccSensor(self.hub, master, "em_type", "emType", ""))
            entities["sensor"].append(AeccSensor(self.hub, master, "em_sn", "emSn", ""))

            # Battery sensors (now properly mapped from storageList)
            entities["sensor"].append(AeccSensor(self.hub, master, "soc", "batSoc", "%"))
            entities["sensor"].append(AeccSensor(self.hub, master, "battery_charge_power", "batChargePower", "W"))
            entities["sensor"].append(AeccSensor(self.hub, master, "battery_discharge_power", "batDischargePower", "W"))
            entities["sensor"].append(AeccSensor(self.hub, master, "pv_charge_power", "pvChargePower", "W"))
            entities["sensor"].append(AeccSensor(self.hub, master, "ac_charge_power", "acChargePower", "W"))
            entities["sensor"].append(AeccSensor(self.hub, master, "device_power", "devicePower", "W"))
            
            # Energy sensors
            entities["sensor"].append(AeccSensor(self.hub, master, "solar_day_energy", "solarDayElec", "kWh"))
            entities["sensor"].append(AeccSensor(self.hub, master, "total_energy", "totalEnergy", "kWh"))
            entities["sensor"].append(AeccSensor(self.hub, master, "today_energy", "todayEnergy", "kWh"))
            entities["sensor"].append(AeccSensor(self.hub, master, "month_energy", "monthEnergy", "kWh"))
            entities["sensor"].append(AeccSensor(self.hub, master, "year_energy", "yearEnergy", "kWh"))

            entities["sensor"].append(AeccSensor(self.hub, master, "device_sn", "deviceSn", ""))
            entities["sensor"].append(AeccSensor(self.hub, master, "system sn", "systemSn", ""))

            entities["sensor"].append(AeccSensor(self.hub, master, "aiSystemStatus", "aiSystemStatus", ""))
        self.entities = entities
        return entities
