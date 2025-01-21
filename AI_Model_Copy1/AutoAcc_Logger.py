import logging
import inspect
from datetime import datetime
import os
import  sys
from modulefinder import ModuleFinder


logging.basicConfig(format="%(levelname)s %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

class AutoAcc_Logger:
    #ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, mode="", enableLevel_i=1, enableLevel=1):
        """
        Initialize a logging record with interesting information.
        """
        self.mode=mode
        self.enableLevel_i = enableLevel_i
        self.enableLevel= enableLevel
        self.t = ""
        self.filename = ""
        self.d_enable = 1
        self.i_enable = 2
        self.e_enable = 4
        self.w_enable = 3
        # self.custom_logging()


    def custom_logging(self):
        ins= inspect.currentframe().f_back.f_back.f_back
        if ins!=None:
            (filenames, line_number, function_name, lines, index) = inspect.getframeinfo(ins)

        finder = ModuleFinder()
        finder.run_script(inspect.getframeinfo(inspect.currentframe().f_back.f_back)[0])
        for name, mod in finder.modules.items():
            logging.getLogger(name).setLevel(logging.ERROR)

        if (self.mode).lower()=="robot":
            self.t = " "
            if ins==None or function_name!="<module>":
                self.enableLevel_i=1
            else:
                self.enableLevel=3
        elif (self.mode).lower()=="python":
            self.t=None
            if ins==None or function_name!="<module>":
                self.enableLevel_i=1
            else:
                self.enableLevel=3
        else:
            if ins==None or function_name!="<module>":
                self.t=ins
                self.enableLevel_i=1
            else:
                t = inspect.currentframe().f_back.f_back.f_back.f_back
                self.t = t
                self.enableLevel=3


    def __convert_to_string(self,msg):
        if isinstance(msg, list) or isinstance(msg,tuple) or isinstance(msg,set):
            msg = ' '.join(msg)
        if isinstance(msg, dict):
            msg = ''.join(', '.join("%s=%r" % (key,val) for (key,val) in list(msg.items())))
        if isinstance(msg, int):
            msg = str(msg)
        return msg

    def __python_msg_format(self,msg):
         msg = " | "+"AutoAcc"+" | "+self.__datetime()+" | "+self.__find_lno_fname()+" | "+msg
         return msg

    def __robot_msg_format(self,msg):
         msg = " | "+"AutoAcc"+" | "+str(self.__find_lno_fname())+" | "+str(msg)
         return msg


    def debug(self, msg):
        if self.enableLevel_i<=self.d_enable or self.enableLevel<=self.d_enable:
            msg = self.__convert_to_string(msg)
            if self.t==None:
                msg = self.__python_msg_format(msg)
            else:
                msg = self.__robot_msg_format(msg)
            return logger.debug(msg)
        else:
            return 0

    def info(self, msg):
        if self.enableLevel_i<=self.i_enable or self.enableLevel<=self.i_enable:
            msg = self.__convert_to_string(msg)
            if self.t==None:
                msg = self.__python_msg_format(msg)
            else:
                msg = self.__robot_msg_format(msg)
            return logger.info(msg)
        else:
            return 0

    def error(self, msg):
        if self.enableLevel_i<=self.e_enable or self.enableLevel<=self.e_enable:
            msg = self.__convert_to_string(msg)
            if self.t==None:
                msg = self.__python_msg_format(msg)
            else:
                msg = self.__robot_msg_format(msg)
            return logger.error(msg)
        else:
            return 0

    def exception(self, msg):
        if self.enableLevel_i<=self.e_enable or self.enableLevel<=self.e_enable:
            msg = self.__convert_to_string(msg)
            if self.t==None:
                msg = self.__python_msg_format(msg)
            else:
                msg = self.__robot_msg_format(msg)
            return logger.error(msg)
        else:
            return 0

    def warning(self, msg):
        if self.enableLevel_i<=self.w_enable or self.enableLevel<=self.w_enable:
            msg = self.__convert_to_string(msg)
            if self.t==None:
                msg = self.__python_msg_format(msg)
            else:
                msg = self.__robot_msg_format(msg)
            return logger.warning(msg)
        else:
            return 0


    def __find_lno_fname(self):
        if __file__[-4:].lower() in ['.pyc', '.pyo']:
            _srcfile = __file__[:-4] + '.py'
        else:
            _srcfile = __file__
        _srcfile = os.path.normcase(_srcfile)

        f = self.__currentframe()
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = os.path.basename(co.co_filename)+":"+str(f.f_lineno)
            break
        return rv

    def __currentframe(self):
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except:
            return sys.exc_info()[2].tb_frame.f_back


    def __datetime(self):
        dt=datetime.now()
        date=dt.strftime("%m/%d/%Y")
        time=dt.strftime("%H:%M:%S")
        ms=dt.strftime("%f")
        ms=(int(ms)/1000)
        dt = "%s %s.%03d" % (str(date),str(time), ms)
        return dt
