
# Import pandas 
import pandas as pd 
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime 

# reading csv file  
df1 = pd.read_csv("ba.csv") 
df2 = pd.read_csv("nike.csv") 
df3 = pd.read_csv("dhanno.csv") 
df4 = pd.read_csv("gs.csv") 
df5 = pd.read_csv("jpmc.csv") 
df6 = pd.read_csv("ibm.csv") 
df7 = pd.read_csv("utx.csv") 
df8 = pd.read_csv("visa.csv") 
df9 = pd.read_csv("pg.csv") 
df10 = pd.read_csv("trv.csv") 


#detrend is done to remove a monotonous trend in the data and places where division by a constant is done to normalise the stock values if at all a bonus or split is there

y1 = df1['Open']
y11 = df1['Close']

y2 = df2['Open']
y2[:499] /= 2
y21 = df2['Close']
y21[:499] /= 2

y3 = df3['Open']
y31 = df3['Close']

y4 = df4['Open']
y41 = df4['Close']

y5 = df5['Open']
y51 = df5['Close']

y6 = df6['Open']
y61 = df6['Close']

y7 = df7['Open']
y71 = df7['Close']

y8 = df8['Open']
y8[:304] /= 4

y81 = df8['Close']
y81[:304] /= 4

y9 = df9['Open']
y91 = df9['Close']

y10 = df10['Open']
y101 = df10['Close']


from scipy import signal



new_y1 = signal.detrend(y1)
new_y1 += y1.min()

new_y2 = signal.detrend(y2)
new_y2 += y2.min()

new_y3 = signal.detrend(y3)
new_y3 += y3.min()

new_y4 = signal.detrend(y4)
new_y4 += y4.min()

new_y5 = signal.detrend(y5)
new_y5 += y5.min()

new_y6 = signal.detrend(y6)
new_y6 += y6.min()

new_y7 = signal.detrend(y7)
new_y7 += y7.min()

new_y8 = signal.detrend(y8)
new_y8 += y8.min()

new_y9 = signal.detrend(y9)
new_y9 += y9.min()

new_y10 = signal.detrend(y10)
new_y10 += y10.min()


new_y11 = signal.detrend(y11)
new_y11 += y11.min()

new_y21 = signal.detrend(y21)
new_y21 += y21.min()

new_y31 = signal.detrend(y31)
new_y31 += y31.min()

new_y41 = signal.detrend(y41)
new_y41 += y41.min()

new_y51 = signal.detrend(y51)
new_y51 += y51.min()

new_y61 = signal.detrend(y61)
new_y61 += y61.min()

new_y71 = signal.detrend(y71)
new_y71 += y71.min()

new_y81 = signal.detrend(y81)
new_y81 += y81.min()

new_y91 = signal.detrend(y91)
new_y91 += y91.min()

new_y101 = signal.detrend(y101)
new_y101 += y101.min()


import pickle
with open("mystocks.pkl", "wb+") as f:
    pickle.dump({
    	"trv_open":new_y10, "trv_close":new_y101 , "trv_untrend_open":y10, "trv_untrend_close":y101 ,
    	"pg_open":new_y9, "pg_close":new_y91
    	"visa_open":new_y8, "visa_close":new_y81 , "visa_untrend_open":y8, "visa_untrend_close":y81 ,"utx_open":new_y7, "utx_close":new_y71 ,"ibm_open":new_y6, "ibm_close":new_y61 ,"jpmc_open":new_y5, "jpmc_close":new_y51 ,"gs_open":new_y4, "gs_close":new_y41 ,"ba_open":new_y1, "ba_close":new_y11, "nike_open":new_y2, "nike_close":new_y21 , "dhanno_open":new_y3 , "dhanno_close":new_y31}, f)