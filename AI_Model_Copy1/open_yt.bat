@echo off
:: Define the playlist URL with videos to be muted
set playlistUrl=https://www.youtube.com/watch?v=YlRatjSfTVw&list=PLySwoo7u9-KKSgXM6a-YfUgJDo9g_Ozrl&mute=1

:: Path to Microsoft Edge executable
set edgePath="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

:: Start Microsoft Edge with the specified URL
start "" %edgePath% %playlistUrl%
