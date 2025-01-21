@echo off
powershell -command "New-Item -Path 'C:\WifiProfiles' -ItemType Directory -Force
(
echo ^<?xml version="1.0"?^>
echo ^<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1"^>
echo ^<name^>HD MS Teams^</name^>
echo ^<SSIDConfig^>
echo ^<SSID^>
echo ^<hex^>4844204D53205465616D73^</hex^>
echo ^<name^>HD MS Teams^</name^>
echo ^</SSID^>
echo ^</SSIDConfig^>
echo ^<connectionType^>ESS^</connectionType^>
echo ^<connectionMode^>auto^</connectionMode^>
echo ^<MSM^>
echo ^<security^>
echo ^<authEncryption^>
echo ^<authentication^>WPA2PSK^</authentication^>
echo ^<encryption^>AES^</encryption^>
echo ^<useOneX^>false^</useOneX^>
echo ^</authEncryption^>
echo ^<sharedKey^>
echo ^<keyType^>passPhrase^</keyType^>
echo ^<protected^>false^</protected^>
echo ^<keyMaterial^>lab4man1!^</keyMaterial^>
echo ^</sharedKey^>
echo ^</security^>
echo ^</MSM^>
echo ^<MacRandomization xmlns="http://www.microsoft.com/networking/WLAN/profile/v3"^>
echo ^<enableRandomization^>false^</enableRandomization^>
echo ^<randomizationSeed^>2707789164^</randomizationSeed^>
echo ^</MacRandomization^>
echo ^</WLANProfile^>
) > C:\WifiProfiles\profile-hd-ms-teams.xml
netsh wlan add profile filename="C:\WifiProfiles\profile-hd-ms-teams.xml"
netsh wlan connect ssid="HD MS Teams" name="HD MS Teams" 