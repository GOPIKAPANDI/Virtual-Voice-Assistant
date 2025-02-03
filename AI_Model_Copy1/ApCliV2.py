import json
import os
import subprocess
import time
import re
from SshLibraryV2 import SshLibraryV2
from AutoAcc_Logger import AutoAcc_Logger
logger = AutoAcc_Logger()


class ApCliV2:
    
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    def __init__(self):
        self.ipaddr = None
        self.username = None
        self.password = None
        self.logfile = 0
        self.shell_v54_passphrase = None
        self.rkscli_prompt = "rkscli:"
        self.shell_prompt = "#"
        self.sshlib = None
        self.ipv6addr_regex = r"inet6 addr:\s*(.*)[/][0-9]*\s*Scope:[Global|Link]"
         
    def login(self, ip, username, password, fips_enabled=False):
        """
        Description :
        Login to AP using SSH credentials

        Mandatory params :
        ip (String): IP address of AP
        username (String): username to login to AP
        password (String): password to login to AP

        Response :
        None
        """
        self.ipaddr = ip
        self.username = username
        self.password = password
        logger.debug("Try SSH login to AP. IP: %s  username: %s  password: %s" % (ip, username, password))

        try:
            self.sshlib = SshLibraryV2()
            self.sshlib.ssh_connect(server=self.ipaddr, username=self.username, password=self.password, prompt="Please login:",fips_enabled=fips_enabled, no_password=True)
            if not self.sshlib:
                raise Exception("Unable to Initialize Ssh Lib: SSH Client to %s" % self.ipaddr)

            self.sshlib.ssh_write(self.username)
            self.sshlib.ssh_read_until_prompt(prompt="password :")
            self.sshlib.ssh_write(self.password)
            self.sshlib.ssh_read_until_prompt(prompt=self.rkscli_prompt)
            logger.debug("SSH login to AP Success! IP: %s  username: %s  password: %s" % (ip, username, password))

        except Exception as e:
            logger.error("SSH Failed to login to AP. IP: %s  username: %s  password: %s" % (ip, username, password))
            if self.sshlib:
                self.sshlib.ssh_close()
            raise e

    def login_any(self, ip, sz_cluster_name, apzone_username, apzone_passwd, 
                            factory_username='super', factory_passwd='sp-admin', timeout="300"):

        """
        Description :
        Try Login to AP using different combinations of SSH credentials

        Mandatory params :
        ip (String): IP address of AP
        sz_cluster_name (String): Cluster name of SZ to use as username and password in login to AP
    apzone_username (String): APzone username
    apzone_passwd (String): APzone password

    Optional params:
    factory_username (String): AP factory username [default: super]
    factory_passwd (String): AP factory password [default: sp-admin]
    timeout (String): AP login_any timeout in secs [Min recommended: 300 secs]

        Response :
        None
        """

        is_login = False
        sleep_time = 100 #sleep time per iteration

        retry = (int(timeout)/sleep_time) + 1
        if (retry < 2):
            retry = 2 #Make sure we allow atleast 2 iterations irrespective of timeout

        self.check_ap_pingable(retry="20")

        for i in range (0, retry):
            try:


                
                logger.debug("Try SSH to login AP with SZ cluster name as username and password [try: %d]" % i)
                self.login(ip, sz_cluster_name, sz_cluster_name)
                is_login = True
                break
            except Exception:

                logger.warning("SSH login to AP failed. Continue with next combination...")
                pass
            try:
                logger.debug("Try SSH to login AP with AP factory username and password [try: %d]" % i)
                self.login(ip, factory_username, factory_passwd)
                is_login = True
                break
            except Exception:
                logger.warning("SSH login to AP failed. Continue with next combination...")
                pass
            try:
                logger.debug("Try SSH to login AP with APzone username and password [try: %d]" % i)
                self.login(ip, apzone_username, apzone_passwd)
                is_login = True
                break
            except Exception:
                logger.warning("SSH login to AP failed. Continue with next combination...")
                pass

            if (i < (retry-1)):
                logger.debug("Sleep for %d secs..." % sleep_time)
                time.sleep(sleep_time)

            if not is_login:
                raise Exception("login_any: SSH login to AP failed")
            else:
                logger.debug("SSH to login AP is successful")

    def logout(self):
        """
        Description :
        Logout from AP. Closes SSH connection only

        Response :
        None
        """
        self.sshlib.ssh_close()

    def _check_ssh_object(func):
        """
        Description :
        check ssh object
        """
        def _validate(self, *args, **kwargs):
            try:
                if not self.sshlib:
                    raise Exception("SSH connection not established yet!")
            except Exception as e:
                raise e
    
            return func(self, *args, **kwargs)
        
        return _validate

    def _enter_shell(self, sesame_ver="v2", v54_passphrase=""):
        """
        Description :
        Enter into AP shell prompt
        
        Mandatory Params:
        sesame_ver (String): sesame version v1 or v2 - currently only v2 is supported
        v54_passphrase (String): AP shell v54 passphrase 
        """
        _passphrase = None
        if v54_passphrase:
           _passphrase = v54_passphrase
        elif self.shell_v54_passphrase:
            _passphrase = self.shell_v54_passphrase
        else:
            raise Exception("AP Shell v54 Passphrase required!")
        try:
            if sesame_ver == "v2":
                self._cmd(cmd="!v54!", prompt="your chow:", timeout="")
                self._cmd(cmd=_passphrase, prompt=self.shell_prompt, timeout="")   
            else:
                raise Exception("Sesame version other than v2 is not implemented yet")
            
        except Exception as e:
            logger.error("Failed to enter AP shell")
            raise e
        
    def _exit_shell(self):
        """
        Description :
        Exit the shell and come back into rkscli prompt
        """
        self._cmd(cmd="rkscli", prompt=self.rkscli_prompt)

    @_check_ssh_object
    def set_ap_ssh_timeout(self, timeout):
        """
        Description :
        Set default timeout for ssh read 

        Mandatory Params :
        timeout (String): timeout in seconds
        """
        if not timeout:
            raise Exception("Invalid argument timeout")

        return self.sshlib.ssh_set_client_configuration(timeout=timeout)

    @_check_ssh_object
    def _cmd(self, cmd, prompt, timeout=""):
        """
        Description :
        Execute Command using SSH and return plain text

        Mandatory Params :
        cmd (String): command to execute
        prompt (String): expected prompt after executing the command

        Response :
        Command Output as text
        """
        if not prompt:
            prompt = self.prompt
        try:
            self.sshlib.ssh_write(cmd)
            res = self.sshlib.ssh_read_until_prompt(prompt, timeout=timeout)
            return res

        except Exception as e:
            logger.error(e)
            raise e

    @_check_ssh_object
    def ap_ssh_write(self, cmd):
        """
        Description :
        Executes command on existing prompt either its rkscli or shell
        
        Mandatory Params :
        cmd (String): AP CLI or shell command to execute
        """
        return self.sshlib.ssh_write(cmd)

    @_check_ssh_object
    def ap_ssh_read_until_prompt(self, prompt, timeout=""):
        """
        Description :
        Read command output until prompt is found
        
        Mandatory Params :
        prompt (String): expected prompt
        
        Optional Params:
        timeout (String): timeout for read until 
        
        Response :
        Returns plain text
        """
        return self.sshlib.ssh_read_until_prompt(prompt, timeout=timeout)

    @_check_ssh_object
    def ap_ssh_read_until_regex(self, regex, timeout=""):
        """
        Description :
        Read command output until prompt is found
        
        Mandatory Params :
        prompt (String): expected prompt
        
        Optional Params:
        timeout (String): timeout for read until 
        
        Response :
        Returns plain text
        """
        return self.sshlib.ssh_read_until_regex(regex, timeout=timeout)

    def execute_rkscli_cmd(self, cmd, timeout=""):
        """
        Description :
        Execute rks CLI command in AP

        Mandatory Params :
        cmd (String): CLI command to execute

        Optional Params :
        timeout (String): wait until the timeout for given command output

        Response :
        Command Output as text
        """
        return self._cmd(cmd=cmd, prompt=self.rkscli_prompt, timeout=timeout)

    def execute_shell_cmd(self, cmd, sesame_ver="v2", v54_passphrase=None, timeout="", prompt=None):
        """
        Description :
        Execute Shell command by login to AP shell and revert to rkscli prompt
        
        Mandatory Params :
        cmd (String): command to execute in AP shell

        Optional Params :
        sesame_ver (String): sesame version v1 or v2. default is v2
        v54_passphrase (String): v54 passphrase to enter to AP shell
        
        Response :
        Command Output as text
        """
        if prompt:
            cmd_prompt = prompt
        else:
            cmd_prompt = self.shell_prompt
        rx = None
        self._enter_shell(sesame_ver=sesame_ver, v54_passphrase=v54_passphrase)
        rx = self._cmd(cmd=cmd, prompt=cmd_prompt, timeout=timeout)
        self._exit_shell()
        return rx

    def set_apshell_v54_passphrase(self, passphrase):
        """
        Description :
        Set sesame v54 passphrase to enter into AP shell

        Mandatory params :
        passphrase (String) : sesame v54 passphrase

        Response :
        None
        """
        logger.debug("Setting Sesame Key : [%s]" % passphrase)
        self.shell_v54_passphrase = passphrase

    def reboot(self, ping_retries="10"):
        """
        Description :
        Reboot the AP and wait until AP is reachable
        
        Optional Params :
        ping_retries (String): ping retry count after reboot
        
        Response :
        None
        """
        res = self.execute_rkscli_cmd("reboot")
        if "OK" not in res:
            raise Exception("AP reboot command failed to execute")

        logger.debug("AP CLI reboot command executed successfully!")
        logger.debug("Sleeping for 30 secs...")
        time.sleep(30)

        self.check_ap_pingable(retry=ping_retries)

    def get_max_wlans_using_rpmkey(self):
        """
        Description :
        Get max WLANs supported in both radios using rpm -a | grep wlan-maxwlans2

        Response :
        tuple contains max_2g wlans and max_5g wlans respectively
        """
        max_wlan_2g = ''
        max_wlan_5g = ''

        cmd = 'rpm -a | grep wlan-maxwlans2'
        res_list = self.execute_shell_cmd(cmd=cmd)
        res_list = res_list.splitlines()
        for item in res_list:
            if 'wifi0/wlan-maxwlans2' in item:
                max_wlan_2g = item.split(':')[-1]
            elif 'wifi1/wlan-maxwlans2' in item:
                max_wlan_5g = item.split(':')[-1]

        if not max_wlan_2g or not max_wlan_5g:
            print("Can't get max wlans:%s" % res_list)

        return max_wlan_2g, max_wlan_5g

    def get_wlanid_in5g(self):
        """
        Description :
        Get Wlan ID in 5g radio which are up

        Response :
        Return list of wlanid
        """

        wlanid_li = []
        res = self.execute_rkscli_cmd(cmd="get wlanlist")
        lines = res.splitlines()
        for item in lines:
            ptn = r'\s*(wlan[0-9]+)\s+up\s+AP\s+(wlan[0-9]+)\s+1.*\s*'
            if re.search(ptn, item):
                wlan_id = item.split()[0]
                wlanid_li.append(wlan_id)
        print("#####", wlanid_li)
        return wlanid_li

    def get_wlanid_in2g(self):
        """
        Description :
        Get Wlan ID in 2.4g radio which are up

        Response :
        Return list of wlanid
        """
        wlanid_li = []
        res = self.execute_rkscli_cmd(cmd="get wlanlist")
        lines = res.splitlines()
        for item in lines:
            ptn = r'\s*(wlan[0-9]+)\s+up\s+AP\s+(wlan[0-9]+)\s+0.*\s*'
            if re.search(ptn, item):
                wlan_id = item.split()[0]
                wlanid_li.append(wlan_id)
        print("#####", wlanid_li)
        return wlanid_li

    def get_wlanid_via_ssid(self, ssid):
        """
        Description :
        Get wlan interface id (for e.g., wlan1 or wlan32) which is having given ssid in AP
        
        Mandatory Params :
        ssid (String): ssid
        
        Response :
        returns a list contaning wlan interface id
        """
        result = []
        try:
            res = self.execute_rkscli_cmd(cmd="get wlanlist")
            ptn = r'wlan[0-9]+.*' + re.escape(ssid) + '.*'
            all_wlaninfo_with_ssid = re.findall(ptn, res)
            for wlan_info in all_wlaninfo_with_ssid: 
                wlan_info_li = wlan_info.splitlines()
                individual_wlan_info = wlan_info_li[0].split()
                result.append(individual_wlan_info[3])
                
        except Exception as e:
            raise e
        
        return result

    def get_ssid(self, wlan_id):
        """
        Description :
        Get ssid using wlan interface id in AP

        Mandatory Params :
        wlan_id (String): wlan id e.g. wlan1 or wlan32

        Response :
        SSID as string
        """
        ssid = None
        res = self.execute_rkscli_cmd(cmd="get ssid %s" % wlan_id)
        ssid = res.splitlines()[0].split(':')[-1].strip()
        return ssid

    def get_wlan_state(self, wlan_id):
        """
        Description :
        Get wlan state using wlan interface id

        Mandatory Params :
        wlan_id (String): for e.g., wifi1 or wifi0 or wlan101

        Response :
        state as string type, up or down
        """
        state = None
        res = self.execute_rkscli_cmd(cmd="get state %s" % wlan_id)
        state = res.splitlines()[0].split(':')[-1].strip()
        return state

    def start_capture_local_mode(self, intf, filter=""):
        """
        Description :
        Start capture on given interface as local mode
        set capture <intf> {idle|[stream|local][-no[b][c][d][p]]}

        Mandatory Params :
        intf (String): interface name (e.g. wifi1 or eth0)

        Optional Params :
        filter (String): nob|noc|nop|nobcp

        Response :
        Returns cmd output
        """
        cap_files_list = self.stop_capture_local_mode(intf=intf, check_for_files="0")
        
        if cap_files_list:
            for file in cap_files_list:
                cmd = 'rm -f %s' % file
                self.execute_shell_cmd(cmd=cmd)

        time.sleep(1)

        cmd = 'set capture %s local' % (intf)
        if filter:
            cmd = '%s-%s' % (cmd, filter)
        result = self.execute_rkscli_cmd(cmd=cmd)
        if "OK" not in result:
            raise Exception("Start capture in AP[%s] failed - %s" % (self.ipaddr, result))

        return result

    def get_capture_state(self, intf):
        """
        Description :
        Get capture state of mentioned interface
        get capture <intf> state

        Mandatory Params :
        intf (String): wlan interface id

        Response :
        returns state idle/local
        """
        cmd = 'get capture %s state' % intf
        res = self.execute_rkscli_cmd(cmd=cmd)
        if 'Packet Capture' not in res:
            raise Exception("Fail to get the capture state of WLAN[%s] - %s" % (intf, res))
        state = res.splitlines()[0].split()[-1]
        return state

    def stop_capture_local_mode(self, intf, check_for_files="1"):
        """
        Description :
        Stop the capture on given interface 
        for e.g., set capture wifi1 idle

        Mandatory Params :
        intf (String): interface name

        Response:
        Captured file names in list
        """
        files_list = []
        stop_capture_cmd = 'set capture %s idle' % (intf)
        result = self.execute_rkscli_cmd(cmd=stop_capture_cmd)
        if "OK" not in result:
            raise Exception("Stop capture in AP[%s] failed - %s" % (self.ipaddr, result))
        list_files_cmd = "ls -l /tmp/capture.pcap*"
        result = self.execute_shell_cmd(cmd=list_files_cmd)
        if check_for_files == "1":
            if "No such file or directory" in result:
                raise Exception("No capture files found - capture.pcap0 or capture.pcap1 in /tmp folder")
        files = re.findall(r".*capture.pcap[0-1]+", result)
        if files:
            for item in files:
                only_file = item.split()[8].replace("/tmp/","")
                files_list.append(only_file)
        return files_list

    def send_capture_files_to_tftpserver(self, tftp_server_ip):
        """
        Description :
        Send capture files (capture.pcap0 and capture.pcap1) to TFTP server

        Mandatory Params :
        tftp_server_ip (String): tftp server ip address
        """
        files_list = []
        list_files_cmd = "ls -l /tmp/capture.pcap*"
        result = self.execute_shell_cmd(cmd=list_files_cmd)
        if "No such file or directory" in result:
            raise Exception("No capture files found - capture.pcap0 or capture.pcap1 in /tmp folder")
        files = re.findall(r".*capture.pcap[0-1]+", result)
        if files:
            for item in files:
                files_list.append(item.split()[8])
        
        if files_list:
            for file in files_list:
                target_file_name = file.strip().split("/")[2]
                tftp_cmd = 'tftp -p -l %s -r %s %s' % (file, target_file_name, tftp_server_ip)
                res = self.execute_shell_cmd(cmd=tftp_cmd)
                if "timeout after" in res:
                    raise Exception("tftp: Failed to connect to tftp server - %s" % res)

    def download_file_using_scp(self, target_ipaddr, username, password, ap_capture_dir, ap_capture_file, 
            capture_rdir="/tmp", capture_rfile="capture.pcap", timeout=None):
        """
        Description:
        API to download file from remote server to local machine  by executing SCP command on remote
        
        Mandatory Params :
        target_ipaddr (String): target ip address to transfer
        username (String): username of target machine
        password (String): password
        ap_capture_dir (String): directory in AP
        ap_capture_file (String): file name in AP
        
        Optional Params :
        capture_rdir (String): target machine directory
        capture_rfile (String): file name to be copied to target machine
        timeout (String): number of seconds to wait for prompt
        
        Response :
        True is success else False
        """
        scp_expect_list_in_ap = [r"\(y(es)?/n(o)?.*\)\s*", r"password:"]
        conn_yes_or_no_string = "yes"
        self._enter_shell()
        res = self.sshlib.scp_download(toaddr=target_ipaddr, username=username, password=password, 
                                       capture_rdir=ap_capture_dir, capture_rfile=ap_capture_file, 
                                       capture_ldir=capture_rdir, capture_lfile=capture_rfile, 
                                       expected_prompt=self.shell_prompt, scp_cmd_output_prompt_list=scp_expect_list_in_ap, 
                                       conn_yes_or_no=conn_yes_or_no_string, timeout=timeout)
        self._exit_shell()
        return res

    def get_scg_control_ip(self):
        """
        Description:
        Get SCG Control IP fetched using AP CLI
        
        Response :
        SCG Control IP to which AP is connected
        """
        scg_ip = None
        res = self.execute_rkscli_cmd(cmd="get scg")
        scg_ip = re.search(r"SSH tunnel connected to (?P<scg_ip>\S+)", res).group("scg_ip")
        return scg_ip.strip()

    def get_ap_conn_state_in_scg_info(self):
        """
        Description:
        Get AP connection state using get scg CLI command
        
        Response :
        AP state (e.g. RUN_STATE or DISC_REQ)
        """
        state = None
        res = self.execute_rkscli_cmd("get scg")
        state = re.search(r"State:\s*(?P<state>\S+)", res).group("state")
        return state.strip()

    def get_ipv6addresses(self, ifname):
        """
        Description:
            Get list of AP global and link local IPv6 addresses
        
        Mandatory Params :
            ifname (String): interface name (eg. br0)
        
        Response :
            List of Global and Link Local IPv6 addresses of AP
        """
        ip6addr_li = []
        cmd = "ifconfig %s" % ifname
        res = self.execute_shell_cmd(cmd)
        match = re.findall(self.ipv6addr_regex,res)
        if match:
            for ipv6addr in match:
                ip6addr_li.append(ipv6addr.strip())
        else:
            raise Exception ("Failed to get the ipv6 addr of intf: %s" % ifname)
        
        return ip6addr_li

    def get_ipv6addr_link_local(self, ifname):
        """
        Description:
            Get Link Local IPv6 address of AP
        
        Mandatory Params :
            ifname (String): interface name (eg. br0)
        
        Response :
            Link Local IPv6 address of AP
        """
        ipv6_link_local_addr = None
        ipv6addr_all = self.get_ipv6addresses(ifname)
        if ipv6addr_all:
            for ipv6addr in ipv6addr_all:
                if re.search(r"fe80", ipv6addr):
                    ipv6_link_local_addr = ipv6addr
                    break
        else:
            raise Exception ("Failed to get Link Local ipv6 addr of intf: %s" % ifname)
        
        if not ipv6_link_local_addr:
            raise Exception ("Failed to get Link Local ipv6 addr of intf: %s" % ifname)

        return ipv6_link_local_addr.strip()
    
    def get_ipv6addr_eiu64(self, ifname, mac_addr):
        """
        Description:
            Get eiu64 IPv6 address of AP
        
        Mandatory Params :
            ifname (String): interface name (eg. br0)
            mac_addr (String): mac address of AP
        
        Response :
            EUI64 IPv6 address of AP
        """
        ipv6_eiu64_addr = None
        mac_addr_match = mac_addr.lower().replace(":","")[-6:]
        ip6addr_li = []
        cmd = "ifconfig %s" % ifname
        res = self.execute_shell_cmd(cmd)
        match = re.findall(r"inet6 addr:\s*(.*)[/][0-9]*\s*Scope:Global",res)
        if match:
            for ipv6addr in match:
                ip6addr_li.append(ipv6addr.strip())
        else:
            raise Exception ("Failed to get the ipv6 addr of intf: %s" % ifname)
        
        for item in ip6addr_li:
            match_item = item.replace(":","")[-6:]
            if match_item == mac_addr_match:
                ipv6_eiu64_addr = item
                break

        if not ipv6_eiu64_addr:
            raise Exception ("Failed to get EIU64 ipv6 addr of intf: %s" % ifname)
        
        return ipv6_eiu64_addr.strip()
    
    def get_dns_spoof_dump_table(self, wlan_id):
        """
        Description:
            get dns-spoof dump-table of wlan id
        
        Mandatory Params :
            wlan_id (String): WLAN ID (eg. wlan32)
        
        Response :
            List of Dns spoof dumple table output
        """
        r_res = self.execute_rkscli_cmd(cmd="get dns-spoof dump-table %s" % wlan_id)
        res = r_res.splitlines()
        return res

    def get_dns_spoof_stats(self, wlan_id, domain_name="www.abc.com"):
        """
        Description:
            get dns-spoof-stats of wlan id
        
        Mandatory Params :
            wlan_id (String): WLAN ID (eg. wlan32)
        
        Optional Params :
            domain_name (String): Domain name to search (eg. www.abc.com)
            
        Response :
            Dictionary with request and response
        """
        resp = {}
        r_res = self.execute_rkscli_cmd(cmd="get dns-spoof-stats %s %s" % (wlan_id, domain_name))
        res = r_res.splitlines()
        for item in res:
            if "Ifname" in item:
                intf = item.split(":")[1].replace(" ","")
                resp['interface'] = intf
            if "Domain" in item:
                dm_name = item.split(":")[1].replace(" ","")
                resp['domain_name'] = dm_name
            if "Request" in item:
                req = item.split(":")[1].replace(" ","")
                resp['requests'] = req
            if "Response" in item:
                response = item.split(":")[1].replace(" ","")
                resp['responses'] = response
        return resp


    def set_wlan_state(self, wlan_id, state):
        """
        Description :
        Set wlan state using wlan interface id

        Mandatory Params :
        wlan_name (String): for e.g., wlan0 or wlan32 or wlan101
        state (String): up | down

        Response :
        None
        """
        res = self.execute_rkscli_cmd(cmd="set state %s %s" % (wlan_id, state))
        print(res)
        if 'OK' in res:
            return True
        else:
            raise Exception("Unable to set wlan state [%s, %s]" % (wlan_id, state) )


    def get_wlanlist(self):
        """
        Description :
        executes the command "get wlanlist"  and returns the parsed output of the command  

        Mandatory Params :
        None

        Optional Params :
        None

        Response :
        dictionary of the parsed output
        """
   
        result = {}
        res = self.execute_rkscli_cmd(cmd="get wlanlist").split('\n')
        for l in res:
            m = re.match(r'(wlan[0-9]+)\s*(down|up)\s*(AP|MON)\s*(wlan[0-9]+)\s*([0-9]+)\s*([0-9a-zA-Z:]+)\s*(.+)', l)
            if m:
                result.update({m.group(1):{'state': m.group(2), 'radio_id': m.group(5), 'bssid': m.group(6), 'ssid': m.group(7).strip()}})

        return result 

    def set_wlan_state_via_ssid(self, ssid, radio_id, state='down'):
        """
        Description :
        Get all wlan 2g/5g state to up/down based on ssid.

        Mandatory Params :
        ssid (String): ssid name
        radio_id (Enum): radio ID (0/1)

        Optional Params :
        state (Enum): up/down (default: down)

        Response :
        return wlan interface of given ssid
        """

        if radio_id not in ["0", "1"]:
            raise Exception("Invalid Radio input!")

        all_wlan_info = self.get_wlanlist()  
        #print all_wlan_info 
        for wlan_id in list(all_wlan_info.keys()):
            if all_wlan_info[wlan_id]['ssid'] == ssid and all_wlan_info[wlan_id]['radio_id'] == radio_id:  
                 logger.info('setting wlan state on %s to %s' % (wlan_id, state))
                 self.set_wlan_state(wlan_id=wlan_id, state=state)
                 break
        time.sleep(2)
        print(json.dumps(self.get_wlanlist(), indent=2))

    def get_wlan_info(self, wlan_id=""):
        """
        Description:
            get wlaninfo using wlan_id
        
        Mandatory Params :
            wlan_id (String): WLAN ID (eg. wlan32)

        Response :
            Dictionary containing {"ssid":"", "bssid":"", "channel":"", "network_security":"", "auth":"", "firewall_id":"", "protocol_version": "", "cipher_algorithm":""}
        """
        resp = {"ssid":"", "bssid":"", "channel":"", "network_security":"", "auth":"", "firewall_id":""}
        res = self.execute_rkscli_cmd("get wlaninfo")
        apcli_out = res.split("\r\n\r\n")
        del apcli_out[-1]
        for item in apcli_out:
            if wlan_id in item:
                wlan_info = item.strip()
                match = re.search(r"\s*%s\s*SSID\s*/\s*BSSID:\s*(?P<ssid>\S+)\s*/\s*(?P<bssid>\S+)" % wlan_id, wlan_info)
                if match:
                    resp["ssid"] = match.group('ssid')
                    resp["bssid"] = match.group('bssid')
                fw_match = re.search(r"\s*FIREWALL ID:\s*(?P<fw_id>\S+)", wlan_info)
                if fw_match:
                    resp["firewall_id"] = fw_match.group('fw_id')
                channel_match = re.search(r"\s*Channel:\s*(?P<channel>\S+)", wlan_info)
                if channel_match:
                    resp["channel"] = channel_match.group('channel')
                net_security_match = re.search(r"\s*Net Security:\s*(?P<net_sec>\S+)", wlan_info)
                if net_security_match:
                    resp["network_security"] = net_security_match.group('net_sec')
                auth_match = re.search(r"\s*Auth:\s*(?P<auth>\S+)", wlan_info)
                if auth_match:
                    resp["auth"] = auth_match.group('auth')
                proto_ver = re.search(r"\s*Protocol Version:\s*(?P<proto_ver>\S+)", wlan_info)
                if proto_ver:
                    resp["protocol_version"] = proto_ver.group('proto_ver')
                cipher_algo = re.search(r"\s*Cipher Algorithm:\s*(?P<cypher_algo>\S+)", wlan_info)
                if cipher_algo:
                    resp["cipher_algorithm"] = cipher_algo.group('cypher_algo')
        return resp

    def get_recovery_ssid(self):
        """
        Description:
            Get recovery ssid wlan interface
        """
        res = self.execute_rkscli_cmd("get ssid wlan102")
        a = re.search("SSID:\s*(?P<name>\S+)\s*", res)
        return a.group('name')

    def get_client_info(self, interface):
        """
        Description:
            get clientinfo using wlan_id

        Mandatory Params :
            wlan_id (String): WLAN ID (eg. wlan32)

        Response :
            Dictionary containing {'summary': '', 'Total Clients': '2', 'Laptop': '1 (  50.0% )', 'Linux': '1 ( 100.0% )', 'WDS Device': '1 (  50.0% )', 'Telnet CPE': '1 ( 100.0% )', 'rkscli': ''}
        """

        res = self.execute_rkscli_cmd("get client-info %s" % interface.strip())
        initial_split_string = res.split("\r")
        response = {}
        init_key = None
        end_keys = False
        for i in initial_split_string:
            if not end_keys:
                if i.strip().endswith("{"):
                    init_key = i.replace("{", "").strip()
                    response[init_key] = {}
                    continue
                if init_key and not end_keys:
                    inner_string_split = i.strip().split(":", 1)
                    if not len(inner_string_split) == 1:
                        first = inner_string_split[0].strip().replace("'", "")
                        second = inner_string_split[1].strip().replace("'", "")
                        response[init_key][first] = second

            if i.strip().startswith("summary:"):
                end_keys = True
            if end_keys and ":" in i and "rkscli" not in i:
                if not len(i) == 1:
                    temp = i.split(":")
                    first = temp[0].strip().replace("'", "")
                    second = temp[1].strip().replace("'", "")
                    response[first] = second
        return response
    
    def get_pid_from_name(self, process_name, restore_rkscli="yes"):
        """
        Description :
        Executes command on existing prompt on Shell , 
        gets process id/ids on process name
        
        Mandatory Params :
        process_name(String): name of the process for which id/ids required
        """

        #command = "ps -aef | grep " + process_name
        command = "pidof "+ process_name
        test = self.execute_shell_cmd(cmd=command)
        #test = self.execute_shell_cmd(cmd=command, restore_rkscli=restore_rkscli)
        result = re.findall(r'\d+', test)
        return result

    def check_file_exists(self, path, restore_rkscli="yes", filename=None):
        """
        Description :
        Executes command on existing prompt on Shell , 
        gets process id/ids on process name
        
        Mandatory Params :
        process_name(String): name of the process for which id/ids required
        """
        if not path.startswith('/'):
            path = '/'+ path

        command = "cd " + path
        self.execute_shell_cmd(cmd=command)
        #self.execute_shell_cmd(cmd=command,  restore_rkscli= restore_rkscli)
        test = self.execute_shell_cmd("ls")
        return test

    def enable_wsgclient_ignore_version(self):
        """
        Description :
            API to set AP under vSZ to ignore firmware upgrade from vSZ
        Enable AP ignore version (ap will not upgrade firmware after joining SZ).

        Response :
            None
        """
        res = self.execute_rkscli_cmd("set rpmkey wsgclient/ignore-fw 1")
        if "OK" not in res:
            raise Exception("Cmd: set wsgclient/ignore-fw  1 is failed")

    def get_model_name(self):
        """
        Description :
            API to get AP model on rkscli 'get boarddata'

        Response :
            Return the AP device string 
        """
        res = self.execute_rkscli_cmd("get boarddata")
        model_match = re.search('Model:\s*(\w+:*)*', res, re.M)
        if model_match:
            return model_match.group().split()[-1]
        else:
            raise Exception("get_model_name: Could not get AP Model!")

    def get_ap_firmware_version(self):
        """
        Description :
            API to get AP firmware version on rkscli using 'get version' AP CLI

        Response :
            Return the AP firmware version 
        """
        res = self.execute_rkscli_cmd('get version')
        version = ""
        for line in res.splitlines():
            if line.lower().startswith("version"):
                version = line.split(':')[-1].strip()
                break

        if not version:
            raise Exception("Could not get AP firmware version")

        return version

    def verify_ap_firmware_version(self, expected_fw):
        """
        Description :
            API to verify AP firmware version on rkscli against expected AP firmware
        Mandatory params :
            expected_fw (String) : Expected AP fwversion. For e.g., 5.2.1.0.100
        Response :
            Return if success
        """
        current_version = str(self.get_ap_firmware_version())
        if (current_version == expected_fw):
            logger.debug("AP Firmware version expected: %s is current version on AP" % (current_version))
            return
        else:
            raise Exception("AP Firmware version expected: %s is NOT same as current version: %s on AP" % (
                               expected_fw, current_version))

    def change_fw_setting(self, host, control):
        """
        Description :
            API to change AP 'fw' settings using rkscli

        Mandatory params :
            host (String) : TFTP server which is having the AP image
        control (String) : Relative path of control AP image file on TFTP server

        Response :
            None
        """

        if not host:
            raise Exception("host is not specified")
        if not control:
            raise Exception("control is not specified")
    
        logger.debug("Change firmware upgrade setting on AP")
        self.execute_rkscli_cmd('fw set control %s' % control)
        self.execute_rkscli_cmd('fw set host %s' % host)
        self.execute_rkscli_cmd('fw set proto tftp')
        self.execute_rkscli_cmd('fw auto disable')


    def update_ap_firmware(self, timeout="180"):
        """
        Description :
            API to start and complete AP 'fw upgrade' on rkscli
        Includes AP reboot

        Optional params :
            timeout (String): number of seconds to wait for prompt after fw update command is executed

        Response :
            None
        """
        odata = self.execute_rkscli_cmd("fw update", timeout=timeout)

        mobj = re.search(r'\*\*fw\((\d+)\)\s*:\s*(completed|no update)', odata[-80:], re.I)
        if mobj:
            res = mobj.group(2).lower()
            if 'completed' in res:
                time.sleep(2)
                logger.debug("AP Upgrade Done. Rebooting AP....")
                self.reboot()
                logger.debug("Reboot AP Done.")
            elif 'no update' in res:
                logger.warning("No Upgrade! AP is running an expected image")
                pass
            else:
                raise Exception('AP fw update procedure returned unexpected result')
        else:
            raise Exception("AP fw update failed after %s seconds" % timeout )

        return odata


    def check_ap_pingable(self, retry="30"):
        """
        Description :
        Check AP is reachable or not

        Optional Params :
        retry (String): number of retry for ping if fails

        Response :
         None
        """
        if int(retry) <= 0:
            raise Exception("Invalid value for retry: %s" % retry)

        ping_result = False
        omsg = None
        for i in range (0, int(retry)):
            logger.debug("ping IP: %s ..." % self.ipaddr)
            cmd_list = ['ping', '-c', '4', '%s' % self.ipaddr]
            pout = subprocess.Popen(cmd_list, stdout=subprocess.PIPE)
            omsg1 = pout.communicate()[0]
            omsg = omsg1.decode('utf-8')
            #print "############", omsg
            if re.search(r"[0-9]+\s+bytes\s+from\s+%s" % self.ipaddr, omsg):
                logger.debug("ping IP: %s success!" % self.ipaddr)
                ping_result = True
                break
            else: 
                sleep_time=20
                logger.debug("ping IP: %s failed. Sleep %d secs and retry [try: %d]..." % (
                                self.ipaddr, sleep_time, i))
                time.sleep(sleep_time)

        logger.debug("ping cmd output:   %s" % omsg)
        if ping_result:
            logger.debug("AP IP: %s reachable" % self.ipaddr)
            return
        else:
            raise Exception("Max retries reached. Ping to IP: %s failed!" % self.ipaddr)


    def get_pmf_details(self, wlan_id):
        """
        Description :
        Output of command get pmf <wlan_id>

        Mandatory Params :
        wlan_id (String): wlan interface id

        Response :
        return dictionary with details
        """
        pmf = {"pmf_mode":"", "assoc-cback_time":"", "saquery_maxtimeout":""}
        out = self.execute_rkscli_cmd("get pmf %s" % wlan_id)
        print("########", out)
        res = out.splitlines()
        for line in res:
            if re.search(r"PMF mode", line): 
                pmf["pmf_mode"]= line.split(":")[1].strip()
            if re.search(r"Association Comeback Time", line):
                pmf["assoc-cback_time"] = line.split(":")[1].strip()
            if re.search(r"SA Query maximum timeout", line):
                pmf["saquery_maxtimeout"] = line.split(":")[1].strip()
        print(pmf)
        return pmf           

    def get_ipv6address_ifname(self,ifname="br0"):
        """
        Description :
        IPv6addess of the given interface

        Mandatory Params :
        ifname (String): interface name

        Response :
        IPv6 Adress
        """
        ipv6addr = ""
        cmd = "ifconfig %s" % ifname
        buf  = self.execute_shell_cmd(cmd)
        buf = buf.splitlines()
        for line in buf:
            if re.search("\s*inet6 addr:\s+.*Scope:Global", line):
                ipv6addr = re.search(r"\s*inet6 addr:\s+(?P<ipv6>\S+)/64\s*Scope:Global\s*", line).group("ipv6")
                return ipv6addr
        raise Exception ("Failed to get the ip addr of %s"% ifname)

    def get_ipv6address_eui64(self, ifname="br0", mac=''):
        """
        Description :
        IPv6address of EUI64 standard of given interface with given macaddress

        Mandatory Params :
        ifname (String): interface name
        mac (String): Mac address 

        Response :
        IPv6address of EUI64 standard
        """
        ipv6addr = ""
        cmd = "ifconfig %s" % ifname
        buf  = self.execute_shell_cmd(cmd)
        buf = buf.splitlines()
        if not mac: raise Exception("MAC not passed")
        mac_str = str(mac[9:].split(':')[0] + ':' + mac[9:].split(':')[1]+mac[9:].split(':')[2]).lower()
        for line in buf:
            if (re.search(r'.*inet6 addr:.*'+ mac_str +'.*Scope:Global.*', line)):
                ipv6addr = line.split() #.split('inet6 addr: ')[1]
                return ipv6addr[2].split("/64")[0]
        raise Exception ("Failed to get the ip addr of %s"% ifname)

    def get_ipv6address_linklocal_ifname(self,ifname="br0"):
        """
        Description :
        IPv6address of Link Local of given interface
        
        Mandatory Params :
        ifname (String): interface name
        
        Response :
        Link Local IPv6address
        """     
        ipv6addr = ""
        cmd = "ifconfig %s" % ifname
        buf  = self.execute_shell_cmd(cmd)
        buf = buf.splitlines()
        for line in buf:
            if (re.search(r'.*inet6 addr:.*Scope:Link.*', line)):
                ipv6addr = re.search(r"\s*inet6 addr:\s+(?P<ipv6>\S+)/64\s*Scope:Link.*", line).group("ipv6")
                #ipv6addr = line.split() #.split('inet6 addr: ')[1]
                return ipv6addr
        raise Exception ("Failed to get the ip addr of %s"% ifname)

    def get_ipv6_info(self, ap_interface='wan',ifconfig_intf="br0"):
        """
        Description :
        Get IPv6 info from AP
        
        Mandatory Params :
        ap_interface (String): interface name eg: wan, eth1
        ifconfig_intf (String): interface name eg: br0
        
        Response :
        IPv6 info from AP
        """
        dict_res = {}
        buf = self.execute_rkscli_cmd('get ipv6addr %s' % ap_interface)
        buf = buf.splitlines()
        for i in buf:
            if re.search(r'Default Gateway:',i):
                dict_res['default_gateway'] = i.split(": ")[1]
            if re.search(r'IPv6 Address Configuration Type', i):
                dict_res['config_type'] = i.split(": ")[1]
            if re.search(r'RA Flags:', i):
                dict_res['ra_flags'] = i.split(": ")[1]
        ipv6addr = self.get_ipv6address_ifname(ifname="%s" % ifconfig_intf)
        dict_res['ipv6_addr'] = ipv6addr
        return dict_res

    def get_ipv6ctrl_all(self, wlan_name='wlan32'):
        """
        Description :
        execute get ipv6ctrl <wlan_name>
        
        Mandatory Params :
        wlan_name (String): wlan interface name/id
        
        Response :
        get ipv6ctrl <wlan_name> output in dictionary
        """
        ipv6_dict = {'nd_proxy':'', 'ns_supress':'','ra_proxy':'','rs_guard':'','ra_guard':'','ra_throttle':'', 'max_ra_allowed':'', 'ra_interval':'', 'ns_suppressed':''}
        buf = (self.execute_rkscli_cmd('get ipv6ctrl %s' % wlan_name)).splitlines()
        for line in buf:
            if (re.search(r'^ND Proxy', line)):
                nd_proxy = line.split('ND Proxy')[1].strip()
                ipv6_dict.update({'nd_proxy':nd_proxy})
            if (re.search(r'^RA Proxy', line)):
                ra_proxy = line.split('RA Proxy')[1].strip()
                ipv6_dict.update({'ra_proxy':ra_proxy})
            if (re.search(r'^NS Suppression', line)):
                ns_supress = line.split('NS Suppression')[1].strip()
                ipv6_dict.update({'ns_supress':ns_supress})
            if (re.search(r'^NS Suppressed', line)):
                ns_suppressed = line.split(':')[1].strip()
                ipv6_dict.update({'ns_suppressed':ns_suppressed})
            if (re.search(r'^RS Guard', line)):
                rs_guard = line.split('RS Guard')[1].strip()
                ipv6_dict.update({'rs_guard':rs_guard})
            if (re.search(r'^RA Guard', line)):
                ra_guard = line.split('RA Guard')[1].strip()
                ipv6_dict.update({'ra_guard':ra_guard})
            if (re.search(r'^RA Throttle', line)):
                ra_throttle = line.split('RA Throttle')[1].strip()
                ipv6_dict.update({'ra_throttle':ra_throttle})
            if (re.search(r'^MAX RA Allowed\s+:\s+(?P<max_ra>\S+)\s+RA Interval\s+:\s+(?P<ra_interval>\S+)\s*', line)):
                max_ra_allowed = re.search(r'^MAX RA Allowed\s+:\s+(?P<max_ra>\S+)\s+RA Interval\s+:\s+(?P<ra_interval>\S+)\s*', line).group('max_ra')
                ra_interval = re.search(r'^MAX RA Allowed\s+:\s+(?P<max_ra>\S+)\s+RA Interval\s+:\s+0\s+hours\s+(?P<ra_interval>\S+)\s+min\s*', line).group('ra_interval')
                ipv6_dict.update({'max_ra_allowed': max_ra_allowed})
                ipv6_dict.update({'ra_interval': ra_interval})

        return ipv6_dict

    def get_ipv6db(self, wlan_name='wlan32', match=False, macaddr="",ipv6addr="", vlan=""):
        """
        Description :
        execute get ipv6db <wlan_name>
        
        Mandatory Params :
        wlan_name (String): wlan interface name/id
  
        Optional Params :
        match (Boolean): True if match with result else false to check mac address
        macaddr (String): Macaddress to check the result has the entry
        ipv6addr (String): ipv6addr to search in command output
        vlan (String): vlan in which client connected
        
        Response :
        get ipv6db <wlan_name> output is bolean
        """
        buf = self.execute_rkscli_cmd('get ipv6db %s' % wlan_name).splitlines()
        if match and not vlan:
            if macaddr and ipv6addr:
                for line in buf:
                    if re.search('%s' % macaddr, line):
                        if re.search('%s' % ipv6addr, line):
                            return True

        if match and vlan:
            if macaddr and ipv6addr:
                for line in buf:
                    if re.search('%s' % macaddr, line):
                        if re.search('%s' % ipv6addr, line):
                            if re.search('%s' % vlan, line):
                                if (line.split()[4] == vlan) and (line.split()[6] == "P"):
                                    return True
        if not match and not vlan and not macaddr: return False
        return buf

    def get_ipv6ctrl_ra_cache(self, wlan_name='wlan32', match=False, mac_addr="", ipv6_gw="", vlan="1", interface="br0"):
        """
        Description :
        execute get ipv6ctrl <wlan_name> ra-cache
        
        Mandatory Params :
        wlan_name (String): wlan interface name/id
  
        Optional Params :
        match (Boolean): True if match with result else false to check mac address
        mac_addr (String): Macaddress to check the result has the entry
        ipv6_gw (String): ipv6addr to search in command output
        vlan (String): vlan in which client connected
        interface (String): interface name of ap eg: br0
        
        Response :
        Get ra-cache entry when RA Proxy is enabled in AP, boolean if success
        """
        bridge=False
        mac=False
        gw=False
        vlan_f=False
        a = []
        buf = self.execute_rkscli_cmd('get ipv6ctrl %s ra-cache' % wlan_name).splitlines()
        if match:
            if mac_addr and ipv6_gw:
                for line in buf:
                    if (re.search('BRIDGE: %s' % interface, line)):
                        bridge=True
                        break
                for line in buf:
                        if re.search('%s' % mac_addr.upper(), line):
                            mac=True
                        if re.search('%s' % ipv6_gw, line):
                            a.append(line.split()[2])
                            gw=True

        if vlan in a: vlan_f=True

        if bridge and mac and gw and vlan_f:
            return True
        else:
            return buf, False
    def get_ap_process_cpu_usage(self, process_name, wait_interval=2, retries=3):
        """
        Description :
        Get AP Process's CPU and Memory usage in percent 

        Mandatory Params :
        process_name(String)          : Name of the AP Process

        Optional Params  :
        wait_interval(String)         : Wait time in seconds before retrying to check CPU Usage
        retries(String)               : Number of retries before arriving at the final CPU Usage 

        Response :
        CPU usage percent(Float)
        """
        result_list = []
        header_cmd = "top -bo | grep %CPU"
        header_result = self.execute_shell_cmd(header_cmd).splitlines()
        cpu_percent_column = header_result[0].split().index("%CPU")

        for index in range(retries):
            cmd = "top -bo | grep %s" % process_name
            result = self.execute_shell_cmd(cmd).splitlines()
            print("Result: \n%s\n%s" % (header_result[0], '\r\n'.join(result)))
            result_index = 0

            if len(result) <= 1:
                raise Exception("get_ap_process_cpu_usage(): Process not found Error!")
            elif len(result) > 2:    ## Multiple processes/threads found, consider entry of parent process only
                for index in range(0, len(result)):
                    if re.search(r'^\s*\d+\s+1\s+', result[index]):
                        result_index = index
                        break
                if index >= len(result):
                    raise Exception("get_ap_process_cpu_usage(): Multiple processes - Parent process not found!")

            result_list.append(result[result_index].split()[cpu_percent_column].strip('%'))
            time.sleep(wait_interval)

        return float(max(result_list))

    def get_memory_info(self):
        """
        Description :
        Get AP Memory Info

        Response :
        Dictionary containing output of free Command
        """

        cmd_str = 'free\n'
        timeout = 1
        retry_times = 5
        res = None

        #If can't get memory, retry some times.
        for i in range(retry_times):
            res = self.execute_shell_cmd(cmd_str,timeout=timeout).splitlines()
            if res and "Mem" in str(res): break
            else: timeout += 2

        free_res = {}
        mem_dict = {}
        swap_dict = {}
        total_dict = {}
        for line in res:
            if 'Mem' in line:
                mem_info = line.split()
                mem_dict['total'] = mem_info[1]
                mem_dict['used'] = mem_info[2]
                mem_dict['free'] = mem_info[3]
                mem_dict['shared'] = mem_info[4]
                mem_dict['buffers'] = mem_info[5]
            elif 'Swap' in line:
                swap_info = line.split()
                swap_dict['total'] = swap_info[1]
                swap_dict['used'] = swap_info[2]
                swap_dict['free'] = swap_info[3]
            elif 'Total' in line:
                total_info = line.split()
                total_dict['total'] = total_info[1]
                total_dict['used'] = total_info[2]
                total_dict['free'] = total_info[3]

        free_res['memory'] = mem_dict
        free_res['swap'] = swap_dict
        free_res['total'] = total_dict

        return free_res

    def get_cpu_info(self, interval = 2):
        """
        Description     :
        Execute top command get top result.

        Optional Params :
        interval        :interval when execute top command

        Response        :
        Dictionary containing CPU information
        """
        cpu_info = {}

        #'CPU:   5% usr   6% sys   0% nic  87% idle   0% io   0% irq   0% sirq'
        cpu_ptn = "CPU:\s+(?P<usr>[0-9]+)%\s+usr\s+(?P<sys>[0-9]+)%\s+sys\s+" \
                   + "(?P<nic>[0-9]+)%\s+nic\s+(?P<idle>[0-9]+)%\s+idle\s+" \
                   + "(?P<io>[0-9]+)%\s+io\s+(?P<irq>[0-9]+)%\s+irq\s+" \
                   + "(?P<sirq>[0-9]+)%\s+sirq"
        regex = re.compile(cpu_ptn)

        top_res = self.get_top_result(interval)
        matcher = regex.search(top_res)
        if matcher: cpu_info = matcher.groupdict()

        return cpu_info

    def get_top_result(self, interval = 2):
        """
        Description      :
        Execute top command get top result

        Optional Params  :
        interval(String) : interval when execute top command.
        
        Response         :
        String containg result of top command
        """
        top_res = ""
        frame_start_pattern = 'Mem:'
        try_times = 3
        data = ""
        timeout = 5
        #Try three times to get top result.
        for i in range(try_times):
            i = i + 1
            is_exec_succ = True
            #Execute top and wait for interval, get result of output.
            self._enter_shell()
            self.ap_ssh_write('top\n')
            time.sleep(interval)
            self.ap_ssh_write(chr(3))  #Send Ctrl+C
            data = self.ap_ssh_read_until_prompt('#',timeout)
            self._exit_shell()

        if data and len(data) > 0:
            # get index of the first occurence
            search_start_pos = 0
            start_frame_idx = data.find(frame_start_pattern, search_start_pos)
            if start_frame_idx >= 0:
                # get index of next occurence
                search_start_pos = start_frame_idx + len(frame_start_pattern)
                next_frame_idx = data.find(frame_start_pattern, search_start_pos)
                end_frame_idx = next_frame_idx-1 if next_frame_idx != -1 \
                                else len(data)-1 # the data has only one frame

                # Get result of one occurence and add to output list.
                top_res = data[start_frame_idx:end_frame_idx]

            # Remove Ctrl+C from result.
            top_res = top_res.replace('\r^C\r', '')

        return top_res

    def get_ap_serial(self):
        """
        Description :
            API to get AP Serial on rkscli 'get boarddata'

        Response :
            Return the AP Serial string 
        """
        res = self.execute_rkscli_cmd("get boarddata")
        serial_match = re.search('Serial#:\s*(\w+)*', res, re.M)
        if serial_match:
            return serial_match.group().split()[-1]
        else:
            raise Exception("get_ap_serial: Could not get AP Serial!")

    def get_ap_uptime(self):
        """
        Description :
            API to get AP Uptime on rkscli 'get uptime'

        Response :
            Return the AP Uptime string 
        """
        res = self.execute_rkscli_cmd("get uptime")
        uptime_match = re.search('Uptime:\s*(\w+|\s+|\d+)*', res, re.M)
        if uptime_match:
            return uptime_match.group().split(":")[-1].split("OK")[0].strip()
        else:
            raise Exception("get_ap_serial: Could not get AP Serial!")

    def get_nodestats_queues(self, wifi_if, mac_address,is_11ax_ap=True):
        """
        Description :
        API to get the nodestats details of AP
        
        Mandatory Params:
        wifi_if (String): WIFI Interface(wifi0/wifi1) to which client is connected
        mac_address (String): MAC Address of the client connected

        Optional params:
        is_11ax_ap (Boolean): Set it to True if AP under test is 11ax or else False

        Response :
        Returns a dictionary containing nodestats details of AP
        """

        res = self.execute_shell_cmd('nodestats '+wifi_if+' '+mac_address,prompt="--\r\n#")
        logger.debug("res is : %s"%res)

        if is_11ax_ap==True:
            get_queues = re.compile(r'MQ\s*Stats\r*\n*\|\s*enq\s*deq\s*drpQ\s*drpT\s*drp_th\s*\|\s*enq\s*deq\s*drpQ\s*drpT\s*drp_th\s*\|\s*enq\s*deq\s*drpQ\s*drpT\s*drp_th\s*\|\s*enq\s*deq\s*drpQ\s*drpT\s*drp_th\s*\r*\n*\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d*\s*)\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d*\s*)\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d*\s*)\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d*\s*)')
            bk_queue = get_queues.search(res).groups()[0]
            be_queue = get_queues.search(res).groups()[1]
            vi_queue = get_queues.search(res).groups()[2]
            vo_queue = get_queues.search(res).groups()[3]

            key_names = ['enq', 'deq', 'drpQ',  'drpT',  'drp_th']
        else:
            get_queues = re.compile(r'MQ\s*Stats\r*\n*\|qed\s*enqueue\s*reenq\s*drop\s*xret\s*xtlm\s*\|qed\s*enqueue\s*reenq\s*drop\s*xret\s*xtlm\s*\|qed\s*enqueue\s*reenq\s*drop\s*xret\s*xtlm\s*\|qed\s*enqueue\s*reenq\s*drop\s*xret\s*xtlm\s*\r*\n*\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*)\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*)\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*)\|(\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*)')
            bk_queue = get_queues.search(res).groups()[0]
            be_queue = get_queues.search(res).groups()[1]
            vi_queue = get_queues.search(res).groups()[2]
            vo_queue = get_queues.search(res).groups()[3]

            key_names = ['qed', 'enqueue', 'reenq',  'drop',  'xret',  'xtlm']

        bk_dictionary = dict(list(zip(key_names,bk_queue.split())))
        be_dictionary = dict(list(zip(key_names,be_queue.split())))
        vi_dictionary = dict(list(zip(key_names,vi_queue.split())))
        vo_dictionary = dict(list(zip(key_names,vo_queue.split())))

        key_names = ['bk', 'be', 'vi', 'vo']
        dict_list = [bk_dictionary, be_dictionary, vi_dictionary, vo_dictionary]
        dictionary = dict(list(zip(key_names,dict_list)))
        logger.debug("dictionary is : %s"%dictionary)
        return dictionary

    def start_logging(self, keyword='', fileName='/tmp/Logging.log', enblemgrinfo=False, bonjour=False):
        """
        Description :
        API to start logging using logread -f shell command
        
        Optional params:
        keyword (String) : Text to grep in logs
        enblemgrinfo (Boolean): if set to True it will Enable apmgrinfo logs
        bonjour (Boolean): if set to True it will enable bonjour logs
        is_11ax_ap (Boolean): Set it to True if AP under test is 11ax or else False

        Response :
        Returns a dictionary containing nodestats details of AP
        """

        """
        start the logging in background and dumps the log data into file
        in /tmp/Logging.log
        """
        try:
            self.stop_logging(fileName)
        except:
            pass
        logFile = fileName
        cmd_remove_log_file = 'rm -rf %s' % fileName
        self.execute_shell_cmd(cmd_remove_log_file)

        if enblemgrinfo==True:
            self.execute_shell_cmd("apmgrinfo -d 7 -m All -c N")
        if bonjour:
            log_cmd = "logread -f | grep '%s' >> %s & " %(keyword, logFile) if keyword else "logread -f >> %s &" %logFile
        else:
            log_cmd = "logread -f | grep %s > %s & " %(keyword, logFile) if keyword else "logread -f > %s 2>&1 &" %logFile
        logger.debug("log_cmd is :%s"%log_cmd)
        res = self.execute_shell_cmd(log_cmd)
        logger.debug("res is :%s"%res)

    def stop_logging(self, fileName=None):
        """
        Description :
        API to stop logread 
        
        Optional params:
        fileName (String): Log FileName

        Response :
        Returns a dictionary containing nodestats details of AP
        """

        cmd_string = "killall logread"
        time.sleep(3)
        if fileName:
            cmd_string = "cat %s" %fileName
            res = self.execute_shell_cmd(cmd_string)
            logger.debug("Debug received log length %s"%str(len(res)))
            logger.debug("%s: log file contents\n" % fileName)
            res = "\r\n".join(res)
            logger.debug("%s"%res)
            return res

    def get_gap_mode(self):
        """
        Description :
        API to get the gap mode details of the AP

        Response :
        Returns a dictionary containing gap mode details of the AP
        """
        res_dictionary = {}
        res = self.execute_rkscli_cmd("get gap mode").splitlines()[:-3]
        logger.debug("get gap mode :%s"%res)
        interface_header = False
        for line in res:
            match_str=re.search('(.*)\s*:\s*(.*)',line)
            if match_str:
                res_dictionary[match_str.group(1).strip()]=match_str.group(2).strip()
                if "Interface" in line:
                    interface_header = True
                    res_dictionary['Interface'] = dict()
                    pass
            elif interface_header:
                if "eth" in line:
                    if_name = line.strip().split()[0]
                    if_forwarding = line.strip().split()[1]
                    res_dictionary['Interface'][if_name] = if_forwarding

        logger.debug("res_dictionary is :%s"%res_dictionary)
        return res_dictionary

    def get_dhcps(self):
        """
        Description :
        API to get the dhcps information
        
        Response :
        Returns a dictionary containing dhcps information
        """
        dhcps_dict = {}
        try:
            cmd_txt = "get dhcps"
            header_list = ['ip_addr', 'mac_addr', 'computer', 'lease_expire_time']
            header_line = False
            dhcp_clients_list = []

            subnet_list = self.execute_rkscli_cmd(cmd_txt).splitlines()
            logger.debug("get dhcps output : %s" % ("\r\n".join(subnet_list)))

            if not "OK" in subnet_list:
                raise Exception("Get dhcps error:%s" % subnet_list)

            for line in subnet_list[:-3]:
                if "DHCP server:" in line:
                    dhcps_dict['status'] = line.split(':')[1].strip()
                elif "IP Address Pool" in line:
                    ptn = "start:\s+([0-9\.]+)\s+end:\s+([0-9\.]+)"
                    regex = re.compile(ptn)
                    r = regex.search(line)
                    if r:
                        start_ip_addr = r.groups()[0]
                        end_ip_addr = r.groups()[1]
                        dhcps_dict['ip_addr_pool'] = {'start_ip_addr': start_ip_addr,
                                                      'end_ip_addr': end_ip_addr}

                elif "IP Address" in line:
                    #Title line.
                    header_line = True
                    pass
                elif "DHCP lease table: empty" in line:
                    #Empty dhcp lease table.
                    dhcp_clients_list = []
                elif header_line:
                    items_list = line.split()
                    info = {}
                    for i in range(0,len(header_list)):
                        info[header_list[i]] = items_list[i]

                    dhcp_clients_list.append(info)
                else:
                    pass

            if dhcp_clients_list: dhcps_dict['dhcp_clients'] = dhcp_clients_list

            logger.debug("Get DHCPS setting:%s"% dhcps_dict)
        except Exception as ex:
            logger.debug("get dhcps can not get DHCPS setting")
            raise Exception('get_dhcps','Can not get DHCPS setting')

        return dhcps_dict

    def get_ip_info(self, interface='wan'):
        """
        Description :
        API to get the nodestats details of AP
        
        Optional Params:
        interface(String) : interface type like wan , lan etc

        Response :
        Returns a dictionary containing connection type, ip_addr, mask, and gateway.
        IP Address Configuration Type: static, IP: 192.168.0.200  Netmask 255.255.255.0  Gateway 192.168.0.252
        """
        ip_re = '([0-9]+.[0-9]+.[0-9]+.[0-9]+)'
        type_re = '\((\w+), vlan ([0-9]+)\)'
        info_re = 'IP Address: %s, IP: %s  Netmask %s  Gateway %s' % (type_re, ip_re, ip_re, ip_re)
        ip_info = {}
        buf = self.execute_rkscli_cmd("get ipaddr %s" % interface).splitlines()[:-3]
        logger.debug("buf is %s" %buf)
        info = re.findall(info_re, buf[0])
        ip_info['type'], ip_info['vlan'], ip_info['ip_addr'], ip_info['net_mask'], ip_info['gateway'] = info[0]
        return ip_info

if __name__ == "__main__":
    ap = ApCliV2()
    ap.login(ip='ip_addr', username='admin', password='ruckus1!')
    ap.get_recovery_ssid()
    #ap.get_wlan_info('wlan32')
    #ap.login(ip='10.1.65.44', username='bala', password='bala')
    #ap.set_ap_ssh_timeout(timeout="30")
    #ap.ap_ssh_write("get scg")
    #ap.set_apshell_v54_passphrase("H9piz34cAq5YFjdY6MTSd8krhF@VuWWK5tybrQZW4oLd1KFhKsH57F7eLBTJ3em")
    #print "##############", ap.stop_capture_local_mode(intf="eth1", check_for_files="1")
    #########################################################
    #print ap.ap_ssh_read_until_prompt("rkscli:")
    #ap.execute_rkscli_cmd(cmd="get version")
    #ap.ap_ssh_write("get eth")
    #ap.ap_ssh_read_until_regex(r"rkscli:")
    """
    ap.ap_ssh_write(cmd="get scg")
    print ap.execute_shell_cmd('rkscli -c "get wlanlist"', restore_rkscli="no")
    ap.ap_ssh_write(cmd="ls -l")
    ap.ap_ssh_read_until_prompt(prompt="#")
    ap.exit_shell()
    #print ap.ap_ssh_read_until_prompt(prompt="#")
    """

    #ap.login(ip='10.1.65.82', username='bdc23', password='bdc23')
    #ap.reboot()
    #ap.enable_wsgclient_ignore_version()
    #ap.get_model_name()
    #ap.get_version()
    #ap.change_fw_setting("10.1.65.51", "5.2.0.0.5500.R710/rcks_fw.bl7")
    #ap.update_ap_firmware()
    #ap.login_any(ip="10.1.65.82", sz_cluster_name="bdc2", apzone_username="admin", apzone_passwd="ruckus1!")
    #ap.verify_ap_firmware_version('5.2.0.0.5500')
    #ap.login(ip='10.1.65.80', username='bala', password='bala')
    #ap.ap_ssh_write(cmd="get scg")
    #print ap.execute_shell_cmd('rkscli -c "get wlanlist"', restore_rkscli="no")
   
    ap.logout()
