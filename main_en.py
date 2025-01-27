import pathlib
import librosa
import warnings
import re
import shutil
import time

from download_en import Download
from fingerprint import FingerprintIdentifier
from search_time import search_subclip
from sliding_audio_split import SlidingWindowProcessor
from time_calculate import time_format
from split_audio_large_segments_en import LargeAudioSplitter
from convert_to_m4a_en import Mp4ToM4aConverter
#user defined exception
class RangeError(Exception):
    pass

def download_sound_file(url, output_path, process_type, url_type,start_time=None, end_time=None):
    """
    Download the audio file based on the URL and process type.
    args:
        url: str, URL of the audio file
        output_path: str, Output path for the downloaded file
        process_type: int, Processing type (1: Download the entire audio, 2: Download a section of the audio)
        url_type: str, URL type (youtube or twitch)
        start_time: int, Start time of the section to download
        end_time: int, End time of the section to download
    """
    # Start with a unified initialization, then decide the download method according to the type.
    downloader = Download(url, output_path)
    if process_type == 1 and url_type=="youtube" :  
        need_download= downloader.download_youtube_m4a()
    elif process_type == 1 and url_type=="twitch":  
        need_download= downloader.download_twitch_mp4()
    elif process_type == 2:  
        need_download= downloader.download_youtube_section_m4a(start_time, end_time)
    else:
        raise ValueError("process_type must be 1 or 2")
    
    # Since the downloaded Twitch file is an audio-only mp4 file, it needs to be converted to m4a
    if url_type=="twitch":
        need_download=convert_mp4_to_m4a(need_download)
    return need_download
    
def convert_mp4_to_m4a(input_file):
    """
    Convert the mp4 file to m4a format.
    args:
        input_file: str, Input file path
    """
    return Mp4ToM4aConverter.convert_mp4_to_m4a(input_file)
    
def get_time_input():
    """
    Prompt the user to enter the start and end times, and re-prompt if the input is invalid.
    Finally, return the start and end times in seconds.
    """
    while True:
        try:
            # default is the preset value when the input is empty, and min_value and max_value define the input range.
            print("\nPlease enter the start time for the highlight video (format MM:SS) : ")
            start_minute = get_valid_number("Start time (minutes, default is 0) : ", default=0, min_value=0, max_value=60)
            start_seconds = get_valid_number("Start time (seconds, default is 0) : ", default=0,min_value=0,max_value=60)

            print("\nPlease enter the end time for the highlight video (format MM:SS) : ")
            end_minute = get_valid_number("End time (minutes, default is 0) : ", default=0, min_value=0, max_value=60)
            end_seconds = get_valid_number("End time (seconds, default is 10) : ", default=10,min_value=0,max_value=60)

            # Convert the time to seconds
            start_hour=end_hour=0
            start = time_format.time_to_sec(start_hour, start_minute, start_seconds)
            end = time_format.time_to_sec(end_hour, end_minute, end_seconds)

            if start < 0 or end <= start:
                raise ValueError("Start time must be less than end time!")

            return start, end 

        except ValueError as e:
            print(f"Invalid input : {e}")
            print("Please try again.")


def get_valid_number(prompt, default=None, min_value=None, max_value=None):
    """
    Validate the user's input number.
    If invalid, output an error message.
    args:
        prompt: str, Message to prompt the user
        default: int, Default value
        min_value: int, Minimum value
        max_value: int, Maximum value
    """
    while True:
        try:
            user_input = input(prompt)
            if user_input == "" and default is not None:
                return default
            value = int(user_input)

            if (min_value is not None and value < min_value or max_value is not None and value >= max_value): 
                raise RangeError(f"Input value must be greater than {min_value} and less than {max_value}!")
            return value
        
        except ValueError:
            print("Invalid input : Please enter an integer!")
        except RangeError as e:
            print(f"Invalid input:{e}")

def get_url(prompt):
    """
    Prompt the user to enter the URL and re-prompt if the input is invalid.
    Finally, return the URL and the type of URL (twitch or youtube).
    args:
        prompt: str, Message to prompt the user
    """
    while True:
        url = input(prompt)
        # Check if the URL is from YouTube or Twitch. If it isn't, ask the user to re-enter.
        if is_valid_twitch_url(url):
            return url.split('&')[0], "twitch"
        elif is_valid_youtube_url(url):
            return url.split('&')[0], "youtube"
        else:
            print("Invalid input. Please re-enter a valid URL.")    

def is_valid_twitch_url(url):
    """
    Check if the input URL is a valid Twitch URL.
    Use regular expressions for validation.
    args: 
        url: str, User input URL
    """
    twitch_regex = re.compile(
        r'^(https?://)?(www\.)?(twitch\.tv)/[^?]+'
    )
    return bool(twitch_regex.match(url))

def is_valid_youtube_url(url):
    """
    Check if the input URL is a valid YouTube URL.
    Use regular expressions for validation.
    args: 
        url: str, User input URL
    """
    youtube_regex = re.compile(
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
    )
    return bool(youtube_regex.match(url))

def process_audio(short_voice_url, long_voice_url, start_time, end_time,short_url_source,long_url_source):
    """
    Segment detection using a "sliding window" approach:
    1) Download: short audio (trimmed from start_time to end_time) & long audio
    2) Generate short fingerprint
    3) Set segment_length, step_size => sliding window
    4) Segment the long audio [seg_start, seg_end], and calculate fingerprint
    5) fingerprint => compare => if determined to contain, find_offset => return time
    args:
        short_voice_url: str, Short audio URL
        long_voice_url: str, Long audio URL
        start_time: int, Short audio start time
        end_time: int, Short audio end time
        short_url_resource: str, Short audio source (twitch or youtube)
        long_url_resource: str, Long audio source (twitch or youtube)
    """
    # Record the start time of the process
    process_start_time=time.time()
    # Set the output path for the downloaded audio files
    download_file_output_path="./audio"
    try:
        # 1) Download the short audio and get its duration
        short_voice_path = download_sound_file(short_voice_url, download_file_output_path, 2,short_url_source ,start_time, end_time)
        short_voice_time = librosa.get_duration(path=short_voice_path)

        # Download the long audio and get its duration
        long_voice_time = Download(long_voice_url, download_file_output_path).get_time_info()
        long_voice_path = download_sound_file(long_voice_url, download_file_output_path, 1,long_url_source)

        # Load the file and get the audio array
        set_sr=16000
        short_audio_array, _ = librosa.load(short_voice_path, sr=set_sr)

        # Divide the original audio file into several large files, with each file being one hour long.
        split_duration = 3600
        spilt_segment_index_start=0 
        spilt_segment_index_end=(long_voice_time//split_duration)+1
        # The output files will be saved in the 'segment' folder, with each segment automatically numbered.
        LargeAudioSplitter.split_audio_ffmpeg(long_voice_path, split_duration, "./segment/segments")

        # The fingerprint recognizer only needs to be initialized once, so it should be placed outside the loop
        anlyzer = FingerprintIdentifier()          

        while spilt_segment_index_start<spilt_segment_index_end:

            spilt_long_voice_path=f"./segment/segments_{spilt_segment_index_start:03d}.m4a"

            long_audio_array, _ = librosa.load(spilt_long_voice_path, sr=set_sr)
            spilt_long_voice_time = librosa.get_duration(path=spilt_long_voice_path)

            # 2) Set sliding detection parameters
            overlap = int(short_voice_time*2)               # Overlap area
            if int(short_voice_time)>60:              
                segment_length = int(short_voice_time) * 6  # Segment length,The multiplier is tested and can be adjusted as needed
            else:
                segment_length = int(short_voice_time) *15  # Segment length,The multiplier is tested and can be adjusted as needed
            seg_index = 0                                   # Segment index
            current_start = 0                               # Current start time
           

            # 3) Start sliding detection

            while current_start < spilt_long_voice_time:
                # Set the query time range, ensuring it does not exceed the audio range
                # The current start time minus the overlap area represents the start point, 
                # and the current start time plus the segment length plus the overlap area gives the end point of the query time range
                seg_start = max(current_start-overlap, 0)
                seg_end   = min(current_start + segment_length + overlap, spilt_long_voice_time)
                if seg_start >= seg_end:
                    break

                print(f"Query time range : {time_format.sec_to_time(spilt_segment_index_start*split_duration+seg_start)} ~ {time_format.sec_to_time(spilt_segment_index_start*split_duration+seg_end)} ")

                # Apply sliding window processing to the segmented files generated earlier.
                spilt_long_audio_array=SlidingWindowProcessor.split_audio(long_audio_array, seg_start, seg_end, 16000)

                # 4) Compare to determine if the segment contains the short audio
                is_match, best_count = anlyzer.identify(spilt_long_audio_array, short_audio_array)
                print(f"Match : {is_match}, Best count : {best_count}")

                # 5) If a match is found, calculate the offset and return the time
                if is_match:
                    print("This fragment matches\n")
                    offset_in_seg = search_subclip.find_offset(spilt_long_audio_array, set_sr,short_audio_array, 10)
                    # Calculate the time relative to the entire audio
                    global_offset_sec = spilt_segment_index_start*split_duration+seg_start + offset_in_seg
                    result = time_format.sec_to_time(int(global_offset_sec))
                    print(f"Final corresponding time = {result}")
                    # Record the end time of the process
                    process_end_time=time.time()
                    # If the segment contains the short audio, exit the loop
                    # Return the processing time
                    return round(process_end_time-process_start_time,2)
                else:
                    print("This fragment does not match")

                # Update the start time and segment index
                current_start += segment_length
                seg_index += 1
            # If no match is found, output a message
            print("No matching segment found in this split file, loading the next segment...")
            # Delete the downloaded audio files
            
            spilt_segment_index_start+=1

        print("No matching segments found in the entire video")
        
    except Exception as e:
        print(f"An error occurred during processing:{str(e)}")
    finally:
        need_delete_dir = download_file_output_path
        if pathlib.Path(short_voice_path).exists():
            shutil.rmtree(need_delete_dir)
        need_delete_dir = "./segment"
        if pathlib.Path(need_delete_dir).exists():
            shutil.rmtree(need_delete_dir)
            
def filter_warning():
    """
    Filter out specific warnings to avoid cluttering the output.
    """
    specific_warning = "PySoundFile failed. Trying audioread instead."
    warnings.filterwarnings("ignore", message=specific_warning)
    warnings.filterwarnings(
        "ignore",
        message=".*librosa.core.audio.__audioread_load.*",
        category=FutureWarning
    )

def main_menu():
    """
    Main menu: Select the function to execute.
    """
    while True:
        print("Please select a function:")
        print("1. Find the position of the highlight video in the original video")
        print("2. Exit")
        choice = input("Please select : ")
        if choice == '1':
            print("Search function selected.\n")
            # Get the URL of the short and long audio files
            # The URL type is also returned (twitch or youtube)
            short_url,short_url_source = get_url("Please enter the highlight video URL  (YouTube or Twitch) : ")
            long_url,long_url_source = get_url("Please enter the original video (live stream) URL (YouTube or Twitch) : ")
            print("Highlight video source :",short_url_source)
            print("Original video source :",long_url_source)

            # Get the start and end times of the short audio file
            start, end = get_time_input()

            # Process the audio files
            process_time=process_audio(short_url, long_url, start, end,short_url_source,long_url_source)
            print(f"Processing time : {process_time} seconds")
            print("Query completed.\n")
        elif choice == '2':
            print("Goodbye!")
            break
        else:
            print("Invalid input, please try again.")


# Entry point
if __name__ == "__main__":
    filter_warning()
    main_menu()