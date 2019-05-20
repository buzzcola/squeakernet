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
servo_pin = config.getint("dispenser", "servo_pin")
alert_weight = config.getint("system", "alert_weight")

pwm_clockwise = pwm_still - crank_speed
pwm_counter_clockwise = pwm_still + crank_speed

def feed_the_cats():
    # make the food come out.
    check_permissions()
    initialize_servo()
    print 'FEED CAT MEOW'
    
    speech.say('Hello nice kitties. Prepare to dispense kibbles.')
    first_attempt = dispense(desired_grams)
    
    if first_attempt <> None:
        dispensed = first_attempt
        print 'Kibbles dispensed: %s grams.' % dispensed
        shortfall = desired_grams - dispensed
        if shortfall >= retry_threshold:
            # the first try fell short, so dispense a bit more to top it up.
            print 'Shortfall of %s grams - kibble contingency activated.' % shortfall
            speech.say("Sub-standard kibble flow detected. Activating kibble contingency plan.")            
            second_attempt = dispense(max(shortfall, 10)) # less than 10 doesn't do much.
            if second_attempt <> None: 
                dispensed += second_attempt

        speech.say('I have dispensed %.1f grams of kibbles for you to enjoy. You are very good cats and I love you.' % dispensed)
        db.write_log(LogCategory.FEED, 'Dispensed %.1fg of kibbles.' % dispensed, dispensed)
        scale.log_weight()
        if dispensed < alert_weight:
            sound_the_alarm()

    else:
        # A None result on dispense() means it couldn't get a reading.
        speech.say('I have dispensed some kibbles for you to enjoy. I hope it\'s enough. You are very good cats and I love you.' % dispensed)
        db.write_log(LogCategory.FEED, 'Kibbles dispensed, probably. Scale failed to read weight.', 0)
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

def dispense(grams):
    # attempt to dispense "grams" grams of food. Return the real
    # number of grams that came out.
    # If the weight reading fails, returns none.
    weight_before = scale.get_weight()
    turn_crank(pwm_clockwise, grams / grams_per_second)
    weight_after = scale.get_weight()
    if weight_after <> None and weight_before <> None:
        return weight_after - weight_before
    else:
        return None

def turn_crank(direction, duration):
    wiringpi.pwmWrite(servo_pin, direction)
    time.sleep(duration)
    wiringpi.pwmWrite(servo_pin, pwm_still)