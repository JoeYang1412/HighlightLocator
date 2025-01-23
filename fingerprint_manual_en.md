# FingerprintIdentifier Document

## Overview
This document is about an audio fingerprint (Music Fingerprint) algorithm class named FingerprintIdentifier. This algorithm is similar to the well-known Shazam music retrieval principle. The class roughly includes the following steps:

1. Spectrogram peak detection (Sparse Constellation/Peaks)
2. Fingerprint generation (Combinatorial Hash / Landmark Hash)
3. Similarity detection (Offset Histogram / Minimum match threshold)

This class is implemented in Python using librosa and is suitable for small or fragmentary audio matching.

## Origin and References
This algorithm is referenced from:

* Shazam music fingerprint core mechanism
Shazam related technical paper (Columbia University):
https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf

In the paper, the Shazam algorithm architecture can be roughly divided into:
1. Spectrogram peak detection
2. Combinatorial hashing (pairing peaks)
3. Searching & Scoring (finding clues based on offset histogram)

## FingerprintIdentifier
Introduction

FingerprintIdentifier is used to identify whether two audio segments are the "same audio (music) fragment". The core concept is:

1. Perform Short-Time Fourier Transform (STFT) on the audio
2. Detect 2D spectrogram peaks → form a constellation map
3. Generate Landmark Hash from peaks → (freqA, freqB, Δt)
4. Compare offset histogram → get the highest alignment score → if ≥ min_count → considered a match

Applicable scope:
* Small or fragmentary audio (a few seconds to tens of seconds) matching
* Higher noise tolerance
* For large files, it is often used with segmentation/streaming

## Initialization Parameters
``` python
def __init__(self,
             sr=16000,
             n_fft=2048,
             hop_length=512,
             peak_threshold=-30.0,
             peak_neighborhood=3,
             fan_value_frames=5,
             min_count=8):
```

Parameters:
* `sr` *(int)*: Default is 16000 Hz, the audio sampling rate (samples/second), assuming the audio is at this sampling rate when performing STFT.
* `n_fft` *(int)*: Default is 2048, the FFT window size used for STFT. It affects the frequency resolution; the larger it is, the higher the frequency resolution, but the lower the time resolution.
* `hop_length` *(int)*: Default is 512, the hop size for STFT (shift between two frames). It affects the time axis resolution (the smaller, the better the resolution).
* `peak_threshold` *(float)*: Default is -30.0, in the dB spectrum, points below this value are not considered peaks. It avoids noise peaks.
* `peak_neighborhood` *(int)*: Default is 3, the neighborhood size for 2D peak detection. When detecting local maxima, it searches locally with freq±3 and time±3.
* `fan_value_frames` *(int)*: Unit is frames, default is 5, when creating Landmark Hash, each anchor peak looks back at peaks within how many frames to form pairs; corresponding to about 5×hop_length time threshold.
* `min_count` (int)*: Default is 8, in the offset histogram, if the maximum value ≥ this → considered a successful match. The larger the number → the lower the false positive rate, but the higher the miss rate.

## Methods
### detect_peaks_2d
``` python
def detect_peaks_2d(self, S_db):
```
Description:
Detect 2D peaks in the spectrogram, i.e., the dB value of the point is not only higher than `peak_threshold`, but also needs to be the maximum value in its "neighborhood (freq±N, time±N)".

Parameters:
* `S_db` *(ndarray)*: 2D spectrogram in dB, size (frequency, time).

Return value:
* `List[Tuple[int, int, float]]`: List of peaks, each peak is in the format (frequency, time, dB value).

General operation principle:
1. Traverse each point `(f, t)` in the spectrogram.
2. Determine the neighborhood range of the point (based on `peak_neighborhood`).
3. Check if the point is a local maximum and exceeds `peak_threshold`.
4. If it meets the conditions, add the point to the peak list.

Example:
[
    [25, 30, 20],
    [22, 35, 28],
    [18, 22, 30]
]
For example, in this matrix, 35 is the local maximum value, its value is higher than the surrounding points.

Code block explanation
``` python
freq_len, time_len = S_db.shape
peaks = []
```
* S_db.shape: Get the size of the spectrogram, freq_len is the length of the frequency dimension, and time_len is the length of the time dimension.
* peaks: Used to store all detected peaks.

``` python
for t in range(time_len):
    for f in range(freq_len):
        val = S_db[f, t]
        if val < self.peak_threshold:
            continue
```
* Outer and inner double loops, traverse each spectrogram point `(f, t)`.
* `val = S_db[f, t]`: Extract the energy value of the point (in dB).
* `if val < self.peak_threshold`: Filter out points below the threshold to speed up the calculation.

``` python
fmin = max(0, f - self.peak_neighborhood)
fmax = min(freq_len, f + self.peak_neighborhood + 1)
tmin = max(0, t - self.peak_neighborhood)
tmax = min(time_len, t + self.peak_neighborhood + 1)
local_patch = S_db[fmin:fmax, tmin:tmax]
```
* Set the local range to ensure no out-of-bounds in the frequency and time directions.
* `local_patch`: Extract the energy value submatrix around `(f, t)`.

``` python
if val >= np.max(local_patch):
    peaks.append((f, t, val))
```
* Determine if the point is the local maximum in `local_patch`.
* If so, add `(f, t, val)` to the `peaks` list.

### build_fingerprint

``` python
def build_fingerprint(self, peaks):
```
Description:
Generate a fingerprint structure from the detected peaks, which is used for quick matching.

Parameters:
* `peaks` *(List[Tuple[int, int, float]])*: List of peaks detected by detect_peaks_2d.

Return value:
* defaultdict: Fingerprint structure, the key is (freqA, freqB, dt), and the value is the list of time offsets [timeA1, timeA2, ...].

Operation principle:
1. Sort the peak list by time to ensure consistent fingerprint generation order.
2. Use two variables (`i` and `j`) to pair each peak with subsequent peaks, with the time difference within the `fan_value_frames` range.
3. Generate `hashkey` for valid pairs and record their time offset `timeA`.

Code block explanation
``` python
peaks_sorted = sorted(peaks, key=lambda x: x[1])
n_peaks = len(peaks_sorted)
hash_dict = defaultdict(list)
```
* `peaks_sorted`: Sort peaks by time to ensure consistent processing order.
* `hash_dict`: Use a dictionary to store the fingerprint structure, the key is hashkey, and the value is the list of time offsets.

``` python
for i in range(n_peaks):
    freqA, timeA, valA = peaks_sorted[i]
    if j < i+1:
        j = i+1
```
* Outer loop traverses each peak `(freqA, timeA)` as the anchor point.
* `j = i+1`: Ensure the inner loop only pairs with subsequent peaks to avoid duplicate pairing.

``` python
while j < n_peaks:
    freqB, timeB, valB = peaks_sorted[j]
    dt = timeB - timeA
    if dt > self.fan_value_frames:
        break
    if dt > 0:
        hashkey = (freqA, freqB, dt)
        hash_dict[hashkey].append(timeA)
    j += 1
```
* Pairing range limit: Only pair if the time difference `dt` is within the `fan_value_frames` range, otherwise break the inner loop.
* Generate fingerprint key: `(freqA, freqB, dt)` as the unique `hashkey`.
* Store offset: Each `hashkey` is associated with the time offset `timeA`.

### identify
``` python
def identify(self, ref_audio, sample_audio):
```
Description:
Compare the reference audio and sample audio to determine if they match by calculating the number of matching offsets.

Parameters:
* `ref_audio` *(ndarray)*: Waveform data of the reference audio.
* `sample_audio` *(ndarray)*: Waveform data of the sample audio.

Return value:
* Tuple[bool, int]: Contains the following two parts:
  * `is_match` *(bool)*: True if matched, otherwise False.
  * `best_count` *(int)*: The highest number of matches.

Operation principle:

1. Reference audio processing:

    * Calculate STFT and convert to dB spectrogram.
    * Detect peaks and generate fingerprints.

2. Sample audio processing:

    * Calculate STFT and convert to dB spectrogram.
    * Detect peaks and generate offset histogram.

3. Matching calculation:

    * Compare sample peaks with reference fingerprints' `hashkey`.
    * Determine if they match based on the highest number of matches in the offset histogram.

Code block explanation
First step: Process long audio (reference audio)
``` python
D_ref = librosa.stft(ref_audio, n_fft=self.n_fft, hop_length=self.hop_length, center=False)
S_ref = np.abs(D_ref)
S_db_ref = librosa.amplitude_to_db(S_ref, ref=np.max)
```
1. `librosa.stft`:
* Perform Short-Time Fourier Transform (STFT) on the reference audio to convert the time-domain signal into a spectrogram.
* Parameters:
    * n_fft: Number of FFT points, affecting frequency resolution.
    * hop_length: Frame shift, affecting time resolution.
    * center=False: Disable padding to prevent data discontinuity caused by centering.
* Result: D_ref is a complex matrix representing the spectrogram in frequency and time.

2. `np.abs`:

* Calculate the magnitude of the spectrogram (take the modulus), removing phase information.
* Result: S_ref is the magnitude matrix.

3. `librosa.amplitude_to_db`:

* Convert the magnitude to decibels (dB) to represent signal strength on a logarithmic scale.
* Result: `S_db_ref` is the spectrogram in dB.

``` python
peaks_ref = self.detect_peaks_2d(S_db_ref)
ref_fp = self.build_fingerprint(peaks_ref)
```
Second step: Process short audio (sample audio)
``` python
D_samp = librosa.stft(sample_audio, n_fft=self.n_fft, hop_length=self.hop_length, center=False)
S_samp = np.abs(D_samp)
S_db_samp = librosa.amplitude_to_db(S_samp, ref=np.max)
```
* Same steps as reference audio processing, converting sample audio to dB spectrogram.

``` python
peaks_samp = self.detect_peaks_2d(S_db_samp)
```
* Detect peaks in the sample audio to get the peak list.

```
offset_map = defaultdict(int)
```
* Initialize the offset histogram to record offsets and their match counts.

Third step: Offset histogram calculation
``` python
peaks_samp_sorted = sorted(peaks_samp, key=lambda x: x[1])
n_samp_peaks = len(peaks_samp_sorted)
```
* Sort the sample peak list by time to ensure consistent processing order.

``` python
for i in range(n_samp_peaks):
    freqA, timeA, valA = peaks_samp_sorted[i]
    if j < i + 1:
        j = i + 1
    while j < n_samp_peaks:
        freqB, timeB, valB = peaks_samp_sorted[j]
        dt = timeB - timeA
        if dt > self.fan_value_frames:
            break
        if dt > 0:
            hashkey = (freqA, freqB, dt)
            sample_offset = timeA
            if hashkey in ref_fp:
                ref_offsets = ref_fp[hashkey]
                for ref_offset in ref_offsets:
                    offset_diff = ref_offset - sample_offset
                    offset_map[offset_diff] += 1
        j += 1
```
1. Use two variables (`i` and `j`) to pair sample peaks.
2. Limit the pairing range based on `fan_value_frames`.
3. If the sample's `hashkey` matches the reference fingerprint's `hashkey`, calculate the offset `offset_diff` and record it in the histogram.

Fourth step: Determine matching result
``` python
if not offset_map:
    return (False, 0)
```
* If the offset histogram is empty, it means no match was found, return directly.

``` python
best_off, best_count = max(offset_map.items(), key=lambda x: x[1])
is_match = (best_count >= self.min_count)
return (is_match, best_count)
```
1. Find the match count corresponding to the maximum peak in the offset histogram `best_count`.
2. Determine if `best_count` exceeds the threshold `min_count` to confirm if it matches.
