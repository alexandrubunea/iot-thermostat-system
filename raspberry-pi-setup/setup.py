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

LOG_FILE = 'log.txt'

def check_for_dependencies():
    with open(LOG_FILE, 'a') as log: # Log for any errors
        result = subprocess.run('sudo apt update && sudo apt upgrade -y',
                                capture_output=True, text=True, shell=True)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f'[{timestamp}] {result.stdout}')
        log.write(f'[{timestamp}] {result.stderr}')

        for package in REQUIRED_PACKAGES:
            result = subprocess.run(f'sudo apt install -y {package}',
                                    capture_output=True, text=True, shell=True)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log.write(f'[{timestamp}] {result.stdout}')
            log.write(f'[{timestamp}] {result.stderr}')

def configure_network():
    with open('/etc/hostapd/hostapd.conf', 'w') as hostapd_conf:
        hostapd_conf.write(HOTSPOT_CONFIG)
    with open('/etc/default/hostapd.conf', 'w') as hostapd_conf:
        hostapd_conf.write('/etc/hostapd/hostapd.conf')

    with open('/etc/dnsmasq.conf', 'w') as dnsmasq_conf:
        dnsmasq_conf.write(DNSMASQ_CONFIG)

    with open('/etc/dhcp/dhcp.conf', 'w') as dhcp_conf:
        dhcp_conf.write(DHCPCD_CONFIG)

    with open(LOG_FILE, 'a') as log:
        result = subprocess.run('sudo iw dev wlan0 interface add wlan0_ap type __ap',
                                capture_output=True, text=True, shell=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f'[{timestamp}] {result.stdout}')
        log.write(f'[{timestamp}] {result.stderr}')

        result = subprocess.run('sudo systemctl unmask hostapd',
                                capture_output=True, text=True, shell=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f'[{timestamp}] {result.stdout}')
        log.write(f'[{timestamp}] {result.stderr}')

        result = subprocess.run('sudo systemctl enable hostapd',
                                capture_output=True, text=True, shell=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f'[{timestamp}] {result.stdout}')
        log.write(f'[{timestamp}] {result.stderr}')

        result = subprocess.run('sudo systemctl start dnsmasq',
                                capture_output=True, text=True, shell=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f'[{timestamp}] {result.stdout}')
        log.write(f'[{timestamp}] {result.stderr}')

def search_for_esp32():
    pass

if __name__ == '__main__':
    check_for_dependencies()
    configure_network()

    os.system('sudo reboot')