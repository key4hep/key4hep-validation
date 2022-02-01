#!/usr/bin/python
# -*- coding:utf-8 -*-

import subprocess
import time, datetime, os
import json
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

    # PRMON testing - we do set these up for compatibility, but they will be filled in a different way
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

    # Patch to use prmon, once we know the PID of the main monitored
    # task we ask prmon to monitor it for us
    prmon_interval = int(self.interval) if int(self.interval) > 0 else 1
    prmon_cmd = ['prmon', '--interval', str(prmon_interval), '--pid', str(self.pid)]
    prmon_subprocess = subprocess.Popen(args = prmon_cmd)
    while True:
      time.sleep(self.interval)
      if not self.process.poll() == None:
        break
      # PRMON loop - read the JSON snapshot file
      try:
        with open('prmon.json_snapshot') as prmon_snapshot:
          prmon_json = json.load(prmon_snapshot)
          print(prmon_json)
          # Now loop over each of the old style monitor classes and push in a prmon value
          # (This selection code scales horribly - convert to a dictionary!)
          for monitor in self.monitorList:
            print(monitor.monitor_name)
            if monitor.monitor_name == 'CPURate':
              monitor.push(prmon_json['Max']['utime'] + prmon_json['Max']['stime'])
            elif monitor.monitor_name == 'VirMem':
              monitor.push(prmon_json['Max']['vmem'])
            elif monitor.monitor_name == 'ResMem':
              monitor.push(prmon_json['Max']['rss'])
      except FileNotFoundError:
        print("Snapshot not found")
        pass
      except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e.msg}")
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
