'''
Methods for reading from a scale. Facade to the hx711 library.
'''
import os
import sys
import ConfigParser
from hx711 import HX711
import db
import time
from logcategory import LogCategory

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))

PIN_DAT = config.getint("scale", "pin_DAT")
PIN_CLK = config.getint("scale", "pin_CLK")
REFERENCE_UNIT = config.getint("scale", "reference_unit")
OFFSET = config.getint("scale", "offset")
MAX_TRIES = 5

def get_weight(verbose = False):
    start_time = time.time()
    
    hx = HX711(PIN_DAT, PIN_CLK)
    readings_per_try = 15

    if verbose:
        print 'scale.py: reading weight.'
        print 'Using offset value: %s' % OFFSET
        print 'Taking %s readings for each of maximum %s tries.' % (readings_per_try, MAX_TRIES)

    try:        
        hx.set_reading_format("LSB", "MSB")
        hx.set_reference_unit(REFERENCE_UNIT)
        hx.set_offset(OFFSET)
        result = None

        tries = MAX_TRIES
        while result is None and tries > 0:
            if verbose:
                print 'Tries remaining: %s...' % tries
            hx.reset()
            result = hx.get_weight(times = readings_per_try)
            
            if verbose:                    
                print 'Got result %s' % result

            tries -= 1

    finally:
        if verbose:
            print 'Cleaning up...'
        hx.cleanup()
    
    end_time = time.time()
    if verbose:
        if result == None:
            print 'Failed to get a value from the scale.'
        else:
            print 'Got weight: %s' % result
        print 'Weight operation completed in ' + str(end_time - start_time)

    return result

def log_weight(value = None):
    if value is None:
        value =  get_weight()
    if value is None:
        print 'No log: Bad reading from scale.'
        db.write_log(LogCategory.ERROR, 'Couldn\'t read scale after %s tries.' % MAX_TRIES)
        return

    last_weight = db.get_last_log(LogCategory.WEIGHT)
    log_threshold = 1

    if last_weight == None or (abs(value - last_weight.reading) > log_threshold):
        db.write_log(LogCategory.WEIGHT, '', value)
        print 'Logged weight of %s to the database.' % value
    else:
        print 'No log: weight change of %s is < %s' % ((value - last_weight.reading), log_threshold)
