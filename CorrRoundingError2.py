import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
from scipy import stats
import pickle
import pandas
from time import perf_counter
import seaborn as sns
class Experiment():

    def __init__(self, Range, Size, Decimals, Seed=39916801, Debug=False):
        self.Corrs = [[],[],[]]
        self.CorrCols = ("RealNumpy", "RoundedNumpy", "ErrorNumpy")
        self.Range = Range
        self.Size = Size
        self.Decimals = Decimals
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

    def _RunRound(self, Range, Size, Decimals, Generator):
        RNG = Generator
        #Time1 = perf_counter()
        RealX = RNG.uniform(-Range, Range, Size)
        RealY = RNG.uniform(-Range, Range,Size)
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

    def CalculateErrors(self):
        self.Corrs[2] = np.subtract(self.Corrs[0],self.Corrs[1])

    def PlotResults(self, Bins="auto"):
        sns.histplot(self.Corrs[2], bins=Bins)
        plt.title(f"Numpy Errors")
        plt.show()

    def MultiRound(self, Repititions):
        for i in range(Repititions):
            self._RunRound(self.Range, self.Size, self.Decimals, self.RNG)
        self.CalculateErrors()
        #self.PlotResults()
        #print("Multiround done")

CoresNo = mp.cpu_count()
ObjectList = [None]*CoresNo

def ParallelRun(RetDict, Index:int, Reps, Range, Size, Decimals, Seed=39916801):
    Obj = Experiment(Range, Size, Decimals, Seed*(Index+1))
    Obj.MultiRound(Reps)
    global ObjectList
    #print(f'{Obj} from {Index}')
    RetDict[Index] = Obj.Corrs[2]
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


