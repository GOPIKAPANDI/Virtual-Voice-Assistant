import os
import sys
import time
import subprocess
from subprocess import Popen, PIPE
from time import sleep
from pathlib import Path
import multiprocessing

sta_list = ['10.74.143.59', '10.74.143.39', '10.74.143.29', '10.74.143.44', '10.74.140.30', '10.74.143.46', 
'10.74.143.36', '10.74.143.34', '10.74.143.22', '10.74.143.23', 
'10.74.143.43', '10.74.143.228', '10.74.143.35',  '10.74.143.228',
'10.74.143.56', '10.74.140.68', '10.74.143.38',  '10.74.140.24',     
'10.74.140.22', '10.74.140.25', '10.74.143.207', '10.74.143.177', '10.74.143.195'
'10.74.143.37', '10.74.143.40','10.74.143.17',
# nw
'10.74.143.47', '10.74.143.182','10.74.140.74','10.74.143.42', '10.74.140.31', '10.74.143.41',
'10.74.140.43', '10.74.143.31', '10.74.140.72'
]

def generate_wifi_profile(folder_name, name):
    command = [f"""netsh wlan export profile name = "{name}" key=clear folder="{folder_name}" """]
    result = subprocess.run(command[0], capture_output=True, text=True)
    print(result)


def generate_batch_content(xml_file_path, profile_name, ssid, name):
    with open(xml_file_path, 'r') as file:
        xml_content = file.read()
    batch_content = """@echo off\npowershell -command "New-Item -Path 'C:\\WifiProfiles' -ItemType Directory -Force\n"""
    batch_content += "(\n"
    for line in xml_content.splitlines():
        batch_content += "echo "
        for l in line.strip():
            if l in ('<', '>'):
                batch_content += "^"
            batch_content += f"{l}"
        batch_content += "\n"
    batch_content += f") > C:\\WifiProfiles\\{profile_name}.xml\n"
    batch_content += f"""netsh wlan add profile filename="C:\\WifiProfiles\\{profile_name}.xml"\nnetsh wlan connect ssid="{ssid}" name="{name}" """
    return batch_content
 
def output(queue, sta_l):   
    start = time.time()
    while True:
        msg = queue.get()
        if msg == 'DONE':
            break
        print('%5.2f' % (time.time() - start) + 's | ' + msg)
   

def worker(sta, queue, argv, sta_list, name, profile_name):
    if '-custom' in argv:
        cmd = ' '.join(argv[2:])
        command = f'psexec \\\\{sta_list[sta]} -u IT -p ruckus -i cmd.exe /C {cmd}'
    elif '-disconnect' in argv:
        command = f'psexec \\\\{sta_list[sta]} -u IT -p ruckus -i netsh wlan delete profile name = "{name}"'
    else: 
        command = f'psexec \\\\{sta_list[sta]} -u IT -p ruckus -i -c "C:\\Users\\gr1073\\OneDrive - CommScope\\Documents\\AI_Model\\{profile_name}.bat"'

    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    output = '%-15s' % sta_list[sta]
    if p.returncode == 0:
        output += ''
    else:
        output += f' | X | Error: {stderr.decode().strip()}'
    queue.put(output)
    return

def ssid_main():

    ssid = "HD MS Teams"
    name = "HD MS Teams"
    profile_name = "profile-hd-ms-teams"
    folder_name = r"C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model"
    xml_file_path = r"C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model\Wi-Fi-HD MS Teams.xml"
    batch_file_path = r"C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model\profile-hd-ms-teams.bat"

    queue = multiprocessing.Queue()
    display = multiprocessing.Process(target=output, args=(queue, sta_list))
    display.daemon = True
    display.start()

    file_path = Path(batch_file_path)

    if not file_path.exists():

        file_path = Path(xml_file_path)

        if not file_path.exists():
            generate_wifi_profile(folder_name, name)

        batch_content = generate_batch_content(xml_file_path, profile_name, ssid, name)

        with open(batch_file_path, "w") as batch_file:
            batch_file.write(batch_content)

    jobs = []
    for sta in range(len(sta_list)):  
        p = multiprocessing.Process(target=worker, args=(sta, queue, sys.argv, sta_list, name, profile_name))
        jobs.append(p)
        p.start()
 
    for job in jobs:
        job.join()
 
    for i in range(3):
        sleep(1)
        print('.')

    queue.put('DONE')


if __name__ == '__main__':
   ssid_main()
