import os
import sys
import time
import subprocess
from subprocess import Popen, PIPE
from time import sleep
from pathlib import Path
import multiprocessing

sta_list = [
    '10.74.140.74','10.74.143.56','10.74.143.23', '10.74.140.22','10.74.140.28','10.74.140.30', '10.74.140.52',
    '10.74.140.31','10.74.143.39', '10.74.143.182','10.74.140.24','10.74.140.72','10.74.143.44'
]

# IP address to device name mapping
device_mapping = {
    '10.74.140.74': 'device1' , '10.74.143.56': 'device2', '10.74.143.23': 'device3', '10.74.140.22': 'device4',
    '10.74.140.28': 'device5', '10.74.140.30': 'device6', '10.74.140.52': 'device7','10.74.140.31': 'device8',
    '10.74.143.39': 'device9','10.74.143.182': 'device10','10.74.140.24': 'device11','10.74.140.72': 'device12',
    '10.74.143.44': 'device13'
}


def generate_wifi_profile(folder_name, name):
    command = [f"""netsh wlan export profile name="{name}" key=clear folder="{folder_name}" """]
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

def output(queue, sta_list):
    start = time.time()
    while True:
        msg = queue.get()
        if msg == 'DONE':
            break
        print('%5.2f' % (time.time() - start) + 's | ' + msg)


def worker(sta, queue, argv, sta_list, name, profile_name, failed_ips):
    if '-custom' in argv:
        cmd = ' '.join(argv[2:])
        command = f'psexec \\\\{sta_list[sta]} -u IT -p ruckus -i cmd.exe /C {cmd}'
    elif '-disconnect' in argv:
        command = f'psexec \\\\{sta_list[sta]} -u IT -p ruckus -i netsh wlan delete profile name="{name}"'
    else: 
        command = f'psexec \\\\{sta_list[sta]} -u IT -p ruckus -i -c "C:\\Users\\gr1073\\OneDrive - CommScope\\Documents\\AI_Model_Copy1\\{profile_name}.bat"'

    p = Popen(command, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    output_msg = '%-15s' % sta_list[sta]
    
    if p.returncode != 0:
        output_msg += f' | X | Error: {stderr.decode().strip()}'
        failed_ips.append(device_mapping[sta_list[sta]])  # Collect failed IPs
    else:
        output_msg += ''
    
    queue.put(output_msg)

def ssid_main():
    ssid = "HD MS Teams"
    name = "HD MS Teams"
    profile_name = "profile-hd-ms-teams"
    folder_name = r"C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model_Copy1"
    xml_file_path = r"C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model_Copy1\Wi-Fi-HD MS Teams.xml"
    batch_file_path = r"C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model_Copy1\profile-hd-ms-teams.bat"

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

    # Use a Manager to share failed_ips across processes
    manager = multiprocessing.Manager()
    failed_ips = manager.list()  # Thread-safe list

    jobs = []
    for sta in range(len(sta_list)):  
        p = multiprocessing.Process(target=worker, args=(sta, queue, sys.argv, sta_list, name, profile_name, failed_ips))
        jobs.append(p)
        p.start()
 
    for job in jobs:
        job.join()

    queue.put('DONE')
    display.join() 

    unique_failed_ips = set(failed_ips)
    # print("Failed ips are",failed_ips)
    # if failed_ips:
    #     failed_ips_str = ', '.join(failed_ips)
    #     print(f"SSID connection failed for the following clients: {failed_ips_str}")
    #     return failed_ips
    # else:
    #     print("All clients connected successfully.")
    if unique_failed_ips:
        # failed_devices_str = ', '.join(unique_failed_ips)
        # print(f"SSID connection failed for the following devices: {failed_devices_str}")
        # print("failed clients===>",list(unique_failed_ips))
        return list(unique_failed_ips)  # Return as a list if needed
    else:
        print("All clients connected successfully.")

if __name__ == '__main__':
   ssid_main()

