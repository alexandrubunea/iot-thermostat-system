"""
    This script will take care of a lot of things regarding the Raspberry Pi to host a web server
    and communicate with the ESP32. But there is one catch, you must run this script at least one
    time while being connected to the network. This is required just ONCE, then the Raspberry Pi
    will be able to be configured from the web application and connect to any network, just by
    connecting to the Pi's hotspot and accessing the web application.

    This script is tested only with the Raspberry Pi OS. I don't know how compatible is with any
    other Debian distribution.

    WARNING: When executing the setup.py ensure that the ESP32 is the only device connected to the
    Raspberry Pi so that the script can grab the MAC address and bind it to an IP static address.
    This action must be done only once, and given this script the ESP32 should be the only device
    connected to the Raspberry Pi.

    Usage: sudo python setup.py
"""

import subprocess, re, time
from datetime import datetime

REQUIRED_PACKAGES = [
    'hostapd',
    'dnsmasq',
    'wireless-tools'
]

HOTSPOT_CONFIG = """
interface=wlan0_ap
driver=nl80211
ssid=Pi-Hotspot
hw_mode=g
channel=6
auth_algs=1
wpa=2
wpa_passphrase=admin2raspi
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
"""

DAEMON_CONF = """
DAEMON_CONF="/etc/hostapd/hostapd.conf"
"""

DNSMASQ_CONFIG = """
interface=wlan0_ap
dhcp-range=192.168.50.10,192.168.50.50,12h
"""

DHCPCD_CONFIG = """
interface wlan0_ap
static ip_address=192.168.50.1/24
nohook wpa_supplicant
nohook wlan0_ap
"""

NETWORK_INTERFACE = """
[Unit]
Description=Add wlan0_ap interface
After=network.target
    
[Service]
Type=oneshot
ExecStart=/sbin/iw dev wlan0 interface add wlan0_ap type __ap
ExecStartPost=/usr/bin/ip link set dev wlan0_ap address 02:22:33:44:55:66
ExecStartPost=/sbin/ifconfig wlan0_ap up
RemainAfterExit=yes
    
[Install]
WantedBy=multi-user.target hostapd.service
"""

LOG_FILE = 'log.txt'

ESP32_IP_ADDRESS = '192.168.50.100'

def run_command(command):
    with open(LOG_FILE, 'a') as log:
        result = subprocess.run(command,
                                capture_output=True, text=True, shell=True)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if result.stdout:
            log.write(f'[{timestamp}] {result.stdout}\n')

        if result.stderr:
            log.write(f'[{timestamp}] {result.stderr}\n')

        return result.stdout, result.stderr

def write_to_file(file, content):
    with open(file, 'w') as f:
        f.write(content)

def check_for_dependencies():
    print("Checking for dependencies...")

    run_command('sudo apt update && sudo apt upgrade -y')

    for package in REQUIRED_PACKAGES:
        run_command(f'sudo apt install -y {package}')

def configure_network():
    print("Configuring network...")

    write_to_file('/etc/systemd/system/wlan0_ap.service', NETWORK_INTERFACE)

    write_to_file('/etc/hostapd/hostapd.conf', HOTSPOT_CONFIG)

    write_to_file('/etc/default/hostapd', DAEMON_CONF)

    write_to_file('/etc/dnsmasq.d/raspi_hotspot.conf', DNSMASQ_CONFIG)

    write_to_file('/etc/dhcpcd.conf', DHCPCD_CONFIG)

    # Modify hostapd.service
    hostapd_service = '/lib/systemd/system/hostapd.service'

    with open(hostapd_service, "r") as file:
        lines = file.readlines()

        modified_lines = []
        after_added = False
        for line in lines:
            modified_lines.append(line)
            if line.strip() == '[Unit]':
                after_added = True
                modified_lines.append('After=network.target\n')

        if not after_added:
            print('Failed to locate [Unit] section in hostapd.service file.')

    with open(hostapd_service, "w") as file:
        file.writelines(modified_lines)

    run_command('sudo systemctl enable wlan0_ap.service')
    run_command('sudo systemctl unmask hostapd')
    run_command('sudo systemctl enable hostapd')
    run_command('sudo systemctl enable dnsmasq')

    # Restart services in order
    run_command('sudo systemctl restart wlan0_ap')
    run_command('sudo systemctl restart dhcpcd')
    run_command('sudo systemctl restart dnsmasq')
    run_command('sudo systemctl restart hostapd')

def search_for_esp32():
    print("Searching for ESP32...")

    esp32_mac = None
    tries = 0

    while not esp32_mac:
        out, _ = run_command('sudo arp | grep "esp32"')

        lines = out.splitlines()
        for line in lines:
            # Match lines containing MAC addresses
            match = re.search(r'([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})', line,
                              re.IGNORECASE)
            if not match:
                continue

            mac = match.group(1).upper()
            esp32_mac = mac

            break

        if not esp32_mac:
            print('No ESP32 device found! Trying again in 3 seconds...')

            # Troubleshooting
            tries += 1
            if tries % 3 == 0:
                run_command('sudo systemctl restart hostapd')

            time.sleep(3)

    # Update dnsmasq configuration for static IP
    dnsmasq_entry = f'dhcp-host={esp32_mac},{ESP32_IP_ADDRESS}\n'
    write_to_file('/etc/dnsmasq.d/esp32_static.conf', dnsmasq_entry)

    # Restart dnsmasq to apply changes
    run_command('sudo systemctl restart dnsmasq')

    print(f'ESP32 device with MAC {esp32_mac} assigned to IP {ESP32_IP_ADDRESS}')

if __name__ == '__main__':
    check_for_dependencies()
    configure_network()
    search_for_esp32()

    print("Setup complete! Please restart the Raspberry Pi & ESP32.")