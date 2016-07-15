import time

from Adafruit_LED_Backpack import SevenSegment

# Create display instance on default I2C address (0x70) and bus number.
display = SevenSegment.SevenSegment()

# Initialize the display. Must be called once before using the display.
display.begin()

# Keep track of the colon being turned on or off.
for i in range (0,10): ##NACHGUCKWN=======================================================================
    colon = False
    display.write_display()
    time.sleep(1)
    colon = not colon
    display.write_display()
    time.sleep(1)
    i +=1

# Run through different number printing examples.
print('Press Ctrl-C to quit.')
numbers = [0.0, 1.0, -1.0, 0.55, -0.55, 10.23, -10.2, 100.5, -100.5]
while True:
    # Print floating point values with default 2 digit precision.
    for i in numbers:
        # Clear the display buffer.
        display.clear()
        # Print a floating point number to the display.
        display.print_float(i)
        # Set the colon on or off (True/False).
        display.set_colon(colon)
        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        display.write_display()
        # Delay for a second.
        time.sleep(1.0)

    display.set_invert(False)
    # Make sure to call write_display() to make the above visible!
    # Flip colon on or off.

