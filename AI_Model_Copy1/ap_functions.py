import re
from SshLibraryV2 import SshLibraryV2
from AutoAcc_Logger import AutoAcc_Logger
from ApCliV2 import ApCliV2

# Initialize instances
apcli = ApCliV2()
logger = AutoAcc_Logger()
sshlib = SshLibraryV2()

# Define the file to log output
output_file_r370 = "r370ap_output.txt"

def log_output_r370(command, output):
    with open(output_file_r370, "a") as f:
        f.write(f"{command}\n{output}\n\n")

def get_r370ap_version():
    apcli.login(ip="ip_addr", username="super", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get version")
    apcli.logout()
    
    log_output_r370("get version", result)
    
    # Use regex to find the version number
    match = re.search(r"Version:\s*(\S+)", result)
    if match:
        return match.group(1)
    return "Unknown version"

def get_r370ap_country_code():
    apcli.login(ip="ip_addr", username="super", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get countrycode")
    apcli.logout()
    
    log_output_r370("get countrycode", result)
    
    # Use regex to find the country code
    match = re.search(r"Country is (\w+)", result)
    if match:
        return match.group(1)
    return "Unknown country code"

def get_r370ap_channel_wifi1():
    apcli.login(ip="ip_addr", username="super", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get channel wifi1")
    apcli.logout()
    
    log_output_r370("get channel wifi1", result)
    
    # Use regex to find the channel information
    match = re.search(r"wifi1 Channel:\s*(\d+)\s*\(([\d\s\w]+)\)", result)
    if match:
        channel_number = match.group(1)
        channel_freq = match.group(2)
        return f"channel number {channel_number} and channel frequency {channel_freq}"
    return "Unknown channel"

def get_r370ap_uptime():
    apcli.login(ip="ip_addr", username="super", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get uptime")
    apcli.logout()
    
    log_output_r370("get uptime", result)
    
    # Use regex to find the uptime
    match = re.search(r"Uptime:\s*(.*)", result)
    if match:
        return match.group(1).strip()
    return "Unknown uptime"

def get_r370ap_ip_address_wan():
    apcli.login(ip="ip_addr", username="super", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get ipaddr wan")
    apcli.logout()
    
    log_output_r370("get ipaddr wan", result)
    
    # Use regex to find the IP address
    match = re.search(r"IP:\s*([\d.]+)", result)
    if match:
        return match.group(1)
    return "Unknown IP address"

#-----------------------------
# common AP

# ----------------------------
# T670

# Define the file to log output
output_file_t670 = "t670ap_output.txt"

def log_output_t670(command, output):
    with open(output_file_t670, "a") as f:
        f.write(f"{command}\n{output}\n\n")

def get_t670ap_version():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get version")
    apcli.logout()
    
    log_output_t670("get version", result)
    
    # Use regex to find the version number
    match = re.search(r"Version:\s*(\S+)", result)
    if match:
        return match.group(1)
    return "Unknown version"

def get_t670ap_country_code():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get countrycode")
    apcli.logout()
    
    log_output_t670("get countrycode", result)
    
    # Use regex to find the country code
    match = re.search(r"Country is (\w+)", result)
    if match:
        return match.group(1)
    return "Unknown country code"

def get_t670ap_channel_wifi1():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get channel wifi1")
    apcli.logout()
    
    log_output_t670("get channel wifi1", result)
    
    # Use regex to find the channel information
    match = re.search(r"wifi1 Channel:\s*(\d+)\s*\(([\d\s\w]+)\)", result)
    if match:
        channel_number = match.group(1)
        channel_freq = match.group(2)
        return f"channel number {channel_number} and channel frequency {channel_freq}"
    return "Unknown channel"

def get_t670ap_uptime():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get uptime")
    apcli.logout()
    
    log_output_t670("get uptime", result)
    
    # Use regex to find the uptime
    match = re.search(r"Uptime:\s*(.*)", result)
    if match:
        return match.group(1).strip()
    return "Unknown uptime"

def get_t670ap_ip_address_wan():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get ipaddr wan")
    apcli.logout()
    
    log_output_t670("get ipaddr wan", result)
    
    # Use regex to find the IP address
    match = re.search(r"IP:\s*([\d.]+)", result)
    if match:
        return match.group(1)
    return "Unknown IP address"

# --------------------------------------------------------------------------------------
# r760

# Define the file to log output
output_file_r760 = "r760ap_output.txt"

def log_output_r760(command, output):
    with open(output_file_r760, "a") as f:
        f.write(f"{command}\n{output}\n\n")

def get_r760ap_version():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get version")
    apcli.logout()
    
    log_output_r760("get version", result)
    
    # Use regex to find the version number
    match = re.search(r"Version:\s*(\S+)", result)
    if match:
        return match.group(1)
    return "Unknown version"

def get_r760ap_country_code():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get countrycode")
    apcli.logout()
    
    log_output_r760("get countrycode", result)
    
    # Use regex to find the country code
    match = re.search(r"Country is (\w+)", result)
    if match:
        return match.group(1)
    return "Unknown country code"

def get_r760ap_channel_wifi1():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get channel wifi1")
    apcli.logout()
    
    log_output_r760("get channel wifi1", result)
    
    # Use regex to find the channel information
    match = re.search(r"wifi1 Channel:\s*(\d+)\s*\(([\d\s\w]+)\)", result)
    if match:
        channel_number = match.group(1)
        channel_freq = match.group(2)
        return f"channel number {channel_number} and channel frequency {channel_freq}"
    return "Unknown channel"

def get_r760ap_uptime():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get uptime")
    apcli.logout()
    
    log_output_r760("get uptime", result)
    
    # Use regex to find the uptime
    match = re.search(r"Uptime:\s*(.*)", result)
    if match:
        return match.group(1).strip()
    return "Unknown uptime"

def get_r760ap_ip_address_wan():
    apcli.login(ip="ip_addr", username="admin", password="Ruckus1!")
    result = apcli.execute_rkscli_cmd("get ipaddr wan")
    apcli.logout()
    
    log_output_r760("get ipaddr wan", result)
    
    # Use regex to find the IP address
    match = re.search(r"IP:\s*([\d.]+)", result)
    if match:
        return match.group(1)
    return "Unknown IP address"

def get_current_AP_R750():
    # nnn


# --------------------------------------------------------------------------------------------------------------------------------------

output_file_r770 = "r770ap_output.txt"

def log_output_r770(command, output):
    with open(output_file_r770, "a") as f:
        f.write(f"{command}\n{output}\n\n")

def get_r770ap_version():
    apcli.login(ip="ip_addr", username="admin", password="Lab4man!@#")
    result = apcli.execute_rkscli_cmd("get version")
    apcli.logout()
    
    log_output_r770("get version", result)
    
    # Use regex to find the version number
    match = re.search(r"Version:\s*(\S+)", result)
    if match:
        return match.group(1)
    return "Unknown version"

def get_r770ap_country_code():
    apcli.login(ip="ip_addr", username="admin", password="Lab4man!@#")
    result = apcli.execute_rkscli_cmd("get countrycode")
    apcli.logout()
    
    log_output_r770("get countrycode", result)
    
    # Use regex to find the country code
    match = re.search(r"Country is (\w+)", result)
    if match:
        return match.group(1)
    return "Unknown country code"

def get_r770ap_channel_wifi1():
    apcli.login(ip="ip_addr", username="admin", password="Lab4man!@#")
    result = apcli.execute_rkscli_cmd("get channel wifi1")
    apcli.logout()
    
    log_output_r770("get channel wifi1", result)
    
    # Use regex to find the channel information
    match = re.search(r"wifi1 Channel:\s*(\d+)\s*\(([\d\s\w]+)\)", result)
    if match:
        channel_number = match.group(1)
        channel_freq = match.group(2)
        return f"channel number {channel_number} and channel frequency {channel_freq}"
    return "Unknown channel"

def get_r770ap_uptime():
    apcli.login(ip="ip_addr", username="admin", password="Lab4man!@#")
    result = apcli.execute_rkscli_cmd("get uptime")
    apcli.logout()
    
    log_output_r770("get uptime", result)
    
    # Use regex to find the uptime
    match = re.search(r"Uptime:\s*(.*)", result)
    if match:
        return match.group(1).strip()
    return "Unknown uptime"

def get_r770ap_ip_address_wan():
    apcli.login(ip="ip_addr", username="admin", password="Lab4man!@#")
    result = apcli.execute_rkscli_cmd("get ipaddr wan")
    apcli.logout()
    
    log_output_r770("get ipaddr wan", result)
    
    # Use regex to find the IP address
    match = re.search(r"IP:\s*([\d.]+)", result)
    if match:
        return match.group(1)
    return "Unknown IP address"

def get_r770ap_client_info():
    apcli.login(ip="ip_addr", username="admin", password="Lab4man!@#")
    result = apcli.execute_rkscli_cmd("get client-info")
    apcli.logout()
    
    log_output_r770("get client-info", result)
    
    # Use regex to find the total number of clients
    match = re.search(r"Total Clients:\s*(\d+)", result)
    if match:
        return match.group(1)  # Return the total number of clients
    return "Unknown number of clients"

# def get_r770ap_ssid_info():
#     apcli.login(ip="10.174.122.37", username="admin", password="Lab4man!@#")
#     result = apcli.execute_rkscli_cmd("get wlanlist")
#     apcli.logout()
    
#     log_output_r770("get wlanlist", result)

#     match = re.search(r"wlan32\s+up\s+AP\s+wlan32\s+\d+\s+[\w:]+\s+(HD MS Teams - 5G)", result)
#     if match:
#         return match.group(1) 
#     return "Unknown number of clients"

def get_r770ap_ssid_info():
    apcli.login(ip="ip_addr", username="admin", password="Lab4man!@#")
    result = apcli.execute_rkscli_cmd("get wlanlist")
    apcli.logout()
    
    log_output_r770("get wlanlist", result)

    # Match wlan32 and capture the SSID
    # match = re.search(r"wlan32\s+up\s+AP\s+wlan32\s+\d+\s+[\w:]+\s+(.+)", result)
    match = re.search(r"wlan32\s+up\s+AP\s+wlan32\s+\d+\s+([0-9a-fA-F:]{17})\s+([0-9a-zA-Z!@#$%^&*()_+=-]+)",result)
    if match:
        ssid = match.group(1).strip()  # Capture and strip whitespace
        return ssid
    return "Unknown number of clients"

def get_current_AP_R770():
    print(get_r770ap_ssid_info())

get_current_AP_R770()
