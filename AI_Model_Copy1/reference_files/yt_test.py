import paramiko

# Remote connection details
hostname = '10.74.140.31'
port = 22
username = 'it'
password = 'ruckus'

# Path to the PowerShell script on the remote machine
remote_script_path = r'C:\Users\IT\Documents\yt_video\yt.ps1'

# PowerShell command to execute the script
powershell_command = f'powershell.exe -ExecutionPolicy Bypass -File "{remote_script_path}"'

try:
    # Create an SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Try connecting
    print(f'Attempting to connect to {hostname}:{port}')
    client.connect(hostname, port, username, password)
    print('Connection successful')
    
    # Test command execution
    test_command = 'powershell.exe -Command "Write-Output HelloWorld"'
    stdin, stdout, stderr = client.exec_command(test_command)
    print('Test Command Output:')
    print(stdout.read().decode())
    print('Test Command Errors:')
    print(stderr.read().decode())
    
    # Execute the PowerShell script
    print(f'Executing PowerShell command: {powershell_command}')
    stdin, stdout, stderr = client.exec_command(powershell_command)
    
    # Print the output and errors
    print('Script Output:')
    print(stdout.read().decode())
    print('Script Errors:')
    print(stderr.read().decode())

except paramiko.ssh_exception.NoValidConnectionsError as e:
    print(f'Connection failed: {e}')
except paramiko.AuthenticationException as e:
    print(f'Authentication failed: {e}')
except Exception as e:
    print(f'An error occurred: {e}')
finally:
    # Close the connection
    client.close()
