import os
import sys
import json
import pickle
import subprocess

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

def convert_to_wav(data: dict, output_path: str = os.getcwd(), fxmanifest: bool = False):
    """
    Converts each item from a list of file paths into the appropriate PCM format as a WAVE file.
    """
    for value in data["sound_files"].values():
        input_path = value["path"]
        output_file = value["file_name"] + '.wav'

        file_path = output_path + "\\audiodirectory\\{0}".format(data["audiobank_name"])

        if not os.path.exists(file_path):
            os.makedirs(file_path)

        formatted_output_path = "{0}\\{1}".format(file_path, output_file)

        ffmpeg_path = get_path("ffmpeg.exe")
        command = [
            ffmpeg_path,
            '-i', input_path,
            '-ar', value["sample_rate"],
            '-f', 'wav',
            '-acodec', 'pcm_s16le',
            '-ac', '1',
            '-fflags', '+bitexact',
            '-flags', '+bitexact',
            '-map_metadata', '-1',
            '-map', '0:a',
            formatted_output_path
        ]

        subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
        
        value["wav_path"] = formatted_output_path
        
        if fxmanifest:
            with open(output_path + "\\fxmanifest.lua", "w") as handler:
                data = f"""fx_version 'cerulean'
game 'gta5'

author 'AWCMaster'
description 'Generated with AWCMaster, a FOSS project'

files {{
    'audiodirectory/{data["audiobank_name"]}.awc',
    'data/{data["audiobank_name"]}.dat54.rel',
}}

data_file "AUDIO_WAVEPACK" "audiodirectory"
data_file "AUDIO_SOUNDDATA" "data/{data["audiobank_name"]}.dat"
"""

                handler.write(data)
                handler.close()

    return data

def get_file_info(file_path: str) -> dict:
    audio_file_info = {}
    ffprobe_path = get_path("ffprobe.exe")

    process = subprocess.Popen(
        [ffprobe_path, '-show_format', '-show_streams', '-of', 'json', file_path],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = process.communicate()

    probe = json.loads(stdout.decode('utf-8'))

    print(probe)

    audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    print(audio_stream)
    if not audio_stream:
        print(f"No audio stream found in {file_path}")
        return None
    
    path, file_extension = os.path.splitext(file_path)
    
    file_name = path.split('\\')[-1]
    path = path + file_extension

    duration = float(audio_stream['duration'])

    sample_rate = int(audio_stream['sample_rate'])
    num_samples = int(audio_stream['nb_frames']) if 'nb_frames' in audio_stream else int(sample_rate * duration)

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