import time
import datetime
import wiringpi
import ConfigParser
import os
import sys
import squeakernet_db
from squeakernet_db import LogCategory
import squeakernet_scale

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))

pwm_still = config.getint("dispenser", "pwm_still")
crank_speed = config.getint("dispenser", "crank_speed")
grams_per_second = config.getfloat("dispenser", "grams_per_second")
desired_grams = config.getfloat("dispenser","desired_grams")
crank_time = desired_grams / grams_per_second
servo_pin = config.getint("dispenser", "servo_pin")

alert_weight = config.getint("system", "alert_weight")

pwm_clockwise = pwm_still - crank_speed
pwm_counter_clockwise = pwm_still + crank_speed

def main():

    if len(sys.argv) > 1 and sys.argv[1] == 'feed':
        feed_the_cats()
    elif len(sys.argv) > 1 and sys.argv[1] == "logweight":
        log_weight()
    elif len(sys.argv) > 1 and sys.argv[1] == 'logs':
        if len(sys.argv) > 2:
            print_logs(sys.argv[2].upper())
        else:
            print_logs()
    elif len(sys.argv) > 1 and sys.argv[1] == 'lastfeed':
        log = squeakernet_db.get_last_log(LogCategory.FEED)
        print 'Dispensed %.2fg of kibbles at %s.' % (log.reading, log.date)
    elif len(sys.argv) > 1 and sys.argv[1] == 'writelog':
        if sys.argv > 2:
            squeakernet_db.write_log(LogCategory.SYSTEM, sys.argv[2])
            print 'Log written to database.'
        else:
            print 'writelog: No log was provided to write.'
    elif len(sys.argv) > 1 and sys.argv[1] == 'query':
        if sys.argv > 2:
            result = squeakernet_db.query(sys.argv[2])
            for row in result:
                print '\t'.join([str(x) for x in row])
        else:
            print 'query: no query was provided to execute.'

    else:
        print_message('Unknown command. Have a nice day.')

def feed_the_cats():
    check_permissions()
    initialize_servo()
    print_message('FEED CAT MEOW: Turning crank for %s seconds.' % crank_time)
    weight_before = squeakernet_scale.get_weight()
    go(pwm_clockwise)
    weight_after = squeakernet_scale.get_weight()
    dispensed = weight_after - weight_before
    squeakernet_db.write_log(squeakernet_db.LogCategory.FEED, 'Turned crank for %s seconds, dispensing %.1fg of kibbles.' % (crank_time, dispensed), dispensed)
    log_weight(weight_after)

    if dispensed < alert_weight:
        sound_the_alarm()

def sound_the_alarm():
    # The feeding didn't work, probably because the hopper is empty.
    # (TBD) probably email me or tweet or something.
    print "ALERT ALERT ALERT HUNGRY CATS"

def log_weight(value = None):
    if value is None:
        value =  squeakernet_scale.get_weight()
    if value is None:
        print 'No log: Bad reading from scale.'
        return

    last_weight = squeakernet_db.get_last_log(LogCategory.WEIGHT)
    change = value - last_weight.reading
    log_threshold = 1

    if(abs(change)) > log_threshold:
        squeakernet_db.write_log(LogCategory.WEIGHT, '', value)
        print 'Logged weight of %s to the database (change of %s).' % (value, change)
    else:
        print 'No log: weight change of %s is < %s' % (change, log_threshold)


def print_logs(category = None):
    if category and not hasattr(squeakernet_db.LogCategory, category):
        raise SystemError('There is no log category called "%s".' % category)
    
    logs = squeakernet_db.get_logs(category and squeakernet_db.LogCategory[category] or None)
    for log in logs:
        print '\t'.join([str(x) for x in log])

def check_permissions():
    if hasattr(os, 'geteuid') and os.geteuid() <> 0:
        raise SystemError('This program must be run as root. Can''t continue.')

def initialize_servo(): 
    # use 'GPIO naming'
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(servo_pin, wiringpi.GPIO.PWM_OUTPUT)
    wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
    
    # divide down clock
    wiringpi.pwmSetClock(192)
    wiringpi.pwmSetRange(2000)
    
def go(direction):
    # turn the crank.
    wiringpi.pwmWrite(servo_pin, direction)
    time.sleep(crank_time)
    wiringpi.pwmWrite(servo_pin, pwm_still)

def print_message(message):
    # write a message to the output.
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print '%s: %s' % (timestamp, message)

if __name__ == "__main__":
    main()