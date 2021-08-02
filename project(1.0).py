import time
import copy
import sys
import math
import operator

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
    self.num_process = 0;
    self.time_slice = t_cs
    self.ms_burst_run = 0

    self.all_number_cpu_brust = []
    self.all_io_brust_time = []

    for i in range(self.number_cpu_brust):
      self.all_number_cpu_brust.append(self.next_exp())
      if(i == self.number_cpu_brust -1):
        break
      self.all_io_brust_time.append(self.next_exp()*10)
    #print(self.all_number_cpu_brust)
    print("Process {} (arrival time {} ms) {} CPU bursts (tau {}ms\
)".format(chr(self.id),self.arrival_time,self.number_cpu_brust,self.predict_cpu_burst_time))

  '''
  def __cmp__(self, obj): 
    if self.time_saved == obj.time_saved:
      return cmp(self.pid, obj.pid)
    return cmp(self.time_saved, obj.time_saved)
  '''

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


class CPU_class(object):
  def __init__(self,ctsw,data,t_cs):
    self.time = 0;
    self.time_context_switch =ctsw;
    self.processList = copy.deepcopy(data)
    self.running = False#is cpu run or not
    self.io_run = False#is io run or not
    self.current_io_run_to = 0#没用到
    self.in_io_process = []
    self.process_terminate = 0
    self.time_slice = t_cs
    self.ms_burst_run = 0
  
  def restart(self):
    self.time = 0;
    self.time_context_switch =ctsw;
    self.processList = copy.deepcopy(data)
    self.running = False#is cpu run or not
    self.io_run = False#is io run or not
    self.current_io_run_to = 0#没用到
    self.in_io_process = []
    self.process_terminate = 0
    self.time_slice = t_cs
    self.ms_burst_run = 0

  def to_str(self,queue):
    ret = ""
    for i in queue:
      ret += chr(i.get_id())
    return ret

  def check_ari(self,queue):
    temp = 0
    for i in self.processList:
      if(i.get_arr() == self.time):
        temp = 1
        queue.append(i)
        print("time {}ms: Process {} arrived; added to ready queue [Q {}]"\
          .format(self.time,chr(i.get_id()),self.to_str(queue)))
    if(temp == 1):
      return True
    else:
      return False

  def add_con_sw_ti(self,queue):
    for i in range((self.time_context_switch)//2):
      self.time +=1
      self.check_ari(queue)
      self.check_io_finish(queue)

  def time_plus(self,time,queue):#没用到
    for i in range(time):
      self.time +=1;
      self.check_ari(queue)
#------------------------------------------------------------------------------#
  def cpu_burst(self,time_in,queue,proc):
    #print("cpu_burst1")
    if(len(queue) == 0):
      print("time {}ms: Process {} started using the CPU for {}ms burst [Q empty]"\
        .format(self.time,chr(proc.get_id()),time_in))
    else:
      print("time {}ms: Process {} started using the CPU for {}ms burst [Q {}]"\
        .format(self.time,chr(proc.get_id()),time_in,self.to_str(queue)))
    #----------------------------------#
    self.running = True;
    for i in range(time_in-1):
      self.time += 1
      if(i < time_in -1):
        self.check_ari(queue)
      if(self.io_run):
        self.check_io_finish(queue)
    proc.num_process+=1
    self.running = False;
    #--------------------------------#
    self.time +=1
    if(proc.get_num_proc() < proc.number_cpu_brust):
      if(len(queue) == 0):
        print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q empty]"\
          .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process))
      else:
        print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q {}]"\
          .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process,\
            self.to_str(queue)))
    else:
      if(len(queue) == 0 ):
        print("time {}ms: Process {} terminated [Q empty ]".format(self.time,chr(proc.get_id())))
        self.add_con_sw_ti(queue)
      else:
        print("time {}ms: Process {} terminated [Q {} ]".format(self.time,chr(proc.get_id()),self.to_str(queue)))
        self.add_con_sw_ti(queue)
    #print("cpu_burst2")
#------------------------------------------------------------------------------#
  def io_burst_bef(self,time_in,queue,proc):
    #print("io_burst_bef1")
    self.io_run = True;
    temp_time = copy.deepcopy(self.time)
    #self.add_con_sw_ti(queue)
    if(len(queue) == 0):
      print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q empty]"\
        .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2))
    else:
      print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q {}]"\
        .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2,self.to_str(queue)))
    self.check_ari(queue)
    self.check_io_finish(queue)
    self.add_con_sw_ti(queue)
    io_run_to = self.time + time_in;
    io_run_to = int(io_run_to)
    self.in_io_process.append([proc,io_run_to])
    self.in_io_process.sort(key = lambda x:x[1])

    #print("io_burst_bef2")

#------------------------------------------------------------------------------#
  def check_io_finish(self,queue):
    #print(self.in_io_process)
    #print(self.time)
    checks1 = 0
    self.in_io_process.sort(key = lambda x:[x[1],x[0].get_id()])
    while_it = 0
    if(len(self.in_io_process)!= 0):
      while(while_it < len(self.in_io_process)):
        if(self.time == self.in_io_process[while_it][1]):
          #for sk in self.in_io_process:
             #print(chr(sk[0].get_id()),self.time)
          checks1 = 1
          queue.append(self.in_io_process[while_it][0])
          print("time {}ms: Process {} completed I/O; added to ready queue [Q {}]"\
            .format(self.time,chr(self.in_io_process[while_it][0].get_id()),self.to_str(queue)))
          self.in_io_process.pop(while_it)
          while_it = 0
          if(len(self.in_io_process) == 0):
            self.io_run = False
        else:
          while_it +=1

    if(checks1 == 1):
      return True
    else:
      return False
#------------------------------------------------------------------------------#
  def check_alg_finish(self,queue):#没用到
    for i in queue:
      if(i.check_end() == False):
        return False
    return True
#------------------------------------------------------------------------------#
  def FCFS(self):
    print("Time {}ms: Simulator started for {} [Q empty]".format(self.time,"FCFS"));
    queue = []#ready queue 
    while(1):
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        queue.pop(0);
        self.add_con_sw_ti(queue);
        cpu_burst_time_temp = proc.get_cpu_time(); 
        io_burst_time_temp = proc.get_io_time();
        print("IO:",io_burst_time_temp)
        self.cpu_burst(cpu_burst_time_temp,queue,proc);
        if(io_burst_time_temp != 0):
          self.io_burst_bef(io_burst_time_temp,queue,proc);
          continue
        else:
          self.process_terminate += 1
          continue
      if(len(queue) == 0 and self.running == False and self.io_run == False\
       and self.process_terminate != 0):
        break
      if(self.running == False):
        #print(self.running, len(queue),self.io_run)
        ck1 = self.check_ari(queue)
        if(ck1 == True):
          continue
        if(self.io_run):
          ck2 = self.check_io_finish(queue)
          if(ck2 == True):
            continue
        self.time += 1
        self.check_ari(queue)
        if(self.io_run):
          self.check_io_finish(queue)

    print("time {}ms: Simulator ended for FCFS [Q empty]".format(self.time))


  def RR(self):
    self.restart()
    print("Time {}ms: Simulator started for RR with time slice {}ms [Q empty]".format(self.time,self.time_slice));
    queue = []#ready queue 


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
 
  predict_cpu_burst_time = 100
  for i in range(int(num_proc_id)):
    arrival_time = math.floor(rand(rand48,in_lambda,up_bound));
    number_cpu_brust = math.ceil(rand48.drand()*100)
    pid = i;
    inputp = [pid,arrival_time,number_cpu_brust,predict_cpu_burst_time,in_lambda,rand48,up_bound];
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
  for i in list_process:
    print(chr(i.get_id()),i.arrival_time)
  cpu = CPU_class(time_context_switch,list_process,time_slics)
  cpu.FCFS()
  
main()