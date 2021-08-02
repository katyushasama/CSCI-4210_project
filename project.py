import time
import copy
import sys
import math
import operator
from FCFS import *
from SJF import *
from SRT import *
from RR import *

class Rand48(object):
    def __init__(self, seed):
        self.n = seed

    def seed(self, seed):
        self.n = seed

    def srand(self, seed):
        self.n = (seed << 16) + 0x330e

    def next(self):
        self.n = (25214903917 * self.n + 11) & (2 ** 48 - 1)
        return self.n

    def drand(self):
        return self.next() / 2 ** 48

    def lrand(self):
        return self.next() >> 17

    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

class process(object):
  def __init__(self,inputp):
    #all these value needs taken from input 
    #here just a example of calculation
    self.id = 65+inputp[0] #from input list chr(proc.get_id())
    self.arrival_time = inputp[1]
    self.number_cpu_brust = inputp[2];
    self.predict_cpu_burst_time = inputp[3]
    self.lambda_in = inputp[4]
    self.rand48 = inputp[5]
    self.upper_bound = inputp[6]
    self.num_process = 0;#
    self.ms_burst_run = 0#
    #for simout
    self.wait_time = 0


    self.all_number_cpu_brust = []
    self.all_io_brust_time = []

    for i in range(self.number_cpu_brust):
      self.all_number_cpu_brust.append(self.next_exp())
      if(i == self.number_cpu_brust -1):
        break
      self.all_io_brust_time.append(self.next_exp()*10)
    #print(self.all_number_cpu_brust)
    if(self.number_cpu_brust == 1):
      print("Process {} (arrival time {} ms) {} CPU burst (tau {}ms)"\
        .format(chr(self.id),self.arrival_time,self.number_cpu_brust,self.predict_cpu_burst_time))
    else:
      print("Process {} (arrival time {} ms) {} CPU bursts (tau {}ms)"\
        .format(chr(self.id),self.arrival_time,self.number_cpu_brust,self.predict_cpu_burst_time))


    self.remain = self.predict_cpu_burst_time - self.ms_burst_run;

  def re_new_re(self):
    self.remain = self.predict_cpu_burst_time - self.ms_burst_run;
  def check_end(self):
    if(self.num_process < self.number_cpu_brust):
      return False
    return True

  def get_id(self):
    return self.id
  def get_arr(self):
    return self.arrival_time

  def add_num_proc(self):
    self.num_process +=1

  def get_num_proc(self):
    return self.num_process
  def get_cpu_pre_time(self):
    return self.all_number_cpu_brust[self.num_process-1]

  def get_cpu_time(self):
    return self.all_number_cpu_brust[self.num_process]
  def get_io_time(self):
    if(self.num_process > len(self.all_io_brust_time)-1):
      return 0
    else:
      return self.all_io_brust_time[self.num_process]


  def next_exp(self):
    while(1):
      arrival_time =  math.ceil(((math.log(self.rand48.drand()))/self.lambda_in)*-1);
      if(arrival_time <= self.upper_bound):
        return arrival_time



'''

def SJF():

def SRT():

'''
def rand(rand48,in_lambda,up_bound):
  while(1):
    ret =((math.log(rand48.drand()))/in_lambda)*-1
    if(ret <= up_bound):
      return ret

def main():
  if(8 < len(sys.argv) or len(sys.argv) <8):
    print("InValid number of argv input")
    sys.exit()
  
  #argv from input
  num_proc_id = int(sys.argv[1])
  seed = int(sys.argv[2])
  in_lambda = float(sys.argv[3])
  up_bound = int(sys.argv[4])
  time_context_switch = int(sys.argv[5])
  alpha_constant = float(sys.argv[6])
  time_slics = int(sys.argv[7])

  rand48 = Rand48(seed)
  rand48.srand(seed)


  list_process = []
 
  predict_cpu_burst_time = 1/in_lambda
  for i in range(int(num_proc_id)):
    arrival_time = math.floor(rand(rand48,in_lambda,up_bound));
    number_cpu_brust = math.ceil(rand48.drand()*100)
    pid = i;
    inputp = [pid,arrival_time,number_cpu_brust,int(predict_cpu_burst_time),in_lambda,rand48,up_bound];
    #print(inputp)
    all_number_cpu_brust = []
    all_io_brust_time = []
    proc = process(inputp)
    list_process.append(proc)
    #print(proc.next_exp())
    #print(proc.next_exp()*10 )
    #rand48 = Rand48(seed)
    #rand48.srand(seed)
    #arrival_time = math.floor(((math.log(rand48.drand()))/in_lambda)*-1);
    #number_cpu_brust = math.ceil(rand48.drand()*100)

    '''
    for i in range(18):
     cpu_burst_time = proc.next_exp(in_lambda,rand48);
     io_burst_time = (proc.next_exp(in_lambda,rand48))*10;
     print(cpu_burst_time)
     print(io_burst_time)
     print("------------------------")
     '''
 #print(list_process)

  #CPU default
  list_process = sorted(list_process, key=operator.attrgetter('arrival_time'))
  #for i in list_process:
  #  print(chr(i.get_id()),i.arrival_time)
  print()
  cpu1 = FCFS(time_context_switch,list_process,time_slics)
  cpu1.FCFS()
  out1 = cpu1.simout()
  print()
  cpu2 = SJF(time_context_switch,list_process,time_slics,alpha_constant)
  cpu2.SJF()
  out2 = cpu2.simout()
  print()
  cpu3 = SRT1(time_context_switch,list_process,time_slics,alpha_constant)
  cpu3.SRT()
  out3 = cpu3.simout()
  print()
  cpu4 = RR(time_context_switch,list_process,time_slics)
  cpu4.RR()
  out4 = cpu4.simout()


  f = open("simout.txt", "w")

  f.write("Algorithm {}\n\
-- average CPU burst time: {:.3f} ms\n\
-- average wait time: {:.3f} ms\n\
-- average turnaround time: {:.3f} ms\n\
-- total number of context switches: {}\n\
-- total number of preemptions: {}\n\
-- CPU utilization: {:.3f}%\n".format(out1[0],out1[1],out1[2],out1[3],out1[4],out1[5],(out1[6])*100))
  f.write("Algorithm {}\n\
-- average CPU burst time: {:.3f} ms\n\
-- average wait time: {:.3f} ms\n\
-- average turnaround time: {:.3f} ms\n\
-- total number of context switches: {}\n\
-- total number of preemptions: {}\n\
-- CPU utilization: {:.3f}%\n".format(out2[0],out2[1],out2[2],out2[3],out2[4],out2[5],(out2[6])*100))
  f.write("Algorithm {}\n\
-- average CPU burst time: {:.3f} ms\n\
-- average wait time: {:.3f} ms\n\
-- average turnaround time: {:.3f} ms\n\
-- total number of context switches: {}\n\
-- total number of preemptions: {}\n\
-- CPU utilization: {:.3f}%\n".format(out3[0],out3[1],out3[2],out3[3],out3[4],out3[5],(out3[6])*100))
  f.write("Algorithm {}\n\
-- average CPU burst time: {:.3f} ms\n\
-- average wait time: {:.3f} ms\n\
-- average turnaround time: {:.3f} ms\n\
-- total number of context switches: {}\n\
-- total number of preemptions: {}\n\
-- CPU utilization: {:.3f}%\n".format(out4[0],out4[1],out4[2],out4[3],out4[4],out4[5],(out4[6])*100))

main()