# Raspberry Pi ESP32 Setup Script

This script automates the setup of a Raspberry Pi as a wireless access point (hotspot) and configures communication with an ESP32 device. It handles network configuration, package installation, and static IP assignment for the ESP32.

## Key Features

- Creates a secure Wi-Fi hotspot on the Raspberry Pi
- Automatically installs required dependencies
- Configures network services (hostapd, dnsmasq)
- Detects and assigns a static IP to the connected ESP32
- Generates detailed logs for troubleshooting

## Prerequisites

- Raspberry Pi running Raspberry Pi OS (compatibility with other Debian distributions is not guaranteed)
- Python 3.x installed
- Root/sudo privileges
- ESP32 device
- Active internet connection (required for initial setup only)

## Installation

1. Clone or download this script to your Raspberry Pi
2. Make sure the ESP32 is the **only** device connected to the Raspberry Pi
3. Run the script with sudo privileges:

```bash
sudo python setup.py
```

## Default Configuration

### Hotspot Settings
- SSID: Pi-Hotspot
- Password: admin2raspi
- IP Range: 192.168.50.10 - 192.168.50.50
- Hotspot IP: 192.168.50.1
- ESP32 Static IP: 192.168.50.100

## Important Notes

**WARNINGS**:
- The script must be run at least once while connected to the internet
- Ensure the ESP32 is the only device connected during initial setup
- A system restart is required after running the script

## Post-Setup

After running the script:
1. Restart both the Raspberry Pi and ESP32
2. The Raspberry Pi will create a hotspot named "Pi-Hotspot"
3. The ESP32 will automatically connect and receive its static IP address
4. The web application can be used to configure additional settings

## Logging

The script generates detailed logs in `log.txt`, which can be useful for troubleshooting. The log includes timestamps and output from all executed commands.

## Network Configuration Details

The script sets up the following services:
- hostapd: Manages the wireless access point
- dnsmasq: Handles DHCP and DNS services
- dhcpcd: Manages IP address assignment
- Custom network interface (wlan0_ap)

## Troubleshooting

If the ESP32 is not detected:
- The script will automatically retry every 3 seconds
- hostapd service will be restarted every 3 attempts
- Check the log file for detailed error messages