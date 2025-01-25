class SlidingWindowProcessor:
    """
    Split audio file
    methods:
        split_audio(audio_array,segment_start, segment_end, sr): Split the audio file based on the start and end times.
    """
    
    def split_audio(audio_array,segment_start, segment_end, sr):
        """
        args:
            audio_array: Audio array
            segment_start: Start time
            segment_end: End time
            sr: Sampling rate
        """
        start_idx = int(segment_start * sr)
        end_idx = int(segment_end * sr)
        segment_audio = audio_array[start_idx:end_idx]
        return segment_audio