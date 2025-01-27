# HighlightLocator

## v1.1.0 Release Notes
- Highlight and original video sources now support Twitch.
- Supports both Chinese and English interfaces.  

For more details, please refer to the Release.

## Features
This project allows you to locate the position (timeline) of a highlight video (short video) within an original live stream or video.  
Key features include:  
1. Locate the position of highlight videos from YouTube and Twitch within the original video.
2. Fast processing (approximately 5 minutes to search a 5-hour live stream, depending on your computer's performance).
3. Works with any language, speaker clarity, or volume levels—accurately identifying and locating the highlight position in the original video.
4. Simple operation—just provide the URLs of the highlight and original videos, and input the specific time range in the highlight video you wish to query.
5. High fault tolerance—even if there is noise or sound effects in the highlight video, the system can still locate its position in the original video.

## Environment
- Ensure at least 2–3 GB of available memory. Although the system has been optimized for handling longer original videos, having this amount of free memory is recommended.
- Reserve sufficient disk space, depending on the length of the audio file.

## Requirements
If you wish to execute the source code directly, you need to install Python.  

Install dependencies as specified below.  

Additionally, whether you are running the source code or the executable, FFmpeg is essential. Without this dependency, the system will not function properly.

You can download FFmpeg here (official website):  
https://www.ffmpeg.org/download.html

## Download and Usage
There are several ways to download this project.

1. Download the source code

    ```bash
    git clone https://github.com/JoeYang1412/HighlightLocator.git
    ```

    Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```
    
    Ensure FFmpeg is installed and added to your environment variables:  

    Download FFmpeg:  
    https://www.ffmpeg.org/download.html

    Run `main_en.py` to use the application:

    ```bash
    python main_en.py
    ```

2. Download executable files
    
    Two types of executables are available for download:

    - A single-file executable with high portability. Its downside is slower initial startup, taking around 20–30 seconds.
    - A bundled version with additional runtime files. This starts faster (around 5 seconds) but comes as an entire folder.

    To use the first type, download `HighlightLocator_en.exe`. After downloading, ensure FFmpeg is installed, then launch the executable.  
    To use the second type, download the `HighlightLocator_dist_en.zip` folder. After downloading, extract it, ensure FFmpeg is installed, navigate to `HighlightLocator_dist_en`, locate `HighlightLocator_en.exe`, and run it.

## Terminology

The following terms might appear interchangeably but refer to the same concepts. This explanation is provided to avoid confusion:  
* Highlight video = short audio = the segment in the short audio the user wants to query.
* Original video = long audio = the full original video = the entire long audio.
* Long audio splitting = segmenting = dividing the original video into multiple large parts.

### Workflow and Steps
1. Download audio from YouTube or Twitch.
2. Load the short audio file.
3. Split the long audio file into multiple segments.
4. Sequentially load each segment of the long audio as a reference file. Using a sliding window approach, match the short audio with the long audio.
5. If no match is found in the current segment, load the next segment and continue until the position of the short audio in the long audio is located.
6. If a match is found in a segment, return the timestamp and inform the user of the short audio's position in the long audio. Otherwise, notify the user that no match was found in the entire original video.
7. Return to the main menu.

For more details on audio fingerprinting, please refer to `fingerprint_manual.md` or `fingerprint_manual_en.md`.

### Usage Instructions
After running the program, follow the prompts:

```
Please select a function:
1. Find the position of the highlight video in the original video
2. Exit
Please select : 1
Search function selected.

Please enter the highlight video URL  (YouTube or Twitch) : example_url
Please enter the original video (live stream) URL (YouTube or Twitch) : example_original_url
Highlight video source : youtube
Original video source : youtube

Please enter the start time for the highlight video (format MM:SS) :
Start time (minutes, default is 0) :
Start time (seconds, default is 0) : 

Please enter the end time for the highlight video (format MM:SS) :
End time (minutes, default is 0) :
End time (seconds, default is 10) : 
Audio length : 10 seconds
Download progress: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████| 
Download completed : audio\example_url.m4a
Audio length : 6642 seconds
Download progress: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████| 
Download completed : audio\example_original_url.m4a
The audio file has been successfully divided into 3600 second segments. Files are saved as: ./segment/segments_xxx.wav

Query time range : 00:00:00 ~ 00:02:50 
Match : False, Best count : 2
This fragment does not match
Query time range : 00:02:10 ~ 00:05:20
.
.
.
Omitted process.
.
.
.
Query time range : 00:52:10 ~ 00:55:20
Match : False, Best count : 1
This fragment does not match
Query time range : 00:54:40 ~ 00:57:50
Match : True, Best count : 72
This fragment matches

Final corresponding time = 00:56:56
Processing time : 61.74 seconds
Query completed.
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


## v1.1.0 更新資訊
- 精華影片及原始影片來源現已支援 Twitch
- 同時支援中文及英文介面

詳請請參閱 Release

## 功能及特色
本專案可以尋找精華影片(短影片)位於原始直播或影片中的位置(時間軸)
有以下特色
1. 可尋找 Youtube 及 Twitch 上的精華影片位於原影片中的位置
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

另外，不論是原始碼或是執行，FFmpeg 都是必須的，若無此依賴，將無法順利運作

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
1. 下載 Youtube 或是 Twitch 音訊
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

請輸入精華影片網址(youtube 或 twitch)：example_url
請輸入原始影片(直播)網址(youtube 或 twitch)：example_orignal_url
精華影片來源： youtube
原始影片來源： youtube

請依順序輸入在精華影片中要查詢的開始時間（分鐘:秒）：
開始時間（分鐘，預設為0）：
開始時間（秒，預設為0）：

請依順序輸入在精華影片中要查詢的結束時間（分鐘:秒）：
結束時間（分鐘，預設為0）：
結束時間（秒，預設為10）：
影音長度：10秒
下載進度：100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████| 
下載完成：audio\example_url.m4a
影音長度：6642秒
下載進度：100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████| 
下載完成：audio\example_orignal_url.m4a
音訊文件已成功分割，每段 3600 秒，輸出到: ./segment/segments_xxx.wav

查詢時間段：00:00:00 ~ 00:02:50 
Match: False, Best count: 2
此段落不匹配
查詢時間段：00:02:10 ~ 00:05:20
Match: False, Best count: 2
.
.
.
過程省略
.
.
.
查詢時間段：00:52:10 ~ 00:55:20
Match: False, Best count: 1
此段落不匹配
查詢時間段：00:54:40 ~ 00:57:50
Match: True, Best count: 72
此段落匹配

最終對應時間 = 00:56:56
處理時間：64.08秒
查詢結束。
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

