# Sunpura Battery Control Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/smartenergycontrol-be/sunpura-cloud-control.svg)](https://github.com/smartenergycontrol-be/sunpura-cloud-control/releases)
[![GitHub license](https://img.shields.io/github/license/smartenergycontrol-be/sunpura-cloud-control.svg)](https://github.com/smartenergycontrol-be/sunpura-cloud-control/blob/main/LICENSE)

A comprehensive Home Assistant integration for monitoring and controlling Sunpura S2400 battery systems through their cloud API.

## Features

✅ **Real-time Monitoring**
- Battery voltage, current, and state of charge (SOC)
- Power flow: charging, discharging, grid import/export
- Inverter status and performance metrics
- Temperature monitoring

✅ **Energy Management**
- Daily, monthly, and total energy production/consumption tracking
- PV generation monitoring
- Load consumption analysis
- Grid interaction metrics

✅ **Battery Control**
- Advanced charging/discharging control
- Multiple operation modes (peak shaving, zero feed, etc.)
- Time-based charging schedules
- Battery protection settings

✅ **Device Management**
- Support for multiple battery units and inverters
- Device status and diagnostics
- Automatic device discovery

## Supported Devices

- Sunpura S2400 Battery Systems
- Compatible Sunpura Inverters with cloud connectivity
- All devices that use the Sunpura cloud API (monitor.ai-ec.cloud)

## Installation

### Option 1: HACS (Recommended)

1. **Add Custom Repository:**
   - Open HACS in Home Assistant
   - Go to **Integrations**
   - Click the **⋮** menu and select **Custom repositories**
   - Add repository URL: `https://github.com/smartenergycontrol-be/sunpura-cloud-control`
   - Category: **Integration**
   - Click **Add**

2. **Install Integration:**
   - Search for "Sunpura Battery Control" in HACS
   - Click **Download**
   - Restart Home Assistant

3. **Configure Integration:**
   - Go to **Settings** → **Devices & Services**
   - Click **Add Integration**
   - Search for "Sunpura Battery Control"
   - Enter your Sunpura app credentials:
     - Username (same as used in Sunpura mobile app)
     - Password (same as used in Sunpura mobile app)

### Option 2: Manual Installation

1. **Download Integration:**
   ```bash
   cd /config/custom_components
   git clone https://github.com/smartenergycontrol-be/sunpura-cloud-control.git
   mv sunpura-cloud-control/custom_components/sunpura_battery .
   rm -rf sunpura-cloud-control
   ```

2. **Restart Home Assistant**

3. **Configure Integration** (same as step 3 above)

## Configuration

The integration uses the same credentials as the Sunpura mobile app:

| Field | Description | Required |
|-------|-------------|----------|
| Username | Your Sunpura cloud account username/email | Yes |
| Password | Your Sunpura cloud account password | Yes |

The integration will automatically:
- Discover your battery systems and inverters
- Create appropriate sensors and controls
- Set up proper device classes and units

## Entities Created

### Sensors
- Battery voltage, current, and SOC
- Power readings (charging/discharging/grid)
- Energy counters (daily/monthly/total)
- Device status and temperatures
- Grid parameters (voltage, frequency)

### Switches
- Battery operation mode controls
- Grid interaction settings
- Device enable/disable controls

### Numbers
- Charging current limits
- Power set points
- Voltage thresholds

### Selects
- Operation mode selection
- Priority settings
- Time schedule selection

## Troubleshooting

### Common Issues

1. **Integration won't load:**
   - Check Home Assistant logs for detailed error messages
   - Verify your Sunpura app credentials are correct
   - Ensure internet connectivity to Sunpura cloud

2. **No devices found:**
   - Verify your battery system is online in the Sunpura app
   - Check that your account has access to the devices
   - Wait a few minutes for device discovery

3. **Sensor values not updating:**
   - Check the integration debug logs
   - Verify cloud API connectivity
   - Restart the integration

### Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.sunpura_battery: debug
```

## Support

- **Issues**: [GitHub Issues](https://github.com/smartenergycontrol-be/sunpura-cloud-control/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/smartenergycontrol-be/sunpura-cloud-control/issues)
- **Documentation**: [GitHub Wiki](https://github.com/smartenergycontrol-be/sunpura-cloud-control/wiki)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially supported by Sunpura. Use at your own risk. The developers are not responsible for any damage to your equipment.