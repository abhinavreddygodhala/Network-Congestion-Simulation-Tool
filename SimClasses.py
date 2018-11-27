import simpy
import random
import copy
from simpy.core import BoundClass
from simpy.resources import base
from heapq import heappush, heappop


class Packet(object):
    """ A very simple class that represents a packet.
        This packet will run through a queue at a switch output port.
        We use a float to represent the size of the packet in bytes so that
        we can compare to ideal M/M/1 queues.

        Parameters
        ----------
        time : float
            the time the packet arrives at the output queue.
        size : float
            the size of the packet in bytes
        id : int
            an identifier for the packet
        src, dst : int
            identifiers for source and destination
        flow_id : int
            small integer that can be used to identify a flow
    """
    def __init__(self, time, size, id, src="a", dst="z", flow_id=0):
        self.time = time
        self.size = size
        self.id = id
        self.src = src
        self.dst = dst
        self.flow_id = flow_id

    def __repr__(self):
        return "id: {}, src: {}, time: {}, size: {}".\
            format(self.id, self.src, self.time, self.size)
	print "id: {}, src: {}, time: {}, size: {}".\
            format(self.id, self.src, self.time, self.size)


class PacketGenerator(object):
    """ Generates packets with given inter-arrival time distribution.
        Set the "out" member variable to the entity to receive the packet.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        adist : function
            a no parameter function that returns the successive inter-arrival times of the packets
        sdist : function
            a no parameter function that returns the successive sizes of the packets
        initial_delay : number
            Starts generation after an initial delay. Default = 0
        finish : number
            Stops generation at the finish time. Default is infinite


    """
    def __init__(self, env, id,  adist, sdist, initial_delay=0, finish=float("inf"), flow_id=0,debug=False):
        self.id = id
        self.env = env
        self.adist = adist
        self.sdist = sdist
        self.initial_delay = initial_delay
        self.finish = finish
        self.out = None
        self.packets_sent = 0
        self.action = env.process(self.run()) 
        self.flow_id = flow_id
	self.debug=debug
	self.size=[]
    def run(self):
        
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            # wait for next transmission
            yield self.env.timeout(self.adist())
            self.packets_sent += 1
            p = Packet(self.env.now, self.sdist(), self.packets_sent,src=self.id,flow_id=self.flow_id)
	    self.size.append(self.sdist())
	    if self.debug:		    
		print p
	    self.out.put(p)

class PacketSink(object):
    """ Receives packets and collects delay information into the
        waits list. You can then use this list to look at delay statistics.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        debug : boolean
            if true then the contents of each packet will be printed as it is received.
        rec_arrivals : boolean
            if true then arrivals will be recorded
        absolute_arrivals : boolean
            if true absolute arrival times will be recorded, otherwise the time between consecutive arrivals
            is recorded.
        rec_waits : boolean
            if true waiting time experienced by each packet is recorded
        selector: a function that takes a packet and returns a boolean
            used for selective statistics. Default none.

    """

    def __init__(self, env, rate, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None):
        self.store = simpy.Store(env)
        self.env = env
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits1 = []
        self.waits2 = []
        self.waits3 = []
        self.resp1 = []
        self.resp2 = []
        self.resp3 = []
        self.rate = rate
        self.arrivals = []
        self.arrivalsrate1 = []
        self.arrivalsrate2 = []
        self.arrivalsrate3 = []
        self.service1=[]
        self.service2=[]
        self.service3=[]
        
        self.debug = debug
        self.packets_rec = 0
        self.bytes_rec = 0
        self.selector = selector
        self.last_arrival = 0.0
	self.type1_rec=0
	self.type2_rec=0
	self.type3_rec=0

    def put(self, pkt):
        if not self.selector or self.selector(pkt):
            now = self.env.now
            if self.rec_waits:
              if (pkt.src == 'type1'):
                #self.resp1.append(self.env.now -pkt.time)#responce time
                #self.waits1.append((self.env.now - pkt.time)-(pkt.size*8.0/self.rate))
                
                self.waits1.append(self.env.now - pkt.time)
                self.resp1.append((pkt.size*8.0/self.rate)+(self.env.now - pkt.time))
                self.service1.append(pkt.size*8.0/self.rate)
              elif(pkt.src == 'type2'):
                #self.waits2.append((self.env.now - pkt.time)-(pkt.size*8.0/self.rate))
                #self.resp2.append(self.env.now -pkt.time)#responce time
               
                
                self.waits2.append(self.env.now - pkt.time)
                self.resp2.append((pkt.size*8.0/self.rate)+(self.env.now - pkt.time))
                self.service2.append(pkt.size*8.0/self.rate)
                
              elif(pkt.src == 'type3'):
                #self.waits3.append((self.env.now - pkt.time)-(pkt.size*8.0/self.rate))
                #self.resp3.append(self.env.now -pkt.time)#responce time
                
                
                self.waits3.append(self.env.now - pkt.time)
                self.resp3.append((pkt.size*8.0/self.rate)+(self.env.now - pkt.time))
                self.service3.append(pkt.size*8.0/self.rate)
                
            if self.rec_arrivals:
                if self.absolute_arrivals:
                  if (pkt.src == 'type1'):
                    self.arrivalsrate1.append(now)
                  elif (pkt.src == 'type2'):
                    self.arrivalsrate2.append(now)
                  elif (pkt.src == 'type3'):
                    self.arrivalsrate3.append(now)
                    
                else:
                  if (pkt.src == 'type1'):
                    self.arrivalsrate1.append(now - self.last_arrival)                    
                  elif (pkt.src == 'type2'):
                    self.arrivalsrate2.append(now - self.last_arrival)
                  elif (pkt.src == 'type3'):
                    self.arrivalsrate3.append(now - self.last_arrival)
                self.last_arrival = now
	    if pkt.src is "type1":
            	self.type1_rec += 1
            	self.bytes_rec += pkt.size
	    elif pkt.src is "type2":
            	self.type2_rec += 1
            	self.bytes_rec += pkt.size
	    elif pkt.src is "type3":
            	self.type3_rec += 1
            	self.bytes_rec += pkt.size
            self.packets_rec=self.type1_rec+self.type2_rec+self.type3_rec
	    if self.debug:
                print(pkt)
		#print "seviced"


class SwitchPort(object):
    """ Models a switch output port with a given rate and buffer size limit in bytes.
        Set the "out" member variable to the entity to receive the packet.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        rate : float
            the bit rate of the port
        qlimit : integer (or None)
            a buffer size limit in bytes or packets for the queue (including items
            in service).
        limit_bytes : If true, the queue limit will be based on bytes if false the
            queue limit will be based on packets.

    """

    def __init__(self, env, rate, qlimit=None, limit_bytes=True, debug=False):
          self.congestion = False
          self.store = simpy.Store(env)
          self.rate = rate
          self.env = env
          self.out = None
          self.packets_rec = 0
          self.packets_drop_1 = 0
          self.packets_drop_2 = 0
          self.packets_drop_3 = 0
          self.qlimit = qlimit
          self.threshold1=int((75*(qlimit-1))/100)
          self.abate_threshold1=int((71*(qlimit-1))/100)
          self.threshold2=int((85*(qlimit-1))/100)
          self.abate_threshold2=int((81*(qlimit-1))/100)
          self.threshold3=int((90*(qlimit-1))/100)
          self.abate_threshold3=int((84*(qlimit-1))/100)
          self.count1=0
          self.count2=0
          self.count3=0
          self.limit_bytes = limit_bytes
          self.byte_size = 0  # Current size of the queue in bytes
          self.debug = debug
          self.busy = 0  # Used to track if a packet is currently being sent
          self.action = env.process(self.run())  # starts the run() method as a SimPy process
      

      
      
    def run(self):
        while True:
	    
            msg = (yield self.store.get())
	    self.busy = 1
            
	    self.byte_size -= msg.size
            yield self.env.timeout(msg.size*8.0/self.rate)
            self.out.put(msg)
            self.busy = 0
	    if self.debug:
       
                print(msg)
               

    def put(self, pkt):
        self.packets_rec += 1
	
	
       
	  # threshold conditions start from here 
        # this is for type 3
        if pkt.src is"type3" and len(self.store.items) <self.threshold1 and len(self.store.items) <=self.qlimit-1 :
              
             if len(self.store.items)<=self.abate_threshold1:
                   self.congestion=False
                   
             if not self.congestion:
                   self.byte_size += pkt.size
                   self.count1 +=1
                   return self.store.put(pkt)
             elif self.congestion:
                   self.packets_drop_3 +=1
      
        # this is also for type 3      
        elif pkt.src is"type3" and len(self.store.items) >=self.threshold1 and len(self.store.items) <=self.qlimit :
              self.packets_drop_3 +=1
              self.congestion = True
              
              
              
        ## this is also for type 2
        elif pkt.src is"type2" and len(self.store.items) <self.threshold2 and len(self.store.items) <=self.qlimit-1 :
          
            if len(self.store.items)<=self.abate_threshold2:
                  self.congestion=False
                  
            if not self.congestion:
                  self.byte_size += pkt.size
                  self.count2 +=1
                  return self.store.put(pkt)
            elif self.congestion:
                  self.packets_drop_2 +=1
        ## this is also for type 2 
        elif pkt.src is"type2" and len(self.store.items) >=self.threshold2 and len(self.store.items) <=self.qlimit :
              self.packets_drop_2 +=1
              self.congestion = True
              
            
            ## this is also for type 1      
        elif pkt.src is"type1" and len(self.store.items) <self.threshold3 and len(self.store.items) <=self.qlimit-1 :
              if len(self.store.items)<=self.abate_threshold3:
                    self.congestion=False
              if not self.congestion:
                    self.byte_size += pkt.size
                    self.count3 +=1
                    return self.store.put(pkt)
              elif self.congestion:
                    self.packets_drop_1 +=1
      
            ## this is also for type 1     
        elif pkt.src is"type1" and len(self.store.items) >=self.threshold3 and len(self.store.items) <=self.qlimit :
              self.packets_drop_1 +=1
              self.congestion = True
              
        ##
        else:
              if not self.congestion and len(self.store.items)<=self.abate_threshold1:
                    self.byte_size += pkt.size
                    return self.store.put(pkt)
            
        
           


class PortMonitor(object):
    """ A monitor for an SwitchPort. Looks at the number of items in the SwitchPort
        in service + in the queue and records that info in the sizes[] list. The
        monitor looks at the port at time intervals given by the distribution dist.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        port : SwitchPort
            the switch port object to be monitored.
        dist : function
            a no parameter function that returns the successive inter-arrival times of the
            packets
    """
    def __init__(self, env, port, dist, count_bytes=False):
        self.port = port
        self.env = env
        self.dist = dist
        self.count_bytes = count_bytes
        self.sizes = []
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(self.dist())
            if self.count_bytes:
                total = self.port.byte_size
            else:
                total = len(self.port.store.items) + self.port.busy
              
		
            self.sizes.append(total)


