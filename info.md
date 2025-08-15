# Sunpura Battery Control Integration

This integration provides comprehensive control and monitoring for Sunpura S2400 battery systems through their cloud API.

## Features

- **Real-time Monitoring**: Battery voltage, current, SOC, power flow
- **Energy Management**: Track daily, monthly, and total energy production/consumption  
- **Battery Control**: Advanced charging/discharging control with multiple modes
- **Grid Interaction**: Monitor and control grid connection parameters
- **Device Management**: Support for multiple battery units and inverters
- **Smart Scheduling**: Time-based charging and discharging schedules

## Supported Devices

- Sunpura S2400 Battery Systems
- Compatible Sunpura Inverters with cloud connectivity
- All devices that use the Sunpura cloud API (monitor.ai-ec.cloud)

## Installation Requirements

- Home Assistant 2023.1.0 or newer
- Valid Sunpura cloud account credentials
- Internet connection for cloud API access

## Configuration

After installation through HACS, configure the integration via:
**Settings** → **Devices & Services** → **Add Integration** → **Sunpura Battery Control**

You will need:
- Username (same as used in the Sunpura mobile app)
- Password (same as used in the Sunpura mobile app)

## Support

For issues and feature requests, please visit:
https://github.com/smartenergycontrol-be/sunpura-cloud-control/issues