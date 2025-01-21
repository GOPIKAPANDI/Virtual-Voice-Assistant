import subprocess
import winrm
import paramiko
import multiprocessing
import sys
import os
from win32com.client import Dispatch

def execute_command(command, ip_address):
    """Execute a command locally and return the result."""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def run_command_via_ssh(ip, command, username, password):
    """Execute a command on a remote machine using SSH with Paramiko."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        stdout_data = stdout.read().decode()
        stderr_data = stderr.read().decode()
        ssh.close()
        if stdout.channel.recv_exit_status() == 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def run_command_via_winrm(ip, command, username, password):
    """Execute a command on a remote machine using WinRM."""
    try:
        session = winrm.Session(f'http://{ip}:5985/wsman', auth=(username, password))
        result = session.run_ps(command)
        if result.status_code == 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def run_command_via_dcom(ip, command):
    """Execute a command on a remote machine using DCOM."""
    try:
        dcom = Dispatch("WScript.Shell")
        dcom.Run(f"cmd /c {command}", 1, True)
        return True
    except Exception as e:
        return False

def run_command_via_rpc(ip, command):
    """Execute a command on a remote machine using RPC."""
    # This method requires detailed RPC setup, which can be complex to script
    return False

def run_command_on_remote(ip, command):
    """Run a command on a remote machine using various methods with fallback logic."""
    # PowerShell command
    full_command = f'psexec \\\\{ip} -u it -p ruckus -i 1 powershell.exe -ExecutionPolicy Bypass -File "{command}"'
    if execute_command(full_command, ip):
        return True
    
    # cmd.exe
    full_command = f'psexec \\\\{ip} -u it -p ruckus -i 1 cmd.exe /c "{command}"'
    if execute_command(full_command, ip):
        return True

    # Remote PsExec cmd (fallback)
    remote_command = f'psexec \\\\{ip} -u it -p ruckus -i 1 cmd.exe /c "start msedge https://www.youtube.com/watch?v=YlRatjSfTVw&list=PLySwoo7u9-KKSgXM6a-YfUgJDo9g_Ozrl&mute=1"'
    if execute_command(remote_command, ip):
        return True

    # WMI method
    wmi_command = f'wmic /node:{ip} process call create "{command}"'
    if execute_command(wmi_command, ip):
        return True

    # Scheduled Task method
    task_file = f'create_task_{ip}.xml'
    create_task_xml = f'''
    <Task xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
      <RegistrationInfo>
        <Date>2024-09-14T08:00:00</Date>
        <Author>Administrator</Author>
      </RegistrationInfo>
      <Triggers>
        <LogonTrigger>
          <Delay>PT5M</Delay>
        </LogonTrigger>
      </Triggers>
      <Actions>
        <Exec>
          <Command>{command}</Command>
        </Exec>
      </Actions>
    </Task>
    '''
    with open(task_file, 'w') as file:
        file.write(create_task_xml)
    
    create_task_command = f'psexec \\\\{ip} -u it -p ruckus -i 1 schtasks /create /tn "RemoteTask" /xml {task_file}'
    if execute_command(create_task_command, ip):
        run_task_command = f'psexec \\\\{ip} -u it -p ruckus -i 1 schtasks /run /tn "RemoteTask"'
        if execute_command(run_task_command, ip):
            return True

    # SSH method
    ssh_command = f"echo '{command}'"
    if run_command_via_ssh(ip, ssh_command, 'it', 'ruckus'):
        return True

    # WinRM method
    if run_command_via_winrm(ip, command, 'it', 'ruckus'):
        return True

    # DCOM method
    if run_command_via_dcom(ip, command):
        return True

    # RPC method (not implemented)
    if run_command_via_rpc(ip, command):
        return True

    return False

def worker(ip, action, queue):
    """Worker function for multiprocessing to execute commands on remote machines."""
    if action == "open":
        command = r'C:\Users\it\Documents\yt_video\yt.ps1'
    elif action == "close":
        command = r'C:\Users\it\Documents\yt_video\close_yt.ps1'
    else:
        queue.put(f'Unknown action: {action}')
        return

    success = run_command_on_remote(ip, command)
    if success:
        queue.put(f'Success: {ip}')
    else:
        queue.put(f'Failed: {ip}')

def main(action):
    ips = [
        '10.74.143.29'
    ]
    queue = multiprocessing.Queue()
    processes = []

    for ip in ips:
        p = multiprocessing.Process(target=worker, args=(ip, action, queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    while not queue.empty():
        print(queue.get())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py [open|close]")
        sys.exit(1)

    action = sys.argv[1]
    if action not in ["open", "close"]:
        print("Invalid action. Use 'open' or 'close'.")
        sys.exit(1)

    main(action)
