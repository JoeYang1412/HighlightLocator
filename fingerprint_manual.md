# FingerprintIdentifier 文件

## 概述
本文檔針對一個音訊指紋（Music Fingerprint）演算法類別，名為 FingerprintIdentifier。此演算法類似於知名的 Shazam 音樂檢索原理，在本類別中，大致包含下列步驟：

1. 頻譜峰值偵測（Sparse Constellation/Peaks）
2. 指紋產生（Combinatorial Hash / Landmark Hash）
3. 相似度檢測（Offset Histogram / Minimum match threshold）

此類別由 Python 與 librosa 完成，並適用於小型或片段式音訊比對。

## 緣起與引用
此演算法參考自

* Shazam 音樂指紋核心機制
Shazam 相關技術論文(Columbia University):
https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf

在該論文中，Shazam 演算法架構大致可分為：
1. Spectrogram peak detection
2. Combinatorial hashing (對 peak 做配對)
3. Searching & Scoring (依 offset histogram 找線索)

##  FingerprintIdentifier
簡介

FingerprintIdentifier 用於辨識兩段音訊是否「相同音訊(音樂)片段」，核心概念是：

1. 對音訊做短時傅立葉轉換（STFT）
2. 偵測 2D 頻譜峰值 → 形成星座圖 (constellation map)
3. 對峰值做 Landmark Hash → (freqA, freqB, Δt)
4. 比對 offset histogram → 取得最高對齊分數 → 若≥ min_count → 視為匹配


適用範圍：
* 小型或片段式音訊（數秒 ~ 數十秒）比對
* 較高雜訊耐受度
* 若要辨識大檔案時多半搭配分段 / streaming

## 初始化參數
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

參數:
* `sr` *(int)*：預設為 16000 Hz，音訊採樣率 (samples/秒)，做 STFT 時假設音訊為此取樣率。
* `n_fft` *(int)*：預設為 2048，STFT 所用之 FFT window size。影響頻率解析度，越大頻率解析度越高，但時間解析度較低。。
* `hop_length` *(int)*：預設為 512，STFT 的 hop size（兩幀之間的位移）。影響時間軸解析度(越小解析度越佳)
* `peak_threshold` *(float)*：預設為 -30.0，在 dB 頻譜中，低於此值的點不視為 peak。避免雜訊峰。
* `peak_neighborhood` *(int)*：預設為 3，2D peak detection 之鄰域大小。檢測局部最大時，以 freq±3、time±3 做局部搜尋。
* `fan_value_frames` *(int)*：單位為幀數，預設為 5，建立 Landmark Hash 時，每個 anchor peak 向後查看多少 frames 之內的 peak 搭配成 pair；對應約 5×hop_length 的時間門檻。
* `min_count` (int)*：預設為 8，在 offset histogram 中，若最大值≥此 → 視為成功匹配。數字越大 → false positive 越低，但漏判機率也上升。


## 各項函數
### detect_peaks_2d
``` python
def detect_peaks_2d(self, S_db):
```
描述:
偵測頻譜圖中的 2D 峰值，亦即該點的 dB 值不僅高於 `peak_threshold`，還需要是它所在之「鄰域 (freq±N, time±N)」裡的最大值。

參數:
* `S_db` *(ndarray)*：以 dB 為單位的 2D 頻譜圖，大小為 (頻率, 時間)。

返回值:
* `List[Tuple[int, int, float]]`：峰值列表，每個峰值的格式為 (頻率, 時間, dB 值)。

大致運作原理:
1. 遍歷頻譜圖的每個點 `(f, t)`。
2. 確定該點的鄰域範圍（根據 `peak_neighborhood`）。
3. 檢查該點是否為局部極大值，且超過 `peak_threshold`。
4. 若符合條件，將該點加入峰值列表。

範例：
[
    [25, 30, 20],
    [22, 35, 28],
    [18, 22, 30]
]
例如在此矩陣中，35 為局部最大值，它的值比周圍的點都高

程式區塊說明
``` python
freq_len, time_len = S_db.shape
peaks = []
```
* S_db.shape: 獲取頻譜圖的大小，freq_len 為頻率維度的長度，time_len 為時間維度的長度。
* peaks: 用於存儲所有偵測到的峰值。

``` python
for t in range(time_len):
    for f in range(freq_len):
        val = S_db[f, t]
        if val < self.peak_threshold:
            continue

```
* 外層和內層雙層迴圈，遍歷每個頻譜點 `(f, t)`。
* `val = S_db[f, t]`: 提取該點的能量值（以 dB 為單位）。
* `if val < self.peak_threshold`: 濾除低於閾值的點，加速計算。

``` python
fmin = max(0, f - self.peak_neighborhood)
fmax = min(freq_len, f + self.peak_neighborhood + 1)
tmin = max(0, t - self.peak_neighborhood)
tmax = min(time_len, t + self.peak_neighborhood + 1)
local_patch = S_db[fmin:fmax, tmin:tmax]
```
* 設置局部範圍，確保在頻率和時間方向上不越界。
* `local_patch`: 提取 `(f, t)` 周圍的能量值子矩陣。

``` python
if val >= np.max(local_patch):
    peaks.append((f, t, val))
```
* 判斷該點是否是 `local_patch` 中的局部極大值。
* 如果是，將 `(f, t, val)` 加入 `peaks` 列表。

### build_fingerprint

``` python
def build_fingerprint(self, peaks):
```
描述:
將偵測到的峰值生成指紋結構，指紋用於快速匹配。

參數:
* `peaks` *(List[Tuple[int, int, float]])*：由 detect_peaks_2d 偵測到的峰值列表。

返回值:
* defaultdict：指紋結構，鍵為 (freqA, freqB, dt)，值為時間偏移量列表 [timeA1, timeA2, ...]。

運作原理:
1. 將峰值列表按時間排序，保證指紋生成順序一致。
2. 使用兩個變數（`i` 和 `j`）將每個峰值與其後的峰值進行配對，時間差需在 `fan_value_frames` 範圍內。
3. 對合法配對生成 `hashkey`，記錄其時間偏移量 `timeA`。


程式區塊說明
``` python
peaks_sorted = sorted(peaks, key=lambda x: x[1])
n_peaks = len(peaks_sorted)
hash_dict = defaultdict(list)
```
* `peaks_sorted`: 按時間對峰值進行排序，保證處理順序一致。
* `hash_dict`: 使用字典存儲指紋結構，鍵為 hashkey，值為時間偏移量列表。

``` python
for i in range(n_peaks):
    freqA, timeA, valA = peaks_sorted[i]
    if j < i+1:
        j = i+1
```
* 外層迴圈遍歷每個峰值 `(freqA, timeA)` 作為錨點。
* `j = i+1`: 確保內層迴圈只配對後面的峰值，避免重複配對。

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
* 配對範圍限制: 只有時間差 `dt` 在 `fan_value_frames` 範圍內才配對，超出則跳出內層迴圈。
* 生成指紋鍵: `(freqA, freqB, dt)` 作為唯一的 `hashkey`。
* 存儲偏移量: 每個 `hashkey` 都與錨點的時間偏移 `timeA` 關聯。


### identify
``` python
def identify(self, ref_audio, sample_audio):
```
描述:
比較參考音檔與樣本音檔，通過計算匹配的偏移數量，判斷是否匹配。

參數:
* `ref_audio` *(ndarray)*：參考音檔的波形數據。
* `sample_audio` *(ndarray)*：樣本音檔的波形數據。

返回值:
* Tuple[bool, int]：包含以下兩部分：
  * `is_match` *(bool)*：若匹配則為 True，否則為 False。
  * `best_count` *(int)*：最高匹配數量。

運作原理:

1. 參考音檔處理：

    * 計算 STFT，轉換為 dB 頻譜圖。
    * 偵測峰值並生成指紋。

2. 樣本音檔處理：

    * 計算 STFT，轉換為 dB 頻譜圖。
    * 偵測峰值並生成偏移直方圖。

3. 匹配計算：

    * 比較樣本峰值和參考指紋的 `hashkey`。
    * 根據偏移直方圖的最高匹配數量判斷是否匹配。

程式區塊說明
第一步：處理長音檔(參考音檔)
``` python
D_ref = librosa.stft(ref_audio, n_fft=self.n_fft, hop_length=self.hop_length, center=False)
S_ref = np.abs(D_ref)
S_db_ref = librosa.amplitude_to_db(S_ref, ref=np.max)
```
1. `librosa.stft`:
* 對參考音檔執行短時傅里葉變換（STFT），將時間域信號轉換為頻譜圖。
* 參數：
    * n_fft：FFT 點數，影響頻率分辨率。
    * hop_length：幀間距，影響時間分辨率。
    * center=False：禁止對信號進行填充，以防止中心化導致數據不連續。
* 結果：D_ref 是一個複數矩陣，表示頻率和時間的頻譜。

2. `np.abs`:

* 計算頻譜的幅度（取模），去掉相位信息。
* 結果：S_ref 是幅度矩陣。

3. `librosa.amplitude_to_db`:

* 將幅度轉換為分貝（dB），以對數尺度表示信號強度。
* 結果：`S_db_ref` 是以 dB 為單位的頻譜圖。

``` python
peaks_ref = self.detect_peaks_2d(S_db_ref)
ref_fp = self.build_fingerprint(peaks_ref)
```
第二步：處理短音檔(樣本音檔)
``` python
D_samp = librosa.stft(sample_audio, n_fft=self.n_fft, hop_length=self.hop_length, center=False)
S_samp = np.abs(D_samp)
S_db_samp = librosa.amplitude_to_db(S_samp, ref=np.max)
```
* 與參考音檔處理步驟相同，將樣本音檔轉換為 dB 頻譜圖。

``` python
peaks_samp = self.detect_peaks_2d(S_db_samp)
```
* 偵測樣本音檔的峰值，得到峰值列表。

```
offset_map = defaultdict(int)
```
* 初始化偏移直方圖，用於記錄偏移量及其匹配數量。

第三步：偏移直方圖計算
``` python
peaks_samp_sorted = sorted(peaks_samp, key=lambda x: x[1])
n_samp_peaks = len(peaks_samp_sorted)
```
* 將樣本峰值列表按時間排序，確保處理順序一致。

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
1. 使用兩個變數（`i` 和 `j`）配對樣本峰值。
2. 根據 `fan_value_frames` 限制配對的時間範圍。
3. 若樣本的 `hashkey` 與參考指紋中的 `hashkey` 匹配，計算偏移量 `offset_diff` 並記錄在直方圖中。

第四步：判斷匹配結果
``` python
if not offset_map:
    return (False, 0)
```
* 若偏移直方圖為空，表示沒有找到匹配，直接返回。

``` python
best_off, best_count = max(offset_map.items(), key=lambda x: x[1])
is_match = (best_count >= self.min_count)
return (is_match, best_count)
```
1. 找到偏移直方圖中最大峰值對應的匹配數量 `best_count`。
2. 判斷 `best_count` 是否超過門檻 `min_count`，確定是否匹配。