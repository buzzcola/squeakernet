'''
Squeakernet can talk! This is a really simple/hacky implementation and only works on linux. I couldn't find
a pip package that ran locally and sounded any good. So instead we use pico2wave to write a wav and then play 
it. Works good.
'''
import os

_COMMAND = 'pico2wave -w foo.wav "%s" && aplay foo.wav && rm foo.wav'

def say(phrase):
    try:
        os.system(_COMMAND % phrase)
    # if something goes wrong, don't fail a larger operation.
    except: 
        print 'squeakernet_speech: say("%s") failed somehow.'