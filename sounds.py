import pygame
from pynput import keyboard
import asyncio
import math
import os
import threading
import time
from winrt.windows.devices.sensors import Accelerometer

pygame.mixer.init()
pygame.mixer.set_num_channels(39)

KEYS = [
    '1','2','3','4','5','6','7','8','9',
    'q','w','e','r','t','y','u','i','o','p',
    'a','s','d','f','g','h','j','k','l',';',
    'z','x','c','v','b','n','m',',','.','/'
]

sounds = {}
wav_files = [f for f in sorted(os.listdir('Sounds')) if f.lower().endswith('.wav')]

# Load sounds 
for i, key in enumerate(KEYS):
    if i < len(wav_files):
        path = os.path.join('Sounds', wav_files[i])
        try:
            sounds[key] = pygame.mixer.Sound(path)
        except Exception as e:
            sounds[key] = None
    else:
        sounds[key] = None

current_tilt = None
active_sounds = {}

def update_tilt():
    async def read_tilt():
        global current_tilt
        accel = Accelerometer.get_default()
        
        while True:
            reading = accel.get_current_reading()
            x = reading.acceleration_x
            y = reading.acceleration_y
            z = reading.acceleration_z
            
            if z > 0:
                current_tilt = math.atan2(math.sqrt(x*x + z*z), y) * (180 / math.pi) - 180
            else:
                current_tilt = 180 - math.atan2(math.sqrt(x*x + z*z), y) * (180 / math.pi)
            
            for key in active_sounds:
                if current_tilt > active_sounds[key]['max_tilt']:
                    active_sounds[key]['max_tilt'] = current_tilt
                volume = 0.2 + (current_tilt + 60) / 135 * 0.8
                volume = max(0.2, min(1.0, volume))
                active_sounds[key]['sound'].set_volume(volume)

            await asyncio.sleep(0.02)

    asyncio.run(read_tilt())

def fade(key, fade_duration):
    s = active_sounds[key]['sound']
    start_volume = s.get_volume()  
    steps = 50
    for i in range(0, steps):
        new_volume = start_volume - (i / steps)
        s.set_volume(new_volume)
        time.sleep(fade_duration / steps)

    s.stop()
    del active_sounds[key]

def on_press(key):
    try:
        if key == keyboard.Key.esc:
            return False 
        
        c = key.char
        if (c not in active_sounds):
            play_sound(c)
        else:
            return
    except AttributeError: 
        pass

def on_release(key):
    try: 
        c = key.char
        if (c in active_sounds.keys()):
            start_tilt = active_sounds[c]['start_tilt']
            tilt_change = abs(active_sounds[c]['max_tilt'] - start_tilt)
            fade_duration = 1/90 * tilt_change + 3

            fade_thread = threading.Thread(target=fade, args=(c, fade_duration))
            fade_thread.start()
    except AttributeError:
        pass


def play_sound(key):
    if sounds[key] is None or current_tilt is None:
        return    

    sounds[key].play(loops=-1)
    active_sounds[key] = {'sound' : sounds[key], 
                        'start_tilt': current_tilt, 
                        'max_tilt': current_tilt}

tilt_thread = threading.Thread(target=update_tilt, daemon=True)
tilt_thread.start()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
listener.join()


