import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter
import seaborn as sns

class Experiment():

    def __init__(self, Range, Size, Decimals, Mean=0, Correlation=0, Seed=39916801, Debug=False):
        self.Corrs = [[], [], []]
        self.CorrCols = ("RealNumpy", "RoundedNumpy", "ErrorNumpy")
        self.Range = Range
        self.Size = Size
        self.Decimals = Decimals
        self.Mean = Mean
        self.Correlation = Correlation
        self.RNG = np.random.default_rng(seed=Seed)
        self.Debug = Debug
        if self.Debug:
            self.Data = [[], [], [], []]
            self.DataCols = ("RealX", "RoundedX", "RealY", "RoundedY")

    def UpdateCorrs(self, Corrs):
        for i in range(len(Corrs)):
            self.Corrs[i].append(Corrs[i])

    def UpdateData(self, Data):
        for i in range(len(Data)):
            self.Data[i].append(Data[i])

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
        Temp = Generator.multivariate_normal(self.Mean, ((1, self.Correlation), (self.Correlation, 1)), size=self.Size)
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

    def CalculateErrors(self):
        self.Corrs[2] = np.subtract(self.Corrs[0], self.Corrs[1])

    def PlotResults(self, Bins="auto"):
        ax = sns.histplot(self.Corrs[2], bins=Bins)
        ax.text(0, 1.03,
                f"Range {self.Range}   Size {self.Size}   Decimals {self.Decimals}   Reps {len(self.Corrs[2])}",
                transform=ax.transAxes)
        # plt.title(f"Numpy Errors")
        plt.show()

    def MultiRound(self, Func, Repititions):
        for i in range(Repititions):
            # self.Func()
            self._RunRound(Func)
        self.CalculateErrors()


def ParallelRun(RetDict, Index: int, Reps, Func, Range, Size, Decimals, Mean=0, Corr=0, Seed=39916801):
    Obj = Experiment(Range, Size, Decimals, Mean, Corr, Seed * (Index + 1))
    Obj.MultiRound(Func, Reps)
    # print(f'{Obj.Corrs} from {Index}')
    RetDict[Index] = Obj.Corrs



