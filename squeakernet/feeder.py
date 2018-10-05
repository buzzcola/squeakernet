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
    dispensed = weight_after - weight_before
    speech.say('I have dispensed %.1f grams of kibbles for you to enjoy. You are very good cats and I love you.' % dispensed)
    db.write_log(LogCategory.FEED, 'Turned crank for %.1f seconds, dispensing %.1fg of kibbles.' % (crank_time, dispensed), dispensed)
    scale.log_weight(weight_after)

    if dispensed < alert_weight:
        sound_the_alarm()

def sound_the_alarm():
    # The feeding didn't work, probably because the hopper is empty.
    # (TBD) probably email me or tweet or something.
    print "ALERT ALERT ALERT HUNGRY CATS"

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