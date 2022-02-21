import numpy as np

#the loops in this code are adapted from an inclass group excercise from Gary's class last semsester. That code was just for one iteration of an American Put so 4 versions are necessary here
#call CRR(S0,K,r,q,vol,T,N) to generate the needed values. I would advise a maximum N value of 8 due to recursion limits
#the original plan was to apply a map function but in reverse order across the array but I could not for the life of me figure out if that was possible

def CRR(S0,K,r,q,vol,T,N):
  output = calculations(S0,K,r,q,vol,T,N)
  t = T/N
  eucall = output[0]
  euput = output[1]
  amcall = output[2]
  amput = output[3]
  stockprices = stockmatrix(S0, K, r, vol, T, N)
  calldelta = (eucall[0,1]-eucall[1,1])/(stockprices[1,1]-stockprices[0,1])
  putdelta = (euput[1,1]-euput[0,1])/(stockprices[1,1]-stockprices[0,1])
  calltheta = ((eucall[1,2]-eucall[0,0])/2*t)
  puttheta = ((euput[1,2]-euput[0,0])/2*t)
  gamma = ((((eucall[2,2]-eucall[2,1])/(stockprices[0,2]-stockprices[1,2]))-((eucall[2,2]-eucall[2,0])/(stockprices[1,2]-stockprices[2,2]))))/(.5*(stockprices[0,2]-stockprices[2,2]))
  dsigmaup  =  vol + .1
  dsigmadown = vol -.1
  sigup=calculations(S0,K,r,q,dsigmaup,T,N)
  sigdown=calculations(S0,K,r,q,dsigmadown,T,N)
  callup = sigup[0][0,0]
  calldown = sigdown[0][0,0]
  vega = (callup-calldown)/(2*.1)
  drhoup = r + .02
  drhodown = r -.02
  sigup=calculations(S0,K,drhoup,q,vol,T,N)
  sigdown=calculations(S0,K,drhodown,q,vol,T,N)
  callup = sigup[0][0,0]
  calldown = sigdown[0][0,0]
  CallRho = (callup-calldown)/(2*.02)
  putup = sigup[1][0,0]
  putdown = sigdown[1][0,0]
  PutRho = (callup-calldown)/(2*.02)

  print('The European Call is ', eucall[0,0])
  print('The European Put is ', euput[0,0])
  print('The American Call is ', amcall[0,0])
  print('The American Put is ', amput[0,0])
  print('Delta of the call is ', calldelta)
  print('Delta of the put is ', putdelta)
  print('Theta of the call is ', calltheta)
  print('Theta of the put is ', puttheta)
  print('Gamma  is ', gamma)
  print('Vega  is ', vega)
  print('Rho of a call  is ', CallRho)
  print('Rho of a put  is ', PutRho)
  return

def stockmatrix(S0, K, r, vol, T, N): #generating the matrix of stock prices 
    s = np.zeros([N+1,N+1])
    j = N+1
    t = T/N
    u = np.exp(vol*np.sqrt(t))
    stockprices = tree(S0,s,u,N)
    return stockprices #however, the matrix is flipped so the greek calculations will reflect this

def tree(S0, s, u, N, i=0, j=0):
    if j < i+1 and i<N+1:
        s[j,i] = S0*u**(2*j - i)
        j = j + 1
        return  tree(S0, s, u, N, i, j)
    elif i < N+1:
        j=0
        i = i + 1
        return tree(S0, s, u, N, i, j)
    else:
        return s

def payofffunc(S, K, AmericanCall, Call, EuropeanCall, AmericanPut,Put,EuropeanPut, p, r, q, t, N, APutConVal, ACallConVal, EPutConVal, ECallConVal, i = 1, j = 0):
    zeros = np.zeros([N+1,N+1])
    if (i < N+1) and (j < N+1-i):
        discount = np.exp(-(r-q)*t)
        ECallConVal[j] = discount*(EuropeanCall[j,-i]*(1-p) + EuropeanCall[j+1,-i]*p)
        EPutConVal[j] = discount*(EuropeanPut[j,-i]*(1-p) + EuropeanPut[j+1,-i]*p)
        ACallConVal[j] = discount*(AmericanCall[j,-i]*(1-p) + AmericanCall[j+1,-i]*p)
        APutConVal[j] = discount*(AmericanPut[j,-i]*(1-p) + AmericanPut[j+1,-i]*p)
        #last semseter, we used a for loop here, which would be easier for calculating the present value of the continuation but the output should be the same
        j= j+1
        payofffunc(S,K,AmericanCall,Call,EuropeanCall,AmericanPut,Put,EuropeanPut,p,r,q,t,N,APutConVal,ACallConVal,EPutConVal,ECallConVal,i=i,j=j)
    if i < N+1:
        EuropeanCall[:,-(i+1)] = np.maximum(zeros[:,-(i+1)], ECallConVal)
        EuropeanPut[:,-(i+1)] = np.maximum(zeros[:,-(i+1)], EPutConVal)
        AmericanCall[:,-(i+1)] = np.maximum(Call[:,-(i+1)],ACallConVal)
        AmericanPut[:,-(i+1)] = np.maximum(Put[:,-(i+1)],APutConVal)
        j = 0
        i = i +1
        return payofffunc(S, K, AmericanCall, Call, EuropeanCall, AmericanPut, Put, EuropeanPut, p, r, q, t, N, APutConVal = np.zeros(N+1), ACallConVal = np.zeros(N+1),EPutConVal = np.zeros(N+1), ECallConVal = np.zeros(N+1), i=i, j=j)
    else:
        return [EuropeanCall, EuropeanPut, AmericanCall, AmericanPut]

def calculations(S0,K,r,q,vol,T,N):
    j = N+1
    t = T/N
    u = np.exp(vol*np.sqrt(t))
    d=1/u
    p = (np.exp((r-q)*t) -d)/(u-d)
    discount = np.exp(-(r-q)*t)
    
    stockprices = stockmatrix(S0,K,r,vol,T,N)
    AmericanCall = np.zeros([N+1,N+1])
    EuropeanCall = np.zeros([N+1,N+1])
    AmericanPut = np.zeros([N+1,N+1])
    EuropeanPut = np.zeros([N+1,N+1])
    #calculations and set up similar to last semseter's code. payoff function is main difference
    
    Call = np.triu(np.maximum(stockprices - K,0))
    Put = np.triu(np.maximum(K - stockprices,0))
    
    EuropeanCall[:,-1] =  Call[:,-1]
    EuropeanPut[:,-1] = Put[:,-1]
    AmericanCall[:,-1] = Call[:,-1]
    AmericanPut[:,-1] = Put[:,-1]
    
    output = payofffunc(stockprices, K, AmericanCall,Call,EuropeanCall,AmericanPut,Put,EuropeanPut,p,r,q,t,N,APutConVal = np.zeros(N+1), ACallConVal = np.zeros(N+1),EPutConVal = np.zeros(N+1), ECallConVal = np.zeros(N+1), i = 1, j = 0)
    return output
