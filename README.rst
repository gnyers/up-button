===============================
up-button -- MicroPython Button
===============================

:date: 2019-02-22
:author: Gábor Nyers, https://github.com/gnyers
:tags: esp8266 MicroPython IoT
:summary: a simple WiFi button

.. contents:: Contents
   :depth: 2

This program has been tested with the ESP8266 chip and the `Wemos D1
Mini`_ board; YMMV.

Preparations on your PC/laptop
------------------------------

#. Create the ``config.py`` file:

   - add the ESSID and passphrase of the WLAN(s) you want the button to
     recognize
   - modify the button's settings in the ``mqtt_client`` dict
   - make sure to set the configure the MQTT server in ``mqtt_server``

#. Install the ``ampy`` utility, which will be used to upload files to
   the microcontroller running MicroPython_: ::

    pip install adafruit-ampy

#. Install `pyserial`_, which contains the `miniterm`_ serial communication
   program. This needed in order to connect to the microcontroller's serial
   port.

    pip install pyserial

#. Install the `esptool`_ utility to deploy new firmware to the ESP8266 or
   ESP32 microcontrollers. See also the MicroPython `flash instructions`_:

#. Download the latest version of MicroPython_ for your board from the
   `MicroPython download page`_ and flash it to the board using the
   `flash instructions`_ 

First use
---------

#. Connect to the serial console of the board (e.g. with ``miniterm``) and
   check the availability of the ``MQTTClient`` module in your version of
   MicroPython: ::

    from umqtt.simple import MQTTClient

   This should work OK, but if it fails you'll also need to upload this file
   to your board: 
   https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/umqtt/simple.py
   ::

    mkdir umqtt
    wget \
    https://raw.githubusercontent.com/micropython/micropython-lib/master/umqtt.simple/umqtt/simple.py \ 
    -O umqtt/simple.py 
    ampy --port /dev/ttyUSB0 --baud 115200 put umqtt

#. Customize your ``upy-button`` by editing its configuration in
   ``config.py``:

   - add new / modify existing WLANs in the ``known_wlans`` dict
   - edit the mqtt client's settings in the ``mqtt_client`` dict
   - edit your mqtt server's settings in the ``mqtt_servers`` list, don't
     forget to modify the ``mqtt_server`` variable, which should point to the
     preferred server

#. Upload the required files to MicroPython: ::

      ampy --port /dev/ttyUSB0 --baud 115200 put config.py
      ampy --port /dev/ttyUSB0 --baud 115200 put main.py

#. After reset, MicroPython will execute the ``main.py`` file

   Connect to the board's serial port with ``miniterm`` to monitor the
   program, it should show something similar: ::

    Starting main()...
    -- Found WLAN: b'<YOURWLAN>'
      -- Known WLAN!, trying to connect...5 ..... connected to: b'<YOURWLAN>'
        ESSID: <YOURWLAN>
        IP: 192.168.0.111
        Netmask: 255.255.255.0
        DefGW: 192.168.0.1
    MQTT connection to <YOURSERVER> is established!
    Registering GPIO: 0
    Connection established with MQTT server <YOURSERVER>
        to publish message: mqtt_c.publish("/my/topic", "My Message")

    MicroPython v1.9.4-8-ga9a3caad0 on 2018-05-11; ESP module with ESP8266
    Type "help()" for more information.
    >>> *** DEBUG: stable measurement False;
    Button event: upy-button-29-139-16.button0.state=False
    *** DEBUG: stable measurement True;
    ...

#. To monitor the messages sent to the configured topic, run the
   ``mosquitto_sub`` utility on your PC: ::

    mosquitto -h <YOURSERVER> -t <YOURTOPIC>

Other Documentation
-------------------

- `Using GPIOs on the ESP8266`_
- `MicroPython Library, MQTT Client`_

- `Wemos D1 Mini`_:

  - Module docs: https://wiki.wemos.cc/products:d1:d1_mini
  - LED pin: GPIO2
  - 1-Button shied v2.0.0 switch pin: GPIO0
  - Wemos 1 Button shield: https://wiki.wemos.cc/products:d1_mini_shields:1-button_shield

.. _pyserial: https://pyserial.readthedocs.io/
.. _miniterm: https://pyserial.readthedocs.io/en/latest/tools.html#module-serial.tools.miniterm
.. _esptool:  https://github.com/espressif/esptool
.. _flash instructions:  http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#deploying-the-firmware
.. _MicroPython download page: https://micropython.org/download 
.. _MicroPython: http://micropython.org/
.. _Wemos D1 Mini: https://wiki.wemos.cc/products:d1:d1_mini
.. _`Using GPIOs on the ESP8266`: https://docs.micropython.org/en/latest/esp8266/quickref.html#pins-and-gpio
.. _`MicroPython Library, MQTT Client`: https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/umqtt/simple.py
