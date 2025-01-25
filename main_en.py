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

#user defined exception
class RangeError(Exception):
    pass

def download_sound_file(url, output_path, process_type, start_time=None, end_time=None):
    """
    Process download and conversion based on process_type
    args:  
    
        url: str, YouTube URL
        output_path: str, Output path
        process_type: int, Processing type; 1: Download full audio, 2: Download partial audio
        start_time: int, Start time
        end_time: int, End time
    """
    downloader = Download(url, output_path)
    if process_type == 1:               # Download the full audio
        return downloader.download_m4a()
    elif process_type == 2:             # Download a section of the audio
        return downloader.download_section_m4a(start_time, end_time)
    else:
        raise ValueError("process type needs to be 1 or 2")
    
def get_time_input():
    """
    Prompt the user to enter the start and end times, and re-prompt if the input is invalid.
    Finally, return the start and end times in seconds.
    """
    while True:
        try:
            print("\nPlease enter the start time for the highlight video in the format (minutes:seconds):")
            start_minute = get_valid_number("Start time (minutes, default is 0):", default=0, min_value=0, max_value=60)
            start_seconds = get_valid_number("Start time (seconds, default is 0):", default=0,min_value=0,max_value=60)

            print("\nPlease enter the end time for the highlight video in the format (minutes:seconds):")
            end_minute = get_valid_number("End time (minutes, default is 0):", default=0, min_value=0, max_value=60)
            end_seconds = get_valid_number("End time (seconds, default is 10):", default=10,min_value=0,max_value=60)
            
            start_hour=end_hour=0

            start = time_format.time_to_sec(start_hour, start_minute, start_seconds)
            end = time_format.time_to_sec(end_hour, end_minute, end_seconds)

            if start < 0 or end <= start:
                raise ValueError("Please ensure that the start time is earlier than the end time.")

            return start, end  

        except ValueError as e:
            print(f"Input error:{e}")
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
                raise RangeError(f"The input must be greater than {min_value} or less than {max_value}！")
            return value
        
        except ValueError:
            print("Invalid input: Please enter an integer!")
        except RangeError as e:
            print(f"Invalid input:{e}")

def get_youtube_url(prompt):
    """
    Prompt the user to enter a YouTube URL, and re-prompt if the input is invalid.
    args:
        prompt: str, Message to prompt
    """
    while True:
        url = input(prompt)
        if is_valid_youtube_url(url):
            return url.split('&')[0]
        else:
            print("Invalid input. Please double-check and enter a valid YouTube URL.")


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


def process_audio(short_voice_url, long_voice_url, start_time, end_time):
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
    """
    # Record the start time of the process
    process_start_time=time.time()
    try:
        # 1) Download the short audio and get its duration
        short_voice_path = download_sound_file(short_voice_url, "./yt_dlp", 2, start_time, end_time)
        short_voice_time = librosa.get_duration(path=short_voice_path)

        # Download the long audio and get its duration
        long_voice_time = Download(long_voice_url, "./yt_dlp").get_time_info()
        long_voice_path = download_sound_file(long_voice_url, "./yt_dlp", 1)

        # Load the file and get the audio array
        set_sr=16000
        short_audio_array, _ = librosa.load(short_voice_path, sr=set_sr)

        split_duration = 3600
        spilt_segment_index_start=0 
        spilt_segment_index_end=(long_voice_time//split_duration)+1
        

        LargeAudioSplitter.split_audio_ffmpeg(long_voice_path, split_duration, "./segment/segments")


        while spilt_segment_index_start<spilt_segment_index_end:

            spilt_long_voice_path=f"./segment/segments_{spilt_segment_index_start:03d}.m4a"

            long_audio_array, _ = librosa.load(spilt_long_voice_path, sr=set_sr)
            spilt_long_voice_time = librosa.get_duration(path=spilt_long_voice_path)

            # 2) Set sliding detection parameters
            overlap = int(short_voice_time)                 # Overlap area
            if int(short_voice_time)>60:              
                segment_length = int(short_voice_time) * 6  # Segment length,The multiplier is tested and can be adjusted as needed
            else:
                segment_length = int(short_voice_time) *12  # Segment length,The multiplier is tested and can be adjusted as needed
            seg_index = 0                                   # Segment index
            current_start = 0                               # Current start time
            anlyzer = FingerprintIdentifier()               # Initialize fingerprint recognizer  

            # 3) Start sliding detection

            while current_start < spilt_long_voice_time:
                # Set the query time range, ensuring it does not exceed the audio range
                # The current start time minus the overlap area represents the start point, 
                # and the current start time plus the segment length plus the overlap area gives the end point of the query time range
                seg_start = max(current_start-overlap, 0)
                seg_end   = min(current_start + segment_length + overlap, spilt_long_voice_time)
                if seg_start >= seg_end:
                    break

                print(f"Time range to query:{time_format.sec_to_time(spilt_segment_index_start*split_duration+seg_start)} ~ {time_format.sec_to_time(spilt_segment_index_start*split_duration+seg_end)} ")

                # Split audio
                spilt_long_audio_array=SlidingWindowProcessor.split_audio(long_audio_array, seg_start, seg_end, 16000)

                # 4) Compare to determine if the segment contains the short audio
                is_match, best_count = anlyzer.identify(spilt_long_audio_array, short_audio_array)
                print(f"Match: {is_match}, Best count: {best_count}")

                # 5) If a match is found, calculate the offset and return the time
                if is_match:
                    print("This segment matches.\n")
                    offset_in_seg = search_subclip.find_offset(spilt_long_audio_array, set_sr,short_audio_array, 10)
                    # Calculate the time relative to the entire audio
                    global_offset_sec = spilt_segment_index_start*split_duration+seg_start + offset_in_seg
                    result = time_format.sec_to_time(int(global_offset_sec))
                    print(f"Final mapped time = {result}")
                    # Record the end time of the process
                    process_end_time=time.time()
                    # If the segment contains the short audio, exit the loop
                    # Return the processing time
                    return round(process_end_time-process_start_time,2)
                else:
                    print("This paragraph does not match.")

                # Update the start time and segment index
                current_start += segment_length
                seg_index += 1
            # If no match is found, output a message
            print("No matching segment found in this split file, loading the next segment...")
            # Delete the downloaded audio files
            
            spilt_segment_index_start+=1

        print("No matching segments found in the entire video.")
        
    except Exception as e:
        print(f"An error occurred while processing the request:{str(e)}")
    finally:
        need_delete_dir = "./yt_dlp"
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
        choice = input("Please select:")
        if choice == '1':
            print("Search Feature")
            # Get the short and long audio URLs and the start and end times
            short_url = get_youtube_url("Please enter the highlight video URL:")
            long_url = get_youtube_url("Please enter the original video (live stream) URL:")
            start, end = get_time_input()
            process_time=process_audio(short_url, long_url, start, end)
            print(f"Processing time:{process_time} seconds")
            print("Search completed.\n")
        elif choice == '2':
            print("Goodbye!")
            break
        else:
            print("Invalid input, please try again.")


# Entry point
if __name__ == "__main__":
    filter_warning()
    main_menu()