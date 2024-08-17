import sys
import os
import ffmpeg

def get_path(file_name: str) -> str:
    """
    Returns the system path for all files depending on whether it is cloned source files or a Pyinstaller build.
    """

    if getattr(sys, 'frozen', False):
        temp_dir = getattr(sys, '_MEIPASS', None)

        if temp_dir:
            path = os.path.join(temp_dir, file_name)
        else:
            path = os.path.join(os.getcwd(), file_name)
    else:
        path = os.path.join(os.path.dirname(__file__), file_name)

    return path

def format_file_size(file_size: int, suffix="B"):
    """
    Returns the formatted, human-readable version of a file's size from bytes.
    """

    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(file_size) < 1024.0:
            return f"{file_size:3.1f} {unit}{suffix}"
        file_size /= 1024.0
    return f"{file_size:.1f} Yi{suffix}"

def convert_to_wav(file_list: list):
    """
    Converts each item from a list of file paths into the appropriate ADPCM format as a WAVE file.
    """

    for file_path in file_list:
        output_file = file_path.rsplit('.', 1)[0] + '.wav'
        
        try:
            ffmpeg.input(file_path).output(output_file, ar=44100, acodec='adpcm_ima_wav').run(overwrite_output=True)
            
            print(f"Successfully converted {file_path} to {output_file}")
        except ffmpeg.Error as e:
            print(f"Error converting {file_path}: {e}")

"""def get_file_info(path: str) -> dict:
    audio_file_info = {}

    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)

        if os.path.isfile(file_path):
            try:
                audio = File(file_path)
                if audio is not None:
                    file_name, file_extension = os.path.splitext(filename)

                    if file_extension not in [".wav", ".mp3", ".ogg"]:
                        continue

                    file_size = os.path.getsize(file_path)
                    file_length = audio.info.length

                    file_extension = file_extension.replace('.', '').upper()
                    file_size = format_file_size(file_size)
                    file_length = f"{round(file_length)}s"

                    audio_file_info['file_name'] = file_name
                    audio_file_info['file_extension'] = file_extension
                    audio_file_info['file_length'] = file_length
                    audio_file_info['file_size'] = file_size
            except Exception:
                return False

    return audio_file_info"""