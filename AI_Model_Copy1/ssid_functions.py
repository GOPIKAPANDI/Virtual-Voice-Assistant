import re
import subprocess
import pyttsx3
import sys

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def normalize_ssid(ssid_name):
    # Mapping of recognized variations to the standard format
    ssid_mapping = {
        "hdms teams": "HD MS Teams",
        "hd ms teams": "HD MS Teams",
        "hdmsteams": "HD MS Teams",
        "hd msteams": "HD MS Teams"
    }
    
    # Normalize the input SSID name
    normalized_ssid = ssid_mapping.get(ssid_name.lower(), ssid_name)
    
    return normalized_ssid

def update_script_content(script_content, ssid_name):
    # Normalize the SSID name for use in the profile name
    normalized_ssid = ssid_name.lower().replace(" ", "-")
    
    # Define patterns to match only the initialization lines
    ssid_pattern = re.compile(r'^(\s*ssid\s*=\s*)".*?"', re.MULTILINE)
    name_pattern = re.compile(r'^(\s*name\s*=\s*)".*?"', re.MULTILINE)
    profile_pattern = re.compile(r'^(\s*profile_name\s*=\s*)".*?"', re.MULTILINE)

    # Replace the initializations for ssid, name, and profile_name
    script_content = ssid_pattern.sub(f'\\1"{ssid_name}"', script_content)
    script_content = name_pattern.sub(f'\\1"{ssid_name}"', script_content)
    script_content = profile_pattern.sub(f'\\1"profile-{normalized_ssid}"', script_content)

    return script_content


# def connect_to_hd_ms_teams(ssid_name):
#     ssid_name = normalize_ssid(ssid_name)
#     target_directory = r'C:\AI_Model_Copy'
    
#     try:
#         # Open Command Prompt in the target directory and run the script
#         subprocess.run(
#             f'start cmd /k "cd /d {target_directory} && python ssid_script.py"',
#             shell=True
#         )

#         # speak("Attempting to connect all clients to HD MS Teams.")
#     except subprocess.CalledProcessError as e:
#         speak("Failed to run the script.")
#         print(f"Error: {e}")

def connect_to_hd_ms_teams(ssid_name):
    ssid_name = normalize_ssid(ssid_name)
    target_directory = r'C:\AI_Model_Copy1'
    
    try:
        # Change the working directory to the target directory
        result = subprocess.run(
            [sys.executable, f"{target_directory}\\ssid_script.py"],
            capture_output=True, text=True, shell=True
        )

        if result.returncode == 0:
            # Parse the output for failed IPs
            output_lines = result.stdout.splitlines()
            failed_ips = [line for line in output_lines if "failed" in line]
            return failed_ips
        else:
            print("Error running the script:", result.stderr)
            return []

    except subprocess.CalledProcessError as e:
        speak("Failed to run the script.")
        print(f"Error: {e}")
        return []


def connectToSSID(ssid_name):
    # ssid_name = get_ssid_name()

    # Update the script with new SSID
    script_path = r'C:\AI_Model_Copy1\ssid_script.py'
    with open(script_path, 'r') as file:
        script_content = file.read()
          
    script_content = update_script_content(script_content, ssid_name)

    with open(script_path, 'w') as file:
        file.write(script_content)

    print(f"Script updated with SSID: {ssid_name}")

    if ssid_name == "hd ms teams" or ssid_name == "HD MS Teams":
        failed_ips = connect_to_hd_ms_teams(ssid_name)
        return failed_ips


def connect_to_ssid_from_query(query):
    match = re.search(r'connect all (clients|claims) to (.+)', query)
    if match:
        ssid_name = match.group(2).strip()
        ssid_name = normalize_ssid(ssid_name)
        speak(f"Connecting all clients to SSID: {ssid_name}")
        failed_ips = connectToSSID(ssid_name)
        return failed_ips
    else:
        speak("Sorry, I couldn't find the SSID in your request.")
        return []


