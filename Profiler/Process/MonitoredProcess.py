#!/usr/bin/python
# -*- coding:utf-8 -*-

import subprocess
import time, datetime
import os
import types
from Profiler.Utils import *
from Process import *

class MonitoredProcess(Process, BaseMonitor):

  def __init__(self, name, cmd, cfg):
    Process.__init__(self, name, cmd, cfg)
    BaseMonitor.__init__(self)

    self.interval = self.cfg.getAttr('timeInterval')
    assert type(self.interval) == types.IntType or type(self.interval) == types.FloatType, 'attribute time interval must be a number'
    assert self.interval <= 10 and self.interval >= 0.3, 'attribute time interval must be a number between 0.3 and 10'
    if self.cfg.getAttr('CPUMonitor'):
      self.monitorList.append(CpuMonitor(self.interval))
    if self.cfg.getAttr('VIRMonitor'):
      self.monitorList.append(VirtMonitor(self.interval))
    if self.cfg.getAttr('RESMonitor'):
      self.monitorList.append(ResMonitor(self.interval))
    self.rootFileName = self.name + '_mem.root'
    self.stdout = self.stderr = open(self.logFileName, 'wb+')

  def run(self):
    self.start = datetime.datetime.now()
    self.process = subprocess.Popen(args = self.executable, shell = self.shell, stdout = self.stdout, stderr = self.stderr)
    self.pid = self.process.pid
    while True:
      time.sleep(self.interval)
      if not self.process.poll() == None:
        break
      for monitor in self.monitorList:
        monitor.do(self.pid)
      if not self._checkLimit():
        break
    self._createOutput()
    for monitor in self.monitorList:
      monitor.done()
      writeMHist(monitor.getHist(), self.rootFile)
    self._burnProcess()
    if self.status == status.SUCCESS and self.name:
      self.stdout.close()
      self._parseLogFile()
    if not self.genLog:
      os.remove(self.logFileName)

  def _parseLogFile(self):
    result, self.fatalLine = self.logParser.parseFile(self.logFileName)
    if not result:
      self.status = status.FAIL
