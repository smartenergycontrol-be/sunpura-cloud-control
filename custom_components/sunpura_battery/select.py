"""Select entities for Sunpura battery operation modes."""
import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .hub import MyIntegrationHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SunpuraBatteryModeSelect(SelectEntity):
    """Select entity for battery operation mode."""

    def __init__(self, hub: MyIntegrationHub, device):
        """Initialize the battery mode selector."""
        self.hub = hub
        self.device = device
        self._attr_name = "Battery Operation Mode"
        self._attr_unique_id = f"{device.device_sn}_battery_mode"
        self._attr_icon = "mdi:battery-sync"
        
        # Available modes based on API documentation
        self._attr_options = [
            "intelligent",      # Normal operation with grid export
            "zero_feed",       # Prevent grid export (powerMode=1)
            "manual_charge",   # Force charging regardless of solar
            "manual_discharge", # Force discharging
            "auto_schedule",   # Time-based scheduling
            "eco_mode"        # Energy saving mode
        ]
        
        self._current_option = "intelligent"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_sn)},
            "name": self.device.device_sn,
            "model": self.device.icon_type,
            "manufacturer": "Sunpura",
        }

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        return self._current_option

    async def async_select_option(self, option: str) -> None:
        """Change the battery operation mode."""
        try:
            await self._set_battery_mode(option)
            self._current_option = option
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Failed to set battery mode to {option}: {e}")

    async def _set_battery_mode(self, mode: str):
        """Set battery operation mode via API."""
        _LOGGER.info(f"Setting battery mode to {mode}")
        
        # Configure parameters based on selected mode
        mode_configs = {
            "intelligent": {
                "energyMode": 0,      # Manual mode
                "powerMode": 0,       # Intelligent - allows grid export
                "antiRefluxSet": 0,   # Allow grid export
                "aiMode": 0,
                "timeMode": 0,
                "forcedPower": 0,
                "description": "Normal operation with grid export of excess solar"
            },
            "zero_feed": {
                "energyMode": 1,      # Zero feed mode
                "powerMode": 1,       # Zero feed - prevents grid export
                "antiRefluxSet": 1,   # Prevent grid export
                "aiMode": 0,
                "timeMode": 0,
                "forcedPower": 0,
                "description": "Prevent all grid export (WARNING: May stop solar production)"
            },
            "manual_charge": {
                "energyMode": 2,      # AI mode
                "powerMode": 0,       # Intelligent
                "antiRefluxSet": 0,   # Allow grid export
                "aiMode": 1,
                "timeMode": 0,
                "forcedPower": 1000,  # Force 1kW charging
                "description": "Force battery charging with grid export allowed"
            },
            "manual_discharge": {
                "energyMode": 2,      # AI mode
                "powerMode": 0,       # Intelligent
                "antiRefluxSet": 0,   # Allow grid export
                "aiMode": 1,
                "timeMode": 0,
                "forcedPower": -1000, # Force 1kW discharging
                "description": "Force battery discharging with grid export allowed"
            },
            "auto_schedule": {
                "energyMode": 2,      # AI mode
                "powerMode": 0,       # Intelligent
                "antiRefluxSet": 0,   # Allow grid export
                "aiMode": 1,
                "timeMode": 1,        # Enable time scheduling
                "forcedPower": 0,
                "description": "Automatic scheduling based on time periods"
            },
            "eco_mode": {
                "energyMode": 0,      # Manual mode
                "powerMode": 0,       # Intelligent
                "antiRefluxSet": 0,   # Allow grid export
                "aiMode": 0,
                "timeMode": 0,
                "forcedPower": 0,
                "description": "Energy saving mode with grid export"
            }
        }
        
        config = mode_configs[mode]
        
        payload = {
            "id": 0,
            "sn": self.device.device_sn,
            "energyMode": config["energyMode"],
            "smartSocketMode": 0,
            "powerSignFlag": 1,
            "basicDisChargeEnable": 0,
            "batBasicDisChargePower": 0,
            "batBasicDisChargeMaxPower": 800,
            "maxFeedPower": 2400,
            "maxChargePower": 2400,
            "antiRefluxSet": config["antiRefluxSet"],
            "forcedPower": config["forcedPower"],
            "temporaryPower": 0,
            "powerMode": config["powerMode"],
            "aiMode": config["aiMode"],
            "ctEnable": 1,
            "timeMode": config["timeMode"],
            "ecVersion": "1.6",
            "plantId": self.hub.senceId,
            "plantType": 1,
            **{f"controlTime{i}": "0,00:00,00:00,0,0,0,0,0,0,100,10" for i in range(1, 17)},
            "powerTimeSetVos": []
        }
        
        # Log the mode change with description
        _LOGGER.info(f"Battery mode '{mode}': {config['description']}")
        
        await self.hub.set_ai_system_energy_mode(payload)


class SunpuraGridModeSelect(SelectEntity):
    """Select entity for grid interaction mode."""

    def __init__(self, hub: MyIntegrationHub, device):
        """Initialize the grid mode selector."""
        self.hub = hub
        self.device = device
        self._attr_name = "Grid Interaction Mode"
        self._attr_unique_id = f"{device.device_sn}_grid_mode"
        self._attr_icon = "mdi:transmission-tower"
        
        self._attr_options = [
            "auto_export",     # Automatic export of excess solar
            "limited_export",  # Limited export (respects maxFeedPower)
            "no_export",      # No grid export (zero feed)
            "grid_charge"     # Allow grid charging of battery
        ]
        
        self._current_option = "auto_export"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device.device_sn)},
            "name": self.device.device_sn,
            "model": self.device.icon_type,
            "manufacturer": "Sunpura",
        }

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        return self._current_option

    async def async_select_option(self, option: str) -> None:
        """Change the grid interaction mode."""
        try:
            await self._set_grid_mode(option)
            self._current_option = option
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Failed to set grid mode to {option}: {e}")

    async def _set_grid_mode(self, mode: str):
        """Set grid interaction mode via API."""
        _LOGGER.info(f"Setting grid mode to {mode}")
        
        mode_configs = {
            "auto_export": {
                "antiRefluxSet": 0,
                "maxFeedPower": 2400,
                "powerMode": 0,
                "description": "Full export of excess solar to grid"
            },
            "limited_export": {
                "antiRefluxSet": 0,
                "maxFeedPower": 1000,  # Limited to 1kW export
                "powerMode": 0,
                "description": "Limited export of excess solar (1kW max)"
            },
            "no_export": {
                "antiRefluxSet": 1,
                "maxFeedPower": 0,
                "powerMode": 1,
                "description": "No grid export (may affect solar production)"
            },
            "grid_charge": {
                "antiRefluxSet": 0,
                "maxFeedPower": 2400,
                "powerMode": 0,
                "description": "Allow grid charging and full solar export"
            }
        }
        
        config = mode_configs[mode]
        
        payload = {
            "id": 0,
            "sn": self.device.device_sn,
            "energyMode": 0,  # Manual mode for grid settings
            "smartSocketMode": 0,
            "powerSignFlag": 1,
            "basicDisChargeEnable": 0,
            "batBasicDisChargePower": 0,
            "batBasicDisChargeMaxPower": 800,
            "maxFeedPower": config["maxFeedPower"],
            "maxChargePower": 2400,
            "antiRefluxSet": config["antiRefluxSet"],
            "forcedPower": 0,
            "temporaryPower": 0,
            "powerMode": config["powerMode"],
            "aiMode": 0,
            "ctEnable": 1,
            "timeMode": 0,
            "ecVersion": "1.6",
            "plantId": self.hub.senceId,
            "plantType": 1,
            **{f"controlTime{i}": "0,00:00,00:00,0,0,0,0,0,0,100,10" for i in range(1, 17)},
            "powerTimeSetVos": []
        }
        
        _LOGGER.info(f"Grid mode '{mode}': {config['description']}")
        
        await self.hub.set_ai_system_energy_mode(payload)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    device_manager = hass.data[DOMAIN]["device_manager"]
    hub = hass.data[DOMAIN]["hub"]
    
    entities = []
    
    # Add select controls for each battery device
    for device in device_manager.devices:
        if device.icon_type == 3:  # Battery storage device
            entities.extend([
                SunpuraBatteryModeSelect(hub, device),
                SunpuraGridModeSelect(hub, device),
            ])
    
    if entities:
        async_add_entities(entities)
        _LOGGER.info(f"Added {len(entities)} select entities")