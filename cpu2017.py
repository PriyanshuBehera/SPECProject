from multiprocessing.dummy import Process
import optparse
import sys
import os
from wsgiref.validate import InputWrapper

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.params import NULL
from m5.util import addToPath, fatal, warn

# addToPath('../common')
# addToPath('../ruby')
# addToPath('../topologies')
addToPath('../')

from common import Options
from common import Simulation
from common import CacheConfig
from common import CpuConfig
from common import ObjectList
from common import MemConfig
from common.Caches import *

import json

num_instances = 1

# copy the inpout and output in spec2017
binary_dir = "/home/debiprasanna/Gem5SPEC/alphaexe/"
data_dir = "/home/debiprasanna/Gem5SPEC/input/"
output_dir = "/home/debiprasanna/Gem5SPEC/output/"
benchmarks_dir ="/home/n313-office-desktop/nitesh_stuff/cpu2017_x86/benchspec/CPU"


cmd_lines_json_file = "/home/n313-office-desktop/nitesh_stuff/mlMem/gem5/configs/example/cmd_lines.json"

with open(cmd_lines_json_file, 'r') as f:
    cmd_data_dict = json.load(f)
    print("reading json completed")


idx = 0

class BenchMark():
    def __init__(self, name, bench_parameter=None) -> None:
        # self.proc = LiveProcess()
        global idx
        self.proc = Process(pid=100 + idx)
        self.proc.gid = os.getgid()
        self.name = name
        # self.proc.cwd = data_dir
        # self.proc.output = output_dir + f"/{name}.out"
        self.proc.executable = binary_dir + f"/{name}_base.x86-gcc94"
        # self.proc.cmd = self.proc.executable + f"{bench_parameter}"
        self.buildBenchMark()
        idx +=1
        
    def buildBenchMark(self, bench_type="int", test_type="rate",input_type="ref", input_num = 1):
        print(self.name)
        benchmark_data = cmd_data_dict[bench_type][self.name]
        bench_cmd = benchmark_data["cmd"][test_type].strip().split('/')[1]
        bench_prefix = benchmark_data["prefix"][test_type].strip()

        bench_dir = benchmarks_dir+ f"/{bench_prefix}.{bench_cmd}"
        # print(bench_cmd)
        # print(bench_dir)
        # print(bench_prefix)

        bench_input_dir = input_type if input_type!="ref" else input_type+test_type 

        if"data" in benchmark_data:
            bench_input_path = f"{bench_dir}/data/{bench_input_dir}/input"
            bench_output_path = f"{bench_dir}/data/{bench_input_dir}/output"

            self.proc.cwd = bench_input_path

        else:
            bench_output_path = f"{bench_dir}/output/"
            if not os.path.exists(bench_output_path):
                os.makedirs(bench_output_path)
            
        
        self.proc.output = bench_output_path + "se.stdout"
        self.proc.errout = bench_output_path + "se.stderr"


        if input_type == "ref":
            if benchmark_data["ref"]["rate_speed_seperate"]:
                print(benchmark_data.keys())
                input_params = benchmark_data["ref"][test_type]
            
            else:
                input_params = benchmark_data["ref"]
        else:
            input_params = benchmark_data[input_type]

        if input_num > input_params["num_inputs"]:
            print("wrong input number")
            exit()
        
        bench_param = input_params["input"][str(input_num)]

        print(bench_param)

        self.proc.executable = f"{bench_dir}/exe/{bench_cmd}_base.mytest-m64"
        print(self.proc.executable + f"{bench_param}")

        

        self.proc.cmd = self.proc.executable + f"{bench_param}"
        # print(self.proc.executable)
        print()


        # print(self.proc.cwd)






#-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1
#-I./lib diffmail.pl 4 800 10 17 19 300
#-I./lib splitmail.pl 6400 12 26 16 100 0
gccObjs = [BenchMark('gcc',)] * num_instances
mcfObjs = [BenchMark('mcf','inp.in')] * num_instances
perlBenchObjs = [BenchMark('perlbench',)] * num_instances

#gcc-pp.c -O3 -finline-limit=0 -fif-conversion -fif-conversion2 -o gcc-pp.opts-O3_-finline-limit_0_-fif-conversion_-fif-conversion2.s
#gcc-pp.c -O2 -finline-limit=36000 -fpic -o gcc-pp.opts-O2_-finline-limit_36000_-fpic.s
#gcc-smaller.c -O3 -fipa-pta -o gcc-smaller.opts-O3_-fipa-pta.s
#ref32.c -O5 -o ref32.opts-O5.s
#ref32.c -O3 -fselective-scheduling -fselective-scheduling2 -o ref32.opts-O3_-fselective-scheduling_-fselective-scheduling2.s 


omnetppObjs = [BenchMark('omnetpp','-c General -r 0')] * num_instances
xalancbmkObjs = [BenchMark('xalancbmk','-v t5.xml xalanc.xsl')] * num_instances

#--pass 1 --stats x264_stats.log --bitrate 1000 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720
#--pass 2 --stats x264_stats.log --bitrate 1000 --dumpyuv 200 --frames 1000 -o BuckBunny_New.264 BuckBunny.yuv 1280x720
#--seek 500 --dumpyuv 200 --frames 1250 -o BuckBunny_New.264 BuckBunny.yuv 1280x720
x264Objs = [BenchMark('x264',)] * num_instances

deepsjengObjs = [BenchMark('deepsjeng','ref.txt')] * num_instances
leelaObjs = [BenchMark('leela','ref.sgf')] * num_instances
exchange2Objs = [BenchMark('exchange2','6')] * num_instances

#cld.tar.xz 160 19cf30ae51eddcbefda78dd06014b4b96281456e078ca7c13e1c0c9e6aaea8dff3efb4ad6b0456697718cede6bd5454852652806a657bb56e07d61128434b474 59796407 61004416 6
#cpu2006docs.tar.xz 250 055ce243071129412e9dd0b3b69a21654033a9b723d874b2015c774fac1553d9713be561ca86f74e4f16f22e664fc17a79f30caa5ad2c04fbc447549c2810fae 23047774 23513385 6e
#input.combined.xz 250 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 40401484 41217675 7
xzObjs = [BenchMark('xz',)] * num_instances
#bwaves_1 < bwaves_1.in 
#bwaves_2 < bwaves_2.in 
#bwaves_3 < bwaves_3.in 
#bwaves_4 < bwaves_4.in 
# bwavesObjs = [BenchMark('bwaves',)] * num_instances 
# cactuBSSNObjs = [BenchMark('cactuBSSN','spec_ref.par')] * num_instances
# namdObjs = [BenchMark('namd','--input apoa1.input --iterations 1 --output apoa1.test.output')] * num_instances
# parestObjs = [BenchMark('parest','ref.prm')] * num_instances
# povrayObjs = [BenchMark('povray','SPEC-benchmark-ref.ini')] * num_instances
# lbmObjs = [BenchMark('lbm','3000 reference.dat 0 0 100_100_130_ldc.of')] * num_instances
# wrfObjs = [BenchMark('wrf','')] * num_instances
# blenderObjs = [BenchMark('blender','sh3_no_char.blend --render-output sh3_no_char_ --threads 1 -b -F RAWTGA -s 849 -e 849 -a')] * num_instances
# cam4Objs = [BenchMark('cam4','')] * num_instances
# pop2Objs = [BenchMark('pop2','')] * num_instances
# imagickObjs = [BenchMark('imagick','-limit disk 0 refrate_input.tga -edge 41 -resample 181% -emboss 31 -colorspace YUV -mean-shift 19x19+15% -resize 30% refrate_output.tga')] * num_instances
# nabObjs = [BenchMark('nab','1am0 1122214447 122')] * num_instances
# fotonik3dObjs = [BenchMark('fotonik3d','')] * num_instances
# romsObjs = [BenchMark('roms','< ocean_benchmark2.in.x')] * num_instances