import os
import random
import glob


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

if __name__ == "__main__":
    print(get_random_audio_path())



