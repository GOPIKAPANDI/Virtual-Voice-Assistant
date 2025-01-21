import sys
import subprocess
import requests  # Add this import for making HTTP requests

# Global variable for remote IPs
remote_ips = []

# List of remote machine IPs
ips = [
    '10.74.140.74','10.74.143.56',
    '10.74.143.23',
    '10.74.140.22','10.74.140.28','10.74.140.30', '10.74.140.52','10.74.140.31','10.74.143.39',
    '10.74.143.182','10.74.140.24','10.74.140.72','10.74.143.44'
]

device_mapping = {
    '10.74.140.74': 'device1' , '10.74.143.56': 'device2',
    '10.74.143.23': 'device3',
    '10.74.140.22': 'device4', '10.74.140.28': 'device5', '10.74.140.30': 'device6', '10.74.140.52': 'device7','10.74.140.31': 'device8',
    '10.74.143.39': 'device9','10.74.143.182': 'device10','10.74.140.24': 'device11','10.74.140.72': 'device12',
    '10.74.143.44': 'device13'
}

def run_command_on_remote(ip, command):
    """Run a command on a remote machine using PsExec."""
    full_command = f'psexec \\\\{ip} -u it -p ruckus -i 1 powershell.exe -ExecutionPolicy Bypass -File "{command}"'
    print(f"Running command on {ip}: {full_command}")

    process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    stdout_decoded = stdout.decode('utf-8', errors='replace')
    stderr_decoded = stderr.decode('utf-8', errors='replace')

    print(f"Output from {ip}: {stdout_decoded}")
    print(f"Error from {ip}: {stderr_decoded}")

    if process.returncode == 0:
        return True  # Success
    else:
        print(f'Error executing command on {ip}: {stderr_decoded}. Error Code: {process.returncode}')
        return False  # Failure

def call_http_endpoint(ip, action):
    """Call the FastAPI endpoint for the specified action."""
    url = f'http://{ip}:8000/runYoutube' if action == 'open' else f'http://{ip}:8000/closeYoutube'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Successfully called {url}: {response.json()}")
            return True
        else:
            print(f"Failed to call {url}: Status Code {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error calling {url}: {str(e)}")
        return False

def main(action):
    global remote_ips

    if len(sys.argv) > 2:
        remote_ips = sys.argv[2].split(',')
    else:
        print("No remote IPs provided.")
        return
    
    if action == "open":
        command = r'C:\Users\it\Documents\yt_video\yt.ps1' 
    elif action == "close":
        command = r'C:\Users\it\Documents\yt_video\close_yt.ps1' 
    else:
        print(f"Unknown action: {action}")
        return

    failed_ips = []

    for ip in remote_ips:
        success = run_command_on_remote(ip, command)
        if not success:
            # If PsExec fails, call the HTTP endpoint
            print(f"Psexec failed on {ip}")
            if not call_http_endpoint(ip, action):
                failed_ips.append(ip)

    remote_ips = []

    if failed_ips:
        failed_device_names = [device_mapping[ip] for ip in failed_ips if ip in device_mapping]
        print("Failed to execute on the following devices:", ', '.join(failed_device_names))
        return failed_device_names  
    else:
        print("All commands executed successfully.")
        return []

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No action provided.")
    else:
        main(sys.argv[1])
