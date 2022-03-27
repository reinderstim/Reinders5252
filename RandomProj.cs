using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Assignment
{
    class Program
    {
        static void Main(string [] args)
        {
            RandMethods x = new RandMethods();
            Random a = new Random();
            Random b = new Random();
            Random c = new Random();
            double SumTwelve = x.SumTwelve(a);

            List<double> Box, Pol, Corr;

            Box = x.BoxMuller(a,b);
            Pol = x.PolarRejection(a,b);

            double p = -2;

            while (Math.Abs(p) > 1)
            {
                Console.WriteLine("Enter a Correlation Coefficient, p:");

                try
                {
                    p = Convert.ToDouble(Console.ReadLine());

                    if (Math.Abs(p) > 1)
                    {
                        Console.WriteLine("p must be between -1 and 1");
                    }
                }
                catch
                {
                    p = -2;
                    Console.WriteLine("Invalid Entry");
                }
            }
            Corr = x.Correlated(a,b,c,p);

            Console.WriteLine("Gaussian using SumTwelve: {0}", SumTwelve);
            Console.WriteLine("Gaussians using BoxMuller: {0}, {1}", Box[0], Box[1]);
            Console.WriteLine("Gaussians using PolarRejection: {0}, {1}", Pol[0], Pol[1]);
            Console.WriteLine("Gaussians from correlated: {0}, {1}", Corr[0], Corr[1]);
        }
    }

    class RandMethods
    {
        public double SumTwelve(Random a)
        {

            List<double> Gaussians = new List<double>();
            double sum = 0;
            for (int k=0; k < 12; k++)
            {
                sum += a.NextDouble();
            }

            sum -= 6;

            return sum;

        }

        public List<double> BoxMuller(Random x1, Random x2)
        {
            double y1, y2;
            y1 = x1.NextDouble();
            y2 = x2.NextDouble(); 

            List<double> gaussians = new List<double>(); 

            double z1,z2;

            z1 = Math.Sqrt(-2*Math.Log(y1)) *Math.Cos(2*Math.PI*y2); 
            z2 = Math.Sqrt(-2*Math.Log(y1)) *Math.Sin(2*Math.PI*y2);

            gaussians.Add(z1); 
            gaussians.Add(z2);

            return gaussians; 


        }

        public List<double> PolarRejection(Random x1, Random x2)
        {
            double y1,y2;
            y1 = x1.NextDouble(); 
            y2 = x2.NextDouble();

            double w = Math.Pow(y1,2) + Math.Pow(y2,2); 
            while (w > 1) 
            {
                y1 = x1.NextDouble();
                y2 = x2.NextDouble();

                w = Math.Pow(y1,2) + Math.Pow(y2,2); 
            }
            double c = Math.Sqrt(-2*Math.Log(w)/w); 

            double z1,z2;
            z1 = c*y1;
            z2 = c*y2;

            List<double> gaussians = new List<double>();

            gaussians.Add(z1);
            gaussians.Add(z2);

            return gaussians; 

        }

        public List<double> Correlated(Random x1, Random x2, Random x3, double p)
        {
            double y1,y2,y3;
            y1 = x1.NextDouble();
            y2 = x2.NextDouble();
            y3 = x3.NextDouble(); 
            
            double z1,z2,z3;

            z1 = y1; 
            z2 = y2;
            z3 = p*z1 + Math.Sqrt(1-Math.Pow(p,2))*z2; 

            List<double> gaussians = new List<double>();

            gaussians.Add(z1); 
            gaussians.Add(z3);

            return gaussians;
        }
    }
}