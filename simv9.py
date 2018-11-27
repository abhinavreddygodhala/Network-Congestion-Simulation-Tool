import random
import functools
import simpy
import numpy as np
import matplotlib.pyplot as plt
from SimClasses import PacketGenerator, PacketSink, SwitchPort, PortMonitor

import pandas as pd
#import pandas_datareader.data as web

# inter arrivals and size of the packet generators
ty1 = functools.partial(random.expovariate,0.50)
tysz1 = functools.partial(random.normalvariate,180,10)  
ty2 = functools.partial(random.expovariate,0.30)
tysz2 = functools.partial(random.normalvariate,230,10)
ty3 = functools.partial(random.expovariate,0.20)
tysz3 = functools.partial(random.normalvariate,260,10)

#sample distance for port monitor
samp_dist = functools.partial(random.normalvariate,0.99985,0)
port_rate = 1024

env = simpy.Environment()  # Create the SimPy environment
# Create the packet generators and sink
ps = PacketSink(env, port_rate, debug=True,rec_arrivals=True, absolute_arrivals=False)
type1 = PacketGenerator(env, "type1", ty1, tysz1,finish=650,debug=False)
type2 = PacketGenerator(env, "type2", ty2, tysz2,finish=650,debug=False)
type3 = PacketGenerator(env, "type3", ty3, tysz3,finish=650,debug=False)
#initialising queue and server
switch_port = SwitchPort(env, port_rate, qlimit=100,limit_bytes=False,debug= False)

# Using a PortMonitor to track queue sizes over time
pm = PortMonitor(env, switch_port,samp_dist)

# Wire packet generators, switch ports, and sinks together
type1.out = switch_port
type2.out = switch_port
type3.out = switch_port

#here it sends the serviced packets to a packet sink
switch_port.out = ps
# Run it
env.run(until=800)


queue=[]
i = 0
for i in range(len(pm.sizes)):
      if pm.sizes[i]>0:
            queue.append(pm.sizes[i])

print("queue sizes: {}".format(pm.sizes))
      

print("Mean number of jobs in the queue = {:.3f}" .format(float(sum(queue))/len(queue)))


print("Mean waiting time               : type1 = {:.3f}    type2 = {:.3f}  type3 = {:.3f}".format((sum(ps.waits1)/len(ps.waits1)),(sum(ps.waits2)/len(ps.waits2)),(sum(ps.waits3)/len(ps.waits3))))
print("Mean waiting times of all types : = {:.3f}".format(((sum(ps.waits1)+sum(ps.waits2)+sum(ps.waits3))/(len(ps.waits1)+len(ps.waits2)+len(ps.waits3)))))
print("Mean response time              : type1 = {:.3f}    type2 = {:.3f}  type3 = {:.3f}".format((sum(ps.resp1)/len(ps.resp1)),(sum(ps.resp2)/len(ps.resp2)),(sum(ps.resp3)/len(ps.resp3))))
print("Mean response time              : = {:.3f}".format((sum(ps.resp1)+sum(ps.resp2)+sum(ps.resp3))/(len(ps.resp1)+len(ps.resp2)+len(ps.resp3))))
print("Arrival rate                    : type1 = {:.3f}      type2 = {:.3f}    type3 = {:.3f}".format(((len(ps.arrivalsrate1))/sum(ps.arrivalsrate1)),((len(ps.arrivalsrate2))/sum(ps.arrivalsrate2)),((len(ps.arrivalsrate3))/sum(ps.arrivalsrate3))))
print("Mean Arrival rate of all types  : = {:.3f}".format(( type1.packets_sent+type2.packets_sent+type3.packets_sent)/(sum(ps.arrivalsrate1)+sum(ps.arrivalsrate2)+sum(ps.arrivalsrate3))))
print("Mean service rate               : type1 = {:.3f}      type2 = {:.3f}    type3 = {:.3f}".format(1/(sum(ps.service1)/len(ps.service1)),(1/(sum(ps.service2)/len(ps.service2))),(1/(sum(ps.service3)/len(ps.service3)))))
print("Mean service rate of all types  : = {:.3f}".format(1/((sum(ps.service1)+sum(ps.service2)+sum(ps.service3))/(len(ps.service1)+len(ps.service2)+len(ps.service3)))))
print("Mean service time               : type1 = {:.3f}      type2 = {:.3f}    type3 = {:.3f}".format((sum(ps.service1)/(len(ps.service1))),(sum(ps.service2)/(len(ps.service2))),(sum(ps.service3)/(len(ps.service3)))))
print("Mean service time of all types  : = {:.3f}".format((sum(ps.service1)+sum(ps.service2)+sum(ps.service3))/(len(ps.service1)+len(ps.service2)+len(ps.service3))))
print("Throughput                      : = {:.3f}".format((ps.packets_rec/(sum(ps.arrivalsrate1)+sum(ps.arrivalsrate2)+sum(ps.arrivalsrate3)))))
print("Utilization                     : = {:.3f}".format((100)*(ps.packets_rec/(sum(ps.arrivalsrate1)+sum(ps.arrivalsrate2)+sum(ps.arrivalsrate3)))*((sum(ps.service1)+sum(ps.service2)+sum(ps.service3))/(len(ps.service1)+len(ps.service2)+len(ps.service3)))))
print("Arrival rate* Mean witing time  : = {:.3f}".format((( type1.packets_sent+type2.packets_sent+type3.packets_sent)/(sum(ps.arrivalsrate1)+sum(ps.arrivalsrate2)+sum(ps.arrivalsrate3)))*((sum(ps.waits1)+sum(ps.waits2)+sum(ps.waits3))/(len(ps.waits1)+len(ps.waits2)+len(ps.waits3)))))


print "------------------------------------------------------------------------"
print("type 1- total sent: {}  recieved: {}  dropped {} \ntype 2- total sent: {}  recieved: {}  dropped {} \ntype 3- total sent: {}  recieved: {}  dropped {}".format(type1.packets_sent,ps.type1_rec,switch_port.packets_drop_1,type2.packets_sent,ps.type2_rec,switch_port.packets_drop_2,type3.packets_sent,ps.type3_rec,switch_port.packets_drop_3))
print("serviced packets:   {}  total sent: {}".format(ps.packets_rec,  type1.packets_sent+type2.packets_sent+type3.packets_sent))
print("loss percent: {:.2f}".format(float(switch_port.packets_drop_1+switch_port.packets_drop_2+switch_port.packets_drop_3)*100/switch_port.packets_rec))
#print("average system occupancy: {:.3f}".format(float(sum(pm.sizes))/len(pm.sizes)))


print switch_port.count1
print switch_port.count2
print switch_port.count3
group_names=['Type 1', 'Type 2', 'Type 3']
group_size=[type1.packets_sent,type2.packets_sent,type3.packets_sent]
subgroup_names=['Recieved: {}'.format(ps.type1_rec), 'Dropped: {}'.format(switch_port.packets_drop_1), 'Recieved: {}'.format(ps.type2_rec), 'Dropped: {}'.format(switch_port.packets_drop_2), 'Recieved: {}'.format(ps.type3_rec), 'Dropped: {}'.format(switch_port.packets_drop_3)]
subgroup_size=[ps.type1_rec,switch_port.packets_drop_1,ps.type2_rec,switch_port.packets_drop_2,ps.type3_rec,switch_port.packets_drop_3]


