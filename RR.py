import time
import copy
import sys
import math
import operator
class RR(object):
  def __init__(self,ctsw,data,t_cs):
    self.time = 0;
    self.time_context_switch =ctsw;
    self.processList = copy.deepcopy(data)
    self.running = False#is cpu run or not
    self.io_run = False#is io run or not
    self.in_io_process = []
    self.process_terminate = 0
    self.time_slice = t_cs

    #testing code
    self.total_wait = 0
    self.cont_swit_total = 0
    self.total_preempt = 0

  def wait_time_add(self,queue):
    for i in queue:
      i.wait_time += 1;

  def to_str(self,queue):
    ret = ""
    for i in queue:
      ret += chr(i.get_id())
    return ret
  def get_proc_cpu_time(self,proc):
    if(proc.ms_burst_run == 0):
      return proc.get_cpu_time()
    else:
      return (proc.get_cpu_time() - proc.ms_burst_run)

  def check_ari(self,queue):
    temp = 0
    for i in self.processList:
      if(i.get_arr() == self.time):
        temp = 1
        queue.append(i)
        if(self.time < 1000):
          print("time {}ms: Process {} arrived; added to ready queue [Q {}]"\
          .format(self.time,chr(i.get_id()),self.to_str(queue)))
    if(temp == 1):
      return True
    else:
      return False
  def add_con_sw_ti0(self,queue):
    self.cont_swit_total +=1
    for i in range((self.time_context_switch)//2):
      self.time +=1
      self.wait_time_add(queue);
      if(i < self.time_context_switch//2-1):
        self.check_ari(queue)
        self.check_io_finish(queue) 

  def for_ti0(self,queue):
    self.check_ari(queue)
    self.check_io_finish(queue)

  def add_con_sw_ti(self,queue):
    self.cont_swit_total +=1
    for i in range((self.time_context_switch)//2):
      self.time +=1
      self.wait_time_add(queue);
      self.check_ari(queue)
      self.check_io_finish(queue)

#------------------------------------------------------------------------------#
  def cpu_burst(self,time_in,queue,proc):
    if(proc.ms_burst_run == 0):
      if(len(queue) == 0):
        if(self.time < 1000):
          print("time {}ms: Process {} started using the CPU for {}ms burst [Q empty]"\
          .format(self.time,chr(proc.get_id()),time_in))
      else:
        if(self.time < 1000):
          print("time {}ms: Process {} started using the CPU for {}ms burst [Q {}]"\
          .format(self.time,chr(proc.get_id()),time_in,self.to_str(queue)))
    else:
      if(len(queue) == 0):
        if(self.time < 1000):
          print("time {}ms: Process {} started using the CPU for remaining {}ms of {}ms burst [Q empty]"\
          .format(self.time,chr(proc.get_id()),time_in,proc.get_cpu_time()))
      else:
        if(self.time < 1000):
          print("time {}ms: Process {} started using the CPU for remaining {}ms of {}ms burst [Q {}]"\
          .format(self.time,chr(proc.get_id()),time_in,proc.get_cpu_time(),self.to_str(queue)))
    self.for_ti0(queue)
    time_temp = min(time_in,self.time_slice)
    time_max = max(time_in,self.time_slice)
    preemption = False
    #----------------------------------#
    self.running = True;
    for i in range(time_temp):
      self.time += 1
      self.wait_time_add(queue);
      proc.ms_burst_run+= 1
      if(i < time_temp -1):
        self.check_ari(queue)
      if(i < time_temp -1 and self.io_run):
        self.check_io_finish(queue)
    
    if(time_temp == self.time_slice and proc.get_cpu_time() - proc.ms_burst_run > 0):
      #-----------------------------------------------#
      if(len(queue) == 0):
        while(len(queue) == 0 and proc.get_cpu_time() -proc.ms_burst_run > 0):
          if(self.time < 1000):
            print("time {}ms: Time slice expired; no preemption because ready queue is empty [Q empty]".format(self.time))
          self.check_ari(queue)
          self.check_io_finish(queue)
          range_4_loop = min(self.time_slice,proc.get_cpu_time() -proc.ms_burst_run)
          other = max(self.time_slice,proc.get_cpu_time() -proc.ms_burst_run)
          for k in range(range_4_loop):
            self.time +=1
            self.wait_time_add(queue);
            proc.ms_burst_run +=1
            if(k < range_4_loop -1):
              self.check_ari(queue)
            if(k < range_4_loop -1 and self.io_run):
              self.check_io_finish(queue)
          #if(proc.get_cpu_time() -proc.ms_burst_run > 0 and len(queue) == 0):
          #  self.check_ari(queue)
          #  self.check_io_finish(queue)
        if(proc.get_cpu_time() -proc.ms_burst_run == 0):
          proc.num_process+=1
          proc.ms_burst_run = 0
        else:
          if(self.time < 1000):
            print("time {}ms: Time slice expired; process {} preempted with {}ms to go [Q {}]"\
          .format(self.time,chr(proc.get_id()),(proc.get_cpu_time() - proc.ms_burst_run),self.to_str(queue)))
          self.total_preempt +=1
          self.total_wait -= self.time_context_switch//2
          queue.append(proc)
          self.check_ari(queue)
          self.check_io_finish(queue)
          self.running = False;
          return False;
      else:
        if(self.time < 1000):
          print("time {}ms: Time slice expired; process {} preempted with {}ms to go [Q {}]"\
          .format(self.time,chr(proc.get_id()),(proc.get_cpu_time() - proc.ms_burst_run),self.to_str(queue)))
        self.total_preempt +=1
        self.total_wait -= self.time_context_switch//2
        queue.append(proc)
        self.running = False;
        return False;
      #-----------------------------------------------#
    else:
      proc.num_process+=1
      proc.ms_burst_run = 0
    self.running = False;
    #--------------------------------#
    if(proc.number_cpu_brust - proc.get_num_proc() > 0):
      if(len(queue) == 0):
        if(proc.number_cpu_brust - proc.num_process == 1 ):
          if(self.time < 1000):
            print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q empty]"\
            .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process))
        else:
          if(self.time < 1000):
            print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q empty]"\
            .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process))
      else:
        if(proc.number_cpu_brust - proc.num_process == 1):
          if(self.time < 1000):
            print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q {}]"\
            .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process,\
              self.to_str(queue)))
        else:
          if(self.time < 1000):
            print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q {}]"\
            .format(self.time,chr(proc.get_id()),proc.number_cpu_brust - proc.num_process,\
              self.to_str(queue)))
    else:
      self.total_wait += proc.wait_time;
      if(len(queue) == 0 ):
        print("time {}ms: Process {} terminated [Q empty]".format(self.time,chr(proc.get_id())))
        self.check_ari(queue)
        self.check_io_finish(queue)
        self.add_con_sw_ti(queue)
      else:
        print("time {}ms: Process {} terminated [Q {}]".format(self.time,chr(proc.get_id()),self.to_str(queue)))
        self.check_ari(queue)
        self.check_io_finish(queue)
        self.add_con_sw_ti(queue)

#------------------------------------------------------------------------------#
  def io_burst_bef(self,time_in,queue,proc):
    #print("io_burst_bef1")
    self.io_run = True;
    temp_time = copy.deepcopy(self.time)
    #self.add_con_sw_ti(queue)
    if(len(queue) == 0):
      if(self.time < 1000):
        print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q empty]"\
          .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2))
    else:
      if(self.time < 1000):
        print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q {}]"\
          .format(temp_time,chr(proc.get_id()),self.time+time_in+self.time_context_switch//2,self.to_str(queue)))
    self.check_ari(queue)
    self.check_io_finish(queue)
    self.add_con_sw_ti(queue)
    io_run_to = self.time + time_in;
    io_run_to = int(io_run_to)
    self.in_io_process.append([proc,io_run_to])
    self.in_io_process.sort(key = lambda x:x[1])



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
          checks1 = 1
          queue.append(self.in_io_process[while_it][0])
          if(self.time < 1000):
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
  def simout(self):
    count_total_burst_time = 0
    for i in self.processList:
      for j in i.all_number_cpu_brust:
        count_total_burst_time += j
    count_burst = 0
    for i in self.processList:
      count_burst += len(i.all_number_cpu_brust)
    return ["RR",count_total_burst_time/count_burst,self.total_wait/count_burst,(self.total_wait+count_total_burst_time+ self.time_context_switch*(self.cont_swit_total//2) )/count_burst\
    ,(self.cont_swit_total)//2,self.total_preempt,count_total_burst_time/self.time]
#------------------------------------------------------------------------------#
  def RR(self):
    print("time {}ms: Simulator started for RR with time slice {}ms [Q empty]".format(self.time,self.time_slice));
    queue = []#ready queue 
    while(1):#self.time < 78000
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        queue.pop(0);
        self.add_con_sw_ti0(queue);
        cpu_burst_time_temp = self.get_proc_cpu_time(proc); 
        io_burst_time_temp = proc.get_io_time();
        #print("IO:",io_burst_time_temp)
        check_io_or_not = self.cpu_burst(cpu_burst_time_temp,queue,proc);
        if(check_io_or_not == False):
          self.add_con_sw_ti(queue);
          continue
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
        self.time +=1
        self.wait_time_add(queue);
        self.check_ari(queue)
        if(self.io_run):
          self.check_io_finish(queue)
    #print(self.process_terminate)
    print("time {}ms: Simulator ended for RR [Q empty]".format(self.time))
