# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two different implementations for integrating Sunpura S2400 battery systems with Home Assistant:

1. **ha_ems_cloud/** - Official Home Assistant integration from Sunpura manufacturer
2. **appdeamon_cloud_api_httpproxy_capture/** - Custom AppDaemon scripts based on HTTP proxy captures

## Architecture and Components

### Official Integration (ha_ems_cloud)
- **Platform**: Home Assistant custom integration
- **Language**: Python 3.x with asyncio
- **Authentication**: Cloud API with MD5 hashed passwords
- **Platforms**: Sensors and switches
- **Issues**: All numeric sensors created as text, no proper icons, poor logical grouping, missing battery control features

Key files:
- `__init__.py` - Integration setup and service registration
- `hub.py` - Core communication hub with cloud API
- `sensor.py` - Sensor entity definitions
- `switch.py` - Switch entity definitions
- `device_entity_manager.py` - Device and entity management
- `config_flow.py` - Configuration flow for setup
- `manifest.json` - Integration metadata

### Custom AppDaemon Scripts
- **Platform**: AppDaemon for Home Assistant
- **Language**: Python 3.x with requests library
- **Authentication**: Direct cloud API authentication
- **Capabilities**: Read battery data, set zero-feed mode, control charge/discharge power

Key files:
- `ai_script.py` - Battery monitoring with 5-second updates
- `set_battery_power.py` - Control battery charge/discharge power
- `zerofeed_toggle.py` - Toggle zero-feed mode
- `apps.yaml` - AppDaemon app configuration

## API Details

The Sunpura cloud API uses:
- **Base URL**: https://monitor.ai-ec.cloud:8443 (official) / https://server-nj.ai-ec.cloud:8443 (custom scripts)
- **Authentication**: MD5 hashed passwords with timestamp-based signatures
- **Data Format**: JSON payloads with specific device serial numbers
- **Key Endpoints**:
  - `/user/login` - Authentication
  - `/openApi/device/getBasicsInfo` - Device configuration
  - `/openApi/device/getRealTimeInfo` - Real-time data
  - `/aiSystem/setAiSystemTimesWithEnergyMode` - Control battery mode

## Development Commands

### Official Integration Development
```bash
# Install in Home Assistant custom_components directory
cp -r ha_ems_cloud/ha_ems_cloud /config/custom_components/

# Restart Home Assistant to load integration
# Configure through UI: Settings > Devices & Services > Add Integration
```

### AppDaemon Scripts Development
```bash
# Install in AppDaemon apps directory
cp appdeamon_cloud_api_httpproxy_capture/*.py /config/appdaemon/apps/
cp appdeamon_cloud_api_httpproxy_capture/apps.yaml /config/appdaemon/apps/

# Restart AppDaemon to load apps
```

## Configuration Requirements

### Credentials (Required for both implementations)
- Email/username for Sunpura cloud account
- Password (will be MD5 hashed)
- Device serial number (format: ZL-XXXXXXXXX-XXXXX)
- Plant/Site ID (for official integration)

### Home Assistant Entities (for AppDaemon scripts)
- `input_number.sunpura_set_battery_power` - Power setting control
- `input_boolean.sunpura_zerofeed_mode` - Zero-feed mode toggle

## Known Issues and Limitations

### Official Integration Problems
1. All numeric sensor values incorrectly created as text entities
2. Missing proper device icons and entity icons
3. Poor logical grouping of related sensors
4. **Major limitation**: No battery charging/discharging control functionality
5. Polling-based updates only (no real-time push)

### Custom Scripts Advantages
1. Proper numeric value handling
2. Direct battery power control capabilities
3. Zero-feed mode control
4. Faster update intervals (5 seconds)
5. Based on actual Android app HTTP captures

## Important Security Notes

- **API Credentials**: Both implementations contain hardcoded credentials that should be externalized
- **MD5 Authentication**: The API uses MD5 hashing which is cryptographically weak
- **HTTPS**: All communications use HTTPS but certificate validation should be verified
- **Device Serial Numbers**: These are sensitive identifiers that should be protected

## API Documentation Reference

The repository includes comprehensive API documentation:
- `2025-05-26，SUNPURA_API_EN_V1.2.2.pdf` - Official Sunpura API documentation v1.2.2
- Contains detailed endpoint specifications, data models, and authentication requirements
- Includes both rated data models and real-time data models
- Documents device parameter control capabilities

## Development Tips

1. **Testing**: Use the AppDaemon scripts as reference for proper API communication patterns
2. **Debugging**: Enable debug logging in Home Assistant for the ha_ems_cloud domain
3. **API Exploration**: The PDF documentation contains complete API specifications
4. **Battery Control**: The custom scripts demonstrate proper implementation of battery control features missing from the official integration
5. **Data Types**: Pay attention to proper numeric vs text entity creation in Home Assistant integrations