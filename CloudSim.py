#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 20:09:47 2018

@author: Deepankar Sharma
"""

import random
import numpy as np
import simpy
from matplotlib import pyplot

SIM_TIME = 10000
RANDOM_SEED = 15
ARRIVAL_TIME = [x*10 for x in reversed(range(1, 11))]
SERVER_CAPACITY = 25000 #in Mbps (20 Gbps)
SERVER_OUTBUFF_SIZE = 100000 #in Mb (10 Gb)
K = 10 #playout buffer length
S = 3 #time of video segment offered by server (in seconds)
PATIENCE = 10 #avg client patience limit in seconds
BITRATE_LIST = np.array([0.7, 1, 2, 4, 6, 13, 34]) #240p,360P,480P,720P,1080P,2K,4K in Mbps
#%% network
class Server(object):
    def __init__(self, env, server):
        self.env = env
        self.server = server

        self.flag = [None]

    def service(self, clientDLspeed, num_segments, segmentId, bitrate, rtt):
        segment_size = BITRATE_LIST[bitrate] * S
        segment_req = num_segments * segment_size
        serveTimeStart = self.env.now
        if (serverOutputBuff[0] + segment_req <= SERVER_OUTBUFF_SIZE): #check if server output buff has space
            with self.server.request() as req:
                serverOutputBuff[0] += segment_req
                results = yield req | self.env.timeout(rtt)
                if req in results:
                    indicator = True
                    serverOutputBuff[0] -= segment_req
                    yield self.env.timeout((segment_req/SERVER_CAPACITY) + rtt)
                else:
                    indicator = False
                    self.flag = [False]
            if indicator:
                yield self.env.timeout(segment_req/clientDLspeed) # client access delay
            self.flag = [True, num_segments]
        else:
            self.flag = [False] #server output buffer full

    #def notoverflow(self, size):
    #    check = (serverOutputBuff[0] + size <= SERVER_OUTBUFF_SIZE)
    #    return check

class Client(object):
    def __init__(self, env, server, clientID, arrivalTime):
        self.env = env
        self.server = server
        self.ID = clientID

        self.startup = 1 #val = 1 if network is starting up
        self.bitrate = [0]
        self.playoutBuffer = Queue()
        self.quit = 0
        self.sessionsCompleted = 0
        self.start = self.env.now
        self.avgArrival = arrivalTime
        self.everPlayed = 0
        self.patience = np.random.normal(PATIENCE,PATIENCE/10)
        self.playTimeStart = 0

    def downloadRequest(self, num_sessions, duration, bandwidth, rtt):
        current_session = 0
        for current_session in range(num_sessions):
            while duration[current_session] + self.start > self.env.now: #if false then client has finished watching video
                request = Server(self.env, self.server)
                if self.everPlayed == 0:
                    segmentId = 0
                    yield self.env.process(request.service(bandwidth, K, segmentId, self.bitrate[-1], rtt))
                else:
                    yield self.env.process(request.service(bandwidth, 1, segmentId, self.bitrate[-1], rtt)) \
                        | self.playback()
    
                if request.flag[0]:
                    #self.startup = 0
                    if self.playoutBuffer.q: #check if buffer is already populated (but maynot be full)
                        seg = [self.playoutBuffer.q[-1] + 1]
                    else:
                        seg = [x for x in range(request.flag[1])]
                    self.playoutBuffer.put(seg)
                    segmentId = self.playoutBuffer.q[-1] + 1 #update ID for next segment
                    self.bitrate.append(self.increase(self.bitrate[-1], bandwidth))
                elif len(self.playoutBuffer.q) == 0:
                    #yield self.env.timeout(np.random.normal(PATIENCE,PATIENCE/10)) #patience for users is modeled as normal df
                    if self.everPlayed == 0:
                        if (self.env.now - self.start) > self.patience:
                            self.quit = 1
                            log_data.append(getCount(network))
                            timestamp.append(self.env.now)
                            serverstatus.append(serverOutputBuff[0])
                            current_session = num_sessions + 1 #to break also from outer loop
                            break # break from inner while loop
                        else:
                            continue
                    else:
                        if (self.env.now - (self.playTimeStart + S)) > self.patience:
                            #if self.startup = 1, then client abandons session due to startup delay
                            #otherwise, client abandons session due to video sta
                            self.quit = 2 
                            log_data.append(getCount(network))
                            timestamp.append(self.env.now)
                            serverstatus.append(serverOutputBuff[0])
                            current_session = num_sessions + 1 #to break also from outer loop
                            break # break from inner while loop
                        else:
                            continue
                else:
                    self.bitrate.append(self.decrease(self.bitrate[-1]))
               
                if self.playoutBuffer.__len__() == K: #playout buffer length
                    yield self.playback()
            
            if self.quit == 0:
                self.sessionsCompleted += 1
            print('current sesh = ',self.sessionsCompleted)
            current_session += 1
            self.everPlayed = 0
        
        self.quit = 3 if self.quit == 0 else self.quit 
        

    def playback(self):
        self.everPlayed = 1
        self.playTimeStart = self.env.now
        if self.playoutBuffer.q:
            self.playoutBuffer.get()
        return self.env.timeout(S)

    @staticmethod
    def increase(bitrate, bandwidth):
        length = len(BITRATE_LIST[BITRATE_LIST < bandwidth])
        return (bitrate + 1) if (bitrate < (length-1)) else bitrate

    @staticmethod
    def decrease(bitrate):
        return (bitrate - 1) if (bitrate > 0) else bitrate

class networkSetup(object):
    def __init__(self, env, server):
        self.env = env
        self.server = server
        self.client = []
        self.clientIDlist = [x for x in range(user_count)]
        random.shuffle(self.clientIDlist)
        
    def clientArrival(self, arrivalTime):
        count = 0
        for user in self.clientIDlist:
            clientID = self.clientIDlist.pop(0) #for randomizing the type of client to arrive
            bandwidth = int(client_data[clientID].split(" ")[1].split("-")[0]) # in Mbps
            num_sessions = int(client_data[clientID].split(" ")[2])
            rtt = float(rtt_data[clientID])/1000 #divided by 1000 to obtain rtt in seconds
            duration = np.empty(num_sessions)
            
            if (bandwidth == 3): duration = random.sample(sessionDurs[0],num_sessions)
            elif (bandwidth == 6): duration = random.sample(sessionDurs[1],num_sessions)
            elif (bandwidth == 9): duration = random.sample(sessionDurs[2],num_sessions)
            elif (bandwidth == 12): duration = random.sample(sessionDurs[3],num_sessions)
            elif (bandwidth == 20): duration = random.sample(sessionDurs[4],num_sessions)
                          
            self.client.append(Client(self.env, self.server, clientID, arrivalTime))
            yield self.env.timeout(np.random.exponential(arrivalTime)) \
              | self.env.process(self.client[count].downloadRequest(num_sessions, duration, bandwidth, rtt))
            count += 1
# =============================================================================
#     @classmethod
#     def clientinfo(cls):
#         
#         return [bandwidth, duration]
# 
# =============================================================================
class Queue(object):
    def __init__(self):
        self.q = [] #contains list of segments with segmentID

    def put(self, seg):
        return self.q.extend(seg)

    def get(self):
        return self.q.pop(0)

    def __len__(self):
        return len(self.q)

#%% Statistics
def getCount(model):
    client_list = [x.quit for x in model.client]
    client_sc = [x.sessionsCompleted for x in model.client]
    Ntotal = len(model.client)
    Nstay = client_list.count(0)
    Nstart = client_list.count(1)
    Nstall = client_list.count(2)
    Nschedule = client_list.count(3)
    SC = np.mean(client_sc)
    return [Ntotal, Nstart, Nstall, Nschedule, Nstay, SC]

#%% Main Program
if __name__ == "__main__":
    # Data processing for using traces from txt files
    session_data = open('session_duration.txt', 'r').read().split('\n')
    session_data.pop(0)
    session_data.pop(-1)
    client_data = open('sessions_per_user.txt','r').read().split('\n')
    client_data.pop(0) #removing useless lines
    client_data.pop(-1)
    user_count = len(client_data)
    rtt_data = open('rtt_samples.txt','r').read().split('\n')
    rtt_data.pop(0)
    rtt_data.pop(-1)
    lenData = len(session_data)
    sessionDurs = [[],[],[],[],[]]
    # sorting session durations by bandwidth of session
    for i in range(0,lenData-1):
        BW = session_data[i].split(" ")[0].split("~")[0]
        if (BW == '3'): #for 3Mbps access capacity
            sessionDurs[0].append(float(session_data[i].split(" ")[1]))
        elif (BW == '6'): #for 6Mbps access capacity
            sessionDurs[1].append(float(session_data[i].split(" ")[1]))
        elif (BW == '9'): #for 9Mbps access capacity
            sessionDurs[2].append(float(session_data[i].split(" ")[1]))
        elif (BW == '12'): #for 12Mbps access capacity
            sessionDurs[3].append(float(session_data[i].split(" ")[1]))
        else: #for 20Mbps access capacity
            sessionDurs[4].append(float(session_data[i].split(" ")[1]))
    
    
    #variables for data monitoring
    log_data = [[]]
    timestamp = []
    serverstatus = []
    section = []

    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    #for arrivalTime in ARRIVAL_TIME:
    arrivalTime = 5
    print('Client arrival time in seconds = ', arrivalTime)
    env = simpy.Environment()
    server = simpy.Resource(env, 1)
    network = networkSetup(env, server)
    serverOutputBuff = [0]
    env.process(network.clientArrival(arrivalTime))
    env.run(until=SIM_TIME)

#%% Plot
# =============================================================================
#     start = []
#     stall = []
#     stay = []
#     schedule = []
#     abandon = []
# 
#     #for j in range(10):
#     stay.append([client_data[section[i]-1][4]/client_data[section[i]-1][0] for i in range(10)])
#     start.append([client_data[section[i]-1][1]/client_data[section[i]-1][0] for i in range(10)])
#     stall.append([client_data[section[i]-1][2]/client_data[section[i]-1][0] for i in range(10)])
#     schedule.append([client_data[section[i]-1][3]/client_data[section[i]-1][0] for i in range(10)])
#     abandon.append([start[i]+stall[i] for i in range(10)])
# 
#     data_stay = [[np.mean(x) for x in stay], [np.max(x)-np.mean(x) for x in stay], [np.mean(x)-np.min(x) for x in stay]]
#     data_start = [[np.mean(x) for x in start], [np.max(x)-np.mean(x) for x in start], [np.mean(x)-np.min(x) for x in start]]
#     data_stall = [[np.mean(x) for x in stall], [np.max(x)-np.mean(x) for x in stall], [np.mean(x)-np.min(x) for x in stall]]
#     data_schedule = [[np.mean(x) for x in schedule], [np.max(x)-np.mean(x) for x in schedule], [np.mean(x)-np.min(x) for x in schedule]]
#     data_abandon = [[np.mean(x) for x in abandon], [np.max(x)-np.mean(x) for x in abandon], [np.mean(x)-np.min(x) for x in abandon]]
# 
#     ind = np.arange(len(ARRIVAL_TIME))
#     width = 0.3
# 
#     #pyplot.errorbar(ARRIVAL, data_abandon[0], yerr=[data_abandon[1], data_abandon[2]], fmt='.:', capsize=5, elinewidth=5)
#     #pyplot.errorbar(ARRIVAL, data_schedule[0], yerr=[data_schedule[1], data_schedule[2]], fmt='.:', capsize=5, elinewidth=5)
#     #pyplot.errorbar(ARRIVAL, data_stay[0], yerr=[data_stay[1], data_stay[2]], fmt='.:', capsize=5, elinewidth=5)
#     pyplot.xlabel('Arrival Rate')
#     pyplot.ylabel('Percentage')
#     pyplot.xticks(ARRIVAL)
#     pyplot.title('Change of Client Trend Chart')
#     pyplot.legend(['abandon', 'duration end', 'remain'])
#     pyplot.tight_layout()
#     pyplot.show()
# 
#     #pyplot.errorbar(ARRIVAL, data_abandon[0], yerr=[data_abandon[1], data_abandon[2]], color='#2ca02c', fmt='--', capsize=5, elinewidth=5)
#     pyplot.bar(1+ind-1/2*width, data_start[0], width, yerr=[data_start[1], data_start[2]], capsize=2)
#     pyplot.bar(1+ind+1/2*width, data_stall[0], width, yerr=[data_stall[1], data_stall[2]], capsize=2)
#     pyplot.xlabel('Arrival Rate')
#     pyplot.ylabel('Percentage')
#     pyplot.xticks(ARRIVAL_TIME)
#     pyplot.title('Service Abandan Trend Chart')
#     pyplot.legend(['abandon', 'startup delay', 'video stall'])
#     pyplot.tight_layout()
#     pyplot.show()
# =============================================================================
#%%    width = 0.25
# =============================================================================
# 
#     fig, ax = pyplot.subplots(2, 2, figsize=(10, 8))
# 
#     label = ['5-10 min', '10-15 min', '15-20 min',
#              '20-25 min', '25-30 min']
#     for i in range(2):
#         x = getData(300, ARRIVAL[i], 300)
#         ind = np.arange(len(x[0])-1)
#         ax[0][i].bar(ind - width, x[0][1:], width)
#         ax[0][i].bar(ind, [x[1][i]+x[2][i] for i in range(1, len(x[0]))], width)
#         ax[0][i].bar(ind + width, [x[3][i]+x[4][i] for i in range(1, len(x[0]))], width)
#         ax[0][i].set_xticks(ind)
#         ax[0][i].set_xticklabels(label)
#         ax[0][i].set_title('Arrival Rate = %d'%ARRIVAL[i*3])
#     for i in range(2):
#         x = getData(300, ARRIVAL[(i+2)], 300)
#         ind = np.arange(len(x[0])-1)
#         ax[1][i].bar(ind - width, x[0][1:], width)
#         ax[1][i].bar(ind, [x[1][i]+x[2][i] for i in range(1, len(x[0]))], width)
#         ax[1][i].bar(ind + width, [x[3][i]+x[4][i] for i in range(1, len(x[0]))], width)
#         ax[1][i].set_xticks(ind)
#         ax[1][i].set_xticklabels(label)
#         ax[1][i].set_title('Arrival Rate = %d'%ARRIVAL[(i+2)*3])
# 
#     fig.text(0, 0.51, 'Number', va='center', rotation='vertical')
#     fig.text(0.35, 0.99, 'Number of Clients in Time Blocks', fontsize='x-large')
#     fig.legend(['New Arrival', 'Error', 'Normal'])
#     pyplot.tight_layout()
# 
# =============================================================================
