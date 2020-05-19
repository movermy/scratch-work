import pygame
import time         #calling for time to provide delays in program

from joystick_utilities import get_random_audio_path

'''
pygame.init()
clock = pygame.time.Clock()

# setup joystick
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
name = joystick.get_name()
assert name.find("logitech") >= 0

# -------- Main Program Loop -----------
done = False
while not done:

    clock.tick(20)

pygame.quit()
'''

class JoystickSoundboard():

    def __init__(self):

        self.pygame = pygame
        self.pygame.init()
        self.add_logitech_joystic()

        self.main_loop()

    def main_loop(self):

        clock = pygame.time.Clock()
        done = False

        while not done:

            for event in self.pygame.event.get():  # User did something.
                if event.type == self.pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")
                elif event.type == self.pygame.JOYBUTTONUP:
                    print("Joystick button released.")

            clock.tick(20)
        self.pygame.quit()

    def add_logitech_joystic(self):
        '''This function looks for the Logitech Attack3 joystick.
        if found, the self.joystick is set to its object'''

        self.pygame.joystick.init()
        joystick_count = self.pygame.joystick.get_count()
        logitech_joystic_index = -1
        for i in range(joystick_count):
            some_joystick = self.pygame.joystick.Joystick(i)
            some_joystick.init()
            name = some_joystick.get_name()
            if name.lower().find("logitech") >= 0:
                # joystick found
                logitech_joystic_index = i
                break

        assert logitech_joystic_index >= 0, "Logitech joystick was not found"

        self.joystick = some_joystick


if __name__ == "__main__":


    js = JoystickSoundboard()

    #print(js.joystick.get_name())
