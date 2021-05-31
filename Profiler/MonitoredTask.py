#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import ROOT
from Valprod.Utils import *
from Sniper import Task

class TaskMonitor(Task, BaseMonitor):

  def __init__(self, name):
    Task.__init__(self, name)
    BaseMonitor.__init__(self)
    self.pid = os.getpid()
    self.exeCount = 0

  def setInterval(self, value):
    self.interval = value

  def setOutput(self, value):
    self.rootFileName = value

  def initialize(self):
    self.monitorList.append(CpuMonitor(self.interval))
    self.monitorList.append(VirtMonitor(self.interval))
    self.monitorList.append(ResMonitor(self.interval))
    return Task.initialize(self)

  def execute(self):
    st = Task.execute(self)
    self.exeCount += 1
    if self.exeCount == self.interval:
      self.exeCount = 0
      for monitor in self.monitorList:
        monitor.do(self.pid)
    return st

  def finalize(self):
    self._createOutput()
    for monitor in self.monitorList:
      monitor.done()
      writeMHist(monitor.getHist(), self.rootFile)
    return Task.finalize(self)
