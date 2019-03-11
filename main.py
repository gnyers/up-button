'''

'''

from config import known_wlans, mqtt_server, mqtt_client
import utime
import machine
import os

# source: https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/umqtt/simple.py
# from umqtt_client import MQTTClient
from umqtt.simple import MQTTClient # nowadays uqmtt.simple is part of MicroPython

import network
wlan0 = network.WLAN(network.STA_IF); wlan0.active(True)

__all__ = '''
          connect_to_first_known_wlan flash_led sw_callback reg_switch_handler
          network_info mqtt_server mqtt_client
          '''.split()
MQTT_SERVER = mqtt_server.get('name')
MQTT_TOPIC = mqtt_server.get('topic')
MYID = '-'.join(map(str, reversed(machine.unique_id()[:-1])))
MYNAME = '{}-{}'.format(mqtt_client.get('name'), MYID)
BUTTON_GPIO = mqtt_client.get('button_gpio')
BUTTON_DEBOUNCE_TIMEOUT = mqtt_client.get('button_debounce_timeout', 150)
LED_GPIO = mqtt_client.get('led_gpio')
mqtt_c = MQTTClient(MYNAME, MQTT_SERVER)
switch_handler_lock = False           # lock switch callback handler
switch_last_used    = 0               # swdebounce: timestamp: utime.ticks_us()
switch_last_state   = True            # swdebounce: the last state of the button

def ls():
    '''List files on the built-in flash
    '''
    return os.listdir()

def network_info():
    '''Returns a string with the current network settings.
    '''
    fields = 'ESSID IP Netmask DefGW DNS'.split()
    values = (wlan0.config('essid'),) + wlan0.ifconfig()
    info = [ '    {}: {}'.format(fields[i], values[i]) for i in range(4)]
    return '\n'.join(info)

def connect_to_first_known_wlan(known_wlans=known_wlans):
    '''Find a well-known WLAN based on the dict passed on in ``known_wlans``
    and log in.
    '''
    if wlan0.isconnected(): return True
    for net in wlan0.scan():
        ssid = net[0]
        print('-- Found WLAN:', ssid)
        if ssid in known_wlans:
            print('  -- Known WLAN!, trying to connect...', end='')
            wlan0.connect(ssid, known_wlans[ssid])
            for attempt in range(5,0,-1):
                if wlan0.isconnected():
                    print('... connected to:', ssid)
                    print(network_info())
                    return ssid
                else:
                    print(attempt, '..', end='')
                utime.sleep(1)
            print('  -- After 5 attempts connection failed to:', ssid)
    return None

def sw_callback(sw_gpio):
    '''A dummy call-back function to demonstrate the handling of an interrupt
    '''
    print('*** interrupt on switch:', sw_gpio.value())

def sw_callback_mqtt_pub(p, conn=mqtt_c):
    '''A call-back function to handle a switch event; publishes state to an
    MQTT topic

    This function is invoked by the MicroPython kernel to handle the interrupt
    caused by a button push.

    Parameters:
    - p: a Pin instance object, which caused the interrupt
    - 
    '''
    global switch_last_used
    global switch_last_state
    # --- make sure no other instance of this handler is running
    if switch_handler_lock:
        print('*** DEBUG: switch_handler_lock is locked, exiting callback')
        return None
    # --- get a stable state of the Pin
    #     (ie.: result of 10 consecutive measurement)
    t, f = (0,0)
    for i in range(30):
        state = p.value()
        if t == 10 or f == 10 : break
        if state: t, f = (t+1, f-1)
        else: t, f = (t-1, f+1)
    else:
        return None
    state = True if t > f else False
    print('*** DEBUG: stable measurement {}; t={},f={}/{}'.format(
               state, t, f, i))

    # --- an attempt for a software de-bouncer; state changes only after a
    #     timeout
    lastused = utime.ticks_us() - switch_last_used
    if not(
        state != switch_last_state
        and
        lastused > BUTTON_DEBOUNCE_TIMEOUT*1000
        ):
        print('*** DEBUG: lastused:{}ms ago (min:{}), last state:{}; exiting'
              'callback'.format(lastused//1000, BUTTON_DEBOUNCE_TIMEOUT,
                                switch_last_state))
        return None
    # --- 
    msg = '{}.button{}.state={}'.format(MYNAME, BUTTON_GPIO, state)
    print('Button event:', msg)
    conn.publish(MQTT_TOPIC, msg)       # pulish switch state to MQTT server
    flash_led(interval=50)              # flash the LED briefly
    switch_last_used = utime.ticks_us()
    switch_last_state = state

def reg_switch_handler(GPIO, callback_f):
    '''Register interrupt handler for GPIO switch
    '''
    print('Registering GPIO:', GPIO)
    button = machine.Pin(GPIO, machine.Pin.IN, machine.Pin.PULL_UP)
    button.irq(trigger=machine.Pin.IRQ_FALLING|machine.Pin.IRQ_RISING,
           handler=callback_f)
    return button

def flash_led(pin=None, interval=100, inverted=True):
    ''' Flash the LED attached to ``pin`` for the given ``interval``
    milliseconds. Use the ``inverted=False`` if the Pin is not inverted logic
    (default=True).

    This function will switch the LED (or rather, the Pin) on and create a
    timer to asynchronously switch it off after the given interval.
    '''
    if pin is None: pin = machine.Pin(LED_GPIO, machine.Pin.OUT, value=inverted)
    on  = pin.off if inverted else pin.on
    off = pin.on  if inverted else pin.off
    on()
    t_off = machine.Timer(-1)
    t_off.init(mode=machine.Timer.ONE_SHOT, period=interval,
               callback=lambda t: off())

def main():
    print('Starting main()...')
    while True:
        if connect_to_first_known_wlan(known_wlans): break
        print('== Was unable to find known WLAN, sleeping for 30s')
        utime.sleep(30)
    try:
        mqtt_c.connect()
        mqtt_c.ping()
        print('MQTT connection to {} is established!'.format(MQTT_SERVER))
        flash_led(interval=50)
        sw = reg_switch_handler(BUTTON_GPIO, sw_callback_mqtt_pub)
    except OSError as e:
        print('MQTT connection to {} has failed! (Error {})'.format(
               MQTT_SERVER, e.args[0]))
    except Exception as e:
        print('*** ERROR: something went wrong: {}'.format(e))
    else:
        print('Connection established with MQTT server {}'.format(MQTT_SERVER))
        print('    to publish message: mqtt_c.publish("/my/topic", "My Message")')
        mqtt_c.publish(MQTT_TOPIC,'{} online'.format(MYNAME))

if __name__ == '__main__':
    # This will NOT be executed when this module is being imported
    main()
