name = 'SqueakerNet FLP'
version = 'v0.004'

'''
SqueakerNet
  - Turns a crank 
  - Has a config file
  - Displays messages on an LED

Setup:
  pip install RPi.GPIO
  pip install wiringpi

'''

import RPi.GPIO as GPIO
import time
import wiringpi
import lcd_display
from lcd_display import lcd_string, lcd_clear, LCD_LINE_1, LCD_LINE_2
import ConfigParser
import os
import sys

config = ConfigParser.ConfigParser()
config.read(os.path.join(sys.path[0], "squeaker_net.ini"))

log_verbose = config.getboolean('system', 'log_verbose')

def printConfig(config):
        print('SqueakerNet Config:')
        for section in config.sections():
                print('  %s' % section)
                for option in config.options(section):
                        print '    %s: %s' % (option, config.get(section, option))

if(log_verbose):
        printConfig(config)

pwm_still = config.getint("servo", "pwm_still")
crank_speed = config.getint("servo", "crank_speed")
crank_time = config.getfloat("servo", "crank_time")
servo_pin = config.getint("servo", "servo_pin")

pwm_clockwise = pwm_still - crank_speed
pwm_counter_clockwise = pwm_still + crank_speed

button_pin = config.getint("button", "button_pin")

lcd_display.init(config)

def main():
        log('SqueakerNet FLP', version)
        
        if len(sys.argv) > 1 and sys.argv[1] == 'feed':
                go(pwm_clockwise)
        else:
                while True:
                        input_state = GPIO.input(button_pin)
                        if input_state == False:
                                log("Let's enjoy!", 'FEED CAT MEOW')
                                go(pwm_clockwise)
                                log('SqueakerNet FLP', version)
                        time.sleep(0.2)

def initializeGPIO():
        # set for standard broadcom pin numbering.
        GPIO.setmode(GPIO.BCM)

def initializeButton():        
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def initializeServo(): 
        '''
        WIP: rewrite servo stuff with the GPIO library. The servo/button code
        is taken from a wiringpi sample while the LED stuff uses wiringpi - 
        it's bush league to have two different libraries here! :)
        
        # set pin to be a PWM output
        #wiringpi.pinMode(servo_pin, wiringpi.GPIO.PWM_OUTPUT)
        GPIO.setup(servo_pin, GPIO.PWM_OUTPUT)
        
        # set the PWM mode to milliseconds stype
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
        
        # divide down clock
        wiringpi.pwmSetClock(192)
        wiringpi.pwmSetRange(2000)

        '''
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

def log(line1, line2):
        # write a message to the output (console and lcd display.)
        print '%s %s' % (line1, line2)
        lcd_string(line1, LCD_LINE_1)
        lcd_string(line2, LCD_LINE_2)

if __name__ == "__main__":
        try:
                initializeButton();
                initializeServo();
                main();
        except KeyboardInterrupt:
                pass
        finally:
                lcd_clear()
                lcd_string("SqueakerNet",LCD_LINE_1)
                lcd_string("** OFFLINE **",LCD_LINE_2)
                GPIO.cleanup()

