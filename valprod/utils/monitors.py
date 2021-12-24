import matplotlib.pyplot as plt
import numpy as np
from valprod.utils.shellUtil import *

class BaseMonitor():

  def __init__(self):
    self.interval = 1
    self.monitorList = []
    self.pid = None

class PidMonitor():
  
  def __init__(self, interval, name):
    self.interval = interval
    self.test_name = name
    self.min = 0.
    self.max = 1e15
    self.results = []
    self.hist = None

  def do(self,pid):
    value = eval(self.fun + "(%s)" % pid)
    if value < self.min:
      self.min = value
    if value > self.max:
      self.max = value
    self.results.append(value)

  def done(self):
    ntime = len(self.results)
    time_seq = np.linspace(0, ntime * self.interval, ntime)
    plt.clf()
    plt.plot(time_seq, self.results)
    plt.xlabel(self.xtitle)
    plt.ylabel(self.ytitle)
    plt.title(self.title)
    plt.savefig(self.test_name + '_' + self.monitor_name + '.png')

class VirtMonitor(PidMonitor):

  def __init__(self, interval, name):
    self.title = "Virtual Memory Usage"
    self.xtitle = "Time [s]"
    self.ytitle = "Virtual Memory Usage [MB]"
    self.fun = "GetVirUse"
    self.monitor_name = "VirMem"
    PidMonitor.__init__(self,interval, name)
    

class ResMonitor(PidMonitor):

  def __init__(self, interval, name):
    self.title = "Resident Memory Usage"
    self.xtitle = "Time [s]"
    self.ytitle = "Resident Memory Usage [MB]"
    self.fun = "GetMemUse"
    self.monitor_name = "ResMem"
    PidMonitor.__init__(self,interval, name)


class CpuMonitor(PidMonitor):

  def __init__(self, interval, name):
    self.title = "CPU Utilization"
    self.xtitle = "Time [s]"
    self.ytitle = "CPU Utilization [/%]"
    self.fun = "GetCpuRate"
    self.monitor_name = "CPURate"
    PidMonitor.__init__(self,interval, name)
