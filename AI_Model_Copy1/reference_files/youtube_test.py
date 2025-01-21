import subprocess
import multiprocessing
import sys

# List of remote machine IPs
ips = [
 '10.74.143.59', '10.74.143.39', '10.74.143.29', '10.74.143.44', '10.74.140.30', '10.74.143.46', 
    # '10.74.143.36', 
    '10.74.143.34', 
    # '10.74.143.22',
      '10.74.143.23', 
    '10.74.143.43', '10.74.143.228', '10.74.143.35',  '10.74.143.228',
    '10.74.143.56', '10.74.140.68', '10.74.143.38',  '10.74.140.24',     
    '10.74.140.22', '10.74.140.25', '10.74.143.207', '10.74.143.195',
    '10.74.143.37', '10.74.143.40', '10.74.143.17',
    # '10.74.143.47', '10.74.143.182', '10.74.140.74', '10.74.143.42', '10.74.140.31', '10.74.143.41',
    # '10.74.140.43', '10.74.143.31', '10.74.140.72'
]

def run_command_on_remote(ip, command):
    """Run a command on a remote machine using PsExec."""
    full_command = f'psexec \\\\{ip} -u it -p ruckus -i 1 powershell.exe -ExecutionPolicy Bypass -File "{command}"'
    # print(f"Running command on {ip}: {full_command}")  # Diagnostic print

    process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # stdout_decoded = stdout.decode('utf-8', errors='replace')
    stderr_decoded = stderr.decode('utf-8', errors='replace')

    # print(f"Output from {ip}: {stdout_decoded}")
    print(f"Error from {ip}: {stderr_decoded}")

    if process.returncode == 0:
        return f'Command executed successfully on {ip}'
    else:
        return f'Error executing command on {ip}: {stderr_decoded}. Error Code: {process.returncode}'

def worker(ip, command, queue):
    """Worker function for multiprocessing to execute commands on remote machines."""
    result = run_command_on_remote(ip, command)
    queue.put(result)

def main(action):
    # Assign the script based on the action (open or close)
    if action == "open":
        command = r'C:\Users\it\Documents\yt_video\yt.ps1' 
    elif action == "close":
        command = r'C:\Users\it\Documents\yt_video\close_yt.ps1' 
    else:
        # print(f"Unknown action: {action}")
        return

    queue = multiprocessing.Queue()

    # Create a process for each remote IP in the ips list
    jobs = []
    for ip in ips:
        process = multiprocessing.Process(target=worker, args=(ip, command, queue))
        jobs.append(process)
        process.start()

    # Wait for all processes to complete
    for job in jobs:
        job.join()

    # Print results from the queue
    while not queue.empty():
        # print(queue.get())
        pass

if __name__ == '__main__':
    # Check if the user provided the action (open or close)
    if len(sys.argv) < 2:
        print("No action provided. Use 'open' or 'close' as the first argument.")
    else:
        main(sys.argv[1])
