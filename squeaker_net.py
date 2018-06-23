'''
SqueakerNet 0.002 : turns a crank, has a config file

Setup:
  pip install RPi.GPIO
  pip install wiringpi

'''

import RPi.GPIO as GPIO
import time
import wiringpi
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("squeaker_net.ini")

pwm_still = config.getint("servo", "pwm_still")
crank_speed = config.getint("servo", "crank_speed")
crank_time = config.getfloat("servo", "crank_time")
servo_pin = config.getint("servo", "servo_pin")

pwm_clockwise = pwm_still - crank_speed
pwm_counter_clockwise = pwm_still + crank_speed

button_pin = config.getint("button", "button_pin")

def waitForButtonPress():
        print 'DO NOT PUSH BUTTON'
        while True:
                input_state = GPIO.input(button_pin)
                if input_state == False:
                        print 'YOU PUSHED THE BUTTON'
                        go(pwm_clockwise)
                        time.sleep(0.2)

def initializeButton():
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
        wiringpi.pwmWrite(servo_pin, direction)
        time.sleep(crank_time)
        wiringpi.pwmWrite(servo_pin, pwm_still)

if __name__ == "__main__":
        initializeButton();
        initializeServo();
        waitForButtonPress();
