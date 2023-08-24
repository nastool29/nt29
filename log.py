import logging
import os
import re
import threading
import time
from collections import deque
from html import escape
from logging.handlers import RotatingFileHandler

from config import Config

logging.getLogger('werkzeug').setLevel(logging.ERROR)
lock = threading.Lock()
LOG_QUEUE = deque(maxlen=500)
LOG_INDEX = 0

_loglevels = {
  "info": logging.INFO,
  "debug": logging.DEBUG,
  "error": logging.ERROR
}


class MessageCenterHandler(logging.Handler):
  """
  nastool 详细中心推送处理器
  """

  def __init__(self, stream=None):
    """
    Initialize the handler.
    """
    logging.Handler.__init__(self)

  def emit(self, record):
    """
    Emit a record.
    """
    try:
      level = _loglevels.get(record.levelname.lower())
      if level == logging.INFO or level == logging.WARN or level == logging.ERROR:
        _append_log_queue(record.levelname, self.format(record))
    except RecursionError:  # See issue 36272
      raise
    except Exception:
      self.handleError(record)


class Logger(logging.Logger):
  __config = None

  def __init__(self, name="app"):
    super().__init__(name)
    self.__config = Config()
    logtype = self.__config.get_config('app').get('logtype') or "console"
    loglevel = self.__config.get_config('app').get('loglevel') or "info"
    self.setLevel(level=_loglevels.get(loglevel))
    if logtype == "server":
      logserver = self.__config.get_config('app').get('logserver', '').split(':')
      if logserver:
        logip = logserver[0]
        if len(logserver) > 1:
          logport = int(logserver[1] or '514')
        else:
          logport = 514
        log_server_handler = logging.handlers.SysLogHandler((logip, logport),
                                                            logging.handlers.SysLogHandler.LOG_USER)
        log_server_handler.setFormatter(logging.Formatter('[%(filename)s:%(lineno)s]: %(message)s'))
        self.addHandler(log_server_handler)
    elif logtype == "file":
      # 记录日志到文件
      logpath = os.environ.get('NASTOOL_LOG') or self.__config.get_config('app').get('logpath') or ""
      if logpath:
        if not os.path.exists(logpath):
          os.makedirs(logpath)
        log_file_handler = RotatingFileHandler(filename=os.path.join(logpath, name + ".log"),
                                               maxBytes=5 * 1024 * 1024,
                                               backupCount=3,
                                               encoding='utf-8')
        log_file_handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s - [%(filename)s:%(lineno)s]: %(message)s'))
        self.addHandler(log_file_handler)
    # 记录日志到终端
    log_console_handler = logging.StreamHandler()
    log_console_handler.setFormatter(logging.Formatter('%(asctime)s\t%(levelname)s - [%(filename)s:%(lineno)s]: %(message)s'))
    self.addHandler(log_console_handler)
    self.addHandler(MessageCenterHandler())


def _append_log_queue(level, text):
  global LOG_INDEX, LOG_QUEUE
  with lock:
    text = escape(text)
    if text.startswith("【"):
      source = re.findall(r"(?<=【).*?(?=】)", text)[0]
      text = text.replace(f"【{source}】", "")
    else:
      source = "System"
    LOG_QUEUE.append({
      "time": time.strftime('%H:%M:%S', time.localtime(time.time())),
      "level": level,
      "source": source,
      "text": text})
    LOG_INDEX += 1


def getLogger(name="app"):
  return Logger(name=name)
