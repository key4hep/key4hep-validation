#!/usr/bin/python
# -*- coding:utf-8 -*-

import subprocess
import time, datetime, os
from valprod.utils.monitors import *
from valprod.workflow.Process import Process,status

class MonitoredProcess(Process, BaseMonitor):

  def __init__(self, name, cmd, cfg):
    Process.__init__(self, name, cmd, cfg)
    BaseMonitor.__init__(self)

    # Set up monitoring time interval
    self.interval = self.cfg.getAttr('timeInterval')
    assert type(self.interval) == int or type(self.interval) == float, 'attribute time interval must be a number'
    assert self.interval <= 10 and self.interval >= 0.3, 'attribute time interval must be a number between 0.3 and 10'

    # Create monitors
    monitor_map = {'CPUMonitor': CpuMonitor, 'VIRMonitor': VirtMonitor, 'RESMonitor': ResMonitor}
    for k,v in monitor_map.items():
      if self.cfg.getAttr(k):
        self.monitorList.append(v(self.interval, self.cfg.getAttr('MonBackend'), self.name))

    self.stdout = self.stderr = open(self.logFileName, 'wb+')

  def run(self):
    print('Running test: %s' % self.name)
    print(self.executable)
    self.start = datetime.datetime.now()
    self.process = subprocess.Popen(args = self.executable, stdout = self.stdout, stderr = self.stderr)
    self.pid = self.process.pid
    while True:
      time.sleep(self.interval)
      if not self.process.poll() == None:
        break
      for monitor in self.monitorList:
        monitor.do(self.pid)
      if not self._checkLimit():
        break
    for monitor in self.monitorList:
      monitor.done()
    self._burnProcess()
    if self.status == status.SUCCESS and self.name:
      self.stdout.close()
      self._parseLogFile()
    if not self.genLog:
      os.remove(self.logFileName)

  def _parseLogFile(self):
    if self.logParser:
      result, self.fatalLine = self.logParser.parseFile(self.logFileName)
      if not result:
        self.status = status.FAIL
