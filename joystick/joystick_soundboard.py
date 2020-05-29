import pygame
import time  
import sys       #calling for time to provide delays in program
import os
import traceback

from joystick_utilities import get_random_audio_path, get_all_audio_paths

class JoystickSoundboard():

    def __init__(self):
        
        self.pygame = pygame
        self.pygame.init()
        self.screen = self.pygame.display.set_mode((400, 400), 0, 32) #this is here for troubleshooting
        
        self.add_logitech_joystick()
        self.pygame.mixer.init()
        self.sound_setup()
        self.main_loop()

    def main_loop(self):

        clock = pygame.time.Clock()
        done = False
        print("Starting Main Loop")
        btn_11_dwn = False
        btn_6_dwn = False
        while not done:

            for event in self.pygame.event.get():  # User did something.
                if event.type == self.pygame.JOYBUTTONDOWN:
                    if (event.button + 1) == 11:
                        btn_11_dwn = True
                    if (event.button + 1) == 6:
                        btn_6_dwn = True
  
                    print("You pressed! {}".format(event.button+1))
                    print("playing {}".format(self.sound_list[event.button]))
                    ch = self.sound_list[event.button].play()
                    while ch.get_busy():
                        pygame.time.delay(100)
                    self.sound_setup()
                elif event.type == self.pygame.JOYBUTTONUP:
                        if (event.button + 1) == 11:
                                btn_11_dwn = False
                        if (event.button + 1) == 6:
                                btn_6_dwn = False
                        print("You released {}".format(event.button+1))
                    
            if btn_6_dwn and btn_11_dwn:
                done = True


            clock.tick(20)
            self.pygame.display.update()
            
        self.pygame.quit()
        sys.exit()

    def sound_setup(self):

        
        #self.random_path = get_random_audio_path()
        #self.random_sound = self.pygame.mixer.Sound(self.random_path)
        
        link = [s for s in get_all_audio_paths() if 'zoup' in s]
        self.zoup = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'lazer' in s]
        self.laser = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'boom-kick' in s]
        self.kick = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'phaser' in s]
        self.phaser = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'space-sound' in s]
        self.space = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'fart-3' in s]
        self.fart = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'gong' in s]
        self.gong = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'game-sound' in s]
        self.game = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'sonar-ping' in s]
        self.sonar = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'whistle' in s]
        self.ladder = self.pygame.mixer.Sound(link[0])
        
        link = [s for s in get_all_audio_paths() if 'pipe' in s]
        self.pipe = self.pygame.mixer.Sound(link[0])
        
        self.sound_list = []
        for i in range(0,11):
                self.sound_list.append(self.fart)
                
        self.sound_list[1] = self.zoup
        self.sound_list[2] = self.space
        self.sound_list[3] = self.phaser
        self.sound_list[4] = self.laser
        self.sound_list[5] = self.pipe
        self.sound_list[6] = self.gong
        self.sound_list[7] = self.game
        self.sound_list[8] = self.sonar
        self.sound_list[9] = self.kick
        self.sound_list[10] = self.ladder
        
        
        
        
        
        

    def add_logitech_joystick(self):
        '''This function looks for the Logitech Attack3 joystick.
        if found, the self.joystick is set to its object'''

        self.pygame.joystick.init()
        joystick_count = self.pygame.joystick.get_count()
        logitech_joystic_index = -1
        for i in range(joystick_count):
            some_joystick = self.pygame.joystick.Joystick(i)
            some_joystick.init()
            name = some_joystick.get_name()
            if name.lower().find("logitech") >= 0 and name.lower().find("3") >= 0:
                # joystick found
                logitech_joystic_index = i
                break

        assert logitech_joystic_index >= 0, "Logitech joystick was not found"

        self.joystick = some_joystick


if __name__ == "__main__":
        
        
    try:
        js = JoystickSoundboard()
    except Exception as e:
        print(e)
        traceback.print_exc()
        js.pygame.quit()
    finally:
        sys.exit()

    #print(js.joystick.get_name())
