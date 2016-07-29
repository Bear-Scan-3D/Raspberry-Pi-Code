import gaugette.rotary_encoder
import gaugette.switch


#wiringPI Pins
A_PIN = 2 # = 22
B_PIN = 3 # = 27
SW_PIN = 7 # = 4

encoder = gaugette.rotary_encoder.RotaryEncoder(A_PIN, B_PIN)
switch = gaugette.switch.Switch(SW_PIN)
last_state = None

while True:
    delta = encoder.get_delta()
    if delta != 0:
        print "rotate %d" % delta

    sw_state = switch.get_state()
    if sw_state != last_state:
        print "switch %d" % sw_state
        last_state = sw_state