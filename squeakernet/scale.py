'''
Methods for reading from a scale. Facade to the hx711 library.
'''
import os
import sys
import ConfigParser
from hx711 import HX711
import db
from logcategory import LogCategory

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))

PIN_DAT = config.getint("scale", "pin_DAT")
PIN_CLK = config.getint("scale", "pin_CLK")
REFERENCE_UNIT = config.getint("scale", "reference_unit")
OFFSET = config.getint("scale", "offset")
MAX_TRIES = 5

def get_weight():
    hx = HX711(PIN_DAT, PIN_CLK)
    try:        
        hx.set_reading_format("LSB", "MSB")
        hx.set_reference_unit(REFERENCE_UNIT)
        hx.set_offset(OFFSET)
        result = None

        tries = MAX_TRIES
        while result is None and tries > 0:
            hx.reset()
            result = hx.get_weight()
            tries -= 1

    finally:
        hx.cleanup()

    return result

def log_weight(value = None):
    if value is None:
        value =  get_weight()
    if value is None:
        print 'No log: Bad reading from scale.'
        db.write_log(LogCategory.ERROR, 'Couldn\'t read scale after %s tries.' % MAX_TRIES)
        return

    last_weight = db.get_last_log(LogCategory.WEIGHT)
    change = value - last_weight.reading
    log_threshold = 1

    if(abs(change)) > log_threshold:
        db.write_log(LogCategory.WEIGHT, '', value)
        print 'Logged weight of %s to the database (change of %s).' % (value, change)
    else:
        print 'No log: weight change of %s is < %s' % (change, log_threshold)
