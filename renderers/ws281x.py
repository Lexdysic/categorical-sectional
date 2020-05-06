"""
Simple driver of the WS281x addressable RGB LED lights.
Based on the AdaFruit code by Tony DiCola
License: Public Domain
"""

from __future__ import division
import time

import lib.local_debug as local_debug
import rpi_ws281x

# LED strip configuration:
LED_COUNT = 16        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

class Ws281xRenderer(object):
    def __init__(self, pixel_count, gpio_pin):
        """
        Create a new controller for the WS281x based lights
        Arguments:
            pixel_count {int} -- The total number of neopixels. Probably a multple of 25.
            gpio_pin {int} -- The GPIO pin 
        """

        self.gpio_pin = gpio_pin
        self.pixel_count = pixel_count

        if not local_debug.is_debug():
            # Specify a hardware SPI connection on /dev/spidev0.0:
            self.pixels = rpi_ws281x.PixelStrip(
                self.pixel_count,
                self.gpio_pin,
                LED_FREQ_HZ,
                LED_DMA,
                LED_INVERT,
                LED_BRIGHTNESS,
                LED_CHANNEL)
            self.pixels.begin()

            # Clear all the pixels to turn them off.
            [self.pixels.setPixelColorRGB(pixel, 0, 0, 0) for pixel in range(0, self.pixel_count)]
            self.pixels.show()

    def set_led(self, pixel_index, color):
        """
        Sets the given airport to the given color
        Arguments:
            pixel_index {int} -- The index of the pixel to set
            color {int array} -- The RGB (0-255) array of the color we want to set.
        """
        if not local_debug.is_debug():
            self.pixels.setPixelColorRGB(pixel_index, color[0], color[1], color[2])
            self.pixels.show()
