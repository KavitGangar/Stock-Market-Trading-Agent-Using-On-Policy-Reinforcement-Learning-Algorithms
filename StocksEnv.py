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
        #self.starting_shares_mean = 0
        #self.randomize_shares_std = 0
        #self.starting_cash_mean = 200
        #self.randomize_cash_std = 0
        
        #-----
        self.low_state = np.zeros((15,))
        self.high_state = np.zeros((15,))+1000000

        self.viewer = None

        #self.action_space = spaces.Box(low=0, high=4,
         #                              shape=(1,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)    
        self.observation_space = spaces.Box(low=self.low_state, high=self.high_state,
                                            dtype=np.float32)        
        
        #===
        
        self.state = np.zeros(15)
        
        self.starting_cash = 2000
        self.buycount=0
        self.sellcount=0
        self.nothing=0
        self.nothingpseudo=0

        self.series_length = 150
        #self.starting_point = 1
        #self.cur_timestep = self.starting_point
        
        #self.state[0] = 70
        #self.starting_portfolio_value = self.portfolio_value_states()
        #self.state[1] = self.starting_cash
        #self.state[2] = apl_open[self.cur_timestep]
        ##self.state[3] = self.starting_portfolio_value
        #self.state[4] = self.five_day_window()
        
        self.max_stride = 5
        self.stride = self.max_stride # no longer varying it
        
        self.done = False
        self.reward = 0
        self.diversification_bonus = 100
        self.inaction_penalty = 0
        self.ps = []
        self.g_t = []
    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):
        profit_sell = 0
        #print("\n previous state", " - " ,self.state[5]," - ",self.state[0], " - ",self.state[1], " - ",self.state[2])
        action = [action,1.]
        #print("\n previous state", " pf- " ,self.portfolio_value()," - ",self.state[0], " - ",self.state[1]," - ",self.state[2])
        cur_timestep = self.cur_timestep
        ts_left = self.series_length - (cur_timestep - self.starting_point)
        retval = None
        cur_value = self.portfolio_value()
        gain = cur_value - self.starting_portfolio_value
        
        
        if cur_timestep >= self.starting_point + (self.series_length * self.stride):
            new_state = [self.state[0], self.state[1], self.next_opening_price(), \
                         *self.five_day_window(),self.state[4],self.next_open_price(self.state[0])]
            self.state = new_state
            bonus = 0.
            if self.state[0] > 0 :
                bonus = self.diversification_bonus 
            self.g_t.append(gain)    
            self.reward +=bonus + gain
            print("\n ", gain ," - " ,self.buycount , " - " ,self.sellcount, "-" ,self.nothing,"- ",self.nothingpseudo) 
            return np.array(new_state), bonus + gain*10000 , True, { "msg": "done"}
        
        
        
        if action[0] == 2:
            if action[1] > self.state[0]:
                self.nothingpseudo+=1
                new_state = [self.state[0], self.state[1] ,self.next_opening_price(), \
                     *self.five_day_window(),self.state[13],self.next_open_price(self.state[0])]
                self.state = new_state
                self.reward += -100000
                retval = np.array(new_state), -ts_left  -1000 , False, { "msg": "nothing" }

            else:
                self.sellcount += 1
                apl_shares = self.state[0] - action[1]
                cash_gained = action[1] * apl_open[cur_timestep] * 0.9
                new_state = [apl_shares , self.state[1] + cash_gained, self.next_opening_price(), \
                       *self.five_day_window(),self.state[13],self.next_open_price(apl_shares)]
                
                self.state = new_state
                profit_sell = apl_open[cur_timestep] - self.state[13]
                self.ps.append(profit_sell)
                cur_value = self.portfolio_value()
                gain = cur_value - self.starting_portfolio_value
                self.reward += -ts_left +gain
                retval = np.array(new_state), -ts_left  + (profit_sell*10) + self.giveShareRew() , False, { "msg": "sold AAPL"}
        
        
        
        if action[0] == 1:
            self.nothing += 1
            new_state = [self.state[0], self.state[1] ,self.next_opening_price(), \
                     *self.five_day_window(),self.state[13],self.next_open_price(self.state[0])]
            self.state = new_state
            self.reward += -self.inaction_penalty-ts_left +gain*100
            retval = np.array(new_state),   -ts_left + self.giveShareRew() , False, { "msg": "nothing" }
        
        if action[0] == 0:
            if action[1] * apl_open[cur_timestep] > self.state[1]:
                new_state = [self.state[0], self.state[1], self.next_opening_price(), \
                         *self.five_day_window(),self.state[13],self.next_open_price(self.state[0])]
                self.state = new_state
                self.reward += -100000
               # print("\nEpisode Terminating Bankrupt REWARD = " ,self.reward," - " ,self.buycount , " - " ,self.sellcount, "-" ,self.nothing ,"- ",self.nothingpseudo)
                
                retval = np.array(new_state), -ts_left -1000 ,False, { "msg": "bankrupted self"}
                
            else:
                self.buycount+=1
                apl_shares = self.state[0] + action[1]
                cash_spent = action[1] * apl_open[cur_timestep] * 1.1
                new_state = [apl_shares, self.state[1] - cash_spent, self.next_opening_price(), \
                        *self.five_day_window(),self.calcAvg(self.state[13],apl_open[cur_timestep]),self.next_open_price(apl_shares)]
                self.state = new_state
                cur_value = self.portfolio_value()
                gain = cur_value - self.starting_portfolio_value
                self.reward += -ts_left +gain
                retval = np.array(new_state), -ts_left + self.giveShareRew(), False, { "msg": "bought AAPL"}
                
        

                

                
        #print("\n action taken: ",action, " pf- " ,self.portfolio_value()," - ",self.state[0],  " - ",self.state[1])
        self.cur_timestep += self.stride

        return retval

    def reset(self):
        self.state = np.zeros(15)
        self.starting_cash = 2500
        self.cur_timestep = 10
        self.starting_point = self.cur_timestep
        self.state[0] = random.randint(20,100)
        self.state[1] = random.randint(1000,5000)
        self.state[2] = apl_open[self.cur_timestep]
        self.starting_portfolio_value = self.portfolio_value_states()
        self.state[3:13] = self.five_day_window()
        self.state[13] = apl_open[self.cur_timestep]
        self.state[14] = self.starting_portfolio_value
        self.buycount=0
        self.sellcount=0
        self.nothing=0
        self.nothingpseudo=0
        self.done = False
        self.reward = 0
        self.ps = []
        
        return self.state

    
    def portfolio_value(self):
        return (self.state[0] * apl_close[self.cur_timestep])  + self.state[1]


    def portfolio_value_states(self):
        return (self.state[0] * apl_open[self.cur_timestep])  + self.state[1]
    
    def next_opening_price(self):
        step = self.cur_timestep + self.stride
        return apl_open[step]
        
    def next_open_price(self,apl_):
        step = self.cur_timestep + self.stride
        return (apl_ * apl_open[step])

    

    def five_day_window(self):
        step = self.cur_timestep
        if step < 5:
            return apl_open[0]
        apl5 = apl_open[step-5:step].mean()
        
        return apl_open[step-10:step]
    
    def calcAvg(self,prev,new):
        return ((prev*self.state[0])+new)/(self.state[0]+1)
    
    def giveShareRew(self):
        return self.state[0]/10
    
    
    def render(self, mode='human'):
        print("Render called")
        plt.plot(self.g_t)
        
        
    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None
    
            
