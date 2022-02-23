import numpy as np
from scipy import stats
from time import perf_counter
import warnings

class ClusterPopulations():

    # Used to find the correlation of the variables with the parent variables
    def CorrFinder(self, Corr: list, CorrCols: list, StartIndex):
        for i in range(StartIndex + 1, len(self.Populations)):
            with warnings.catch_warnings():
                warnings.simplefilter("error", category=stats.PearsonRConstantInputWarning)
                try:
                    Corr.append(stats.pearsonr(self.Populations[StartIndex], self.Populations[i])[0])
                except Exception as e:
                    print(f'\tError caught: {e}')
                    Corr.append(0)
                finally:
                    CorrCols.append(f'{self.DataCols[StartIndex]}{self.DataCols[i]}')


    def __init__(self, L, Seed=39916801):
        self.StartTime = perf_counter()
        #self.Populations = [[] for i in range(5)]
        self.rng = np.random.default_rng(seed=Seed)
        self.Populations = []
        # Parent Variable V
        self.Populations.append(self.rng.integers(-500, -200, endpoint=True, size=L))
        # Parent Variable W
        self.Populations.append(self.rng.normal(-75, 74, size=L))
        # Parent Variable X
        self.Populations.append(self.rng.chisquare(7, size=L))
        # Parent Variable Y
        self.Populations.append(self.rng.poisson(999, size=L))
        # Parent Variable Z
        self.Populations.append(self.rng.binomial(198, 0.5, size=L))
        '''for i in range(L):
            self.Populations[0].append(self.rng.integers(-500, -200, endpoint=True))
            self.Populations[1].append(self.rng.normal(-75, 74))
            self.Populations[2].append(self.rng.chisquare(7))
            self.Populations[3].append(self.rng.poisson(999))
            self.Populations[4].append(self.rng.binomial(198, 0.5))'''
        self.DataCols = ["V", "W", "X", "Y", "Z"]
        #print(self.Populations)
        #print(type(self.Populations))
        #print(len(self.Populations))


        self.StdDiv = []
        self.Mean = []
        for i in range(len(self.Populations)):
            self.StdDiv.append(np.std(self.Populations[i]))
            self.Mean.append(np.mean(self.Populations[i]))

        # Creates the linear combination of the remaining 243 variables
        for i in range(3**5):
            # Find coefficients of linear combination
            a = (i%3) - 1
            b = ((i//3)%3) - 1
            c = ((i//9)%3) - 1
            d = ((i//27)%3) - 1
            e = ((i//81)%3) - 1
            # Create Variable and append it
            Arr = (e*self.Populations[0] +
                   d*self.Populations[1] +
                   c*self.Populations[2] +
                   b*self.Populations[3] +
                   a*self.Populations[4])
            self.Populations.append(Arr)

            #self.DataCols.append(f'U{e+1}{d+1}{c+1}{b+1}{a+1}')
            self.DataCols.append(f'{e + 1}{d + 1}{c + 1}{b + 1}{a + 1}')
            # Calculate Standard Deviation and Mean of Variable
            self.StdDiv.append(np.sqrt(e*e*self.StdDiv[0]+
                                       d*d*self.StdDiv[1]+
                                       c*c*self.StdDiv[2]+
                                       b*b*self.StdDiv[3]+
                                       a*a*self.StdDiv[4]))
            self.Mean.append(e*self.Mean[0]+
                             d*self.Mean[1]+
                             c*self.Mean[2]+
                             b*self.Mean[3]+
                             a*self.Mean[4])

        # Caluclates the correlations
        self.Vcorr, self.VcorrCols = [], []
        self.Wcorr, self.WcorrCols = [], []
        self.Xcorr, self.XcorrCols = [], []
        self.Ycorr, self.YcorrCols = [], []
        self.Zcorr, self.ZcorrCols = [], []
        self.CorrFinder(self.Vcorr, self.VcorrCols, 0)
        self.CorrFinder(self.Wcorr, self.WcorrCols, 1)
        self.CorrFinder(self.Xcorr, self.XcorrCols, 2)
        self.CorrFinder(self.Ycorr, self.YcorrCols, 3)
        self.CorrFinder(self.Zcorr, self.ZcorrCols, 4)
        # Makes a universal array with the individual correlation arrays
        self.Corr = [self.Vcorr, self.Wcorr, self.Xcorr, self.Ycorr, self.Zcorr]
        self.CorrCols = [self.VcorrCols,
                         self.WcorrCols,
                         self.XcorrCols,
                         self.YcorrCols,
                         self.ZcorrCols]

        self.FinishTime = perf_counter()
        self.TotalTime = self.FinishTime - self.StartTime
        print(f'Time taken to create population: {self.TotalTime}seconds')

# Note to self for next time: Create an object for each random variable
# The object will have real correlation, mean and standard deviation
# All approximations for mean, correlations and standard deviation
# And it will have functions to check convergence etc, and it will have convergence attributes


class ClusterSampler():

    def __init__(self, ObjPopulations:ClusterPopulations, Seed=433494437):
        # Population object, RNG generator and length of population
        self.ObjPop = ObjPopulations
        self.rng = np.random.default_rng(seed=Seed)
        PopLen = len(self.ObjPop.Populations)
        # Lists that stor correlations, standard deviations and means
        self.VCorr = [[] for _ in range(PopLen - 1)] # Does not contain Variable V
        self.WCorr = [[] for _ in range(PopLen - 2)] # Does not contain Variables V to W
        self.XCorr = [[] for _ in range(PopLen - 3)] # Does not contain Variables V to X
        self.YCorr = [[] for _ in range(PopLen - 4)] # Does not contain Variables V to Y
        self.ZCorr = [[] for _ in range(PopLen - 5)] # Does not contain Variables V to Z
        self.Corrs = [self.VCorr, self.WCorr, self.XCorr, self.YCorr, self.ZCorr]
        self.StdDivs = [[] for _ in range(PopLen)]
        self.Means = [[] for _ in range(PopLen)]
        # Data list that stores the sampled data
        self.Data = [[] for _ in range(PopLen)]
        # Recent data list used to contain data sampled in latest round
        self.RecentData = []
        # Round number used to keep track
        self.RoundNo = 0

    # Function to pull samples out of subset of the population population each round
    # Args(Sample size, Size of population subset, Round number,
    #       List of random variables to pull samples from (Default is all),
    #       List of indices of samples to be pulled from population subset
    #       (Default is random generated by numpy))
    def PullSamples(self, SampleSize:int, PopSize:int, RoundNo:int,
                    IndicesList = None, SampleInd:np.ndarray = None):
        PopNo = len(self.ObjPop.Populations)
        PopElementsNo = len(self.ObjPop.Populations[0])
        if SampleSize>PopSize:
            print("Sample>Pop")
            SampleSize  = PopSize
        if PopSize > PopElementsNo:
            print("Pop>DataLen")
            PopSize = PopElementsNo
        if (PopSize*RoundNo+SampleSize) > PopElementsNo:
            print("(PopSize*RoundNo+SampleSize) > len(self.Population)")
            print(f'({PopSize}*{RoundNo}+{SampleSize}) > {PopElementsNo}')
            return [[] for i in range(PopNo)]

        if type(SampleInd) == type(None):
            SampleIndices = self.rng.choice(PopSize,size=SampleSize, replace=False)
        else:
            SampleIndices = SampleInd.copy()

        if type(IndicesList) == type(None):
            IndexList = [i for i in range(PopNo)]
        else:
            Temp = IndicesList[:]
            Temp = Temp + 5
            IndexList = [0,1,2,3,4]
            IndexList.append(Temp)

        #print(f'The ting go: {PopSize*RoundNo}')
        #print(f'\t{SampleIndices}')
        SampleIndices += PopSize*RoundNo
        #print(f'\t{SampleIndices}')
        Res = [[] for i in range(PopNo)]
        Updated = [False for i in range(PopNo)]
        for i in IndexList:
            for j in SampleIndices:
                Res[i].append(self.ObjPop.Populations[i][j])
            Updated[i] = True
        return Res, Updated

    # Function to update the correlations out of all the collected data (Usually after each round)
    # Arg(A list of variables that got new data)
    def UpdateCorr(self, UpdateList):
        for i in range(5):
            if UpdateList[i]:
                for j in range(i+1, len(UpdateList)):
                    if UpdateList[j]:
                        # Make warning into error.
                        # This is to catch the warning made when the correlation of a constant list to be taken.
                        # Scipy gives None. I want to catch that and write 0 instead.
                        with warnings.catch_warnings():
                            warnings.simplefilter("error", category=stats.PearsonRConstantInputWarning)
                            try:
                                self.Corrs[i][j-(i+1)].append(stats.pearsonr(self.Data[i], self.Data[j])[0])
                            except Exception as e:
                                #print(f'\tError caught: {e}')
                                self.Corrs[i][j-(i+1)].append(0)
                        #self.Corrs[i][j-(i+1)].append(stats.pearsonr(self.Data[i], self.Data[j])[0])
                    else:
                        if len(self.Corrs[i][j-(i+1)]) == 0:
                            self.Corrs[i][j-(i+1)].append(0)
                        else:
                            self.Corrs[i][j-(i+1)].append(self.Corrs[i][j-(i+1)][-1])
            else:
                for j in range(i+1, len(UpdateList)):
                    if len(self.Corrs[i][j-(i+1)]) == 0:
                        self.Corrs[i][j-(i+1)].append(0)
                    else:
                        self.Corrs[i][j-(i+1)].append(self.Corrs[i][j-(i+1)][-1])
    # Update standard deviation from available data (Usually after every round)
    def UpdateStdDiv(self, UpdateList):
        for i in range(len(UpdateList)):
            if UpdateList[i]:
                self.StdDivs[i].append(np.std(self.Data[i]))
            else:
                if len(self.StdDivs[i]) == 0:
                    self.StdDivs[i].append(0)
                else:
                    self.StdDivs[i].append(self.StdDivs[i][-1])
    # Update mean from available data (Usually after every round)
    def UpdateMeans(self, UpdateList):
        for i in range(len(UpdateList)):
            if UpdateList[i]:
                self.Means[i].append(np.mean(self.Data[i]))
            else:
                if len(self.Means[i]) == 0:
                    self.Means[i].append(0)
                else:
                    self.Means[i].append(self.Means[i][-1])

    # Check if approximated mean and standard deviation converge to real values
    def CheckConverge(self, Index, MeanEpsilon, StdDivEpsilon):
        Res = [[1, False], [1, False]]

        DoMean, DoStdDiv = True, True

        if len(self.Means[Index]) == 0:   DoMean = False
        if len(self.StdDivs[Index]) == 0: DoStdDiv = False

        if DoMean:
            MeanSum = abs(self.Means[Index] - self.ObjPop.Mean[Index])
            if MeanSum <= MeanEpsilon:
                Res[0] = [MeanSum, True]
            else:
                Res[0] = [MeanSum, False]
        if DoStdDiv:
            StdDivSum = abs(self.StdDivs[Index] - self.ObjPop.StdDiv[Index])
            if StdDivSum <= StdDivEpsilon:
                Res[1] = [StdDivSum, True]
            else:
                Res[1] = [StdDivSum, False]
        return Res
    # Check if approximated correlation converge to real values
    def CheckCorrConverge(self, Index, CorrIndex, Epsilon = 0.0005):
        Res = [1, False]
        ModifiedIndex = Index - (CorrIndex + 1)
        if (Index <= CorrIndex) or (len(self.Corrs[CorrIndex][ModifiedIndex]) == 0):
            return Res
        else:
            Sum = abs(self.Corrs[CorrIndex][ModifiedIndex] - self.ObjPop.Corr[CorrIndex][ModifiedIndex])
            if Sum <= Epsilon:
                Res = [Sum, True]
            else:
                Res = [Sum, False]
        return Res

    # Run a round. Round number is updated accordingly
    def run(self, SampleSize, PopSize, indicesList = None):
        self.RecentData, UpdateList = self.PullSamples(SampleSize, PopSize, self.RoundNo, indicesList)
        # print(self.RecentData)
        for i in range(len(self.RecentData)):
            for j in self.RecentData[i]:
                self.Data[i].append(j)
        self.UpdateCorr(UpdateList)
        self.UpdateMeans(UpdateList)
        self.UpdateStdDiv(UpdateList)
        self.RoundNo += 1
    # Quick run runs all possible rounds and only approximates after all rounds are done
    def QuickRun(self, SampleSize, PopSize):
        UpdateList = []
        #print(f"Len: {len(self.ObjPop.Populations[0])}\n"
        #      f"PopSize: {PopSize}\n"
        #      f"Res: {len(self.ObjPop.Populations[0])//PopSize}")
        for i in range(len(self.ObjPop.Populations[0])//PopSize):
            self.RecentData, UpdateList = self.PullSamples(SampleSize, PopSize, self.RoundNo, None)
            # print(self.RecentData)
            for i in range(len(self.RecentData)):
                for j in self.RecentData[i]:
                    self.Data[i].append(j)
            self.RoundNo += 1
        #print(UpdateList)
        self.UpdateCorr(UpdateList)
        self.UpdateMeans(UpdateList)
        self.UpdateStdDiv(UpdateList)

    """
    # Not implemented yet due to huge number of variables
    def runUntilConverge(self,epsilon:float, SampleSize, PopSize, Sorted=False):
        while not self.CheckCorrConverge(epsilon)[0][1]:
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
    """
    # Gets the approximations made after a specific round
    # Args(Round number(Default is last round), If to include parent variables W,V,X,Y,Z)
    def GetRoundData(self, Round = -1, IncludeParents = True):
        if IncludeParents:
            Means = [self.Means[i][Round] for i in range(len(self.Means))]
            StdDivs = [self.StdDivs[i][Round] for i in range(len(self.StdDivs))]
            Corrs = [[1]
                     ,[self.VCorr[0][Round], 1]
                     ,[self.VCorr[1][Round], self.WCorr[0][Round], 1]
                     ,[self.VCorr[2][Round], self.WCorr[1][Round], self.XCorr[0][Round], 1]
                     ,[self.VCorr[3][Round], self.WCorr[2][Round], self.XCorr[1][Round], self.YCorr[0][Round], 1]]
            for i in range(5):
                for j in range(len(self.Corrs[i])):
                    Corrs[i].append(self.Corrs[i][j][Round])
        else:
            Means = [self.Means[i][Round] for i in range(5,len(self.Means))]
            StdDivs = [self.StdDivs[i][Round] for i in range(5,len(self.StdDivs))]
            Corrs = [[] for _ in range(5)]
            for i in range(5):
                for j in range((4-i), len(self.Corrs[i])):
                    Corrs[i].append(self.Corrs[i][j][Round])
        return {"Means":Means, "StdDivs":StdDivs,
                "V":Corrs[0], "W":Corrs[1], "X":Corrs[2], "Y":Corrs[3], "Z":Corrs[4]}
    # Cluster the approximated data in a specific round.
    # Arg(Round to cluster data from (Dafault is last round))
    # Mean clusters are: ]-infty.-100], ]-100,-10[, [-10, 10], ]10, 100], ]100, infty[
    # Standard deviation clusters are: [0,20[, [20,40[, [40,60[, [60,80[, [80, infty[
    # Clustering by correlation is done by putting it in the cluster
    # of the parent variable (V,W,X,Y,Z) it is most correlated to,
    # or in an 6th cluster if it is not correlated to any parent variable
    # by more than 0.5 (Absolute value).
    def ClusterAll(self, Round=-1):
        MeanCluster = [{},{},{},{},{}]
        MeanLabels = []
        StdDivCluster = [{},{},{},{},{}]
        StdDivLabels = []
        CorrCluster = [{},{},{},{},{},{}]
        CorrLabels = []
        for i in range(len(self.Means)):
            Val = self.Means[i][Round]
            if Val<=-100:
                MeanCluster[0].update({self.ObjPop.DataCols[i]:Val})
                MeanLabels.append(0)
            elif Val >= -100 and Val < -10:
                MeanCluster[1].update({self.ObjPop.DataCols[i]:Val})
                MeanLabels.append(1)
            elif Val >= -10 and Val <= 10:
                MeanCluster[2].update({self.ObjPop.DataCols[i]:Val})
                MeanLabels.append(2)
            elif Val > 10 and Val <= 100:
                MeanCluster[3].update({self.ObjPop.DataCols[i]:Val})
                MeanLabels.append(3)
            else:
                MeanCluster[4].update({self.ObjPop.DataCols[i]:Val})
                MeanLabels.append(4)
        for i in range(len(self.StdDivs)):
            Val = self.StdDivs[i][Round]
            if Val >= 0 and Val < 20:
                StdDivCluster[0].update({self.ObjPop.DataCols[i]:Val})
                StdDivLabels.append(0)
            elif Val >= 20 and Val < 40:
                StdDivCluster[1].update({self.ObjPop.DataCols[i]:Val})
                StdDivLabels.append(1)
            elif Val >= 40 and Val < 60:
                StdDivCluster[2].update({self.ObjPop.DataCols[i]:Val})
                StdDivLabels.append(2)
            elif Val >= 60 and Val < 80:
                StdDivCluster[3].update({self.ObjPop.DataCols[i]:Val})
                StdDivLabels.append(3)
            else:
                StdDivCluster[4].update({self.ObjPop.DataCols[i]:Val})
                StdDivLabels.append(4)
        for i in range(5):
            CorrCluster[i].update({self.ObjPop.DataCols[i]:1})
            CorrLabels.append(i)
        for i in range(5,len(self.ObjPop.Populations)):
            #Values = []
            Max = 0
            MaxInd = -1
            for j in range(5):
                #Values.append(self.Corrs[j][i-1-j])
                Val = abs(self.Corrs[j][i-1-j][Round])
                try:
                    if abs(Val) >= Max:
                        Max = Val
                        MaxInd = j
                except TypeError as e:
                    print(f'\tValue is {Val}\n\t{e}')
            if MaxInd < 0 or Max < 0.5:
                CorrCluster[5].update({self.ObjPop.DataCols[i]:Max})
                #CorrCluster[5].update({self.ObjPop.CorrCols[MaxInd][i - (MaxInd+1)]: Max})
                CorrLabels.append(5)
            else:
                CorrCluster[MaxInd].update({self.ObjPop.DataCols[i]: Max})
                #CorrCluster[MaxInd].update({self.ObjPop.CorrCols[MaxInd][i - (MaxInd + 1)]: Max})
                CorrLabels.append(MaxInd)

        return MeanCluster, StdDivCluster, CorrCluster, MeanLabels, StdDivLabels, CorrLabels




'''
for i in range(3**5):
    print((i // 81) % 3, end="")
    print((i // 27) % 3, end="")
    print((i // 9) % 3, end="")
    print((i // 3) % 3, end="")
    print(i % 3)

for i in range(3**5):
    print((i // 81) % 3 - 1, end="")
    print((i // 27) % 3 - 1, end="")
    print((i // 9) % 3 - 1, end="")
    print((i // 3) % 3 - 1, end="")
    print(i % 3 - 1)
'''

