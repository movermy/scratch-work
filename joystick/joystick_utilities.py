import os
import random
import glob
import pygame
import sys


def get_audio_directory_path():
    """returns absolute path to audio files assuming
    1) directory is at the same level as scratchwork repo
    2) this function is run in a directory in scratchwork
    3) name of directory is 'audio_files'   """


    name_of_audio_directory = 'audio_files'

    main_repo_dir = os.path.split(os.getcwd())[0]
    above_repo_dir = os.path.split(main_repo_dir)[0]
    return os.path.join(above_repo_dir, name_of_audio_directory)

def get_random_audio_path():

    search_str = os.path.join(get_audio_directory_path(), "*.wav")
    all_audio_paths = glob.glob(search_str)
    return random.choice(all_audio_paths)
    
def get_all_audio_paths():
    
    search_str = os.path.join(get_audio_directory_path(), "*.wav")
    all_audio_paths = glob.glob(search_str)
    return all_audio_paths
    
def test_all_sounds():
    
    search_str = os.path.join(get_audio_directory_path(), "*.wav")
    all_audio_paths = glob.glob(search_str)
    
    pygame.init()
    pygame.mixer.init()

    for path in all_audio_paths:
        print(f"Attempting to play {path}")
        try:
            sound = pygame.mixer.Sound(path)
            ch = sound.play()
            while ch.get_busy():
                pygame.time.delay(100)
            print(f"Able to play {path}")
            print(" ")
        except Exception as e:
            print(e)
            print()
            
    pygame.quit()
    sys.exit()
        
    
    

if __name__ == "__main__":
    test_all_sounds()



