import librosa
import numpy as np
from collections import defaultdict

class FingerprintIdentifier:
    """
    This class implements a music fingerprint recognition algorithm, 
    similar to the Shazam music fingerprint recognition algorithm.
    For more details, refer to https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf, 
    which is a website of Columbia University.

    In this class, we divide the algorithm into two steps:
        1) Generate music fingerprints
        2) Identify music fingerprints

    args:
        sr: Audio sampling rate

        n_fft: FFT size for STFT, the window size for Short-Time Fourier Transform (STFT), 
        the larger the size, the higher the frequency resolution.

        hop_length: Hop size for STFT, the step size for STFT, controlling the time resolution.

        peak_threshold: dB threshold, the threshold for peak detection, 
        the energy in the spectrum must be higher than this value to be considered a valid peak.

        peak_neighborhood: 2D peak detection neighborhood size, the neighborhood size for detecting 2D peaks, 
        ensuring the peak is a local maximum.

        fan_value_frames: Number of peak frames to pair from the anchor, 
        the time range (in frames) for pairing each peak in fingerprint generation.

        min_count: Minimum number of matching points for the result, determining whether the audio files match.

    methods:
        detect_peaks_2d: 2D peak detection, detecting peaks in the 2D spectrum.
        build_fingerprint: Generate music fingerprints, pairing peaks to generate fingerprints.
        identify: Identify music fingerprints, determining whether two audio files match.

    For detailed instructions on this class, please refer to the fingerprint_manual.md or fingerprint_manual_en.md document.
    """

    def __init__(self,sr=16000,n_fft=2048,hop_length=512,peak_threshold=-30.0,peak_neighborhood=3, fan_value_frames=5,min_count=8):

        self.sr = sr
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.peak_threshold = peak_threshold
        self.peak_neighborhood = peak_neighborhood
        self.fan_value_frames = fan_value_frames
        self.min_count = min_count

    def detect_peaks_2d(self, S_db):
        """
        Perform 2D peak detection on a spectrogram.

        Args:
            S_db (ndarray): 2D spectrogram in decibels, shape (freq_len, time_len).

        Returns:
            List[Tuple[int, int, float]]: List of peaks as (freq, time, magnitude).
        """
        freq_len, time_len = S_db.shape
        peaks = []
        # Traverse the spectrogram to find peakss.
        for t in range(time_len):
            for f in range(freq_len):
                # Skip points below the peak threshold
                val = S_db[f, t]
                if val < self.peak_threshold:
                    continue
                # Define local neighborhood boundaries
                fmin = max(0, f - self.peak_neighborhood)
                fmax = min(freq_len, f + self.peak_neighborhood + 1)
                tmin = max(0, t - self.peak_neighborhood)
                tmax = min(time_len, t + self.peak_neighborhood + 1)
                # Extract the local neighborhood around the point
                local_patch = S_db[fmin:fmax, tmin:tmax]
                # Check if the point is a local maximum
                if val >= np.max(local_patch):
                    peaks.append((f, t, val))
        # Return the peaks list.
        return peaks

    def build_fingerprint(self, peaks):
        """
        Converts a list of peaks into a fingerprint structure.

        The fingerprint structure:
        - hashkey: (freqA, freqB, dt), representing two frequencies and the time difference.
        - value: A list of time offsets (timeA) where this hashkey occurs.

        Args:
            peaks (List[Tuple[int, int, float]]): List of peaks, each represented as (freq, time, magnitude).

        Returns:
            defaultdict: A dictionary-like structure where keys are hashkeys, and values are lists of time offsets.
        """
        # Sort peaks by time for consistent pair generation
        peaks_sorted = sorted(peaks, key=lambda x:x[1])  # x[1] is the time index
        n_peaks = len(peaks_sorted)

        # Dictionary to store the fingerprint (hashkey -> list of offsets)
        hash_dict = defaultdict(list)

        # Use two variables to traverse the entire peaks_sorted list
        # Initialize the second pointer
        j = 0
        for i in range(n_peaks):
            freqA, timeA, valA = peaks_sorted[i]
            # Ensure the second pointer starts after the first pointer
            if j < i+1:
                j = i+1

            # Match the current peak with subsequent peaks within the fan-out limit
            while j < n_peaks:
                freqB, timeB, valB = peaks_sorted[j]
                dt = timeB - timeA

                # If the time difference exceeds the fan-out limit, break the loop
                if dt > self.fan_value_frames:
                    break

                # Only consider valid pairs where dt > 0
                if dt> 0:
                    # Generate a hashkey using frequencies and time difference
                    hashkey = (freqA, freqB, dt)
                    # Store the time offset (timeA) for the hashkey
                    hash_dict[hashkey].append(timeA)
                # Move the second pointer forward
                j+=1

        # Return the fingerprint dictionary
        return hash_dict

    def identify(self, ref_audio, sample_audio):
        """
        Compare two audio files to determine if they match.

        Steps:
            1) Generate fingerprints for the reference audio.
            2) Detect peaks and compare fingerprints with the sample audio.
            3) Count matches and decide based on a minimum threshold.

        Args:
            ref_audio (ndarray): Reference audio signal.
            sample_audio (ndarray): Sample audio signal to compare.

        Returns:
            Tuple[bool, int]: (is_match, best_count), where:
                - is_match (bool): True if match is found, False otherwise.
                - best_count (int): Highest number of matching fingerprints.
        """

        # A) Generate fingerprints for the reference audio
        # Compute STFT and convert to dB
        D_ref = librosa.stft(ref_audio, n_fft=self.n_fft, hop_length=self.hop_length, center=False)
        S_ref = np.abs(D_ref)
        S_db_ref = librosa.amplitude_to_db(S_ref, ref=np.max)

        # Detect peaks and build fingerprints
        peaks_ref = self.detect_peaks_2d(S_db_ref)
        ref_fp = self.build_fingerprint(peaks_ref)

        # B) Process the sample audio
        # Compute STFT and convert to dB
        D_samp = librosa.stft(sample_audio, n_fft=self.n_fft, hop_length=self.hop_length, center=False)
        S_samp = np.abs(D_samp)
        S_db_samp = librosa.amplitude_to_db(S_samp, ref=np.max)

        # Detect peaks in the sample audio
        peaks_samp = self.detect_peaks_2d(S_db_samp)

        # Compare sample peaks against reference fingerprints
        offset_map = defaultdict(int)
        peaks_samp_sorted = sorted(peaks_samp, key=lambda x:x[1])
        n_samp_peaks= len(peaks_samp_sorted)
        
        # Compare peaks using a two-pointer approach
        j=0
        for i in range(n_samp_peaks):
            freqA, timeA, valA= peaks_samp_sorted[i]
            if j< i+1:
                j= i+1
            while j< n_samp_peaks:
                freqB, timeB, valB= peaks_samp_sorted[j]
                dt= timeB - timeA
                if dt> self.fan_value_frames:
                    break
                if dt> 0:
                    hashkey= (freqA, freqB, dt)
                    sample_offset= timeA
                    if hashkey in ref_fp:
                        ref_offsets = ref_fp[hashkey]
                        for ref_offset in ref_offsets:
                            offset_diff= ref_offset- sample_offset
                            offset_map[offset_diff]+=1
                j+=1

        # Determine the best match from the offset histogram
        if not offset_map:
            return (False,0)

        best_off, best_count= max(offset_map.items(), key=lambda x:x[1])
        is_match= (best_count>= self.min_count)
        return (is_match, best_count)
