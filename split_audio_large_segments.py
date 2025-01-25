import subprocess
import os
class LargeAudioSplitter:
    def split_audio_ffmpeg(input_file, segment_duration, output_prefix):
        """
        Split the audio file using FFmpeg and save the segments.

        Parameters:
            input_file (str): Path to the input audio file.
            segment_duration (int): Duration of each segment (in seconds).
            output_prefix (str): Prefix path for the output segment files.

        Returns:
            None
        """
        output_dir = os.path.dirname(output_prefix)
    
        # Create the output directory if it does not exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        cmd = [
            "ffmpeg",
            "-loglevel", "quiet",
            "-i", input_file,
            "-f", "segment",
            "-segment_time", str(segment_duration),
            "-c", "copy",
            f"{output_prefix}_%03d.m4a"
        ]
        subprocess.run(cmd, check=True)
        print(f"音訊文件已成功分割，每段 {segment_duration} 秒，輸出到: {output_prefix}_xxx.wav\n")

