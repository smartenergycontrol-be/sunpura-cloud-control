# Sunpura Battery Control

A Home Assistant custom integration for controlling Sunpura S2400 battery systems via cloud API.

## Features

- **Complete sensor monitoring**: Battery state, solar production, grid consumption, and more
- **Battery control**: Charge/discharge control with proper solar production handling
- **Grid interaction**: Configure grid export limits and zero-feed modes
- **Fixed data types**: All numeric sensors display as proper numbers (not text)
- **Smart operation**: Excess solar always exports to grid unless specifically disabled

## Installation

1. Copy the `sunpura_battery` folder to your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/sunpura_battery/
   ```

2. Restart Home Assistant

3. Add the integration via Settings → Devices & Services → Add Integration
   - Search for "Sunpura Battery Control"
   - Enter your Sunpura cloud credentials

## Control Entities

- `number.battery_power_control`: Battery charge/discharge (-2400W to +2400W)
- `number.max_grid_feed_power`: Maximum grid export power (0W to 2400W)
- `number.minimum_discharge_soc`: Minimum battery discharge level (5% to 50%)
- `select.battery_operation_mode`: Operation modes (intelligent, zero_feed, manual, etc.)
- `select.grid_interaction_mode`: Grid interaction settings

## Key Improvement

**Solar Production Issue Fixed**: Unlike other implementations, this integration ensures that when battery control is active, excess solar production continues to export to the grid instead of stopping solar panel production entirely.

## Requirements

- Home Assistant 2023.1+
- Sunpura S2400 battery system
- Valid Sunpura cloud account credentials

## API Documentation

Based on official Sunpura API v1.2.2 with comprehensive battery control capabilities.
