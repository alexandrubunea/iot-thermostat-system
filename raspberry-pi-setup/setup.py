"""
    This script will take care of a lot of things regarding the Raspberry Pi to host a web server
    and communicate with the ESP32. But there is one catch, you must run this script at least one
    time while being connected to the network. This is required just ONCE, then the Raspberry Pi
    will be able to be configured from the web application and connect to any network, just by
    connecting to the Pi's hotspot and accessing the web application.

    The ESP32 should be turned on and configured to connect to the Raspberry Pi's hotspot, because
    the script will not finish running until it gets ESP32's MAC address so it can be bound to
    a permanent ip address.

    This script is tested only with the Raspberry Pi OS. I don't know how compatible is with any
    other Debian distribution.

    Usage: sudo python setup.py
"""

import os, subprocess
from datetime import datetime

REQUIRED_PACKAGES = [
    'hostapd',
    'dnsmasq',
    'wireless-tools',
    'arp-scan',
    'git'
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

DNSMASQ_CONFIG = """
    interface=wlan0_ap
    dhcp-range=192.168.50.10,192.168.50.50,12h
"""

DHCPCD_CONFIG = """
    interface wlan0_ap
    static ip_address=192.168.50.1/24 
"""

NETWORK_INTERFACE = """
    [Unit]
    Description=Add wlan0_ap interface
    After=network.target
    
    [Service]
    Type=oneshot
    ExecStart=/sbin/iw dev wlan0 interface add wlan0_ap type __ap
    RemainAfterExit=yes
    
    [Install]
    WantedBy=multi-user.target
"""

LOG_FILE = 'log.txt'

def run_command(command):
    with open(LOG_FILE, 'a') as log:
        result = subprocess.run(command,
                                capture_output=True, text=True, shell=True)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f'[{timestamp}] {result.stdout}')
        log.write(f'[{timestamp}] {result.stderr}')

def write_to_file(file, content):
    with open(file, 'w') as f:
        f.write(content)

def check_for_dependencies():
    run_command('sudo apt update && sudo apt upgrade -y')

    for package in REQUIRED_PACKAGES:
        run_command(f'sudo apt install -y {package}')

def configure_network():
    write_to_file('/etc/systemd/system/wlan0_ap.service', NETWORK_INTERFACE)

    write_to_file('/etc/hostapd/hostapd.conf', HOTSPOT_CONFIG)
    write_to_file('/etc/default/hostapd.conf', HOTSPOT_CONFIG)

    write_to_file('/etc/dnsmasq.conf', DNSMASQ_CONFIG)

    write_to_file('/etc/dhcp/dhcp.conf', DHCPCD_CONFIG)

    run_command('sudo systemctl enable wlan0_ap.service')
    run_command('sudo systemctl unmask hostapd')
    run_command('sudo systemctl enable hostapd')
    run_command('sudo systemctl enable dnsmasq')


def search_for_esp32():
    pass

if __name__ == '__main__':
    check_for_dependencies()
    configure_network()

    os.system('sudo reboot')