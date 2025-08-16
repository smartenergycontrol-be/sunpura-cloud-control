"""Number entities for Sunpura battery control."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.number import NumberEntity, NumberDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .hub import MyIntegrationHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SunpuraBatteryPowerNumber(NumberEntity):
    """Number entity for controlling battery charge/discharge power."""

    def __init__(self, hub: MyIntegrationHub, device):
        """Initialize the battery power control."""
        self.hub = hub
        self.device = device
        self._attr_name = "Battery Power Control"
        self._attr_unique_id = f"{device.device_sn}_battery_power_control"
        self._attr_device_class = NumberDeviceClass.POWER
        self._attr_native_unit_of_measurement = "W"
        self._attr_native_min_value = -2400  # Max discharge
        self._attr_native_max_value = 2400   # Max charge
        self._attr_native_step = 50
        self._attr_icon = "mdi:battery-charging"
        self._current_value = 0

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_sn)},
            "name": self.device.device_sn,
            "model": self.device.icon_type,
            "manufacturer": "Sunpura",
        }

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._current_value

    async def async_set_native_value(self, value: float) -> None:
        """Set new battery power value."""
        try:
            # Positive = charging, Negative = discharging
            await self._set_battery_power(int(value))
            self._current_value = value
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Failed to set battery power to {value}W: {e}")

    async def _set_battery_power(self, power: int):
        """Set battery power via API - simplified for EMHASS control."""
        _LOGGER.info(f"Setting battery power to {power}W (+ = charge, - = discharge)")
        
        # Simplified logic: always preserve solar export regardless of battery action
        if power == 0:
            # No battery action - pure intelligent mode
            energy_mode = 0  # Manual mode
            time_mode = 0    # No time scheduling
            control_time = "0,00:00,00:00,0,0,0,0,0,0,100,10"
            power_time_set_vos = []
            forced_power = 0
        else:
            # Battery action requested - use time scheduling for precise control
            energy_mode = 0  # Manual mode (not AI) for predictable behavior
            time_mode = 1    # Enable time scheduling
            
            now = datetime.now()
            start_time = now.strftime("%H:%M")
            end_time = (now + timedelta(hours=1)).strftime("%H:%M")
            
            control_time = f"1,{start_time},{end_time},{power},0,6,0,0,0,100,10"
            power_time_set_vos = [
                {
                    "timeSwitch": 1,
                    "startTime": start_time,
                    "endTime": end_time,
                    "forcedPower": power,
                    "temporaryPower": 0,
                    "mode": 6,  # Guardian mode for precise control
                    "weatherLevel": 0,
                    "weather": "0",
                    "energyConsume": "0",
                    "electricPrice": "0",
                    "dischargingSOC": 10,  # Stop discharge at 10%
                    "chargingSOC": 100     # Charge to 100%
                }
            ]
            forced_power = power

        # Fixed parameters to ensure solar always exports to grid
        payload = {
            "id": 0,
            "sn": self.device.device_sn,
            "energyMode": energy_mode,
            "smartSocketMode": 0,
            "powerSignFlag": 1,
            "basicDisChargeEnable": 0,
            "batBasicDisChargePower": 0,
            "batBasicDisChargeMaxPower": 800,
            "maxFeedPower": 2400,        # Always allow full solar export
            "maxChargePower": 2400,
            "antiRefluxSet": 0,          # Always allow grid export
            "forcedPower": forced_power,
            "temporaryPower": 0,
            "powerMode": 0,              # Always intelligent mode
            "aiMode": 0,                 # No AI interference
            "ctEnable": 1,               # Enable CT for accurate measurement
            "timeMode": time_mode,
            "ecVersion": "1.6",
            "plantId": self.hub.senceId,
            "plantType": 1,
            "controlTime1": control_time,
            **{f"controlTime{i}": "0,00:00,00:00,0,0,0,0,0,0,100,10" for i in range(2, 17)},
            "powerTimeSetVos": power_time_set_vos
        }

        await self.hub.set_ai_system_energy_mode(payload)


class SunpuraMaxFeedPowerNumber(NumberEntity):
    """Number entity for controlling maximum grid feed power."""

    def __init__(self, hub: MyIntegrationHub, device):
        """Initialize the max feed power control."""
        self.hub = hub
        self.device = device
        self._attr_name = "Max Grid Feed Power"
        self._attr_unique_id = f"{device.device_sn}_max_feed_power"
        self._attr_device_class = NumberDeviceClass.POWER
        self._attr_native_unit_of_measurement = "W"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 2400
        self._attr_native_step = 100
        self._attr_icon = "mdi:transmission-tower"
        self._current_value = 2400

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_sn)},
            "name": self.device.device_sn,
            "model": self.device.icon_type,
            "manufacturer": "Sunpura",
        }

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._current_value

    async def async_set_native_value(self, value: float) -> None:
        """Set maximum grid feed power."""
        try:
            await self._set_max_feed_power(int(value))
            self._current_value = value
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Failed to set max feed power to {value}W: {e}")

    async def _set_max_feed_power(self, max_power: int):
        """Set maximum grid feed power via API."""
        _LOGGER.info(f"Setting max grid feed power to {max_power}W")
        
        payload = {
            "id": 0,
            "sn": self.device.device_sn,
            "energyMode": 0,  # Manual mode for simple parameter change
            "smartSocketMode": 0,
            "powerSignFlag": 1,
            "basicDisChargeEnable": 0,
            "batBasicDisChargePower": 0,
            "batBasicDisChargeMaxPower": 800,
            "maxFeedPower": max_power,    # The parameter we're changing
            "maxChargePower": 2400,
            "antiRefluxSet": 0,           # Always allow export
            "forcedPower": 0,
            "temporaryPower": 0,
            "powerMode": 0,               # Intelligent mode
            "aiMode": 0,
            "ctEnable": 1,
            "timeMode": 0,
            "ecVersion": "1.6",
            "plantId": self.hub.senceId,
            "plantType": 1,
            **{f"controlTime{i}": "0,00:00,00:00,0,0,0,0,0,0,100,10" for i in range(1, 17)},
            "powerTimeSetVos": []
        }

        await self.hub.set_ai_system_energy_mode(payload)


class SunpuraDischargeSOCNumber(NumberEntity):
    """Number entity for controlling minimum discharge SOC."""

    def __init__(self, hub: MyIntegrationHub, device):
        """Initialize the discharge SOC control."""
        self.hub = hub
        self.device = device
        self._attr_name = "Minimum Discharge SOC"
        self._attr_unique_id = f"{device.device_sn}_min_discharge_soc"
        self._attr_device_class = NumberDeviceClass.BATTERY
        self._attr_native_unit_of_measurement = "%"
        self._attr_native_min_value = 5
        self._attr_native_max_value = 50
        self._attr_native_step = 5
        self._attr_icon = "mdi:battery-low"
        self._current_value = 10

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_sn)},
            "name": self.device.device_sn,
            "model": self.device.icon_type,
            "manufacturer": "Sunpura",
        }

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._current_value

    async def async_set_native_value(self, value: float) -> None:
        """Set minimum discharge SOC."""
        try:
            await self._set_discharge_soc(int(value))
            self._current_value = value
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Failed to set discharge SOC to {value}%: {e}")

    async def _set_discharge_soc(self, soc: int):
        """Set minimum discharge SOC via device parameter API."""
        _LOGGER.info(f"Setting minimum discharge SOC to {soc}%")
        
        # This uses the setParam API for device-level settings
        await self.hub.set_device_parameter("batStopSOC", str(soc))


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""
    device_manager = hass.data[DOMAIN]["device_manager"]
    hub = hass.data[DOMAIN]["hub"]
    
    entities = []
    
    # Add battery control numbers for each device
    for device in device_manager.devices:
        if device.icon_type == 3:  # Battery storage device
            entities.extend([
                SunpuraBatteryPowerNumber(hub, device),
                SunpuraMaxFeedPowerNumber(hub, device),
                SunpuraDischargeSOCNumber(hub, device),
            ])
    
    if entities:
        async_add_entities(entities)
        _LOGGER.info(f"Added {len(entities)} number entities")