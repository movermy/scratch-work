from pygame import mixer #calling for pygame mixer to play audio files
import time         #calling for time to provide delays in program

from joystick_utilities import get_random_audio_path

pygame.init()
clock = pygame.time.Clock()
pygame.joystick.init()


# -------- Main Program Loop -----------
done = False
while not done:

    clock.tick(20)

pygame.quit()
