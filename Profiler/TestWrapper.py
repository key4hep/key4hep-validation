import Utils
import copy
import types
import sys
from Process import *

class TestWrapper:

  def __init__(self, name, cmd, cfg, **kwa):
    self.subprocess = None
    self.cfg = copy.deepcopy(cfg)
    self.cfg.update(**kwa)

    # Setup sub-process
    if self.cfg.getAttr('CPUMonitor') or self.cfg.getAttr('RESMonitor') or self.cfg.getAttr('VIRMonitor'):
      self.subprocess = MonitoredProcess(name, cmd, self.cfg)
    else:
      self.subprocess = Process(name, cmd, self.cfg)

    # Setup plot reference
    self.plotTester = None
    plotRef = self.cfg.getAttr('plotRef')
    if plotRef:
      assert type(plotRef) == types.StringType or type(plotRef) == types.ListType
      self.plotTester = Utils.PlotTester(self.cfg, plotRef)

  def run(self):
    self.subprocess.run()
    res, dec = self.subprocess.outcome()
    # If process ends succefully, invoke plotTester, if there's one
    if res and self.plotTester:
      res, dec = self.plotTester.run()
    return res, dec
