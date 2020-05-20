import pygame
import time         #calling for time to provide delays in program

from joystick_utilities import get_random_audio_path

class JoystickSoundboard():

    def __init__(self):

        self.pygame = pygame
        self.pygame.init()
        self.screen = self.pygame.display.set_mode((400, 400), 0, 32) #this is here for troubleshooting

        self.add_logitech_joystic()
        self.sound_setup()

        self.main_loop()

    def main_loop(self):

        clock = pygame.time.Clock()
        done = False
        print("Starting Main Loop")
        while not done:

            for event in self.pygame.event.get():  # User did something.
                if event.type == self.pygame.JOYBUTTONDOWN:
                    if (event.button + 1) == 11:
                        done = True
                    else:
                        print("You pressed! {}".format(event.button+1))
                        print("playing {}".format(self.random_path))
                        ch = self.random_sound.play()
                        while ch.get_busy():
                            pygame.time.delay(100)
                elif event.type == self.pygame.JOYBUTTONUP:
                    print("You released {}".format(event.button+1))


            clock.tick(20)
            self.pygame.display.update()
        self.pygame.quit()

    def sound_setup(self):

        self.pygame.mixer.init()
        self.random_path = get_random_audio_path()
        self.random_sound = self.pygame.mixer.Sound(self.random_path)

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
