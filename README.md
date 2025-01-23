# HighlightLocator

## Features
This project can locate highlight clips (short videos) within the original live stream or video (timeline).
Features include:

1. Can locate highlight clips on YouTube within the original video.
2. Fast positioning (approximately 5 minutes to locate within a 5-hour live stream).
3. No language restrictions, no accuracy requirements for the speaker's pronunciation, and no volume limitations. It can locate and identify the position within the original video.
4. Simple operation, just provide the URL of the highlight clip and the original video, and enter the time point you want to query in the highlight clip.
5. Certain fault tolerance, even if there is noise or sound effects in the highlight clip, it can still locate the position within the original video.

## Environment
It is recommended to reserve about 2 GB of memory. Although the system has special handling for longer original videos, it is advisable to have at least the aforementioned free memory.
Reserve appropriate hard disk space, depending on the length of the audio file.

## Requirements
If you want to run the source code directly, you need to install Python and install the required dependencies as specified below.

FFmpeg is required. Without this dependency, the system will not function properly.
You can download it here (official website):
https://www.ffmpeg.org/download.html

## Download
There are several ways to download:

1. Download the source code

    ```bash
    git clone https://github.com/JoeYang1412/HighlightLocator.git
    ```

    After downloading and meeting the above environment requirements, enter the following command in CMD:

    ```bash
    pip install -r requirements.txt
    ```

    After installation, execute the following command to use the program:

    ```bash
    python main.py
    ```
2. Download the executable
    There are two types of executables available for download:

    a. Single file
    b. A folder containing the executable
    Please refer to the release page for instructions and download.

## Terminology
The following explanations may use different terms interchangeably, but they all refer to the same meaning.
* Highlight clip = short audio file = the segment the user wants to query in the short audio file.
* Original video = long audio file = the entire original video = the entire long audio file.
* Long audio file segmentation = segmented file = splitting the original video into multiple large segments.

### Operation Logic and Steps
1. Download YouTube audio.
2. Read the short audio file.
3. Split the long audio file into multiple segments.
4. Sequentially read the long audio file segments and use them as reference audio files. Using a sliding window approach, match the short audio file with the long audio file.
5. If there is no match in the segment, read the next segment and repeat until the position of the short audio file in the long audio file is found.
6. If a match is found, return the time and inform the user of the position of the short audio file in the long audio file. Otherwise, notify the user that the highlight clip was not found in the entire original video.
7. Return to the main menu.

For documentation related to audio fingerprint recognition, please refer to `fingerprint_manual.md` or `fingerprint_manual_en.md` for detailed explanations.
### Usage Instructions
When you run this program, the following content should appear. Follow the steps to operate:

The following steps are the English translation of the original text in Traditional Chinese.
```
Please select a function:
1. Find the position of the highlight clip in the original video
2. Exit
Please select: 1
Query function
Please enter the URL of the highlight clip: example_url
Please enter the URL of the original video (live stream): example_original_url
Please enter the start time in the highlight clip (minutes:seconds):
Start time (minutes, default is 0):
Start time (seconds, default is 0):
Please enter the end time in the highlight clip (minutes:seconds):
End time (minutes, default is 0):
End time (seconds, default is 10):
Audio length: 10 seconds
Download progress: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████|
Download completed: yt_dlp\example_url.m4a
Audio length: 16255 seconds
Download progress: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████|
Download completed: yt_dlp\example_original_url.m4a
Audio files successfully segmented, each segment 3600 seconds, output to: ./segment/segments_xxx.wav
Query time period (seconds): 00:00:00 ~ 00:02:10
Match: False, Best count: 1
.
.
.
Process omitted
.
.
.
Query time period (seconds): 03:15:50 ~ 03:18:10
Match: True, Best count: 79
This segment matches
Final corresponding time = 03:17:44
Processing time: 292.65 seconds
```

## Current Issues
1. There may be unknown errors.
2. Accuracy needs to be verified.
3. Although it can tolerate noise and sound effects, and even allow some segments to contain other parts, the specific tolerance level has not been verified, and it is uncertain how much can be tolerated while remaining accurate.

## Contribution
Found an issue or have a suggestion?
You can help with the following:

Report issues: Check the Issues page, or if not reported, create a new issue.

Submit changes: Fork the project, modify the code, and submit a pull request.

Improve documentation: If you find errors or omissions in the documentation, feel free to supplement and submit.

Thank you for your contribution to making this project better! 😊


## 功能及特色
本專案可以尋找精華影片(短影片)位於原始直播或影片中的位置(時間軸)
有以下特色
1. 可尋找 youtube 上的精華影片位於原影片中的位置
2. 快速定位（5 小時的直播影片約 5 分鐘可尋找完成）
3. 不限語言，不限說話者的發聲準不準確，不限大小聲，皆可定位及辨識在原始影片中的位置
4. 操作簡單，僅需提供精華影片網址及原影片網址，並輸入你在精華影片中想查詢的時間點即可
5. 有一定的容錯性，即使精華影片中有雜音或是音效，也可定位在原始影片中的位置

## 環境：
建議保留約 2 GB 以上左右的記憶體，雖本系統對較長的原始影片有另做處理，但建議至少要有前述的空閒記憶體較妥當
保留適當硬碟空間，具體視音檔長度而定

## 需求：  
若你想直接使用原始碼來執行，你需要安裝 python 才可以執行

並依照下面要求安裝依賴項

FFmpeg 是必須的，若無此依賴，將無法順利運作

可從這裡下載（官網）：
https://www.ffmpeg.org/download.html


## 下載
有幾種方法提供下載

1. 下載原始碼

    ```bash
    git clone https://github.com/JoeYang1412/HighlightLocator.git
    ```

    下載完成後且滿足上述環境後，接著在 CMD 輸入以下指令

    ``` bash
    pip install -r requirements.txt
    ```
    安裝完成後

    執行 main.py 即可使用
    ```
    python main.py
    ```

2. 下載執行檔
    
    有兩種類型執行檔可供下載

    a. 單一檔案

    b. 單個資料夾內含執行檔

    請至 release 頁面查看說明及下載

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

