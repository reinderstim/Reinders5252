!pip install yfinance
import yfinance as yf
import numpy as np
from scipy.stats import norm
from scipy.optimize import fmin
import pandas as pd
import matplotlib.pyplot as plt

#black scholes code

#enter option type as the first input as 'C' for a call and 'P' for a put
def OptionPrice(option, S, K, T, r, vol):
    d1 = (np.log(S / K) + (r + vol ** 2 / 2) * T) / (vol * np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    if option == 'C':
      price = S*norm.cdf(d1)-K*np.exp(-r*T)*norm.cdf(d2)
    else:
      price = K*np.exp(-r*T)*norm.cdf(-d2)-S*norm.cdf(-d1)
    return price

def BiImpVol(option, initialprice, S, K, T, r):
  vol = .9
  minVol = .0001
  maxVol = 1

  diff = OptionPrice(option, S, K, T, r, vol) - initialprice
  while abs(diff) > .00001:
    if diff < 0:
      minVol = vol
      vol = (maxVol + vol)/2
    else:
      maxVol = vol
      vol = (minVol + vol)/2

    diff = OptionPrice(option, S, K, T, r, vol) - initialprice
  return vol

BiImpVol('P', 10, 50, 50, 1, .05)

BiImpVol('C', 10, 50, 50, 1, .05)

#Newton's Method
def vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / sigma * np.sqrt(T)
    vega = S * norm.pdf(d1) * np.sqrt(T)
    return vega

#enter option type as the first input as 'C' for a call and 'P' for a put
def NewtonImpliedVol(option, initialprice, S, K, T, r):

    vol = 0.9 #inital vol
    dx=0.001
    
    for i in range(1000):
        diff = OptionPrice(option, S, K, T, r, vol) - initialprice

        if abs(diff) < dx:
            break

        vol = vol - diff / vega(S, K, T, r, vol)

    return vol

NewtonImpliedVol('C', 10, 50, 50, 1, .05)

NewtonImpliedVol('P', 10, 50, 50, 1, .05)

vix=yf.Ticker("DHR")
exps = vix.options
options = pd.DataFrame()
for i in exps:
  opt = vix.option_chain(i)
  opt = pd.DataFrame().append(opt.calls).append(opt.puts)
  opt['expirationDate'] = i
  options = options.append(opt, ignore_index=True)

options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x) #extra column to make it a call/put
options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
options['mark'] = (options['bid'] + options['ask']) / 2 # Calculate the midpoint of the bid-ask
options = options.drop(columns = ['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice'])

plt.plot(options["expirationDate"])

MarOpt = options.loc[options["expirationDate"]=='2022-09-16'] #taking only the contracts expiring in about 6 months
MarOpt = MarOpt.reset_index()
MarOptCalls = MarOpt.loc[MarOpt["CALL"]==True]
MarOptPuts = MarOpt.loc[MarOpt["CALL"]==False]

plt.scatter(MarOpt["strike"],MarOpt["impliedVolatility"])

def optfunc(x):
  diffcall = np.array([])
  for i in range(MarOpt.shape[0]):
    callfunc = lambda x: x[0] + np.abs(x[1])*(x[2]*(MarOpt['strike'][i] - x[3]) + np.sqrt((MarOpt['strike'][i] - x[3])**2 + x[4]**2))
    diffsq = (callfunc(x) - MarOpt['impliedVolatility'][i])**2
    diffcall = np.append(diffcall, diffsq)
  return diffcall.sum()

variables = fmin(optfunc,[MarOpt['impliedVolatility'].min(),.5,-.5,MarOpt['strike'].min(),1])

print('a = ', variables[0])
print('b = ', np.abs(variables[1]))
print('rho = ', variables[2])
print('m = ', variables[3])
print('sigma = ', np.abs(variables[4]))

SVIskew = lambda x: variables[0] + np.abs(variables[1])*(variables[2]*(x - x[3]) + np.sqrt((x - variables[3])**2 + variables[4]**2))
plt.scatter(MarOpt["strike"],MarOpt["impliedVolatility"])
plt.scatter(MarOpt['strike'], SVIskew(MarOpt['strike']))
plt.legend(["Options Data","SVI Fit"])
plt.xlabel("Strike Price")
plt.ylabel("Implied Volatility")
plt.title("Danaher Options Implied Volatility by Strike")

plt.show()
