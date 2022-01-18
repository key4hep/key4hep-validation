## Use valprod to build unit test cases

### Via the jMonitor command

The jMonitor command monitors the executable by adding a thin shell on top of it.
Example:

`jMonitor runSimulation.exe`

The detailed usage:
```
usage: jMonitor [-h] [-T MAXTIME] [-WT WALLTIME] [-M MAXVIR] [--enable-parser]
                [-p FATALPATTERN] [--enable-monitor] [-i INTERVAL]
                [-b {root,matplotlib}] [--enable-plotref] [-f PLOTREFFILE]
                [-o PLOTREFOUTPUT] [-m {Kolmogorov,Chi2}] [-c HISTTESTCUT]
                [--gen-log] [-n NAME]
                command

positional arguments:
  command               job to be monitored

optional arguments:
  -h, --help            show this help message and exit
  -T MAXTIME, --max-time MAXTIME
                        Time limit of process (s), if exceeded, process will
                        be killed
  -WT WALLTIME, --walltime WALLTIME
                        Time limit of process (hh:mm:ss) for PBS, if exceeded,
                        process will be killed
  -M MAXVIR, --max-memory MAXVIR
                        Memory limit of process (Mb), if exceeded, process
                        will be killed
  --enable-parser       If enabled, log of the process will be parsed
  -p FATALPATTERN, --pattern FATALPATTERN
                        Python re patterns for the parser
  --enable-monitor      If enabled, process will be monitored (memory, cpu)
  -i INTERVAL, --interval INTERVAL
                        Time interval for monitor
  -b {root,matplotlib}, --monitor-backend {root,matplotlib}
                        Backend for drawing monitoring figures
  --enable-plotref      If enabled, results of the process will be compared
  -f PLOTREFFILE, --plotref-files PLOTREFFILE
                        reference file for plot testing
  -o PLOTREFOUTPUT, --plotref-output PLOTREFOUTPUT
                        output root file for plot comparison
  -m {Kolmogorov,Chi2}, --histtest-method {Kolmogorov,Chi2}
                        Method of histogram testing
  -c HISTTESTCUT, --histtest-cut HISTTESTCUT
                        P-Value cut for histogram testing
  --gen-log             whether to generate log file
  -n NAME, --name NAME  name of the job
```
