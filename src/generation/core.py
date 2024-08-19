import xml.etree.ElementTree as ET
import os

class SimpleSound:
    def __init__(self, track_data: dict, audio_bank_name: str, soundset_name: str, output_dir: str = './output'):
        """
        SimpleSound setter function for file names and track data.
        """

        self.track_data = track_data
        self.audio_bank_name = audio_bank_name
        self.soundset_name = soundset_name
        self.output_dir = output_dir
        self.data_dir = os.path.join(self.output_dir, 'data')
        self.audio_dir = os.path.join(self.output_dir, 'audiodirectory')

        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)

    def construct(self):
        self._construct_awc()
        self._construct_dat54()

    def _construct_awc(self):
        container_paths = {"Item": []}
        for value in self.track_data.values():
            container_paths_track = f'{self.output_dir}\\{value["track"]}'
            container_paths["Item"].append(container_paths_track)

        track_info = []
        for value in self.track_data.values():
            simple_info = [
                {"Item": {"Type": "peak"}},
                {"Item": {"Type": "data"}},
                {
                    "Item": {
                        "Type": "format",
                        "Codec": "PCM",
                        "Samples": {"@value": value["samples"]},
                        "SampleRate": {"@value": value["sample_rate"]},
                        "Headroom": {"@value": "-100"},
                        "PlayBegin": {"@value": "0"},
                        "PlayEnd": {"@value": "0"},
                        "LoopBegin": {"@value": "0"},
                        "LoopEnd": {"@value": "0"},
                        "LoopPoint": {"@value": "-1"},
                        "Peak": {"@unk": "0"},
                    }
                }
            ]
            streaming_sound = {
                "Item": {
                    "Name": value["track"],
                    "FileName": value["tracks"]["ss"],
                    "Chunks": {"Item": [item["Item"] for item in simple_info]},
                }
            }
            track_info.append(streaming_sound)

        obj = {
            "AudioWaveContainer": {
                "Version": {"@value": "1"},
                "ChunkIndices": {"@value": "True"},
                "Streams": {"Item": [item["Item"] for item in track_info]},
            }
        }

        self.write_xml_file(obj, f'{self.audio_bank_name}.awc.xml')

    def _construct_dat54(self):
        container_paths = {"Item": []}
        for value in self.track_data.values():
            container_paths_track = f'audiodirectory\\{value["track"]}'
            container_paths["Item"].append(container_paths_track)

        track_info = []
        sound_set_info = []
        for value in self.track_data.values():
            simple_sound1 = {
                "Item": {
                    "@type": "SimpleSound",
                    "Name": f'{value["track"]}_sp',
                    "Header": {
                        "Flags": {"@value": self.merge_flags(value["flags"])},
                        "Volume": {"@value": "200"},
                        "Category": "scripted",
                    },
                    "ContainerName": f'audiodirectory/{self.audio_bank_name}',
                    "FileName": value["track"],
                    "WaveSlotNum": {"@value": "0"},
                }
            }
            track_info.append(simple_sound1)

            sound_sets = {
                "Item": {
                    "ScriptName": value["track"],
                    "ChildSound": f'{value["track"]}_sp',
                }
            }
            sound_set_info.append(sound_sets)

        simple_sound2 = {
            "Item": {
                "@type": "SoundSet",
                "Name": self.soundset_name,
                "Header": {"Flags": {"@value": "0xAAAAAAAA"}},
                "SoundSets": {"Item": [item["Item"] for item in sound_set_info]},
            }
        }
        track_info.append(simple_sound2)

        obj = {
            "Dat54": {
                "Version": {"@value": "7314721"},
                "ContainerPaths": {"Item": f'audiodirectory\\{self.audio_bank_name}'},
                "Items": {"Item": [item["Item"] for item in track_info]},
            }
        }

        self.write_xml_file(obj, f'{self.audio_bank_name}.dat54.rel.xml')

    def merge_flags(self, flag_list: list):
        """
        Small helper function for 16-bit hexadecimal addition for the `Flags` section of the Dat54 header.      
        
        Raises:
        -------
        ValueError
            In the case that a flag does not exist within the definition of the hex map below, a `ValueError` is thrown.
        """

        hex_map = {
            'Flags2': 0x00000001,
            'Unk01': 0x00000002,
            'Volume': 0x00000004,
            'VolumeVariance': 0x00000008,
            'Pitch': 0x00000010,
            'PitchVariance': 0x00000020,
            'Pan': 0x00000040,
            'PanVariance': 0x00000080,
            'PreDelay': 0x00000100,
            'PreDelayVariance': 0x00000200,
            'StartOffset': 0x00000400,
            'StartOffsetVariance': 0x00000800,
            'AttackTime': 0x00001000,
            'ReleaseTime': 0x00002000,
            'DopplerFactor': 0x00004000,
            'Category': 0x00008000,
            'LPFCutOff': 0x00010000,
            'LPFCutOffVariance': 0x00020000,
            'HPFCutOff': 0x00040000,
            'HPFCutOffVariance': 0x00080000,
            'UnkHash3': 0x00100000,
            'DistanceAttentuation': 0x00200000,
            'Unk19': 0x00400000,
            'Unk20': 0x00800000
        }

        result = 0

        for field in flag_list:
            if field in hex_map:
                result += hex_map[field]
            else:
                raise ValueError(f"Unknown field name: {field}")

        return f"0x{result:08X}"
    
    def dict_to_element(self, tag, content):
        element = ET.Element(tag)

        for key, value in content.items():
            if key.startswith('@'):
                element.set(key[1:], value)
            elif isinstance(value, dict):
                child = self.dict_to_element(key, value)
                element.append(child)
            elif isinstance(value, list):
                for item in value:
                    child = self.dict_to_element(key, item)
                    element.append(child)
            else:
                child = ET.SubElement(element, key)
                child.text = str(value)
        return element
    
    def write_xml_file(self, obj: dict, filename: str) -> bool:
        """
        Write the XML output to the file based on the directory declared in `__init__()`.
        """

        # Retrieve the first key from the dictionary `obj` and convert the key-value pair into an XML element
        root_element = self.dict_to_element(list(obj.keys())[0], obj[list(obj.keys())[0]])
        tree = ET.ElementTree(root_element)
        
        ET.indent(tree, space=" ", level=0)

        if "dat54" in filename:
            output_file = os.path.join(self.data_dir, filename)
        elif "awc" in filename:
            output_file = os.path.join(self.audio_dir, filename)
        else:
            return False

        tree.write(output_file, encoding='utf-8', xml_declaration=True, method='xml')
        return True