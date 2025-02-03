import time
import select
import os
import re
import socket
import paramiko
from robot.libraries.BuiltIn import BuiltIn
from AutoAcc_Logger import AutoAcc_Logger
log = AutoAcc_Logger()

class SshLibraryV2:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        # Create a new SSH client
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.transport = None
        self.channel = None
        self.sftp = None
        self.server = None
        self.sock = None
        self.login_type = None
        self.channel_recvbufsize = 4096
        self.channel_select_tout = 5
        self.scp_select_timeout = 15
        self.recvbuf = None
        self.is_pcapclient = False
        self.is_closed = False
        self.prompt = None
        self.login_type = "interactive"
        self.server = None
        self.buffer = ""
        self.timeout = 30
        self.newline = '\n'
        self.term_type = None
        self.width = None
        self.height = None
        self.path_separator = None
        self.encoding = None

    def __del__(self):
        try:
            self.channel.close()
            self.transport.close()
            del self.ssh
            del self.channel
            del self.transport
        except:
            pass

    def _bind_address(self, bind_addr, dest_addr, port=22):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((bind_addr, 0))           # set source address
        sock.connect((dest_addr, port))       # connect to the destination address
        return sock

    def ssh_connect(self, server, username,pub_file=None,pub_file_type=None,
                    prompt='$', bind_addr=None,fips_enabled=False,no_password=False,password=None,
                    enable_sftp="0",port=22):
        """
        Description :
            Connect to SSH Server

        Mandatory params :
            server (String) : Server name
            username (String) : Username
            password (String) : Password

        Optional params :
            prompt (String) : Expected prompt after login is success
            bind_addr (String) : Binding address for the client
            enable_sftp (String): enable sftp to server over this connection (enable: "1")

        Response :
            Return data recvd after login
        """
        gss_kex=False
        gss_deleg_creds=True

        self.server = server
        self.prompt = prompt

        if bind_addr:
            self.sock = self._bind_address(bind_addr, server, port)
            if not self.sock:
                raise Exception("Bind to local address: %s or connect to server: %s failed" % (bind_addr, server))

        if fips_enabled:
            password = ""

        if pub_file:
            self.ssh.connect(server, username=username, key_filename=pub_file, sock=self.sock, port=port)

        elif no_password is False:
            try:
                self.ssh.connect(server, username=username, password=password,
                                 sock=self.sock, port=port)
            except paramiko.SSHException as err:
                log.info("Paramiko SSH Exception occurred :: %s !! so will try without ssh-agent !!" % err)
                self.ssh_close()
                time.sleep(5)
                self.ssh.connect(server, username=username, password=password,
                                 sock=self.sock, allow_agent=False, port=port)
        else:
            if ":" in server:
                self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((server, port))
            self.ssh._transport = paramiko.Transport(self.sock, gss_kex=gss_kex, gss_deleg_creds=gss_deleg_creds)
            self.ssh._transport.start_client()
            self.ssh._transport.auth_none(username=username)

        self.transport = self.ssh.get_transport()
        self.channel = self.transport.open_session()
        self.channel.get_pty()
        self.channel.invoke_shell()

        if enable_sftp == "1":
            log.info("Enabling SFTP on existing paramiko connection")
            try:
                self.sftp = self.ssh.open_sftp()
            except Exception as e:
                log.error("Error while enabling SFTP on the open connection")
                raise e

        try:
            if self.login_type == "interactive":
                log.info("Connect: Waiting for prompt: %s" % prompt)
                return self.ssh_read_until_prompt(prompt)
            else:
                raise Exception("login_type: %s not implemented yet!" % self.login_type)
        except Exception as e:
            raise e

    def _read(self, readbufsize=None, allow_emptybuf=False):
        try:
            _buflen = 0
            if readbufsize:
                _buflen = int(readbufsize)
            else:
                _buflen = int(self.channel_recvbufsize)

            if (_buflen <= 0):
                raise Exception("Invalid readbufsize: %s" % _buflen)


            buf = (self.channel.recv(_buflen)).decode('utf-8', "ignore")
            #print(str(buf))
            #log.info("Rx: %s" % buf)
            if len(buf) == 0 and allow_emptybuf == False:
                log.error("EOF recvd on channel")
                return None
            else:
                return buf
        except socket.timeout as e:
            log.error("socket receive timeout")
            raise e

    def _read_until(self, expected, timeout=None, readbufsize=None, is_prompt=False, allow_emptybuf=False):
        _timeout = 0
        if not expected:
            raise Exception("_read_until: expected value must not be empty")
        if not timeout:
            _timeout = int(self.timeout)
        else:
            _timeout = int(timeout)

        recvbuf = ""
        is_match = False

        while True:
            r, w, e = select.select([self.channel], [], [], _timeout)
            if self.channel in r:
                try:
                    buf = self._read(readbufsize, allow_emptybuf=allow_emptybuf)

                    if buf or allow_emptybuf:
                        #log.info("The buf is {}".format(str(buf)))
                        recvbuf = recvbuf + buf
                        if is_prompt:
                            #do not use regex. for e,g., prompt '$' means endofline in regex instead of actual character '$'
                            if expected in recvbuf:
                                is_match = True
                                break
                        elif re.search(expected, recvbuf, re.I|re.M):
                            is_match = True
                            break
                        else:
                            #nothing to do
                            pass
                    else:
                        return None
                except socket.timeout:
                    log.info(recvbuf)
                    log.error("socket recv timeout")
                    return None
            else:
                log.info(recvbuf)
                log.warning("select() timedout on read channel")
                return None

        #log.info(recvbuf)

        if is_match:
            return recvbuf
        else:
            return None

    def _write(self, data):
        #log.info(data)
        self.channel.sendall(data)

    def ssh_write(self, line):
        """
        Description :
            API to do ssh write. A newline is automatically appended

        Mandatory params :
            line (String) : Line

        Response :
            return data until new line after reading from SSH channel
        """
        self._write(line + self.newline)
        res =  self._read_until(self.newline, readbufsize=1) #read byte by byte until newline is matched
        print("Response for write")
        if res:
            log.info(res)
        return res

    def ssh_close(self):
        """
        Description :
            API to Close SSH connection to remote

        Response :
            True or False
        """
        try:
            if self.login_type == "interactive":
                log.info("Shutdown ssh channel to server: %s" % self.server)
                self.channel.shutdown(2)
            log.info("Closing ssh to server: %s..." % self.server)
            self.ssh.close()
            self.__del__()
            self.__init__()

            log.info("Closed ssh to server: %s..." % self.server)
            self.is_closed = True
            return True
        except Exception as err:
            log.error("Exception - %s" % str(err))
            return False

    def ssh_read_until_regex(self, regex, timeout=None, allow_emptybuf=False):
        """
        Description :
            API to read SSH until the given regular expression is matched

        Mandatory params :
            regex (String) : Expected regular expression

        Optional params :
            timeout (String) : Timeout period

        Response :
            Data recvd from remote
        """
        buf = ""
        try:
            buf = self._read_until(regex, timeout=timeout, allow_emptybuf=allow_emptybuf)
            if not buf:
                raise Exception("Expected regex: %s not matched" % regex)
        except Exception as e:
            raise e

        return buf

    def ssh_read_until_prompt(self, prompt, timeout=None, allow_emptybuf=False):
        """
        Description :
            API to read SSH until given prompt is found

        Mandatory params :
            prompt (String) : Prompt character

        Optional params :
            timeout (String) : Timeout period

        Response :
            Data recvd from remote
        """
        buf = ""
        try:
            buf = self._read_until(prompt, timeout=timeout, is_prompt=True, allow_emptybuf=allow_emptybuf)
            #log.info("--------------------------------------------------------------------------------------------------------------")
            # log.info(buf)
            # #log.info("--------------------------------------------------------------------------------------------------------------")
            if not buf:
                raise Exception("Expected Prompt: %s not found" % prompt)
        except Exception as e:
            raise e

        return buf

    def file_exists(self, path):
        """
        Description:
            Check File exists or not in Remote machine

        Mandatory Params :
            path (String): Complete File path to check exists or not

        Optional Params:
            None

        Response:
            True or False
        """

        try:
            self.sftp.stat(path)
        except IOError:
            log.info("File does not exist")
            return False
        else:
            log.info("File exist")
            return True

    def read_file(self, path):
        """
        Description :
            Read remote file and return file sciContent

        Mandatory Params :
            path (String): Complete File path to read and return sciContent

        Optional Params :
            None

        Response :
            Return file content
        """

        if self.file_exists(path):
            try:
                file_obj = self.sftp.open(path)
                return file_obj.read()
            except Exception as  e:
                log.error("Error while reading the file")
                log.error(str(e))
                raise e
        else:
            raise Exception("File does not exist")

    def delete_file(self, path):
        """
        Description :
            Deletes the file on remote machine

        Mandatory Params :
            path (String): Complete File path

        Optional Params :
            None

        Response
            None
        """

        if self.file_exists(path):
            try:
                return self.sftp.remove(path)
            except Exception as e:
                log.error("Error while trying to delete the file")
                log.error(str(e))
                raise e
        else:
            log.error("File does not exist")
            raise Exception("File does not exist")

    def list_files(self, path):
        """
        Description :
            List all the files in the directory

        Mandatory Params :
            path (String): Complete File path

        Optional Params :
            None

        Response :
            Returns all the files present in the path
        """

        if self.file_exists(path):
            try:
                #dir_obj = self.sftp.open(path)
                #return dir_obj.listdir()
                return self.sftp.listdir(path)
            except Exception as e:
                log.error("Error while trying to list the directory")
                log.error(str(e))
                raise e
        else:
            raise Exception("File does not exist")

    def ssh_set_client_configuration(self, timeout=None, prompt=None, newline=None):
        """
        Description :
            Use this API to set ssh client configuration

        Mandatory params :
            None

        Optional params :
            timeout (String) : Timeout period
            prompt (String) : Prompt
            newline (String) : Newline

        Response :
            None
        """

        if prompt:
            self.prompt = prompt
        if timeout:
            self.timeout = int(timeout)
        if newline:
            self.newline = newline

    def scp_download(self, toaddr, username, password, capture_rdir, capture_rfile,
            capture_ldir, capture_lfile, expected_prompt=None,
            scp_cmd_output_prompt_list=[r"\(yes/no\)\?\s*|\(yes/no/\[fingerprint\]\)\?\s*", r"Password:\s*"], conn_yes_or_no="yes", timeout=None):
        """
        Description:
        API to download file from remote server to local machine  by executing SCP command on remote

        Mandatory Params :
        toaddr (String): target ip address to transfer
        username (String): username of target machine
        password (String): password
        capture_rdir (String): remote directory - from
        capture_rfile (String): remote file name - from
        capture_ldir (String): local directory - to
        capture_lfile (String): local file - to

        Optional Params :
        expected_prompt (String): expected prompt after executing scp command
        scp_cmd_output_prompt_list (List): list of expected prompt after scp command excution. default - [r"\(yes/no\)\?\s*", r"Password:\s*"]
        conn_yes_or_no (String): enter yes|no or y|n based on output. default - yes
        timeout (String): number of seconds to wait for prompt after scp command is executed

        Response :
        True is success else Error Exception
        """
        prompt = ""
        _capture_local_filename = capture_ldir + "/" + capture_lfile
        _capture_remote_filename = capture_rdir + "/" + capture_rfile
        if not self.channel:
            raise Exception("failed to perform scp operation from remote as SSH is not alive to remote node")
        try:
            if (not toaddr) or (not username) or (not password):
                raise Exception("scp_download: Error - Invalid param")

            if self.login_type == "interactive":
                if not expected_prompt:
                    prompt = self.prompt
                else:
                    prompt = expected_prompt

                #expect following prompts from scp command on remote
                scp_expect = scp_cmd_output_prompt_list
                scp_cmd = 'scp' + ' ' + _capture_remote_filename + ' ' + username + '@' + toaddr + ':' + \
                        _capture_local_filename

                self.ssh_write(scp_cmd)

                recvbuf = ""
                buf = ""
                _timeout = 0

                if timeout:
                    _timeout = int(timeout)
                else:
                    _timeout = int(self.scp_select_timeout)

                if (_timeout <= 0):
                    raise Exception("Invalid scp select timeout value: %s" % _timeout)

                while True:
                    r, w, e = select.select([self.channel], [], [], _timeout)
                    if self.channel in r:
                        try:
                            buff = self.channel.recv(self.channel_recvbufsize)
                            if type(buff) == bytes:
                                buf =  buff.decode()
                            else:
                                buf=buff

                            if len(buf) == 0:
                                raise Exception("Error! EOF recvd on channel")
                            recvbuf = recvbuf + buf

                            if re.search(scp_expect[0], recvbuf, re.I|re.M):
                                self.ssh_write(conn_yes_or_no)
                                recvbuf = ""
                                continue
                            elif re.search(scp_expect[1], recvbuf, re.I|re.M):
                                self.ssh_write(password)
                                recvbuf = ""
                                break
                            else:
                                #go and read more data
                                pass
                        except socket.timeout:
                            raise Exception("scp_download: Error! Socket recv timeout")
                    else:
                        log.error("select() timedout on read channel")
                        raise Exception("Expected String not found in recvd data on SSH channel")

                #wait for prompt after entering password
                res = self.ssh_read_until_prompt(prompt)
                if res:
                    if re.search("Permission denied", res, re.I|re.S):
                        raise Exception("scp_download: Permission denied")
                    elif re.search("No such file or directory", res, re.I|re.S):
                        raise Exception("scp_download: No such file or directory")
                    else:
                        #log.info("scp_download: scp successful!!")
                        return True
        except Exception as e:
            raise e

    def replace_string_in_file(self,file_path, old_string, new_string):
        # Read the entire file content
        remote_file = self.sftp.open(file_path,'r')
        file_content = remote_file.read()
        file_content = file_content.decode('utf-8')
        print(type(file_content))
        remote_file = self.sftp.open(file_path, 'w')
        # Replace the old string with the new string
        new_content = file_content.replace(old_string, new_string)

        remote_file.write(new_content)
        remote_file.close()


if __name__ == '__main__':
    obj = SshLibraryV2()
    obj.ssh_connect(server="server_ip", username="administrator", password="ruckus", prompt='$')
    obj.ssh_write("cd")
    obj.ssh_close()
    #obj.ssh_read_until_prompt()
    #obj.ssh_write("ls -l")
    #obj.ssh_read_until_prompt(prompt="#", timeout=None)
    #obj.file_exists(path="/opt/tftpboot/capture.pcap0")
