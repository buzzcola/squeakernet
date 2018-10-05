import os

_COMMAND = 'pico2wave -w foo.wav "%s" && aplay foo.wav && rm foo.wav'

def say(phrase):
    try:
        os.system(_COMMAND % phrase)
    # if something goes wrong, don't fail a larger operation.
    except: 
        print 'squeakernet_speech: say("%s") failed somehow.'