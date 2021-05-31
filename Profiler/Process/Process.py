import datetime
import os,sys
import select
import subprocess
from Profiler.Utils import *

class status:
  (SUCCESS, FAIL, TIMEOUT, OVERFLOW, ANR) = range(0, 5)
  DES = {
          FAIL: 'Return code is not zero',
          TIMEOUT: 'Run time exceeded',
          OVERFLOW: 'Memory overflow',
          ANR: 'Not responding'
        }
  @staticmethod
  def describe(stat):
    if status.DES.has_key(stat):
      return status.DES[stat]
    

class Process:

  def __init__(self, name, exe, cfg):

    print('')
    self.cfg = cfg
    self.name = name or 'test'
    self.logParser = cfg.getAttr('parser') and Parser(cfg) or None
    if self.cfg.getAttr('shell'):
      self.executable = exe
      self.shell = True
    else:
      self.executable = exe.split()
      self.shell = False
    self.genLog = self.cfg.getAttr('genLog')

    # Log file name depends on what we are running
    self.logFileName = self.cfg.getAttr('logName') or self.name + '.log'
    if self.cfg.getAttr('step'):
        self.logFileName = self.cfg.getAttr('step')+'.log'

    # Merge stdout and stderr
    self.stdout = self.stderr = subprocess.PIPE
    self.process = None
    self.pid = None
    self.returncode = None
    self.status = None
    self.timeout = self.cfg.getAttr('timeout')
    if self.timeout:
      assert type(self.timeout) == int, 'attribute timeout must be an int'
    self.timeLimit = self.cfg.getAttr('maxTime')
    if self.timeLimit:
      assert type(self.timeLimit) == int, 'attribute maxTime must be an int'
    self.virLimit = self.cfg.getAttr('maxVIR')
    if self.virLimit:
      assert type(self.virLimit) == int, 'attribute maxVIR must be an int'
    self.duration = None
    self.start = None
    self.killed = None
    self.fatalLine = None

  def run(self):
    self.start = datetime.datetime.now()
    self.process = subprocess.Popen(args = self.executable, shell = self.shell, stdout = self.stdout, stderr = subprocess.STDOUT)
    self.pid = self.process.pid
    if self.genLog:
      # TODO
      # * allow specify log directory
      # * should support directory structure

      logDir = os.path.dirname(self.logFileName)
      if len(logDir) and not os.path.exists(logDir):
        os.makedirs(logDir)
      logFile = open(self.logFileName, 'w')
    while True:
      fs = select.select([self.process.stdout], [], [], self.timeout)
      if not fs[0]:
        # No response
        self.status = status.ANR
        self._kill()
        break
      if self.process.stdout in fs[0]:
        # Incoming message to parse
        data = os.read(self.process.stdout.fileno(), 1024)
        if not data:
          break
        # If it is called in analysis step, we print the log info to screen
        if self.cfg.getAttr("step"):
          for l in data.splitlines(): print("[%d]: "%self.pid, l)
        if self.genLog:
          logFile.write(data)
        if self.logParser:
          if not self._parseLog(data):
            self.status = status.FAIL
            self._kill()
            break
        if not self._checkLimit():
          break
    self._burnProcess()
    self._checkLimit()
    if self.genLog:
      logFile.close()

  def getDuration(self):
    return self.duration

  def _checkLimit(self):
    self.duration = (datetime.datetime.now() - self.start).seconds
    if self.timeLimit and (self.duration >= self.timeLimit):
      # Time out
      self.status = status.TIMEOUT
      self._kill()
      return False
    if self.virLimit and (self._getVirt() >= self.virLimit):
      # Memory overflow
      self.status = status.OVERFLOW
      self._kill()
      return False
    return True

  def _kill(self):
    if not self.process:
      return
    import os, signal
    try:
      os.kill(self.pid, signal.SIGKILL)
      os.waitpid(-1, os.WNOHANG)
    except:
      pass

  def _parseLog(self, data):
    result, self.fatalLine = self.logParser.parse(data)
    return result

  def _burnProcess(self):
    self.returncode = self.process.wait()
    if self.status:
      return
    if 0 == self.returncode:
      self.status = status.SUCCESS
    else:
      self.status = status.FAIL
    #FIXME: it seems that root macro process won't give a 0 return code
    if type(self.executable) == list and self.executable[0] == 'root':
      self.status = status.SUCCESS
    if type(self.executable) == str and self.executable.startswith('root'):
      self.status = status.SUCCESS

  def _getVirt(self):
    if not self.pid:
      return 0
    else:
      return GetVirUse(self.pid)

  def outcome(self):
    if self.status == status.SUCCESS:
      return True, ''
    if self.fatalLine:
      return False, 'FatalLine: ' + self.fatalLine
    return False, status.describe(self.status)
