import logging
from datetime import datetime

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import BaseEntity
from .const import DOMAIN
import re
_LOGGER = logging.getLogger(__name__)



class AeccSwitch(SwitchEntity):
    """Representation of a switch."""

    def __init__(self,hass, hub,device, name, key):
        """Initialize the switch."""
        super().__init__()

        self.device = device
        self.hass = hass
        self.hub = hub
        self._state = STATE_OFF
        self.pf = "switch"
        self._available= True
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._key = key
        self._name = name
        self._unique_id = self._generate_unique_id()
        self._unit = ""
        self._attributes = {}
        _LOGGER.info(f"创建开关实体: {self._name}, hass={self.device.device_sn}")
        # 注册到hub
        hub.add_entity(self)



    def _generate_unique_id(self):
        device_sn = re.sub(r"[^a-z0-9]", "", self.device.device_sn.lower())
        key = re.sub(r"[^a-z0-9]", "", self._name.lower())

        return f"{device_sn}_{key}"

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return f"{self.device.device_sn} {self._name}"

    @property
    def available(self) -> bool:
        return self._available
    @property
    def is_on(self):
        """Return true if switch is on."""
        return  True if self._state==STATE_ON else False


    def disable_entity(self):
        self._available = False
    def update_data(self, new_data,d,ai):
        # _LOGGER.info(f"switch更新: {self._name}")
        _LOGGER.debug(f"switch更新时按钮状态: {self._name},{self.state},{self.is_on}")
        # 解析嵌套数据示例
        # _LOGGER.warning(new_data)
        # v = new_data.get(self._key)
        v = new_data.get(self._key)
        if 'loadList' in new_data and new_data['loadList']:
            for load in new_data['loadList']:
                if not v is not None:
                    sn = load.get('deviceSn')
                    if sn == self.device.device_sn:
                        v  = load.get('switchStatus')
                        break

        if  v is None:
            if 'chargerList' in new_data and new_data['chargerList']:
                for charger in new_data['chargerList']:
                    if v is None:
                        sn = charger.get('deviceSn')
                        if sn == self.device.device_sn:
                            v = charger.get('switchStatus')
                            break
        if  v is None:
            if 'heatPumpList' in new_data and new_data['heatPumpList']:
                for heat in new_data['heatPumpList']:
                    if v is None:
                        sn = heat.get('deviceSn')
                        if sn == self.device.device_sn:
                            v = heat.get('switchStatus')
                            break
        # u = new_data.get(self._unit)
        # _LOGGER.warning(f"{self._key},{v}")
        if v is not None:
            # _LOGGER.info(f"{self._name}更新状态:{v}")

            self._state =STATE_ON if v==1 else STATE_OFF
            _LOGGER.debug(f"{self._name}更新状态:{self._state}")
        else:
            self._state = STATE_OFF
        #     return
        if not hasattr(self, "hass") or self.hass is None:
            _LOGGER.debug("实体未完成初始化，跳过状态更新")
            return
        # _LOGGER.info(self.device)
        if self.device:
            attrs ={
                "deviceSn": self.device.device_sn,
                "iconType": self.device.icon_type,
                "dtc": self.device.device_code_type,
                "plantId": self.hub.senceId,
            }
        else:
            attrs = {
                "plantId": self.hub.senceId,
            }


        self._attributes = {
            "last_updated": datetime.now().isoformat(),
            "attrs": attrs,
        }
        # pass

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        # Implement the logic to turn the switch on

        _LOGGER.info(f"按钮开启")
        _LOGGER.info(f"{self.device.icon_type}")
        if self.device.icon_type == 5:
            await self.hub.switch_socket(self.device.device_sn, 1)
        elif self.device.icon_type == 6:
            await self.hub.switch_charger(self.device.device_sn, 1)
        else:
            await self.hub.switch_product(self.device.device_sn, 1)
        self._state = STATE_ON
        self.hub.async_update_data()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        # Implement the logic to turn the switch off
        _LOGGER.info(f"{self.device.icon_type}")
        _LOGGER.info(f"按钮关闭")

        if self.device.icon_type == 5:
            await self.hub.switch_socket(self.device.device_sn, 0)
        elif self.device.icon_type == 6:
            await self.hub.switch_charger(self.device.device_sn, 0)
        else:
            await self.hub.switch_product(self.device.device_sn, 0)
        self._state = STATE_OFF
        self.hub.async_update_data()
        self.async_write_ha_state()



async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    _LOGGER.info(f"加载 switch实体：{hass.data[DOMAIN]['device_manager'].entities["switch"]}")
    switches = hass.data[DOMAIN]['device_manager'].entities["switch"]
    async_add_entities(switches)