import sys
import os
import ffmpeg
import pickle

def save_project(path: str, data: dict) -> bool:    
    with open(path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def open_project(path: str) -> dict:    
    with open(path, 'rb') as handle:
        return pickle.load(handle)

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

def get_file_info(file_path: str) -> dict:
    try:
        audio_file_info = {}

        probe = ffmpeg.probe(file_path)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        
        if not audio_stream:
            print(f"No audio stream found in {file_path}")
            return None
        
        path, file_extension = os.path.splitext(file_path)
        
        file_name = path.split('\\')[-1]

        duration = float(audio_stream['duration'])

        sample_rate = int(audio_stream['sample_rate'])
        num_samples = int(sample_rate * duration)

        duration = f"{round(duration)}s"
        file_extension = file_extension.replace('.', '', 1)
        
        file_size = os.path.getsize(file_path)
        file_size = format_file_size(file_size)

        audio_file_info['file_name']      = file_name
        audio_file_info['file_extension'] = file_extension
        audio_file_info['path']           = path
        audio_file_info['duration']       = duration
        audio_file_info['file_size']      = file_size
        audio_file_info['samples']        = num_samples

        return audio_file_info
    
    except ffmpeg.Error as e:
        print(f"Error getting properties for {file_path}: {e}")
        return None