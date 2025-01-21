# without admin priviledges

def connect_to_hd_ms_teams(ssid_name):
    ssid_name = normalize_ssid(ssid_name)
    target_directory = r'C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model'
    
    try:
        # Open Command Prompt in the target directory and run the script
        subprocess.run(
            f'start cmd /k "cd /d {target_directory} && python ssid_script.py"',
            shell=True
        )

        speak("Attempting to connect all clients to HD MS Teams.")
    except subprocess.CalledProcessError as e:
        speak("Failed to run the script.")
        print(f"Error: {e}")


# with admin priviledges

def connect_to_hd_ms_teams(ssid_name):
    ssid_name = normalize_ssid(ssid_name)
    # Path to change the directory to
    target_directory = r'C:\Users\gr1073\OneDrive - CommScope\Documents\AI_Model'
    
    # Command to run the Python script (test.py) in the target directory
    command = 'python ssid_script.py'
    
    try:
        # Using PowerShell to open an elevated CMD window in the specified directory and run the command
        subprocess.run([
            'powershell', 
            '-Command', 
            f'Start-Process cmd -ArgumentList \'/c cd /d "{target_directory}" && {command}\' -Verb RunAs'
        ], check=True)
    except subprocess.CalledProcessError as e:
        speak("Failed to run the script with administrator privileges.")
        print(f"Error: {e}")