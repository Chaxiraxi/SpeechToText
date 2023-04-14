from typing import List
from tqdm import tqdm
from API_KEY import API_KEY
import openai, os, wave
openai.api_key = API_KEY

def transcribe_file(file: str, prompt: str = None) -> str:
    """Transcribe an audio file.

    Args:
        file (str): File to transcribe
        prompt (str, optional):An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language. Defaults to None.

    Returns:
        str: Transcribed text
    """    
    audio_file = open(file, "rb")
    return openai.Audio.transcribe("whisper-1", audio_file, prompt=prompt, response_format="text")

# Split file into 24 MB chunks
def split_audio_file(input_file_path: str, output_directory: str) -> None:
    """Split an audio file into 24 MB files.

    Args:
        input_file_path (str): File to split
        output_directory (str): Output directory containing the split files
    """    
    # Set the maximum size of each output file to 24 MB
    max_size_bytes: int = 24 * 1024 * 1024

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
        for i in range(num_output_files):
            # Calculate the start and end frames for the current output file
            start_frame: int = i * max_frames_per_file
            end_frame: int = min((i + 1) * max_frames_per_file, num_frames)

            # Calculate the output file path
            output_file_path: str = os.path.join(output_directory, f"{os.path.splitext(os.path.basename(input_file_path))[0]}_{i+1}.wav")

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


def transcribe(file):
    if os.path.getsize(file) > 24 * 1024 * 1024:
        # Create a cache folder next to the script if it does not exist
        cache_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio_cache')
        if not os.path.exists(cache_folder): os.mkdir(cache_folder)

        split_audio_file(file, cache_folder)
        output = []
        for file in tqdm(os.listdir(cache_folder)):
            output.append(transcribe_file(os.path.join(cache_folder, file), output[-1] if len(output) > 0 else None))

        # Delete the cache folder contents
        for file in os.listdir(cache_folder):
            os.remove(os.path.join(cache_folder, file))

        return " ".join(output)
    else:
        return transcribe_file(file)
    
if __name__ == "__main__":
    # Transcribe argument file
    import sys
    trascription = transcribe(sys.argv[1])

    # Write transcribed text to a file
    with open("output.txt", "w") as f:
        f.write(trascription)