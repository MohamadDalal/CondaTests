import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
from scipy import stats
import pickle
import pandas
from time import perf_counter
import seaborn as sns

"""
def Rounding(Func):
    def wrapper(self, *args, **kwargs):
        Time1 = perf_counter()
        RealX, RealY = Func(self)
        Time2 = perf_counter()
        RoundedX, RoundedY = np.round(RealX, self.Decimals), np.round(RealY, self.Decimals)
        Time3 = perf_counter()
        RealCorr = np.corrcoef(RealX, RealY)[0][1]
        Time4 = perf_counter()
        RoundedCorr = np.corrcoef(RoundedX, RoundedY)[0][1]
        Time5 = perf_counter()
        self.UpdateCorrs((RealCorr, RoundedCorr))
        Time6 = perf_counter()
        if self.Debug:
            print(f'Time steps:\t{Time2 - Time1}\t{Time3 - Time2}\t{Time4 - Time3}\t{Time5 - Time4}\t{Time6 - Time5}')
            # self.UpdateData((RealX, RoundedX, RealY, RoundedY))

    return wrapper
"""

class Experiment():

    def __init__(self, Range, Size, Decimals, Mean=0, Correlation=0, Seed=39916801, Debug=False):
        self.Corrs = [[],[],[]]
        self.CorrCols = ("RealNumpy", "RoundedNumpy", "ErrorNumpy")
        self.Range = Range
        self.Size = Size
        self.Decimals = Decimals
        self.Mean = Mean
        self.Correlation = Correlation
        self.RNG = np.random.default_rng(seed=Seed)
        self.Debug = Debug
        if self.Debug:
            self.Data = [[],[],[],[]]
            self.DataCols = ("RealX","RoundedX","RealY","RoundedY")

    def UpdateCorrs(self, Corrs):
        for i in range(len(Corrs)):
                self.Corrs[i].append(Corrs[i])

    def UpdateData(self, Data):
        for i in range(len(Data)):
                self.Data[i].append(Data[i])

    """
    def Rounding(self, func):
        def wrapper(*args, **kwargs):
            Time1 = perf_counter()
            RealX, RealY = func(*args, **kwargs)
            Time2 = perf_counter()
            RoundedX, RoundedY = np.round(RealX, self.Decimals), np.round(RealY, self.Decimals)
            Time3 = perf_counter()
            RealCorr = np.corrcoef(RealX, RealY)[0][1]
            Time4 = perf_counter()
            RoundedCorr = np.corrcoef(RoundedX, RoundedY)[0][1]
            Time5 = perf_counter()
            self.UpdateCorrs((RealCorr, RoundedCorr))
            Time6 = perf_counter()
            if self.Debug:
                print(f'Time steps:\t{Time2 - Time1}\t{Time3 - Time2}\t{Time4 - Time3}\t{Time5 - Time4}\t{Time6 - Time5}')
                #self.UpdateData((RealX, RoundedX, RealY, RoundedY))
        return wrapper
    """


    def Uniform(self):
        Generator = self.RNG
        RealX = Generator.uniform(-self.Range, self.Range, self.Size)
        RealY = Generator.uniform(-self.Range, self.Range, self.Size)
        return RealX, RealY

    def Normal(self):
        Generator = self.RNG
        RealX = Generator.normal(self.Mean, self.Range, self.Size)
        RealY = Generator.normal(self.Mean, self.Range, self.Size)
        return RealX, RealY

    def Bivariate(self):
        Generator = self.RNG
        Temp = Generator.multivariate_normal(self.Mean, ((1,self.Correlation),(self.Correlation,1)), size=self.Size)
        Temp2 = Temp.transpose()
        return Temp2[0], Temp2[1]

    def _RunRound(self, Func):
        Time1 = perf_counter()
        RealX, RealY = Func(self)
        Time2 = perf_counter()
        RoundedX, RoundedY = np.round(RealX, self.Decimals), np.round(RealY, self.Decimals)
        Time3 = perf_counter()
        RealCorr = np.corrcoef(RealX, RealY)[0][1]
        Time4 = perf_counter()
        RoundedCorr = np.corrcoef(RoundedX, RoundedY)[0][1]
        Time5 = perf_counter()
        self.UpdateCorrs((RealCorr, RoundedCorr))
        Time6 = perf_counter()
        if self.Debug:
            print(f'Time steps:\t{Time2 - Time1}\t{Time3 - Time2}\t{Time4 - Time3}\t{Time5 - Time4}\t{Time6 - Time5}')
            # self.UpdateData((RealX, RoundedX, RealY, RoundedY))

    def _OldRunRound(self, Range, Size, Decimals, Generator):
        RNG = Generator
        #Time1 = perf_counter()
        #RealX = RNG.uniform(-Range, Range, Size)
        #RealY = RNG.uniform(-Range, Range,Size)
        #RealX = RNG.normal(0, Range, Size)
        #RealY = RNG.normal(0, Range, Size)
        RealX = RNG.normal(0, Range, Size)
        RealY = RealX + RNG.normal(0, 0.1, Size)
        #Time2 = perf_counter()
        RoundedX = np.round(RealX, Decimals)
        RoundedY = np.round(RealY, Decimals)
        #Time3 = perf_counter()
        RealCorrNP = np.corrcoef(RealX, RealY)[0][1]
        RoundedCorrNP = np.corrcoef(RoundedX, RoundedY)[0][1]
        #Time4 = perf_counter()
        self.UpdateCorrs((RealCorrNP,RoundedCorrNP))
        #Time5 = perf_counter()
        #print(f'Time steps:\t{Time2-Time1}\t{Time3-Time2}\t{Time4-Time3}\t{Time5-Time4}')
        if self.Debug:
            self.UpdateData((RealX,RoundedX,RealY,RoundedY))

    def _RunRound2(self, Covariance, Size, Decimals, Generator, Mean=(0,0)):
        RNG = Generator
        Time1 = perf_counter()
        Temp = RNG.multivariate_normal(Mean, Covariance, size=Size)
        Time2 = perf_counter()
        Temp2 = Temp.transpose()
        Time3 = perf_counter()
        RealX, RealY = Temp2[0], Temp2[1]
        Time4 = perf_counter()
        RoundedX, RoundedY = np.round(RealX, Decimals), np.round(RealY, Decimals)
        Time5 = perf_counter()
        RealCorr = np.corrcoef(RealX, RealY)[0][1]
        Time6 = perf_counter()
        RoundedCorr = np.corrcoef(RoundedX, RoundedY)[0][1]
        Time7 = perf_counter()
        self.UpdateCorrs((RealCorr, RoundedCorr))
        Time8 = perf_counter()
        #print(f'{Time2-Time1} {Time3-Time2} {Time4-Time3} {Time5-Time4} {Time6-Time5} {Time7-Time6} {Time8-Time7}')
        #print(f'Corr {RealCorr}, Rounded Corr {RoundedCorr}')
        if self.Debug:
            self.UpdateData((RealX,RoundedX,RealY,RoundedY))

    def CalculateErrors(self):
        self.Corrs[2] = np.subtract(self.Corrs[0],self.Corrs[1])

    def PlotResults(self, Bins="auto"):
        ax =sns.histplot(self.Corrs[2], bins=Bins)
        ax.text(0, 1.03, f"Range {self.Range}   Size {self.Size}   Decimals {self.Decimals}   Reps {len(self.Corrs[2])}", transform=ax.transAxes)
        #plt.title(f"Numpy Errors")
        plt.show()

    def MultiRound(self, Func, Repititions):
        for i in range(Repititions):
            #self.Func()
            self._RunRound(Func)
        self.CalculateErrors()

    def OldMultiRound(self, Repititions):
        for i in range(Repititions):
            self._OldRunRound(self.Range, self.Size, self.Decimals, self.RNG)
        self.CalculateErrors()
        #self.PlotResults()
        #print("Multiround done")

    def MultiRound2(self, Repititions, Correlation):
        Correlation = 1 - (1-Correlation)*(abs(Correlation)<=1)
        print(f'Correlation is {Correlation}')
        for i in range(Repititions):
            self._RunRound2(((1,Correlation),(Correlation,1)),self.Size, self.Decimals, self.RNG)
        self.CalculateErrors()

CoresNo = mp.cpu_count()
ObjectList = [None]*CoresNo

def ParallelRun(RetDict, Index:int, Reps, Func, Range, Size, Decimals, Mean=0, Corr=0, Seed=39916801):
    Obj = Experiment(Range, Size, Decimals, Mean, Corr, Seed*(Index+1))
    #if FixCorr:
    #    Obj.MultiRound2(Reps, Corr)
    #else:
    #    Obj.MultiRound(Reps)
    Obj.MultiRound(Func, Reps)
    global ObjectList
    #print(f'{Obj.Corrs} from {Index}')
    RetDict[Index] = Obj.Corrs
    #ObjectList[Index] = Obj

"""
def main(Reps, Range, Size, Decimals):
    RepsPerCore = Reps//CoresNo
    print(f'Number of cores {CoresNo}')
    print(f'Repititions per core {RepsPerCore}')
    Processes = []
    Time1 = perf_counter()
    for i in range(CoresNo):
        P = mp.Process(target=ParallelRun, args=(i, RepsPerCore, Range, Size, Decimals,))         # Map function to process
        Processes.append(P)                                                                       # Append process to list
        Processes[-1].start()                                                                           # Start the newly appended process
        print(f'Succeeded with process {i}')
    Time2 = perf_counter()
    for P in Processes:
        P.join()						                        # Join the processes one by one
    Time3 = perf_counter()
    print(f'Time taken to create processes = {Time2-Time1}')
    print(f'Time taken for all processes to finish = {Time3-Time2}')
    #AllErrors = np.concatenate((i.Corrs[2] for i in ObjectList))
    #sns.histplot(AllErrors, bins="auto")
    #plt.title(f"Numpy Errors")
    #plt.show()

if __name__=="__main__":
    main(1000, 1, 1000, 3)
"""


