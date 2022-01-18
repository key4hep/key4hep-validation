import copy
import sys
from valprod.workflow.MonitoredProcess import MonitoredProcess
from valprod.workflow.Process import Process

class TestWrapper:

  def __init__(self, name, cmd, cfg, **kwa):
    self.subprocess = None
    self.cfg = copy.deepcopy(cfg)
    self.cfg.update(**kwa)

    # Setup sub-process
    for attr in ['CPUMonitor', 'RESMonitor', 'VIRMonitor']:
      if self.cfg.getAttr(attr):
        self.subprocess = MonitoredProcess(name, cmd, self.cfg)
        break
    if not self.subprocess: self.subprocess = Process(name, cmd, self.cfg)

    # Setup plot reference
    self.plotTester = None
    plotRef = self.cfg.getAttr('plotRef')
    if plotRef:
      assert type(plotRef) == str or type(plotRef) == list
      from valprod.utils.PlotTester import PlotTester
      self.plotTester = PlotTester(self.cfg, plotRef)

  def run(self):
    self.subprocess.run()
    ok, summary = self.subprocess.outcome()
    # If process ends succefully, invoke plotTester, if there's one
    if ok and self.plotTester:
      ok, dec = self.plotTester.run()
    return ok, summary
