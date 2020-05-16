from pygame import mixer #calling for pygame mixer to play audio files
import time         #calling for time to provide delays in program

from joystick_utilities import get_random_audio_path

# Starting the mixer
mixer.init()

# Loading the song
mixer.music.load(get_random_audio_path())

# Setting the volume
mixer.music.set_volume(0.7)

# Start playing the song
mixer.music.play(-1)
time.sleep(3)

'''
if __name__ == "__main__":
    print(get_audio_directory_path())
'''