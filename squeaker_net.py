'''
SqueakerNet 0.001 : turns a crank

Setup:
  pip install RPi.GPIO
  pip install wiringpi

'''

import RPi.GPIO as GPIO
import time
import wiringpi

SPEED = 10
STILL = 150
CLOCKWISE = STILL - SPEED
COUNTER_CLOCKWISE = STILL + SPEED

delay_period = 2.4;
servo_pin = 18;
button_pin = 23;

def waitForButtonPress():
        print 'DO NOT PUSH BUTTON'
        while True:
                input_state = GPIO.input(button_pin)
                if input_state == False:
                        print 'YOU PUSHED THE BUTTON'
                        go(CLOCKWISE)
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
        time.sleep(delay_period)
        wiringpi.pwmWrite(servo_pin, STILL)

if __name__ == "__main__":
        initializeButton();
        initializeServo();
        waitForButtonPress();
