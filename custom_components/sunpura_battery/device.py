import logging
from enum import Enum
from .entity import BaseEntity

_LOGGER = logging.getLogger(__name__)

class DeviceType(Enum):
    ENERGY_MANAGER = 1  # 储能控制器
    INVERTER = 2  # 逆变器
    BATTERY = 3  # 电池
    SOCKET = 5  # 插座
    CHARGER = 6  # 充电桩
    METER = 7  # 电表
    RELAY = 8  # 继电器
    POWER_CONTROLLER = 9  # 功率控制器
    HEAT_PUMP = 10  # 热泵
    

class BaseDevice(BaseEntity):
    """设备基类，所有具体设备类型都应该继承这个类"""
    
    def __init__(self, hass, hub, device_type: DeviceType):
        super().__init__(hass, hub)
        self.device_type = device_type
        self.device_name = None
        self.device_sn = None
        self.datalog_sn = None
        # 实际设备类型 短类型

        self.type= None
        # 图标类型
        self.icon_type = None
        self.device_mode = None
        # 长类型
        self.device_code_type = None
        self.master_type = None
        self.rated_power = None
        self.power = None
        self.status = None
        self.switch_status = None
        self.inter_connect_status = None
        self.value = None


        
    def update_device_info(self, device_info: dict):
        """更新设备基本信息"""
        _LOGGER.info(f"更新设备信息：{device_info}")
        self.device_name = device_info.get("deviceName")
        self.device_sn = device_info.get("deviceSn")
        self.datalog_sn = device_info.get("datalogSn")
        # 实际设备类型
        self.type = device_info.get("type") if device_info.get("type") else -1
        # 图标类型
        self.icon_type = device_info.get("iconType")
        self.device_code_type = device_info.get("deviceCodeType")
        self.switch_status = device_info.get("switchStatus")
        self.status = device_info.get("status")


class EnergyManager(BaseDevice):
    """能管设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.ENERGY_MANAGER)

class Meter(BaseDevice):
    """电表设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.METER)

class Battery(BaseDevice):
    """电池设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.BATTERY)

class Socket(BaseDevice):
    """插座设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.SOCKET)

class Charger(BaseDevice):
    """充电桩设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.CHARGER)

class Inverter(BaseDevice):
    """逆变器设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.INVERTER)

class Relay(BaseDevice):
    """继电器设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.RELAY)

class PowerController(BaseDevice):
    """功率控制器设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.POWER_CONTROLLER)

class HeatPump(BaseDevice):
    """热泵设备"""
    def __init__(self, hass, hub):
        super().__init__(hass, hub, DeviceType.HEAT_PUMP)