using System; 
using System.Collections.Generic;
using System.Text;
using System.Linq;
namespace MonteCarloProject
{
    class Program
    {
        static void Main(string[] args)
        {
            //Get inputs with initial values
            Console.WriteLine("Is your option a call or a put? (0 = call, 1 = put)");
            int call = Convert.ToInt32(Console.ReadLine());

            double s0 = 1000;
            Console.WriteLine("What is the price of your stock?");
            s0 = Convert.ToDouble(Console.ReadLine());

            double strike = 1000;
            Console.WriteLine("What is the strike for your option?");
            strike = Convert.ToDouble(Console.ReadLine());

            double vol = .75;
            Console.WriteLine("What is the vol of your stock?");
            vol = Convert.ToDouble(Console.ReadLine());

            double rate = 0.05;
            Console.WriteLine("What is the risk-free rate of your stock?");
            rate = Convert.ToDouble(Console.ReadLine());
        
            double Tenor = 1;
            Console.WriteLine("What is the Tenor your option?");
            Tenor = Convert.ToDouble(Console.ReadLine());
           
            int steps = 252;
            Console.WriteLine("How many steps for your option? ");
            steps = int.Parse(Console.ReadLine());
            
            int paths = 1000;
            Console.WriteLine("How many paths for your option?");
            paths = int.Parse(Console.ReadLine());


            //get paths and put those into the option calculator
            double[,] sim = GeneratePaths(paths,steps,s0,Tenor,vol,rate);
            double price = OptionPriceCalculator(sim,strike,rate,Tenor,call);
            double[] OptionPrices = new double[paths];
            for(int x=0; x<paths ; x++)
            {
                OptionPrices[x] = Math.Max((sim[x,steps-1]-strike)*Math.Pow(-1,call),0);
            }
            double StdError = StandardError(OptionPrices);
            double[] greeks = GetGreeksandError(paths,steps,s0,strike,Tenor,vol,rate,call);
            Console.WriteLine("The option price via Monte Carlo is {0}", price);
            //price seems to work with a smaller number of steps/paths compared to the greeks
            Console.WriteLine();
            Console.WriteLine("The Standard Error was {0}", StdError);
            Console.WriteLine();
            Console.WriteLine("The option Delta is {0}", greeks[0]);
            Console.WriteLine();
            Console.WriteLine("The option Gamma is {0}", greeks[1]);
            Console.WriteLine();
            Console.WriteLine("The option Theta is {0}", greeks[2]);
            Console.WriteLine();
            Console.WriteLine("The option Vega is {0}", greeks[3]);
            Console.WriteLine();
            Console.WriteLine("The option Rho is {0}", greeks[4]);

        }
        static double[] BoxMuller() //taken from last project
        {
            Random rate = new Random();
            double x1 = rate.NextDouble();
            double x2 = rate.NextDouble();
            double z1 = Math.Sqrt(-2*Math.Log(x1))*Math.Cos(2*Math.PI*x2);
            double z2 = Math.Sqrt(-2*Math.Log(x1))*Math.Sin(2*Math.PI*x2);
            double[] gaussians = {z1,z2};
            return gaussians;
        }
        static double StandardError(double[] inputprices)
        {
            double avg = inputprices.Average();
            double SE = 0;
            foreach(double row in inputprices)
            {
                SE += Math.Pow((row - avg),2);
            }
            SE = Math.Sqrt(SE/(inputprices.Length-1));
            SE = SE/(Math.Sqrt(inputprices.Length));
            
            return(SE);

        }
       
        static double[,] GeneratePaths(int paths, int steps, double s0, double Tenor, double vol, double rate)
        {
        
            double dt = new double();
            dt = Tenor/Convert.ToDouble(steps);
            double[,] gaussians = new double[paths, steps];

            for(int y = 0; y < steps; y++)
            {
                for(int x = 0; x < paths; x++)
                {
                    gaussians[x,y] = BoxMuller()[1];
                }
            }
            
            double[,] Prices = new double[paths,steps];
            for(int x=0; x < paths ; x++)
            {
                Prices[x,0] = s0;
            }

    
            for(int y = 0; y<(steps-1); y++)
            {
                for(int x = 0; x < paths; x++)
                {
                    Prices[x,y+1] = Prices[x,y]*Math.Exp((rate-Math.Pow(vol,2)*.5)*dt + vol*Math.Sqrt(dt)*gaussians[x,y]);
                }
            }
            
            return(Prices);
            
        }
        
        static double OptionPriceCalculator(double[,] Prices, double strike, double rate, double Tenor, int call)
        {
            double[] ST = new double[Prices.GetLength(0)];
            for(int x = 0; x<Prices.GetLength(0); x++)
            {
            ST[x] = Prices[x,Prices.GetLength(1)-1];
            }
            double[] payoff = new double[ST.Length];

            //payoffs for call/put
            if(call == 1)
            {
                for(int y = 0; y<ST.Length;y++)
                {
                    payoff[y] = Math.Max(strike - ST[y] ,0);
                    payoff[y] = payoff[y]*Math.Exp(-rate*Tenor);
                }
            }
            else
            {
                 for(int y = 0; y<ST.Length;y++)
                {
                    payoff[y] = Math.Max(ST[y]-strike ,0);
                    payoff[y] = payoff[y]*Math.Exp(-rate*Tenor);
                }
            }
            return(payoff.Average());
        }
        static double[] GetGreeksandError(int paths, int steps, double s0, double strike, double Tenor, double vol, double rate, int call)
        {
            //as a note, it's really hard to get the right values here, I'm not sure what the right number of steps and paths I need to get good convergence. The formulas are from lec10 slide 31 and on
            double deltaS0 = s0/10;
            double[,] Sim = GeneratePaths(paths,steps,s0,Tenor,vol,rate);
            double[,] SimU = GeneratePaths(paths,steps,s0+deltaS0,Tenor,vol,rate);
            double[,] SimD = GeneratePaths(paths,steps,s0-deltaS0,Tenor,vol,rate);

            double delta = (OptionPriceCalculator(SimU,strike,rate,Tenor,call) - OptionPriceCalculator(SimD,strike,rate,Tenor,call))/(2*deltaS0);
          
            double gamma = (OptionPriceCalculator(SimU,strike,rate,Tenor,call) - 2*OptionPriceCalculator(Sim,strike,rate,Tenor,call) + OptionPriceCalculator(SimD,strike,rate,Tenor,call))/(Math.Pow(deltaS0,2));
 
            double deltaVol = vol/10;
            double[,] SigU = GeneratePaths(paths,steps,s0,Tenor,vol+deltaVol,rate);
            double[,] SigD = GeneratePaths(paths,steps,s0,Tenor,vol-deltaVol,rate);
            double vega = (OptionPriceCalculator(SigU,strike,rate,Tenor,call) - OptionPriceCalculator(SigD,strike,rate,Tenor,call))/(2*deltaVol);

            double deltaT = Tenor/10;
            double[,] ThetaSim = GeneratePaths(paths,steps,s0,Tenor+deltaT,vol,rate);
            double theta = (OptionPriceCalculator(ThetaSim,strike,rate,Tenor+deltaT,call) -  OptionPriceCalculator(Sim,strike,rate,Tenor, call))/deltaT;

            double DeltaR = rate/10;
            double[,] RhoU = GeneratePaths(paths,steps,s0,Tenor,vol,rate+DeltaR);
            double[,] RhoD = GeneratePaths(paths,steps,s0,Tenor,vol,rate-DeltaR);
            double rho = (OptionPriceCalculator(RhoU,strike,rate+DeltaR,Tenor, call) - OptionPriceCalculator(RhoD,strike,rate-DeltaR,Tenor, call))/(2*DeltaR);
            
            double[] greeks = new double[]{delta,gamma,vega,theta,rho}; //C# can return arrays instead of multiple values
            return(greeks);
        }
    }
}