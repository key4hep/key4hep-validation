#!/usr/bin/python

import ROOT
from . shellUtil import *

class BaseMonitor():

  def __init__(self):
    self.interval = 1
    self.monitorList = []
    self.rootFileName = None
    self.rootFile = None
    self.pid = None

  def _createOutput(self):
    if not self.rootFileName:
      self.rootFileName = "result.root"
    self.rootFile = ROOT.TFile(self.rootFileName, "recreate")
    self.rootFile.cd()

class PidMonitor():
  
  def __init__(self, interval):
    self.interval = interval
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
    self.hist = ROOT.TH1F(self.name, self.title, ntime + 1, 0., ntime * self.interval)
    self.hist.GetXaxis().SetTitle(self.xtitle)
    self.hist.GetYaxis().SetTitle(self.ytitle)
    
    for i in range(ntime):
      self.hist.SetBinContent(i, self.results[i])

  def getHist(self):
    return self.hist

class VirtMonitor(PidMonitor):

  def __init__(self, interval):
    self.name = "Virtual"
    self.title = "Virtual Memory Usage"
    self.xtitle = "Time usage [s]"
    self.ytitle = "Virtual Memory Usage [MB]"
    self.fun = "GetVirUse"
    PidMonitor.__init__(self,interval)
    

class ResMonitor(PidMonitor):

  def __init__(self, interval):
    self.name = "Resident"
    self.title = "Resident Memory Usage"
    self.xtitle = "Time usage [s]"
    self.ytitle = "Resident Memory Usage [MB]"
    self.fun = "GetMemUse"
    PidMonitor.__init__(self,interval)


class CpuMonitor(PidMonitor):

  def __init__(self, interval):
    self.name = "CPU"
    self.title = "CPU Utilization"
    self.xtitle = "Time usage [s]"
    self.ytitle = "CPU Utilization [/%]"
    self.fun = "GetCpuRate"
    PidMonitor.__init__(self,interval)

