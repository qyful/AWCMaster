import sys, os

def get_path():
    """
    Returns the system path for all files depending on whether it is cloned source files or a Pyinstaller build.
    """

    if getattr(sys, 'frozen', False):
        temp_dir = getattr(sys, '_MEIPASS', None)

        if temp_dir:
            ffmpeg_path = os.path.join(temp_dir, 'ffmpeg.exe')
        else:
            ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
    else:
        ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')

    return ffmpeg_path