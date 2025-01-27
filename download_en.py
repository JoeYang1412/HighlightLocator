import yt_dlp
import re
from tqdm import tqdm
from yt_dlp.utils import download_range_func
class Download:
    """
    A class to download audio files from YouTube using yt-dlp.
    Attributes:
        url (str): The URL of the YouTube video.
        output_path (str): The path to save the downloaded audio file.
        fixed_filename (str): The filename of the downloaded audio file without special characters.
    
    Methods:
        generate_filename(url): Generate a filename based on the URL.Supports YouTube and Twitch.
        remove_special_characters(filename): Remove special characters from the filename.The purpose is to use this name as the file name.
        download_youtube_m4a(): Download the m4a file from the YouTube video.
        download_youtube_section_m4a(start_time, end_time): Download a section of the audio file based on the start and end times.
        download_twitch_mp4(): Download the mp4 file from the Twitch video.
        get_time_info(): Get the duration of the YouTube video.
    """
    def __init__(self, url, output_path):
        # Initialize the Download class with the URL and output path.
        self.url = url
        self.output_path = output_path
        self.fixed_filename = self.generate_filename(url)
    
    def generate_filename(self, url):
        """
        Generate a filename based on the URL.
        Supports YouTube and Twitch.
        """
        if 'twitch.tv/videos/' in url:
            # Extract the ID from Twitch URLs
            raw_filename = url.split('videos/')[-1].split('?')[0]
        elif '=' in url:
            # Extract the ID from YouTube URLs
            raw_filename = url.split('=')[-1]
        else:
            # Default to the full URL if no specific rule matches
            raw_filename = url

        # Remove special characters
        return self.remove_special_characters(raw_filename)
    
    def remove_special_characters(self, filename):
        return re.sub(r'[^a-zA-Z0-9]', '', filename)
        
    
    def download_youtube_m4a(self):
        progress_bar = None

        # Progress hook for the progress bar
        # if the status is 'downloading', update the progress bar
        # if the status is 'finished', close the progress bar
        def progress_hook(d):
            nonlocal progress_bar
            if d['status'] == 'downloading':
                clean_percent_str = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', d['_percent_str'])
                percent = float(clean_percent_str.strip('%'))
                progress_bar.n = percent
                progress_bar.refresh()
            elif d['status'] == 'finished':
                progress_bar.n = 100
                progress_bar.close()
                print(f"Download completed : {d['filename']}")
        # Set the download options
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best[ext=m4a]',                       #downloading the best audio quality
            'progress_hooks': [progress_hook],                                  #progress bar
            'outtmpl': f'{self.output_path}/{self.fixed_filename}.%(ext)s',     #output path
            'postprocessors': [],                                               #no postprocessing
            'nooverwrites': False,                                              #overwrite existing files
            'quiet': True,                                                      #no logging                               
            'noprogress':True                                                   #no progress messages
        }

        # Display time information and show progress bar while downloading the file
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            
            info = ydl.extract_info(self.url, download=False)
            print("Audio length : "+str(info['duration'])+" seconds")
            progress_bar = tqdm(total=100, desc="Download progress", unit="%")
            ydl.download(self.url)
            filename = ydl.prepare_filename(info)
            # Return the file name, which refers to the path, for example: ./video_id.m4a
            return filename

    def download_youtube_section_m4a(self, start_time, end_time):
        # Download a section of the audio file based on the start and end times.
        def progress_hook(d):
            nonlocal progress_bar
            if d['status'] == 'downloading':
                clean_percent_str = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', d['_percent_str'])
                percent = float(clean_percent_str.strip('%'))
                progress_bar.n = percent
                progress_bar.refresh()
            elif d['status'] == 'finished':
                progress_bar.n = 100
                progress_bar.close()
                print(f"Download completed : {d['filename']}")
        # Set the download range based on the start and end times.
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/best',                                                #downloading the best audio quality                     
            'progress_hooks': [progress_hook],                                                  #progress bar                         
            'outtmpl': f'{self.output_path}/{self.fixed_filename+str(start_time)}.%(ext)s',     #output path
            'postprocessors': [],                                                               #no postprocessing
            'nooverwrites': False,                                                              #overwrite existing files
            'download_ranges': download_range_func(None, [(start_time, end_time)]),             #download range
            'force_keyframes_at_cuts': True,                                                    #force keyframes at cuts
            'quiet': True,                                                                      #no logging                               
            'noprogress':True                                                                   #no progress messages
        }
        # download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            
            info = ydl.extract_info(self.url, download=False)
            print("Audio length : "+str(end_time-start_time)+" seconds")
            progress_bar = tqdm(total=100, desc="Download progress", unit="%")
            ydl.download(self.url)
            filename = ydl.prepare_filename(info)
            # Return the file name, which refers to the path, for example: ./video_id.m4a
            return filename
        
    def download_twitch_mp4(self):
        progress_bar = None

        # Progress hook for the progress bar
        # if the status is 'downloading', update the progress bar
        # if the status is 'finished', close the progress bar
        def progress_hook(d):
            nonlocal progress_bar
            if d['status'] == 'downloading':
                clean_percent_str = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', d['_percent_str'])
                percent = float(clean_percent_str.strip('%'))
                progress_bar.n = percent
                progress_bar.refresh()
            elif d['status'] == 'finished':
                progress_bar.n = 100
                progress_bar.close()
                print(f"Download completed : {d['filename']}")
        # Set the download options
        ydl_opts = {
            'format': 'Audio_Only',                                             #downloading the best audio quality
            'outtmpl': f'{self.output_path}/{self.fixed_filename}.%(ext)s',     #output path
            'progress_hooks': [progress_hook],                                  #progress bar
            'postprocessors': [],                                               #no postprocessing
            'nooverwrites': False,                                              #overwrite existing files
            'quiet': True,                                                      #no logging                       
            'noprogress':True,                                                  #no progress messages                 
            'concurrent_fragment_downloads': 6 ,                                #number of concurrent fragment downloads
            'nopart': True,                                                     #do not use .part files  
                                                
        }

        # Display time information and show progress bar while downloading the file
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            
            info = ydl.extract_info(self.url, download=False)
            print("Audio length : "+str(info['duration'])+" seconds")
            progress_bar = tqdm(total=100, desc="Download progress", unit="%")
            ydl.download(self.url)
            filename = ydl.prepare_filename(info)
            # Return the file name, which refers to the path, for example: ./video_id.m4a
            return filename
           
    def get_time_info(self):
        # Get the duration of the YouTube
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.output_path}/{self.fixed_filename}.%(ext)s', 
            'postprocessors': [],  
            'nooverwrites': False,  
            'quiet': True,                                                                                 
            'noprogress':True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            
            info = ydl.extract_info(self.url, download=False)
            return info['duration'] 

