import time
import datetime
import wiringpi
import ConfigParser
import os, sys

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeakernet.ini"))

pwm_still = config.getint("servo", "pwm_still")
crank_speed = config.getint("servo", "crank_speed")
crank_time = config.getfloat("servo", "crank_time")
servo_pin = config.getint("servo", "servo_pin")

pwm_clockwise = pwm_still - crank_speed
pwm_counter_clockwise = pwm_still + crank_speed

def main():
        log('SqueakerNet FLP')
        
        checkPermissions()

        if len(sys.argv) > 1 and sys.argv[1] == 'feed':
                initializeServo()
                log('FEED CAT MEOW: Turning crank for %s seconds.' % crank_time)
                go(pwm_clockwise)
        else:
                log('Unknown command. Have a nice day.')

def checkPermissions():
        if hasattr(os, 'geteuid') and os.geteuid() <> 0:
                raise SystemError('This program must be run as root. Can''t continue.')

def initializeServo(): 
        # use 'GPIO naming'
        wiringpi.wiringPiSetupGpio()
        
        # set pin to be a PWM output
        wiringpi.pinMode(servo_pin, wiringpi.GPIO.PWM_OUTPUT)
        
        # set the PWM mode to milliseconds stype
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
        
        # divide down clock
        wiringpi.pwmSetClock(192)
        wiringpi.pwmSetRange(2000)
        

def go(direction):
        # turn the crank.
        wiringpi.pwmWrite(servo_pin, direction)
        time.sleep(crank_time)
        wiringpi.pwmWrite(servo_pin, pwm_still)

def log(message):
        # write a message to the output.
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print '%s: %s' % (timestamp, message)

if __name__ == "__main__":
        main()