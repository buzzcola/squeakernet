import os
import sys
import ConfigParser
from hx711 import HX711

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))

PIN_DAT = config.getint("scale", "pin_DAT")
PIN_CLK = config.getint("scale", "pin_CLK")
REFERENCE_UNIT = config.getint("scale", "reference_unit")
OFFSET = config.getint("scale", "offset")

def get_weight():
    try:
        hx = HX711(PIN_DAT, PIN_CLK)
        hx.set_reading_format("LSB", "MSB")
        hx.set_reference_unit(REFERENCE_UNIT)
        hx.set_offset(OFFSET)
        result = None

        while result is None:
            hx.reset()
            result = hx.get_weight()
    finally:
        hx.cleanup()

    return result
