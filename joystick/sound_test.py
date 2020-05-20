from pygame import mixer #calling for pygame mixer to play audio files
import pygame
import time         #calling for time to provide delays in program

from joystick_utilities import get_random_audio_path

#pygame.init()  #adding this causes intermittent errors with GIL

mixer.init()

random_sound = mixer.Sound(get_random_audio_path())
random_sound.play()
time.sleep(random_sound.get_length())

#pygame.quit() #adding this causes intermittent errors with GIL
