Stock Trading Agent Using Reinforcement Learning:

In order to use the code, add the environment to the installed openai gym library and then run the given StockTraderagent file for the execution of the algoritms

Environment (StocksEnv.py):

It is an OpenAI Gym compatible environment.

Observation Space:

The observation space is of type “Box” containing 15 states.
All the values are positive.
The least value is zero.
The stock prices are in dollars

Following are the 15 state variables:		

1)Stock Quantity currently with the agent
2)Current Cash with the agent
3)Opening price of stock at current timestep
4)Last 10 days’ opening prices (4 to 13)
5)The average cost of the total stocks bought
6)The portfolio value which is the sum of the cash and the current stock investments

Action Space: 

It has 3 possibe actions and type is discrete(3)

0 Buy
1 Sell
2 Do nothing / sit


StockTraderagent.ipynb:

It is created on googlecolab and can be used directly on colab

It has 4 cells, the first cell is to import gym and spinning up and then copying the trading environment from git 

The next three cells are the execution of algorithms

DataProcessing.py

This file contains the code to process the stock data from quandl and dump it into a pickle file
