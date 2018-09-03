import time
import datetime
import wiringpi
import ConfigParser
import os
import sys
import squeakernet_db

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))

pwm_still = config.getint("servo", "pwm_still")
crank_speed = config.getint("servo", "crank_speed")
crank_time = config.getfloat("servo", "crank_time")
servo_pin = config.getint("servo", "servo_pin")

pwm_clockwise = pwm_still - crank_speed
pwm_counter_clockwise = pwm_still + crank_speed

def main():

    if len(sys.argv) > 1 and sys.argv[1] == 'feed':
        feed_the_cats()
    elif len(sys.argv) > 1 and sys.argv[1] == 'logs':
        if len(sys.argv) > 2:
            print_logs(sys.argv[2].upper())
        else:
            print_logs()
    elif len(sys.argv) > 1 and sys.argv[1] == 'last':
        print squeakernet_db.get_last_feed()

    else:
        print_message('Unknown command. Have a nice day.')

def feed_the_cats():
    check_permissions()
    initialize_servo()
    print_message('FEED CAT MEOW: Turning crank for %s seconds.' % crank_time)
    go(pwm_clockwise)
    squeakernet_db.write_log(squeakernet_db.LogCategory.FEED, 'Turned crank for %s seconds.' % crank_time, crank_time)

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