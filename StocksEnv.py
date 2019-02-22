import math
import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np
import random

import matplotlib.pyplot as plt

import pickle
with open("./aplmsfopenclose.pkl", "rb") as f:
    d = pickle.load(f)


apl_open = d["ao"]
apl_close = d["ac"]
msf_open = d["mo"]
msf_close = d["mc"]


class StocksEnv(gym.Env):
    

    def __init__(self):
        
        self.starting_shares_mean = 0
        self.randomize_shares_std = 0
        self.starting_cash_mean = 200
        self.randomize_cash_std = 0
        self.buycount = 0
        self.sellcount = 0
        self.sitcount = 0
        #-----
        self.low_state = np.zeros((14,))
        self.high_state = np.zeros((14,))+100000000

        self.viewer = None

        #self.action_space = spaces.Box(low=0, high=4,
         #                              shape=(1,), dtype=np.float32)
        self.action_space = spaces.Discrete(5)    
        self.observation_space = spaces.Box(low=self.low_state, high=self.high_state,
                                            dtype=np.float32)        
        
        #===
        
        self.state = np.zeros(14)
        
        self.starting_cash = 2000

        self.series_length = 200
        self.starting_point = 41
        self.cur_timestep = self.starting_point
        
        self.state[0] = random.randint(0,10)
        self.state[1] = random.randint(0,10)
        self.starting_portfolio_value = self.portfolio_value_open()
        self.state[2] = self.starting_cash
        self.state[3] = apl_open[self.cur_timestep]
        self.state[4] = msf_open[self.cur_timestep]
        self.state[5] = self.starting_portfolio_value
        self.state[6] = self.five_day_window()[0]
        self.state[7] = self.five_day_window()[1]
        self.state[8] = self.five_day_window()[2]
        self.state[9] = self.five_day_window()[3]
        self.state[10] = self.five_day_window()[4]
        self.state[11] = self.five_day_window()[5]
        self.state[12] = self.five_day_window()[6]
        self.state[13] = self.five_day_window()[7]
        
        self.max_stride = 3
        self.stride = self.max_stride # no longer varying it
        
        self.done = False
        self.diversification_bonus = 1.
        self.inaction_penalty = 0

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):

      	#print("\n previous state", " - " ,self.state[5]," - ",self.state[0], " - ",self.state[1], " - ",self.state[2])
        action = [action,1.]
        #print("\n previous state", " - " ,self.state[5]," - ",self.state[0], " - ",self.state[1], " - ",self.state[2])
        cur_timestep = self.cur_timestep
        #ts_left = self.series_length*self.stride - (cur_timestep - self.starting_point)
        ts_left = 0
        retval = None
        cur_value = self.portfolio_value()
        gain = cur_value - self.starting_portfolio_value
        
        if cur_timestep >= self.starting_point + (self.series_length * self.stride):
            new_state = [self.state[0], self.state[1], self.state[2], *self.next_opening_price(), \
                        cur_value, *self.five_day_window()]
            self.state = np.array(new_state)
            bonus = 0.
            if self.state[0] > 0 and self.state[1] > 0:
                bonus = self.diversification_bonus
            #print("\nEpisode Terminating done  -- portfoliovalue is " , cur_value )
            #print("\nendstate",self.state)
            return np.array(new_state), bonus+gain, True, { "msg": "done"}
        
        if action[0] == 2:
            self.sitcount = self.sitcount + 1
            new_state = [self.state[0], self.state[1], self.state[2], *self.next_opening_price(), \
                    self.next_open_price(self.state[0],self.state[1])+self.state[2], *self.five_day_window()]
            self.state = np.array(new_state)
            retval = np.array(new_state), -100, False, { "msg": "nothing" }
            
        if action[0] == 0:
            self.buycount = self.buycount + 1
            if action[1] * apl_open[cur_timestep] > self.state[2]:
                new_state = [self.state[0], self.state[1], self.state[2], *self.next_opening_price(), \
                        cur_value, *self.five_day_window()]
                self.state = np.array(new_state)
                #print("\nEpisode Terminating Bankrupt")
                retval = np.array(new_state), -100000, True, { "msg": "bankrupted self"}
            else:
                apl_shares = self.state[0] + action[1]
                cash_spent = action[1] * apl_open[cur_timestep] * 1.1
                new_state = [apl_shares, self.state[1], self.state[2] - cash_spent, *self.next_opening_price(), \
                       self.next_open_price(apl_shares,self.state[1]) + self.state[2] - cash_spent, *self.five_day_window()]
                self.state = np.array(new_state)
                cur_value = self.portfolio_value()
                gain = cur_value - self.starting_portfolio_value
                retval = np.array(new_state), self.inaction_penalty-ts_left+gain, False, { "msg": "bought AAPL"}
                
        if action[0] == 3:
            self.buycount = self.buycount + 1
            if action[1] * msf_open[cur_timestep] > self.state[2]:
                new_state = [self.state[0], self.state[1], self.state[2], *self.next_opening_price(), \
                        cur_value, *self.five_day_window()]
                self.state = np.array(new_state)
                #print("\nEpisode Terminating Bankrupt__")
                retval =  np.array(new_state), -100000, True, { "msg": "bankrupted self"}
            else:
                msf_shares = self.state[1] + action[1]
                cash_spent = action[1] * msf_open[cur_timestep] * 1.1
                new_state = [self.state[0], msf_shares, self.state[2] - cash_spent, *self.next_opening_price(), \
                       self.next_open_price(self.state[0],msf_shares)  + self.state[2] - cash_spent , *self.five_day_window()]
                self.state = np.array(new_state)
                cur_value = self.portfolio_value()
                gain = cur_value - self.starting_portfolio_value
                retval = np.array(new_state), self.inaction_penalty-ts_left+gain, False, { "msg": "bought MSFT"}
        

        if action[0] == 1:
            self.sellcount = self.sellcount + 1
            if action[1] > self.state[0]:
                new_state = [self.state[0], self.state[1], self.state[2], *self.next_opening_price(), \
                        cur_value, *self.five_day_window()]
                self.state = np.array(new_state)
                #print("\nEpisode Terminating soldmore")
                retval = np.array(new_state), -100000, True, { "msg": "sold more than have"}
            else:
                apl_shares = self.state[0] - action[1]
                cash_gained = action[1] * apl_open[cur_timestep] * 0.9
                new_state = [apl_shares, self.state[1], self.state[2] + cash_gained, *self.next_opening_price(), \
                       self.next_open_price(apl_shares,self.state[1]) + self.state[2] + cash_gained, *self.five_day_window()]
                self.state = np.array(new_state)
                cur_value = self.portfolio_value()
                gain = cur_value - self.starting_portfolio_value
                retval = np.array(new_state), self.inaction_penalty-ts_left+gain, False, { "msg": "sold AAPL"}
                
        if action[0] == 4:
            self.sellcount = self.sellcount + 1
            if action[1] > self.state[1]:
                new_state = [self.state[0], self.state[1], self.state[2], *self.next_opening_price(), \
                        cur_value, *self.five_day_window()]
                self.state = np.array(new_state)
                #print("\nEpisode Terminating soldmore4")
                retval = np.array(new_state), -100000, True, { "msg": "sold more than have"}
            else: 
                msf_shares = self.state[1] - action[1]
                cash_gained = action[1] * msf_open[cur_timestep] * 0.9
                new_state = [self.state[0], msf_shares, self.state[2] + cash_gained, *self.next_opening_price(), \
                       self.next_open_price(self.state[0],msf_shares) + self.state[2] + cash_gained , *self.five_day_window()]
                self.state = np.array(new_state)
                cur_value = self.portfolio_value()
                gain = cur_value - self.starting_portfolio_value
                retval = np.array(new_state), self.inaction_penalty-ts_left+gain, False, { "msg": "sold MSFT"}
                
        #print("\n action taken: ",action, " - " ,self.state[5]," - ",self.state[0], " - ",self.state[1], " - ",self.state[2]," g ",gain)
        self.cur_timestep += self.stride
        #if retval[2] == True:
         #   print("\nendstate",self.state)
        return retval

    def reset(self):
       # print ("\n",self.buycount,"  ",self.sitcount,"  ",self.sellcount)
        self.state = np.zeros(14)
        self.starting_cash = 200
        self.cur_timestep = 41
        self.state[0] = random.randint(20,100)
        self.state[1] = random.randint(20,100)
        self.state[2] = random.randint(100,2000)
        self.state[3] = apl_open[self.cur_timestep]
        self.state[4] = msf_open[self.cur_timestep]
        self.starting_portfolio_value = self.portfolio_value()
        self.state[5] = self.starting_portfolio_value
        self.state[6] = self.five_day_window()[0]
        self.state[7] = self.five_day_window()[1]  
        self.state[8] = self.five_day_window()[2]
        self.state[9] = self.five_day_window()[3]
        self.state[10] = self.five_day_window()[4]
        self.state[11] = self.five_day_window()[5]
        self.state[12] = self.five_day_window()[6]
        self.state[13] = self.five_day_window()[7]
        
        self.done = False
        self.buycount = 0
        self.sellcount = 0
        self.sitcount = 0
        
        #print("\nState:",self.state)
        return self.state
        

    
    def portfolio_value(self):
        return (self.state[0] * apl_close[self.cur_timestep]) + (self.state[1] * msf_close[self.cur_timestep]) + self.state[2]
    
    def portfolio_value_open(self):
        return (self.state[0] * apl_open[self.cur_timestep]) + (self.state[1] * msf_open[self.cur_timestep]) + self.state[2]
   
    
    def next_opening_price(self):
        step = self.cur_timestep + self.stride
        return [apl_open[step], msf_open[step]]
    
    def next_open_price(self,apl_,msf_):
        step = self.cur_timestep + self.stride
        return (apl_ * apl_open[step]) + (msf_ * msf_open[step]) 
           
    
    '''
    def five_day_window(self):
        step = self.cur_timestep
        if step < 5:
            return [apl_open[0], msf_open[0]]
        apl5 = apl_open[step-5:step].mean()
        msf5 = msf_open[step-5:step].mean()
        return [apl5, msf5]
    '''
    def five_day_window(self):
        step = self.cur_timestep
        if step < 5:
            return [apl_open[0], msf_open[0]]
        apl10 = apl_open[step-10:step].mean()
        msf10 = msf_open[step-10:step].mean()
        apl20 = apl_open[step-20:step-10].mean()
        msf20 = msf_open[step-20:step-10].mean()
        apl30 = apl_open[step-30:step-20].mean()
        msf30 = apl_open[step-30:step-20].mean()
        apl40 = msf_open[step-40:step-30].mean()
        msf40 = msf_open[step-40:step-30].mean()
        return [apl10, msf10, apl20, msf20, apl30, msf30, apl40, msf40]
    
    
    def render(self, mode='human'):
        print("Render called")
        
    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None
