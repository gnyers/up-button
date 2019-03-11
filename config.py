# On boot the upy-button will scan the available WLANs and connect to 
# to the first, which is mentioned in this dict
known_wlans = {
   b'YourWiFi': 'YourWiFiPassphrase',
   b'SomeOtherWiFi': 'Itspassphrase',
   b'PublicWLAN': '',                  # empty passphrase
}

mqtt_client = {                        # The parameters for the upy-button
    'name': 'upy-button',
    'button_gpio': 0,                  # Wemos 1-button shield v2.0.0
    'button_debounce_timeout': 150,    # 150ms
    'led_gpio': 2,                     # Wemos Mini D1
}

mqtt_servers = [                       # list of MQTT servers
    {
        'name': '192.168.0.100',
        'topic': '/test/topic',
        'username': '',
        'passwd': '',
    },
    {
        'name': '',                    # An empty mqtt server config record
        'topic': '',
        'username': '',
        'passwd': '',
    },
]
mqtt_server = mqtt_servers[0]          # The preferred MQTT server
