using System; 
using System.Collections.Generic;
using System.Text;
using System.Linq;
namespace MyApp
{
    class Program
    {
        static void Main(string[] args)
        {
            //Get inputs with initial values
            Console.WriteLine("Is your option a call or a put? (0 = call, 1 = put)");
            int call = Convert.ToInt32(Console.ReadLine());

            Console.WriteLine("Do you want to use antithetic variance reduction? (1 = Yes, 0 = No)");
            int anti = Convert.ToInt32(Console.ReadLine());

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

            double[][,] sim = GeneratePaths(paths,steps,s0,Tenor,vol,rate,anti);
            double price = OptionPriceCalculator(sim[0],strike,rate,Tenor,call);
            double[] optionPrices = new double[paths];
            for(int j=0; j<paths ; j++)
            {
                optionPrices[j] = (Math.Max(sim[0][j,steps-1],strike,call) + Math.Max(sim[1][j,steps-1],strike,paths))/2;
                //This how I calculated it last time but I changed it for antithetic and it's throwing an error but frankly I ran out of time to debug
            }
            double StdError = StandardError(optionPrices);

            double[] greeks = GetGreeks(steps,paths,s0,strike,Tenor,vol,rate,call,anti);

            Console.WriteLine("The option price via Monte Carlo is {0}", optionPrices);
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
        static double[] BoxMuller()
        {
            Random r = new Random();
            double x1 = r.NextDouble();
            double x2 = r.NextDouble();
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
       

        static double[][,] GeneratePaths(int paths, int steps, double s0, double Tenor, double vol, double rate, int anti)
        {
        
            double dt = new double();
            dt = Tenor/Convert.ToDouble(steps);
        
            double[,] gaussians = new double[paths, steps];

            for(int i = 0; i < steps; i++)
            {
                for(int j = 0; j < paths; j++)
                {
                    gaussians[j,i] = BoxMuller()[1];
                }
            }
            

            double[,] regPrices = new double[steps,paths];
            double[,] antiPrices = new double[steps,paths];
            for(int j=0; j < paths ; j++)
            {
                regPrices[j,0] = s0;
                antiPrices[j,0] = s0;

            }


            if(anti==1){
                for(int i = 0; i<(steps-1); i++){
                    for(int j = 0; j < paths; j++){
                        regPrices[j,i+1] = regPrices[j,i]*Math.Exp((rate-Math.Pow(vol,2)*.5)*dt + vol*Math.Sqrt(dt)*gaussians[j,i]);
                        antiPrices[j,i+1] = antiPrices[j,i]*Math.Exp((rate-Math.Pow(vol,2)*.5)*dt - vol*Math.Sqrt(dt)*gaussians[j,i]);
                    }
                }
            }else{
                for(int i = 0; i<(steps-1); i++){
                    for(int j = 0; j < paths; j++){
                        regPrices[j,i+1] = regPrices[j,i]*Math.Exp((rate-Math.Pow(vol,2)*.5)*dt + vol*Math.Sqrt(dt)*gaussians[j,i]);
                    }
                }

            }
            double[][,] PriceArray = new double[2][,];

            if(anti==1){
                PriceArray[0] = regPrices;
                PriceArray[1] = antiPrices;
            }else{
                PriceArray[0] = regPrices;
                PriceArray[1] = regPrices;
            }

            return(PriceArray);
        }
        
        static double OptionPriceCalculator(double[,] regPrices, double strike, double rate, double Tenor, int call)
        {

            double[] ST = new double[regPrices.GetLength(0)];

            for(int j = 0; j<regPrices.GetLength(0); j++)
            {
            ST[j] = regPrices[j,regPrices.GetLength(1)-1];
            }

            double[] payoff = new double[ST.Length];

            if(call == 1){
                for(int i = 0; i<ST.Length;i++ )
                {
                    payoff[i] = Math.Max(strike - ST[i] ,0);
                    payoff[i] = payoff[i]*Math.Exp(-rate*Tenor);
                }
            }else{
                 for(int i = 0; i<ST.Length;i++ )
                {
                    payoff[i] = Math.Max(ST[i]-strike ,0);
                    payoff[i] = payoff[i]*Math.Exp(-rate*Tenor);
                }
            }
            return(payoff.Average());
        }

       
        static double[] GetGreeks(int paths, int steps, double s0, double strike, double Tenor, double vol, double rate, int call, int anti)
        {
            double deltas0 = s0*.001;

            double[][,] Sim = GeneratePaths(paths,steps,s0,Tenor,vol,rate,anti);
            double[][,] SimU = GeneratePaths(paths,steps,s0+deltas0,Tenor,vol,rate,anti);
            double[][,] SimD = GeneratePaths(paths,steps,s0-deltas0,Tenor,vol,rate,anti);

            double delta = (OptionPriceCalculator(SimU[0],strike,rate,Tenor,call) - OptionPriceCalculator(SimD[0],strike,rate,Tenor,call))/(2*deltas0);
            if(anti==1){
                double antiDelta = (OptionPriceCalculator(SimU[1],strike,rate,Tenor,call) - OptionPriceCalculator(SimD[1],strike,rate,Tenor,call))/(2*deltas0);
                delta = (delta+antiDelta)/2;
            }

            double gamma = (OptionPriceCalculator(SimU[0],strike,rate,Tenor,call) - 2*OptionPriceCalculator(Sim[0],strike,rate,Tenor,call) + OptionPriceCalculator(SimD[0],strike,rate,Tenor,call))/(Math.Pow(deltas0,2));
            if(anti==1){
            double antiGamma = (OptionPriceCalculator(SimU[1],strike,rate,Tenor,call) - 2*OptionPriceCalculator(Sim[1],strike,rate,Tenor,call) + OptionPriceCalculator(SimD[1],strike,rate,Tenor,call))/(Math.Pow(deltas0,2));
                gamma = (gamma+antiGamma)/2;
            }

            double deltavol = vol*.001;
            double[][,] SigU = GeneratePaths(steps,paths,s0,Tenor,vol+deltavol,rate,anti);
            double[][,] SigD = GeneratePaths(steps,paths,s0,Tenor,vol-deltavol,rate,anti);
            double vega = (OptionPriceCalculator(SigU[0],strike,rate,Tenor,call) - OptionPriceCalculator(SigD[0],strike,rate,Tenor,call))/(2*deltavol);
            if(anti==1){
                double antiVega =  (OptionPriceCalculator(SigU[1],strike,rate,Tenor,call) - OptionPriceCalculator(SigD[1],strike,rate,Tenor,call))/(2*deltavol);
                vega = (antiVega+vega)/2;
            }
 
            double deltaT = Tenor*.001;
            double[][,] ThetaSim = GeneratePaths(steps,paths,s0,Tenor+deltaT,vol,rate,anti);
            double theta = (OptionPriceCalculator(ThetaSim[0],strike,rate,Tenor+deltaT,call) -  OptionPriceCalculator(Sim[0],strike,rate,Tenor, call))/deltaT;
            if(anti==1){
                double antiTheta = (OptionPriceCalculator(ThetaSim[1],strike,rate,Tenor+deltaT,call) -  OptionPriceCalculator(Sim[1],strike,rate,Tenor, call))/deltaT;
                theta = (antiTheta+theta)/2;
            }

            double DeltaR = rate*.001;
            double[][,] RhoU = GeneratePaths(steps,paths,s0,Tenor,vol,rate+DeltaR,anti);
            double[][,] RhoD = GeneratePaths(steps,paths,s0,Tenor,vol,rate-DeltaR,anti);
            double rho = (OptionPriceCalculator(RhoU[0],strike,rate+DeltaR,Tenor, call) - OptionPriceCalculator(RhoD[0],strike,rate-DeltaR,Tenor, call))/(2*DeltaR);
            if(anti == 1){
                double antiRho = (OptionPriceCalculator(RhoU[1],strike,rate+DeltaR,Tenor, call) - OptionPriceCalculator(RhoD[1],strike,rate-DeltaR,Tenor, call))/(2*DeltaR);
                rho = (antiRho + rho)/2;
            }

            double[] greeks = new double[]{delta,gamma,vega,theta,rho};
            return(greeks);
        }

  
    }

}