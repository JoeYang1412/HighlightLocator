# HighlightLocator

## v1.0.1 Release Notes
- Added English interface
- Optimized display logic

For more details, please refer to the Release Notes.

## Features
This project helps locate highlight clips (short videos) within original live streams or videos (timestamps).  
Features include:  
1. Locate YouTube highlight clips within their original videos.  
2. Fast processing: A 5-hour live stream can be analyzed in about 5 minutes(depends on the computer's performance.).  
3. Works regardless of language, speaker clarity, or volume—accurately identifies and matches the highlight location in the original video.  
4. Simple to use: Provide the highlight video URL, the original video URL, and specify the start and end timestamps to locate the segment.  
5. Error-tolerant: Even with noise or sound effects in the highlight video, it can still locate the corresponding position in the original video.

## Environment
It is recommended to have 2–3 GB of available memory. While the system handles longer original videos, having sufficient memory ensures smooth operation.  
Reserve adequate disk space depending on the audio file length (at least 1 GB suggested).  

## Requirements
To execute the source code directly, Python must be installed, and the following dependencies are required:  

FFmpeg is essential. Without it, the program will not function correctly.  
You can download FFmpeg here:  
https://www.ffmpeg.org/download.html  

## Download and Usage
Several methods are available for downloading:

1. Download the source code:

    ```bash
    git clone https://github.com/JoeYang1412/HighlightLocator.git
    ```

    Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    Ensure FFmpeg is installed and added to your PATH:

    Download FFmpeg:
    https://www.ffmpeg.org/download.html

    Run the main program:

    ```bash
    python main_en.py
    ```

2. Download the executable:

    Two types of executables are available for download:

    - **Single-file executable**: Portable but slower to launch on the first run (20-30 seconds).  
    - **Folder-based executable**: Contains additional runtime dependencies, faster launch time (around 5 seconds), but includes a complete folder.

    For the single-file version, download `HighlightLocator_en.exe`. Ensure FFmpeg is installed before running.  
    For the folder-based version, download `HighlightLocator_dist_en.zip`, extract the folder, ensure FFmpeg is installed, navigate to `HighlightLocator_dist_en`, and run `HighlightLocator_en.exe`.

## Usage Notes
### Terminology
The following terms may appear interchangeably but refer to the same concepts:  
- **Highlight clip** = Short audio = The segment being queried.  
- **Original video** = Long audio = The entire original live stream or video.  
- **Segmented long audio** = Split files = The original video divided into multiple chunks.  

### Workflow
1. Download YouTube audio.  
2. Load the highlight clip.  
3. Split the original video into segments.  
4. Process each segment, using a sliding window to match the highlight clip.  
5. If no match is found in a segment, process the next segment until the highlight clip's location is identified.  
6. If a match is found, return the timestamp and inform the user. If not, notify the user that no match was found in the entire video.  
7. Return to the main menu.  

Refer to `fingerprint_manual.md` or `fingerprint_manual_en.md` for detailed information about audio fingerprinting.

### Usage Instructions
After running the program, follow the prompts:

```
Please select a function:
1. Find the position of the highlight video in the original video
2. Exit
Please select:1
Search Feature
Please enter the highlight video URL:example_url
Please enter the original video (live stream) URL:example_original_url

Please enter the start time for the highlight video in the format (minutes:seconds):
Start time (minutes, default is 0):
Start time (seconds, default is 0):

Please enter the end time for the highlight video in the format (minutes:seconds):
End time (minutes, default is 0):
End time (seconds, default is 10):
Video length:10 seconds
Download progress:: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 
Download complete:yt_dlp\example_url.m4a
Video length:6642 seconds
Download progress:: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 
Download complete:yt_dlp\example_original_url.m4a
The audio file has been successfully divided into 3600 second segments. Files are saved as: ./segment/segments_xxx.wav

Time range to query:00:00:00 ~ 00:02:10 
Match: False, Best count: 2
This paragraph does not match.
Time range to query:00:01:50 ~ 00:04:10
Match: False, Best count: 2
.
.
.
Process omitted
.
.
.
Time range to query:00:55:50 ~ 00:58:10
Match: True, Best count: 25
This segment matches.

Final mapped time = 00:56:56
Processing time:61.87 seconds
Search completed.
```

## Known Issues
1. Potential unknown errors.  
2. Matching accuracy requires further validation.  
3. While noise and effects are tolerated, the exact distortion threshold for accurate matching remains unverified.  

## Contributing
Found an issue or have suggestions? You can help by:  

- Reporting issues: Check the Issues page or create a new issue if not listed.  
- Submitting modifications: Fork the project, make improvements, and create a Pull Request.  
- Updating documentation: If you find errors or omissions, feel free to contribute fixes.  

Thank you for your contributions to improve this project!😊


## v1.0.1 更新資訊
- 新增英文介面
- 優化顯示邏輯

詳請請參閱 Release

## 功能及特色
本專案可以尋找精華影片(短影片)位於原始直播或影片中的位置(時間軸)
有以下特色
1. 可尋找 youtube 上的精華影片位於原影片中的位置
2. 快速定位（5 小時的直播影片約 5 分鐘可尋找完成，視電腦效能而定）
3. 不限語言，不限說話者的發聲準不準確，不限大小聲，皆可定位及辨識在原始影片中的位置
4. 操作簡單，僅需提供精華影片網址及原影片網址，並輸入你在精華影片中想查詢的時間點即可
5. 有一定的容錯性，即使精華影片中有雜音或是音效，也可定位在原始影片中的位置

## 環境：
建議保留約 2-3 GB 以上左右的可用記憶體，雖本系統對較長的原始影片有另做處理，但建議至少要有前述的空閒記憶體較妥當
保留適當硬碟空間，具體視音檔長度而定

## 需求：  
若你想直接使用原始碼來執行，你需要安裝 python 才可以執行

並依照下面要求安裝依賴項

FFmpeg 是必須的，若無此依賴，將無法順利運作

可從這裡下載（官網）：
https://www.ffmpeg.org/download.html


## 下載及使用
有幾種方法提供下載

1. 下載原始碼

    ```bash
    git clone https://github.com/JoeYang1412/HighlightLocator.git
    ```

    安裝依賴

    ``` bash
    pip install -r requirements.txt
    ```
    
    確保安裝 FFmpeg 並已添加至環境變數：

    下載 FFmpeg
    https://www.ffmpeg.org/download.html

    執行 main.py 即可使用

    ```
    python main.py
    ```

2. 下載執行檔
    
    有兩種類型執行檔可供下載

    一種是只有單個檔案，可攜性高，缺點是首次開啟時較慢，可能需要20-30秒
    另一種是包含其他執行環境的，exe 被包含在這個資料夾中，啟動速度較快，5秒左右可以開啟，缺點是它是一整個資料夾

    若要使用第一種，下載 `HighlightLocator.exe` 即可，下載完後，確認有安裝 `FFmpeg`，即可啟動
    若要使用第二種，下載 `HighlightLocator_dist.zip` 這個資料夾，下載完後，解壓縮，並確認你有安裝 `FFmpeg`，點進 `HighlightLocator_dist`，找到 `HighlightLocator.exe`，並執行即可

## 使用相關
名詞用語相關

以下說明可能不時會有不同用語出現，然而都是指同一個意思

在此先說明以避免誤解
* 精華影片=短音檔=短音檔中使用者要查詢的片段
* 原始影片=長音檔=整個原始影片=整個長音檔
* 長音檔分割=分割檔=將原始影片分割為多個大片段

### 運作邏輯及步驟
1. 下載 youtube 音訊
2. 讀進短音檔
3. 將長音檔分割成多段
4. 依序讀進長音檔分割，並以此當作參考音檔，以滑動視窗的方式，將短音檔與長音檔做匹配
5. 若該段無匹配結果，則讀進下一段分割檔，以此類推，直到找到短音檔在長音檔中的位置為止
6. 若有某段匹配到，則回傳時間，並告訴使用者短音訊在長音訊中的位置，否則通知使用者，在整個原始影片中查無此精華影片的位置
7. 回到主選單

有關音訊指紋辨識相關文件可參考 fingerprint_manual.md 或是 fingerprint_manual_en.md，有詳細說明

### 使用方法及步驟：
當你執行本程式後，應該會出現以下內容，依步驟操作即可
```
請選擇功能：
1. 查找精華影片在原始影片位置
2. 離開
請選擇：1
查詢功能
請輸入精華影片網址：example_url
請輸入原始影片(直播)網址：example_original_url
請依順序輸入在精華影片中要查詢的開始時間（分鐘:秒）：
開始時間（分鐘，預設為0）：
開始時間（秒，預設為0）：
請依順序輸入在精華影片中要查詢的結束時間（分鐘:秒）：
結束時間（分鐘，預設為0）：
結束時間（秒，預設為10）：
影音長度：10秒
下載進度：: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 
下載完成：yt_dlp\example_url.m4a
影音長度：16255秒
下載進度：: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 
下載完成：yt_dlp\example_original_url.m4a
音訊文件已成功分割，每段 3600 秒，輸出到: ./segment/segments_xxx.wav

查詢時間段(秒)：00:00:00 ~ 00:02:10 
Match: False, Best count: 1
.
.
.
過程省略
.
.
.
查詢時間段(秒)：03:15:50 ~ 03:18:10
Match: True, Best count: 79
此段落匹配
最終對應時間 = 03:17:44
處理時間：292.65秒
```

## 相關問題
目前有以下幾個問題
1. 可能有未知的錯誤
2. 準確度有待驗證
3. 雖說可以容忍雜音及特效，甚至可以容許部分片段出現別的段落，但是具體可以容忍多少，並未驗證過，不確定多少以內會是準確的

## 貢獻方式
發現問題或有建議？
您可以協助以下事項：

回報問題：查看 Issues 頁面，或如果尚未回報，請創建新的 Issue。

提交修改：Fork 專案、修改原始碼，並發起 Pull Request。

增修相關文檔：若發現文件錯誤或缺失，歡迎進行補充並提交。

感謝您的貢獻，讓這個專案變得更好！😊

