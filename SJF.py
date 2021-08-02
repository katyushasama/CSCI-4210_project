import time
import copy
import sys
from math import ceil
import operator

class SJF(object):
  def __init__(self,ctsw,data,t_cs,alpha_constant):
    self.time = 0
    self.taus = {}# make a dict
    self.time_context_switch = ctsw
    self.alpha = alpha_constant
    
    self.processList = copy.deepcopy(data)
    for i in self.processList:
      self.taus[chr(i.id)] = i.predict_cpu_burst_time
    self.running = False#is cpu run or not
    self.io_run = False#is io run or not
    self.current_io_run_to = 0#没用到
    self.in_io_process = []
    self.process_terminate = 0

    #testing code
    self.total_wait = 0
    self.cont_swit_total = 0
    self.total_preempt = 0 
  
    #def SJF(self):
  def wait_time_add(self,queue):
    for i in queue:
      i.wait_time += 1;

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
        x = 0
        while x < len(queue):
          if i.id < queue[x].id:
            break
          x += 1
        queue.insert(x,i)
        if(self.time < 1000):
          print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue [Q {}]"\
          .format(self.time,chr(i.get_id()),self.taus[chr(i.id)],self.to_str(queue)))
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

  def time_plus(self,time,queue):#没用到
    for i in range(time):
      self.time +=1;
      self.check_ari(queue)
#------------------------------------------------------------------------------#
  def cpu_burst(self,time_in,queue,proc):

    if(len(queue) == 0):
      if(self.time < 1000):
        print("time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst [Q empty]"\
        .format(self.time,chr(proc.get_id()),self.taus[chr(proc.id)],time_in))
      
    else:
      if(self.time < 1000):
        print("time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst [Q {}]"\
        .format(self.time,chr(proc.get_id()),self.taus[chr(proc.id)],time_in,self.to_str(queue)))
    self.for_ti0(queue)
    #self.current_burst = proc.all_number_cpu_brust
    #----------------------------------#
    self.running = True;
    for i in range(time_in-1):
      self.time += 1
      self.wait_time_add(queue);
      if(i < time_in -1):
        self.check_ari(queue)
      if(self.io_run):

        self.check_io_finish(queue)
    proc.num_process+=1
    self.running = False;
    
    #--------------------------------#
    self.time +=1
    self.wait_time_add(queue);
    if(proc.get_num_proc() < proc.number_cpu_brust):
      x = 1

      tmp = self.taus[chr(proc.id)]

      self.taus[chr(proc.id)] = ceil(self.taus[chr(proc.id)]*
        (1-self.alpha) + proc.get_cpu_pre_time()*self.alpha)

      if(proc.number_cpu_brust - proc.num_process == 1):
        if(len(queue) == 0):
          if(self.time < 1000):
            print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst to go [Q empty]"\
            .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process))
          if(self.time < 1000):
            print("time {}ms: Recalculated tau from {}ms to {}ms for process {} [Q empty]"\
            .format(self.time, tmp, self.taus[chr(proc.id)],chr(proc.get_id())))
        
        
        else:
          if(self.time < 1000):
            print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst to go [Q {}]"\
            .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process,\
              self.to_str(queue)))
          if(self.time < 1000):
            print("time {}ms: Recalculated tau from {}ms to {}ms for process {} [Q {}]"\
            .format(self.time, tmp, self.taus[chr(proc.id)],  chr(proc.get_id()),self.to_str(queue)))
        
      else:

        if(len(queue) == 0):
          if(self.time < 1000):
            print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} bursts to go [Q empty]"\
            .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process))
          if(self.time < 1000):
            print("time {}ms: Recalculated tau from {}ms to {}ms for process {} [Q empty]"\
            .format(self.time, tmp, self.taus[chr(proc.id)],chr(proc.get_id())))
        
        
        else:
          if(self.time < 1000):
            print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} bursts to go [Q {}]"\
            .format(self.time,chr(proc.get_id()),tmp,proc.number_cpu_brust - proc.num_process,\
              self.to_str(queue)))
          if(self.time < 1000):
            print("time {}ms: Recalculated tau from {}ms to {}ms for process {} [Q {}]"\
            .format(self.time, tmp, self.taus[chr(proc.id)],  chr(proc.get_id()),self.to_str(queue)))
        
    else:
      self.total_wait += proc.wait_time;
      if(len(queue) == 0 ):
        print("time {}ms: Process {} terminated [Q empty]".format(self.time,chr(proc.get_id())))
        self.check_io_finish(queue)
        self.add_con_sw_ti(queue)
      else:
        print("time {}ms: Process {} terminated [Q {}]".format(self.time,chr(proc.get_id()),self.to_str(queue)))
        self.check_io_finish(queue)
        self.add_con_sw_ti(queue)
#------------------------------------------------------------------------------#
  def io_burst_bef(self,time_in,queue,proc):

    self.io_run = True;
    temp_time = copy.deepcopy(self.time)
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
    checks1 = 0
    self.in_io_process.sort(key = lambda x:[x[1],x[0].get_id()])
    while_it = 0
    if(len(self.in_io_process)!= 0):
      while(while_it < len(self.in_io_process)):
        if(self.time == self.in_io_process[while_it][1]):
          checks1 = 1
          tmp = self.taus[chr((self.in_io_process[while_it][0]).id)]
          x = 0
          while x <len(queue):
            if(tmp < self.taus[chr(queue[x].id)]):
              break
            if((tmp == self.taus[chr(queue[x].id)]) \
              and (self.in_io_process[while_it][0]).id < queue[x].id):
              break
            x += 1
            
          queue.insert(x,self.in_io_process[while_it][0])
          if(self.time < 1000):
            print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue [Q {}]"\
            .format(self.time,chr(self.in_io_process[while_it][0].get_id()),self.taus[chr((self.in_io_process[while_it][0]).id)],self.to_str(queue)))
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
  def check_time_slice(self,queue,time_in):#for RR
    if(time_in > self.time_slice):
      return True
    return False
#------------------------------------------------------------------------------#
  def check_alg_finish(self,queue):#没用到
    for i in queue:
      if(i.check_end() == False):
        return False
    return True
#------------------------------------------------------------------------------#
  def simout(self):
    count_total_burst_time = 0
    for i in self.processList:
      for j in i.all_number_cpu_brust:
        count_total_burst_time += j
    count_burst = 0
    for i in self.processList:
      count_burst += len(i.all_number_cpu_brust)
    return ["SJF",count_total_burst_time/count_burst,self.total_wait/count_burst,(self.total_wait+count_total_burst_time+ self.time_context_switch*(self.cont_swit_total//2) )/count_burst\
    ,(self.cont_swit_total)//2,self.total_preempt,count_total_burst_time/self.time]
  #------------------------------------------------------------------------------#
  def SJF(self):
    print("time {}ms: Simulator started for {} [Q empty]".format(self.time,"SJF"))
    queue = []#ready queue 
    
    while (1):#self.time < 107
      if(self.running == False and len(queue) != 0):
        proc = copy.deepcopy(queue[0])
        
        queue.pop(0)
        self.add_con_sw_ti0(queue);
        cpu_burst_time_temp = proc.get_cpu_time()
        io_burst_time_temp = proc.get_io_time()
        
        #print("IO:",io_burst_time_temp)
        self.cpu_burst(cpu_burst_time_temp,queue,proc)
        if(io_burst_time_temp != 0):
          self.io_burst_bef(io_burst_time_temp,queue,proc)
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
        self.wait_time_add(queue);
        self.check_ari(queue)
        if(self.io_run):
          self.check_io_finish(queue)

    print("time {}ms: Simulator ended for SJF [Q empty]".format(self.time))