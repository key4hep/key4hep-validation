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
    assert self.interval <= 60 and self.interval >= 0.3, 'attribute time interval must be a number between 0.3 and 60'

    # Create monitors
    self.usePrmon = self.cfg.getAttr('prmon')
    monitor_map = {'CPUMonitor': CpuMonitor, 'VIRMonitor': VirtMonitor, 'RESMonitor': ResMonitor}
    for k,v in monitor_map.items():
      if self.cfg.getAttr(k):
        self.monitorList.append(v(self.interval, self.cfg.getAttr('MonBackend'), self.name))

    self.stdout = self.stderr = open(self.logFileName, 'wb+')

  def run(self):
    self._start_process()

    # Use prmon to monitor the process
    if self.usePrmon:
      prmon_output = self.name + '.prmon'
      prmon_cmd = ['prmon', '--interval', str(self.interval), '--pid', str(self.pid), '--filename', prmon_output]
      try:
        prmon_subprocess = subprocess.Popen(args = prmon_cmd)
      except FileNotFoundError:
        print("prmon not found. Switching to default monitor")
        self.usePrmon = False

    # The main loop. Wait until the process finishes or the limit is reached
    while True:
      time.sleep(self.interval)
      if not self.process.poll() == None:
        break
      if not self.usePrmon:
        # Collect metrics for default monitors
        for monitor in self.monitorList:
          monitor.do(self.parent_pid, self.child_pids)
      if not self._checkLimit():
        break

    ## Draw profiling figures
    if self.usePrmon:
      prmon_rc = prmon_subprocess.wait()
      if 0==prmon_rc:
        # Draw figures using the prmon_plot.py tool
        os.system("prmon_plot.py --input %s --xvar wtime --yvar vmem,pss,rss,swap --yunit GB" % prmon_output)
        os.system("prmon_plot.py --input %s --xvar wtime --yvar vmem,pss,rss,swap --diff --yunit MB" % prmon_output)
        os.system("prmon_plot.py --input %s --xvar wtime --yvar utime,stime --yunit SEC --diff --stacked" % prmon_output)
    else:
      for monitor in self.monitorList:
        monitor.done()
    
    ## Check if the process ends successfully
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
