import numpy as np
from scipy import stats
from time import perf_counter

class DPS:

    def GenDataPool(self, Size):
        for i in range(Size):
            TempAddition = self.rng.normal(0, 0.5)
            self.Temperature += TempAddition
            if (self.Temperature > 40) or (self.Temperature < -10):
                self.Temperature -= 2 * TempAddition

            U = self.Temperature
            V = np.abs(self.rng.normal(0,1))
            W = np.abs(self.rng.normal(2,2))
            X = U - V
            Y = U - W

            self.Population[0].append(U)
            self.Population[1].append(V)
            self.Population[2].append(W)
            self.Population[3].append(X)
            self.Population[4].append(Y)

    def __init__(self, PoolSize=100000):
        StartTime = perf_counter()
        self.rng = np.random.default_rng(seed=39916801)
        self.Population = []
        self.Data = []
        self.DataOrdered = []
        self.RecentData = []
        self.RecentDataOrdered = []
        self.DataCols = ["X", "Y"]
        self.CorrCols = ["XY"]
        self.Correlations = [[]]
        self.SingleRoundCorr = [[]]
        self.OrderedCorr = [[]]
        self.SingleRoundOrderedCorr = [[]]
        self.RoundNo = 0
        for i in range(5):
            self.Population.append([])
        for i in range(2):
            self.Data.append([])
            self.RecentData.append([])
            self.DataOrdered.append([])
            self.RecentDataOrdered.append([])
        self.Temperature = 15
        self.GenDataPool(PoolSize)
        self.RealCorr = stats.pearsonr(self.Population[3], self.Population[4])[0]
        EndTime = perf_counter()
        print(f'DATA POOL GENERATED:\tTime taken is {EndTime-StartTime}')

    def PullSamples(self, SampleSize:int, PopSize:int, RoundNo:int, SampleInd = None):
        if SampleSize>PopSize:
            print("Sample>Pop")
            SampleSize  = PopSize
        if PopSize > len(self.Population[0]):
            print("Pop>DataLen")
            PopSize = len(self.Population[0])
        if (PopSize*RoundNo+SampleSize) > len(self.Population[0]):
            print("(PopSize*RoundNo+SampleSize) > len(self.Population)")
            print(f'({PopSize}*{RoundNo}+{SampleSize}) > {len(self.Population[0])}')
            return [[],[]]

        if type(SampleInd) == type(None):
            SampleIndices = self.rng.choice(PopSize,size=SampleSize, replace=False)
        else:
            SampleIndices = SampleInd.copy()
        #print(f'The ting go: {PopSize*RoundNo}')
        #print(f'\t{SampleIndices}')
        SampleIndices += PopSize*RoundNo
        #print(f'\t{SampleIndices}')
        Res = [[],[]]
        for i in SampleIndices:
            Res[0].append(self.Population[3][i])
            Res[1].append(self.Population[4][i])
        return Res

    def PullSamplesSorted(self, SampleSize:int, PopSize:int, RoundNo:int, SampleInd = None):
        if SampleSize>PopSize:
            print("Sample>Pop")
            SampleSize  = PopSize
        if PopSize > len(self.Population[0]):
            print("Pop>DataLen")
            PopSize = len(self.Population[0])
        if (PopSize*RoundNo+SampleSize) > len(self.Population[0]):
            print("(PopSize*RoundNo+SampleSize) > len(self.Population)")
            print(f'({PopSize}*{RoundNo}+{SampleSize}) > {len(self.Population[0])}')
            return [[],[]]

        if type(SampleInd) == type(None):
            SampleIndices = self.rng.choice(PopSize,size=SampleSize, replace=False)
        else:
            SampleIndices = SampleInd.copy()
        #print(f'The ting go: {PopSize * RoundNo}')
        #print(f'\t{SampleIndices}')
        np.sort(SampleIndices)
        SampleIndices += PopSize*RoundNo
        #print(f'\t{SampleIndices}')
        Res = [[],[]]
        for i in SampleIndices:
            Res[0].append(self.Population[3][i])
            Res[1].append(self.Population[4][i])
        return Res

    def UpdateCorr(self):
        self.Correlations[0].append(stats.pearsonr(self.Data[0], self.Data[1])[0])
        self.SingleRoundCorr[0].append(stats.pearsonr(self.RecentData[0], self.RecentData[1])[0])

    # Used to check if the correlation data is converging
    # Takes two arguments (epsilon: The bound of divergence, CheckNum: Number of correlation data to check)
    def CheckCorrConverge(self, epsilon: float = 0.0005):
        Res = []
        if len(self.Correlations[0]) == 0:
            for i in self.Correlations:
                Res.append([1, False])
        else:
            for i in self.Correlations:
                Sum = abs(self.RealCorr - i[-1])
                if Sum < epsilon:
                    Res.append([Sum, True])
                else:
                    Res.append([Sum, False])
        return Res

    def Clean(self):
        self.Data = []
        self.DataOrdered = []
        self.RecentData = []
        self.RecentDataOrdered = []
        self.Correlations = [[]]
        self.SingleRoundCorr = [[]]
        self.OrderedCorr = [[]]
        self.SingleRoundOrderedCorr = [[]]
        self.RoundNo = 0
        for i in range(2):
            self.Data.append([])
            self.RecentData.append([])
            self.DataOrdered.append([])
            self.RecentDataOrdered.append([])
        self.Temperature = 15

    def run(self, SampleSize, PopSize, Sorted=False):
        if Sorted:
            self.RecentData = self.PullSamplesSorted(SampleSize, PopSize, self.RoundNo)
        else:
            self.RecentData = self.PullSamples(SampleSize, PopSize, self.RoundNo)
        #print(self.RecentData)
        for i in range(len(self.RecentData)):
            for j in self.RecentData[i]:
                self.Data[i].append(j)
        self.UpdateCorr()
        self.RoundNo += 1

    def runUntilConverge(self,epsilon:float, SampleSize, PopSize, Sorted=False):
        while not self.CheckCorrConverge(epsilon)[0][1]:
            if Sorted:
                self.RecentData = self.PullSamplesSorted(SampleSize, PopSize, self.RoundNo)
            else:
                self.RecentData = self.PullSamples(SampleSize, PopSize, self.RoundNo)
            for i in range(len(self.RecentData)):
                for j in self.RecentData[i]:
                    self.Data[i].append(j)
            self.UpdateCorr()
            self.RoundNo += 1
            if self.RoundNo > (len(self.Population[0])//PopSize):
                print("Could not reach close enough to real correlation")
        print(f'Reached close enough to real correlation after {self.RoundNo} rounds')
        print(f'\tReal correlation:{self.RealCorr}\n'
              f'\tApproximated correlation:{self.Correlations[0][-1]}\n'
              f'\tDifference: {self.RealCorr - self.Correlations[0][-1]}')

    def UpdateCorrOrdered(self):
        self.Correlations[0].append(stats.pearsonr(self.Data[0], self.Data[1])[0])
        self.SingleRoundCorr[0].append(stats.pearsonr(self.RecentData[0], self.RecentData[1])[0])
        self.OrderedCorr[0].append(stats.pearsonr(self.DataOrdered[0], self.DataOrdered[1])[0])
        self.SingleRoundOrderedCorr[0].append(stats.pearsonr(self.RecentDataOrdered[0], self.RecentDataOrdered[1])[0])

    def runCompareOrder(self, SampleSize, PopSize):
        #print(f'The ting go: {SampleSize}, {PopSize}')
        SampleIndices = self.rng.choice(PopSize,size=SampleSize, replace=False)
        #print(SampleIndices)
        self.RecentDataOrdered = self.PullSamplesSorted(SampleSize, PopSize, self.RoundNo, SampleIndices)
        self.RecentData = self.PullSamples(SampleSize, PopSize, self.RoundNo, SampleIndices)
        for i in range(len(self.RecentData)):
            for j in range(len(self.RecentData[i])):
                self.Data[i].append(self.RecentData[i][j])
                self.DataOrdered[i].append((self.RecentDataOrdered[i][j]))
        self.UpdateCorrOrdered()
        self.RoundNo += 1



