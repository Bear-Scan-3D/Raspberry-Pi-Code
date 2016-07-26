import time

from Adafruit_LED_Backpack import SevenSegment

# Create display instance on default I2C address (0x70) and bus number.
display = SevenSegment.SevenSegment()

# Initialize the display. Must be called once before using the display.
display.begin()

# Keep track of the colon being turned on or off.
print 'Beginne Testprogramm'

# Run through different number printing examples.
print('Press Ctrl-C to quit.')
number = 10
while True:
    # Print floating point values with default 2 digit precision.
    # Clear the display buffer.
    display.clear()
    # Print a floating point number to the display.
    #display.print_number_str(number)
    number += 1
    #display.write_display()
    # Delay for a second.
    time.sleep(1.0)

    display.print_float(0.10)
    display.set_colon(False)
    display.set_brightness(1)
    display.write_display()

    time.sleep(1.0)

    display.print_number_str('A234')
    display.set_colon(False)
    display.set_brightness(15)
    display.write_display()
    time.sleep(1.0)
    i = 0
    while i < 10:

        display.set_brightness(15)
        time.sleep(1.0)
        display.set_brightness(1)
        time.sleep(1.0)

        i +=1



    #display.set_invert(False)
    # Make sure to call write_display() to make the above visible!
