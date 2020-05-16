import pygame.mixer #calling for pygame mixer to play audio files
import time         #calling for time to provide delays in program


pygame.mixer.init(48000, -16, 1, 1024)  #initializing audio mixer

audio1 = pygame.mixer.Sound("buzzer.wav")      #calling for audio file


channel1 = pygame.mixer.Channel(1)   #using channel one for first button


channel1.play(audio1)          #if button one is pressed(grounded) play audio file one
