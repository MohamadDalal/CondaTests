import numpy as np
import matplotlib.pyplot as plt
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
        #self.UpdateCorrs((RealCorrNP, RoundedCorrNP, 0, 0))
        #Time5 = perf_counter()
        #print(f'Time steps:\t{Time2-Time1}\t{Time3-Time2}\t{Time4-Time3}\t{Time5-Time4}')
        if self.Debug:
            self.UpdateData((RealX,RoundedX,RealY,RoundedY))
        #print(f'Real correlation by Numpy = {RealCorrNP}')
        #print(f'Rounded correlation by Numpy = {RoundedCorrNP}')
        #print(f'Real correlation by Scipy = {RealCorrScipy}')
        #print(f'Rounded correlation by Scipy = {RoundedCorrScipy}')
        #print(f'Error by Numpy = {RealCorrNP - RoundedCorrNP}')
        #print(f'Error by Scipy = {RealCorrScipy - RoundedCorrScipy}')
        #return ((RealCorrNP, RoundedCorrNP), (RealCorrScipy, RoundedCorrScipy))

    def CalculateErrors(self):
        self.Corrs[2] = np.subtract(self.Corrs[0],self.Corrs[1])

    def PlotResults(self, Bins="auto"):
        ax = sns.histplot(self.Corrs[2], bins=Bins)
        #plt.title(f"Numpy Errors")
        ax.text(0, 1.03,f"Range {self.Range}   Size {self.Size}   Decimals {self.Decimals}   Reps {len(self.Corrs[2])}",transform=ax.transAxes)
        plt.show()

    def MultiRound(self, Repititions):
        for i in range(Repititions):
            self._RunRound(self.Range, self.Size, self.Decimals, self.RNG)
        self.CalculateErrors()
        self.PlotResults()
        print("Multiround done")

class Experiment2(Experiment):

    def __init__(self, Range, Size, Decimals, Seed=39916801, Debug=False):
        super().__init__(Range, Size, Decimals, Seed, Debug)
        self.Corrs = [[],[],[],[],[],[]]
        self.CorrCols = ("RealNumpy", "RoundedNumpy","RealScipy", "RoundedScipy", "ErrorNumpy", "ErrorScipy")

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
        RealCorrScipy = stats.pearsonr(RealX, RealY)[0]
        RoundedCorrScipy = stats.pearsonr(RoundedX, RoundedY)[0]
        #Time5 = perf_counter()
        self.UpdateCorrs((RealCorrNP,RoundedCorrNP,RealCorrScipy,RoundedCorrScipy))
        #self.UpdateCorrs((RealCorrNP, RoundedCorrNP, 0, 0))
        #Time6 = perf_counter()
        #print(f'Time steps:\t{Time2-Time1}\t{Time3-Time2}\t{Time4-Time3}\t{Time5-Time4}\t{Time6-Time5}')
        if self.Debug:
            self.UpdateData((RealX,RoundedX,RealY,RoundedY))
        #print(f'Real correlation by Numpy = {RealCorrNP}')
        #print(f'Rounded correlation by Numpy = {RoundedCorrNP}')
        #print(f'Real correlation by Scipy = {RealCorrScipy}')
        #print(f'Rounded correlation by Scipy = {RoundedCorrScipy}')
        #print(f'Error by Numpy = {RealCorrNP - RoundedCorrNP}')
        #print(f'Error by Scipy = {RealCorrScipy - RoundedCorrScipy}')
        #return ((RealCorrNP, RoundedCorrNP), (RealCorrScipy, RoundedCorrScipy))

    def CalculateErrors(self):
        self.Corrs[4] = np.subtract(self.Corrs[0],self.Corrs[1])
        self.Corrs[5] = np.subtract(self.Corrs[2],self.Corrs[3])

    def PlotResults(self, Bins="auto"):
        #self.Histogram = [np.histogram(self.Corrs[4], bins=Bins),np.histogram(self.Corrs[5], bins=Bins)]
        for i in range(2):
            #plt.hist(i, bins=Bins)
            ax = sns.histplot(self.Corrs[4+i], bins=Bins)
            ax.text(0, 1.03, f"Histogram {i+1}\tRange {self.Range}\tSize {self.Size}\tDecimals {self.Decimals}\tReps {len(self.Corrs[4])}", transform=ax.transAxes)
            #plt.title(f"Histogram {i+1}")
            plt.show()

# This function is used to create pandas dataframes of the lists of lists generated by the RNG objects
# Cols is the column names list that is found in RNG1 and RNG2 for example
def makeDF(List, Cols=None):
    DF = []
    try:
        DF = pandas.DataFrame(List,columns=Cols)
    except Exception as e:
        print(e)
        New = np.transpose(List)
        DF = pandas.DataFrame(New, columns=Cols)
    finally:
        #print(DF)
        return DF

# Write pickle object
def PickleWrite(Obj, Path):
    with open(Path, "wb") as file:
        pickle.dump(Obj, file)

# Read pickled object
def PickleRead(Path):
    with open(Path, "rb") as file:
        result = pickle.load(file)
    return result

if __name__ == "__main__":
    Start = perf_counter()
    Res = Experiment(1, 1000, 3)
    Res.MultiRound(1000)
    Finish = perf_counter()
    print(f'Time taken {Finish-Start}')

