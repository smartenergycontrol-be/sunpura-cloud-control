import logging
from typing import Dict, List, Optional, Type
from .device import BaseDevice, DeviceType, EnergyManager, Meter, Socket, Charger, Inverter, Battery, Relay, PowerController, HeatPump

_LOGGER = logging.getLogger(__name__)

class DeviceManager:
    """设备管理器，负责创建和管理不同类型的设备实例"""
    
    def __init__(self, hass, hub):
        self.hass = hass
        self.hub = hub
        self.devices: Dict[str, BaseDevice] = {}
        self._device_type_map = {
            DeviceType.ENERGY_MANAGER: EnergyManager,  # 储能控制器
            DeviceType.INVERTER: Inverter,  # 逆变器
            DeviceType.BATTERY: Battery,  # 电池
            DeviceType.SOCKET: Socket,  # 插座
            DeviceType.CHARGER: Charger,  # 充电桩
            DeviceType.METER: Meter,  # 电表
            DeviceType.RELAY: Relay,  # 继电器
            DeviceType.POWER_CONTROLLER: PowerController,  # 功率控制器
            DeviceType.HEAT_PUMP: HeatPump  # 热泵
        }
    
    def create_device(self, device_info: dict) -> Optional[BaseDevice]:
        """根据设备信息创建对应类型的设备实例"""
        device_type = device_info.get("iconType")
        if not device_type:
            _LOGGER.error(f"设备信息中缺少iconType字段: {device_info}")
            return None
            
        try:
            device_type_enum = DeviceType(device_type)
            device_class = self._device_type_map.get(device_type_enum)
            if not device_class:
                _LOGGER.error(f"未知的设备类型: {device_type}")
                return None
                
            device = device_class(self.hass, self.hub)
            device.update_device_info(device_info)
            self.devices[device.device_sn] = device
            return device
            
        except ValueError as e:
            _LOGGER.error(f"创建设备实例失败: {e}")
            return None
    
    def get_device(self, device_sn: str) -> Optional[BaseDevice]:
        """根据设备序列号获取设备实例"""
        return self.devices.get(device_sn)
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[BaseDevice]:
        """获取指定类型的所有设备实例"""
        return [device for device in self.devices.values() if device.device_type == device_type]
    
    def update_device(self, device_sn: str, device_info: dict):
        """更新设备信息"""
        device = self.get_device(device_sn)
        if device:
            device.update_device_info(device_info)
        else:
            _LOGGER.warning(f"未找到设备: {device_sn}")