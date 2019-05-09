'''
Control a feeder that dispenses kibbles. Specifically, a continuous rotation servo controlled via PWM.
'''
import time
import datetime
import wiringpi
import ConfigParser
import os
import sys
import db
from logcategory import LogCategory
import scale
import speech

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))

pwm_still = config.getint("dispenser", "pwm_still")
crank_speed = config.getint("dispenser", "crank_speed")
grams_per_second = config.getfloat("dispenser", "grams_per_second")
desired_grams = config.getfloat("dispenser","desired_grams")
retry_threshold = config.getfloat("dispenser","retry_threshold")
crank_time = desired_grams / grams_per_second
servo_pin = config.getint("dispenser", "servo_pin")

alert_weight = config.getint("system", "alert_weight")

pwm_clockwise = pwm_still - crank_speed
pwm_counter_clockwise = pwm_still + crank_speed

def feed_the_cats():
    check_permissions()
    initialize_servo()
    print 'FEED CAT MEOW: Turning crank for %s seconds.' % crank_time
    weight_before = scale.get_weight()
    speech.say('Hello nice kitties. Prepare to dispense kibbles.')
    go(pwm_clockwise)
    weight_after = scale.get_weight()
    
    if weight_after <> None and weight_before <> None:        
        dispensed = weight_after - weight_before
        print 'Kibbles dispensed: %s grams.' % dispensed
        shortfall = desired_grams - dispensed
        if shortfall >= retry_threshold:
            print 'Shortall of %s grams - kibble contingency activated.' % shortfall
            weight_before = scale.get_weight()
            speech.say("Inadquate kibble flow detected. Activating kibble contingency plan.")
            go(pwm_clockwise, shortfall / grams_per_second)
            weight_after = scale.get_weight()
            if weight_after <> None and weight_before <> None: 
                dispensed += (weight_after - weight_before)

        speech.say('I have dispensed %.1f grams of kibbles for you to enjoy. You are very good cats and I love you.' % dispensed)
        db.write_log(LogCategory.FEED, 'Turned crank for %.1f seconds, dispensing %.1fg of kibbles.' % (crank_time, dispensed), dispensed)
        scale.log_weight(weight_after)
        if dispensed < alert_weight:
            sound_the_alarm()

    else:
        speech.say('I have dispensed some kibbles for you to enjoy. I hope it\'s enough. You are very good cats and I love you.' % dispensed)
        db.write_log(LogCategory.FEED, 'Turned crank for %.1f seconds. Scale failed to read weight.' % crank_time, 0)
        scale.log_weight()

def sound_the_alarm():
    # The feeding didn't work, probably because the hopper is empty.
    # (TBD) probably email me or tweet or something.
    for _ in range(5):
        speech.say("ALERT ALERT ALERT HUNGRY CATS NEED MORE KIBBLES")

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
    
def go(direction, amount = crank_time):
    # turn the crank.
    wiringpi.pwmWrite(servo_pin, direction)
    time.sleep(amount)
    wiringpi.pwmWrite(servo_pin, pwm_still)