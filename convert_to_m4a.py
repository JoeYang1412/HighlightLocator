import subprocess
import os

class Mp4ToM4aConverter:
    def convert_mp4_to_m4a(input_file, output_file=None):
    
        if output_file is None:
            # Change the extension to .m4a
            output_file = os.path.splitext(input_file)[0] + ".m4a"

        try:
            # FFmpeg command
            command = [
                "ffmpeg",
                "-loglevel", "quiet",  # No logging
                "-i", input_file,      # Input file
                "-vn",                 # Exclude video
                "-c:a", "copy",        # Copy audio without re-encoding
                output_file            # Output file
            ]
            
            # Run the command
            subprocess.run(command, check=True)
            print(f"轉換完成: {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"轉換失敗: {e}")
        except FileNotFoundError:
            print("找不到 FFmpeg 命令。請確保已安裝 FFmpeg。")

