#loading needed packages
from scipy.stats import norm 
import numpy as np

# S is the underlying stock price
#K is the strike price
#r is the risk free rate expressed as a decimal
#Vol is the volatility expressed as a decimal
#T is tenor in years

#d1 and d2 to be used in other equations
d1 = lambda S, K , r, vol, T: (np.log(S/K) + ((r + ((vol**2)/2))*T))/(vol*np.sqrt(T))
d2 = lambda S, K, r, vol, T: d1(S, K, r, vol, T) - vol*np.sqrt(T)

#delta of calls and puts
CallDelta = lambda S, K, r, vol, T: norm.cdf(d1(S, K, r, vol, T))
PutDelta = lambda S, K, r, vol, T: (norm.cdf(d1(S, K, r, vol, T))-1)

#Call and put prices
CallPrice = lambda S, K , r, vol, T: S*norm.cdf(d1(S, K , r, vol, T))-K*np.exp(-r*T)*norm.cdf(d2(S, K , r, vol, T))
PutPrice = lambda S, K , r, vol, T: K*np.exp(-r*T)*norm.cdf(-d2(S, K , r, vol, T))-S*norm.cdf(-d1(S, K , r, vol, T))

#gamma function
gamma = lambda S, K , r, vol, T: norm.pdf(d1(S, K , r, vol, T))/(S*vol*np.sqrt(T))

#Vega
vega = lambda S, K , r, vol, T: S*norm.pdf(d1(S, K , r, vol, T))*np.sqrt(T)

#theta for call and put
CallTheta = lambda S, K , r, vol, T: ((-S*norm.pdf(d1(S, K , r, vol, T))*vol)/2*np.sqrt(T))-r*K*np.exp(-r*T)*norm.cdf(d2(S, K , r, vol, T))
PutTheta = lambda S, K , r, vol, T: ((-S*norm.pdf(d1(S, K , r, vol, T))*vol)/2*np.sqrt(T))+r*K*np.exp(-r*T)*norm.cdf(-d2(S, K , r, vol, T))

#Rho for call and put
CallRho = lambda S, K , r, vol, T: K*T*np.exp(-r*T)*norm.cdf(d2(S, K , r, vol, T))
PutRho = lambda S, K , r, vol, T: -K*T*np.exp(-r*T)*norm.cdf(-d2(S, K , r, vol, T))

