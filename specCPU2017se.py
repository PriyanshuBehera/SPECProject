import argparse
import sys
import os

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.params import NULL
from m5.util import addToPath, fatal, warn


addToPath('../')

# addToPath('../common')
# addToPath('../ruby')
# addToPath('../topologies')

# import Options
# import Ruby
# import Simulation
# import CacheConfig
# import MemConfig
# from Caches import *

import cpu2017

from common import Options
from common import Simulation
from common import CacheConfig
from common import CpuConfig
from common import ObjectList
from common import MemConfig
from common.FileSystemConfig import config_filesystem
from common.Caches import *
from common.cpu2000 import *


# Get paths we might need.  It's expected this file is in m5/configs/example.
config_path = os.path.dirname(os.path.abspath(__file__))
# printconfig_path
config_root = os.path.dirname(config_path)+"/common"
# print config_root
m5_root = os.path.dirname(config_root)
# print m5_root

multiprocesses = []



def addToMultipurpose(processname, procNum):
	if processname == 'perlbench':
		process = cpu2017.perlbenchObjs
	elif processname == 'bzip2':
		process = cpu2017.bzip2Objs
	elif processname == 'gcc':
		process = cpu2017.gccObjs
	elif processname == 'bwaves':
		process = cpu2017.bwavesObjs
	elif processname == 'gamess':
		process = cpu2017.gamessObjs
	elif processname == 'gamess2':
		process = cpu2017.gamess2Objs
	elif processname == 'gamess3':
		process = cpu2017.gamess3Objs
	elif processname == 'gamess4':
		process = cpu2017.gamess4Objs
	elif processname == 'mcf':
		process = cpu2017.mcfObjs
	elif processname == 'milc':
		process = cpu2017.milcObjs
	elif processname == 'zeusmp':
		process = cpu2017.zeusmpObjs
	elif processname == 'gromacs':
		process = cpu2017.gromacsObjs
	elif processname == 'cactusADM':
		process = cpu2017.cactusADMObjs
	elif processname == 'leslie3d':
		process = cpu2017.leslie3dObjs
	elif processname == 'namd':
		process = cpu2017.namdObjs
	elif processname == 'gobmk':
		process = cpu2017.gobmkObjs
	elif processname == 'dealII':
		process = cpu2017.dealIIObjs
	elif processname == 'soplex':
		process = cpu2017.soplexObjs
	elif processname == 'povray':
		process = cpu2017.povrayObjs
	elif processname == 'calculix':
		process = cpu2017.calculixObjs
	elif processname == 'hmmer':
		process = cpu2017.hmmerObjs
	elif processname == 'sjeng':
		process = cpu2017.sjengObjs
	elif processname == 'GemsFDTD':
		process = cpu2017.GemsFDTDObjs
	elif processname == 'libquantum':
		process = cpu2017.libquantumObjs
	elif processname == 'h264ref':
		process = cpu2017.h264refObjs
	elif processname == 'tonto':
		process = cpu2017.tontoObjs
	elif processname == 'lbm':
		process = cpu2017.lbmObjs
	elif processname == 'omnetpp':
		process = cpu2017.omnetppObjs
	elif processname == 'astar':
		process = cpu2017.astarObjs
	elif processname == 'wrf':
		process = cpu2017.wrfObjs
	elif processname == 'sphinx3':
		process = cpu2017.sphinx3Objs
	elif processname == 'xalancbmk':
		process = cpu2017.xalancbmkObjs
	elif processname == 'specrand_i':
		process = cpu2017.specrand_iObjs
	elif processname == 'custom1':
		process = cpu2017.custom_bench1Objs
	elif processname == 'custom2':
		process = cpu2017.custom_bench2Objs
	elif processname == 'custom3':
		process = cpu2017.custom_bench3Objs
	elif processname == 'custom4':
		process = cpu2017.custom_bench4Objs
	exec("workload = %s(buildEnv['TARGET_ISA', 'linux', '%s')" % (
                processname, process[0].proc.cmd))
	# multiprocesses.append(process)
	multiprocesses.append(workload.makeProcess())

# parser = optparse.OptionParser()
parser = argparse.ArgumentParser()
Options.addCommonOptions(parser)
Options.addSEOptions(parser)

# execfile(os.path.join(config_root, "Options.py"))

# (options, args) = parser.parse_args()

options = parser.parse_args()

# if args:
#     print "Error: script doesn't take any positional arguments"
#     sys.exit(1)
processes = options.bench.split(":")
numPros = len(processes)
print(f"num_processes = {numPros}")

proc_num = 0
for process in processes:
	addToMultipurpose(process, proc_num)
	proc_num +=1


(CPUClass, test_mem_mode, FutureClass) = Simulation.setCPUClass(options)
CPUClass.numThreads = len(multiprocesses)
mp0_path = multiprocesses[0][0].proc.executable

if options.smt and options.num_cpus > 1:
    fatal("You cannot use SMT with multiple CPUs!")

np = options.num_cpus

if numPros != np:
	fatal("Number of processes =  Number of CPUs")

system = System(cpu = [CPUClass(cpu_id=i) for i in range(np)],#num_cpus=np,
                mem_mode = test_mem_mode,
                mem_ranges = [AddrRange(options.mem_size)],
                cache_line_size = options.cacheline_size)

system.voltage_domain = VoltageDomain(voltage = options.sys_voltage)
system.clk_domain = SrcClockDomain(clock =  options.sys_clock,voltage_domain = system.voltage_domain)
system.cpu_voltage_domain = VoltageDomain()
system.cpu_clk_domain = SrcClockDomain(clock = options.cpu_clock,voltage_domain = system.cpu_voltage_domain)
for cpu in system.cpu:
    cpu.clk_domain = system.cpu_clk_domain

for i in range(np): 
	print(multiprocesses[i][0].name, i)
	# system.cpu[i].workload = multiprocesses[i][0].proc # need to change this 0 to which instance of process
	system.cpu[i].workload = multiprocesses[i] # need to change this 0 to which instance of process

MemClass = Simulation.setMemClass(options)

system.membus = SystemXBar()
system.system_port = system.membus.cpu_side_ports
CacheConfig.config_cache(options, system)
MemConfig.config_mem(options, system)
config_filesystem(system, options)

system.workload = SEWorkload.init_compatible(mp0_path)


if options.wait_gdb:
    system.workload.wait_for_remote_gdb = True

root = Root(full_system = False, system = system)

Simulation.run(options, root, system, FutureClass)


# where to populate system workload
# check if multiprocesses are correctly assigned into workloads
# define process in cpu2017.py
# what about multithreading and smt like in the se.py 
# what about the builEnv thing 