from typing import List
import openai, os, wave, subprocess, sys

def transcribe_file(file: str, api_key: str, prompt: str = None) -> str:
    """Transcribe an audio file.

    Args:
        file (str): File to transcribe
        prompt (str, optional):An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language. Defaults to None.

    Returns:
        str: Transcribed text
    """    
    openai.api_key = api_key
    audio_file = open(file, "rb")
    return openai.Audio.transcribe("whisper-1", audio_file, prompt=prompt, response_format="text")

def is_wave_format(file_path: str) -> bool:
    """Detect if a file is a wave file.

    Args:
        file_path (str): File to check

    Returns:
        bool: True if the file is a wave file, False otherwise
    """    
    try:
        with wave.open(file_path, 'rb') as file:
            if file.getnchannels() == 0:
                return False
            else:
                return True
    except:
        return False
    
# Split file into 24 MB chunks
def split_audio_file(input_file_path: str, output_directory: str) -> None:
    """Split an audio file into 24 MB files, and convert it to wave if necessary. This is required because the OpenAI API has a 25 MB limit per file.

    Args:
        input_file_path (str): File to split
        output_directory (str): Output directory containing the split files
    """    
    # Set the maximum size of each output file to 24 MB
    max_size_bytes: int = 24 * 1024 * 1024

    # Check if the input file is a wave file
    if not is_wave_format(input_file_path):
        # Convert the input file to a wave file
        print(f"Converting {input_file_path} to wave...")
        cache_folder = create_cache_folder()
        converted_file = cache_folder + "/converted.wav"
        # If we're on Windows, we need to use ffmpeg.exe
        if sys.platform == "win32":
            subprocess.run([os.path.join(sys._MEIPASS, 'ffmpeg.exe'), '-i', input_file_path,
                       '-acodec', 'pcm_s16le', '-ar', '44100', converted_file])
        elif sys.platform == "darwin":
            subprocess.run([os.path.join(sys._MEIPASS, './ffmpeg-macos'), '-i', input_file_path,
                        '-acodec', 'pcm_s16le', '-ar', '44100', converted_file])
        else:
            subprocess.run([os.path.join(sys._MEIPASS, './ffmpeg'), '-i', input_file_path,
                        '-acodec', 'pcm_s16le', '-ar', '44100', converted_file])
        input_file_path = converted_file

    # Open the input audio file
    with wave.open(input_file_path, 'rb') as input_file:
        # Get the number of frames in the input file
        num_frames: int = input_file.getnframes()

        # Get the sample width of the input file
        sample_width: int = input_file.getsampwidth()

        # Get the number of channels in the input file
        num_channels: int = input_file.getnchannels()

        # Get the sample rate of the input file
        sample_rate: int = input_file.getframerate()

        # Calculate the maximum number of frames per output file
        max_frames_per_file: int = int(
            max_size_bytes / (sample_width * num_channels))

        # Calculate the number of output files required
        num_output_files: int = (num_frames + max_frames_per_file - 1) // max_frames_per_file

        # Split the input file into smaller files
        print(f"Splitting {input_file_path} into {num_output_files} files...")
        for i in range(num_output_files):
            # Calculate the start and end frames for the current output file
            start_frame: int = i * max_frames_per_file
            end_frame: int = min((i + 1) * max_frames_per_file, num_frames)

            # Calculate the output file path
            output_file_path: str = os.path.join(output_directory, f"{os.path.splitext(os.path.basename(input_file_path))[0]}_{i+1:03}.wav")

            # Open the output file
            with wave.open(output_file_path, 'wb') as output_file:
                # Set the output file parameters
                output_file.setnchannels(num_channels)
                output_file.setsampwidth(sample_width)
                output_file.setframerate(sample_rate)

                # Set the output file data
                input_file.setpos(start_frame)
                output_file.writeframes(
                    input_file.readframes(end_frame - start_frame))

    if os.path.exists(converted_file):
        os.remove(converted_file)

def create_cache_folder() -> str:
    """Create a folder to store the split audio files.

    Returns:
        str: Path to the cache folder
    """    
    # Create a cache folder next to the script if it does not exist
    cache_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_cache')
    if not os.path.exists(cache_folder):
        os.mkdir(cache_folder)

    return cache_folder

def transcribe(file: str, api_key: str) -> str:
    """Transcribe an audio file.

    Args:
        file (str): File to transcribe
        api_key (str): OpenAI API key

    Returns:
        str: Transcribed text
    """    
    if os.path.getsize(file) > 24 * 1024 * 1024:
        cache_folder = create_cache_folder()

        empty_cache_folder(cache_folder)

        split_audio_file(file, cache_folder)
        output: List[str] = []
        print("Transcribing...")
        files = os.listdir(cache_folder)
        files.sort()
        for file in files:
            file_to_transcribe = os.path.join(cache_folder, file)
            prompt = output[-1] if len(output) > 0 else None
            transcription = transcribe_file(file_to_transcribe, api_key, prompt)
            output.append(transcription)

        empty_cache_folder(cache_folder)

        return " ".join(output)
    else:
        return transcribe_file(file, api_key)
    
def empty_cache_folder(folder):
    # Delete the cache folder contents
    for file in os.listdir(folder):
        os.remove(os.path.join(folder, file))

# if __name__ == "__main__":
#     # Transcribe argument file with argument API key
#     from sys import argv
#     trascription = transcribe(argv[1], argv[2])

#     # Write transcribed text to a file
#     with open("output.txt", "w") as f:
#         f.write(trascription)