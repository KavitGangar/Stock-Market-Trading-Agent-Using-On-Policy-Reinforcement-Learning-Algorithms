# Import pandas 
import pandas as pd 
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime 

# reading csv file  
df1 = pd.read_csv("SBI.csv") 
df2 = pd.read_csv("nike.csv") 

# Turns out that on 19 Nov 2014, SBI stock was split in the ratio of 1:10. So, we divide everything before element 214 in the stock array by 10 to correct for this.

open_df_1 = df1['Open']
open_df_1[:214] /= 10
close_df_1 = df1['Close']
close_df_1[:214] /= 10

# Same case with nike

open_df_2 = df2['Open']
open_df_2[:499] /= 2
close_df_2 = df2['Close']
close_df_2[:499] /= 2


from scipy import signal


# we need to de-trend the data. We want the AI to learn the fundamentals of the stock signal - buy if it's going to rise. If we do not remove the trend, maybe the agent only learn to buy at the start and hold till the end since there is general upward trend
detrended_open_df_1 = signal.detrend(open_df_1)
detrended_open_df_1 += -detrended_open_df_1.min()

detrended_close_df_1 = signal.detrend(close_df_1)
detrended_close_df_1 += -detrended_close_df_1.min()


detrended_open_df_2 = signal.detrend(open_df_2)
detrended_open_df_2 += open_df_2.min()


detrended_close_df_2 = signal.detrend(close_df_2)
detrended_close_df_2 += close_df_2.min()

plt.plot(detrended_open_df_1)
plt.plot(detrended_close_df_1)


plt.plot(detrended_open_df_2)
plt.plot(detrended_close_df_2)


plt.show()


# We had already created a pickle file for apple and microsoft stocks. So I am loading those stocks directly from attached pickle file and saving them to the final pickle 
import pickle
with open("aplmsfopenclose.pkl", "rb") as f:
    d = pickle.load(f)

# We have loaded with data and if you will print d, you can see the format of the pickle file. We are storing the contents of ao,ac,mo,mc (apple open, apple close, microsoft open, microsoft close) to our local variables which will then again be saved in final fyp.pkl file
variable_apl_open = d["ao"]
variable_apl_close = d["ac"]
variable_msft_open = d["mo"]
variable_msft_close = d["mc"]

with open("apple_test.pkl", "rb") as f:
    d = pickle.load(f)
print (d)
variable_apl_test_open = d["ao"]
variable_apl_test_close = d["ac"]

# Dump everything in final pickle file
import pickle
with open("FYP.pkl", "wb+") as f:
    pickle.dump({
    	"SBI_open":detrended_open_df_1, "SBI_close":detrended_close_df_1, "Nike_open":detrended_open_df_2, "Nike_close":detrended_close_df_2, "Apple_open": variable_apl_open, "Apple_close": variable_apl_close,"Microsoft_open": variable_msft_open, "Microsoft_close": variable_msft_close, "Apple_test_open": variable_apl_test_open, "Apple_test_close":variable_apl_test_close }, f)
