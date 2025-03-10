import numpy as np
from scipy import stats
from time import perf_counter
import warnings

class ClusterPopulations():
    # Object that creates populations of 10 random variables
    def __init__(self, L, Seed=39916801):
        self.StartTime = perf_counter()
        self.rng = np.random.default_rng(seed=Seed)
        self.Populations = []                           # Array holding the populations
        self.Pos = [[2,8],[3,6],[5,7],[3,4],[6,5],      # Array holding position of variables on cartesian plane
                     [1,8],[3,9],[9,8],[9,4],[1,6]]
        self.DataCols = []                              # Array holding names of variables V0-V9
        for i in range(10):
            print(f'\tDatacols{i}')
            self.DataCols.append(f'V{i}')

        # Generate V0 and the V1-V9
        # V0 ~ N(100,10)
        # V1-9 = V0 + N(0, 2C)
        # Where C (The modifier) is the distance from V0 squared
        self.Populations.append(self.rng.normal(100, 10, size=L))
        for i in range(1,10):
            print(f'\tPopulations{i}')
            Modifier = (self.Pos[i][0] - 2)**2 + (self.Pos[i][1] - 8)**2
            print(f'\t\tModifier is {Modifier}')
            Arr = self.Populations[0] + self.rng.normal(0,(Modifier*2), size=L)
            self.Populations.append(Arr)

        # Calculate mean and standard deviation of variables
        self.StdDiv = []
        self.Mean = []
        for i in range(len(self.Populations)):
            print(f'\tStdDiv and Mean {i}')
            self.StdDiv.append(np.std(self.Populations[i]))
            self.Mean.append(np.mean(self.Populations[i]))


        # Caluclate the correlation between V0 and V1-V9 and then cluster them according to those correlations
        self.Corr = []
        self.Cluster = []
        for i in range(10):
            print(f'\tCorrelation{i}')
            self.Corr.append(stats.pearsonr(self.Populations[0], self.Populations[i])[0])
            self.Cluster.append(int(abs(np.floor(self.Corr[i]*4.9999) + 1)))

        self.FinishTime = perf_counter()
        self.TotalTime = self.FinishTime - self.StartTime
        print(f'Time taken to create population: {self.TotalTime}seconds')


class ClusterSampler():
    # Object that collects samples from the population object
    def __init__(self, ObjPopulations:ClusterPopulations, Seed=433494437):
        # Population object, RNG generator and length of population
        self.ObjPop = ObjPopulations
        self.rng = np.random.default_rng(seed=Seed)
        PopLen = len(self.ObjPop.Populations)
        # Correlations, standard deviations and means
        self.Corrs = [[] for _ in range(PopLen)]
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
    def PullSamples(self, SampleSize:int, SubSetSize:int, RoundNo:int,
                    IndicesList = None, SampleInd:np.ndarray = None):
        PopLen = len(self.ObjPop.Populations)
        PopElementsLen = len(self.ObjPop.Populations[0])
        # Safety checks that fix error inducing arguments
        if SampleSize>SubSetSize:
            print("Sample>SubSet")
            SampleSize  = SubSetSize
        if SubSetSize > PopElementsLen:
            print("SubSet>DataLen")
            SubSetSize = PopElementsLen
        if (SubSetSize*RoundNo+SampleSize) > PopElementsLen:
            print("(SubSetSize*RoundNo+SampleSize) > len(Population)")
            print(f'({SubSetSize}*{RoundNo}+{SampleSize}) > {PopElementsLen}')
            return [[] for i in range(PopLen)]

        # If no sampling list (List of data to be sampled) is provided then randomly create one
        # This list can be used if one wants to sample the same indices more than once in a row
        if type(SampleInd) == type(None):
            SampleIndices = self.rng.choice(SubSetSize,size=SampleSize, replace=False)
        else:
            SampleIndices = SampleInd.copy()

        # If no list is provided, the make a list with all variables so that all can be sampled
        if type(IndicesList) == type(None):
            IndexList = [i for i in range(PopLen)]
        else:
            IndexList = IndicesList[:]

        SampleIndices += SubSetSize*RoundNo             # Use round number to not sample from same subset
        Res = [[] for i in range(PopLen)]
        Updated = [False for i in range(PopLen)]        # List of variables that were sampled in this round
        for i in IndexList:
            for j in SampleIndices:
                Res[i].append(self.ObjPop.Populations[i][j])
            Updated[i] = True
        return Res, Updated

    # Function to update the correlations out of all the collected data (Usually after each round)
    # Arg(A list of variables that got new data)
    def UpdateCorr(self, UpdateList:list):
        for i in range(len(UpdateList)):
            if UpdateList[i]:
                # Make warning into error.
                # This is to catch the warning made when the correlation of a constant list to be taken.
                # Scipy gives None. I want to catch that and write 0 instead.
                with warnings.catch_warnings():
                    warnings.simplefilter("error", category=stats.PearsonRConstantInputWarning)
                    try:
                        self.Corrs[i].append(stats.pearsonr(self.Data[i], self.Data[0])[0])
                    except Exception as e:
                        print(f'\tError caught: {e}')
                        self.Corrs[i].append(0)
            else:
                if len(self.Corrs[i]) == 0:
                    self.Corrs[i].append(0)
                else:
                    self.Corrs[i].append(self.Corrs[i][-1])

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
    def CheckCorrConverge(self, Var, Epsilon = 0.0005, Round = -1):
        if len(self.Corrs[Var]) == 0:
            Res = [1, False]
        else:
            Sum = abs(self.Corrs[Var][Round] - self.ObjPop.Corr[Var])
            if Sum <= Epsilon:
                Res = [Sum, True]
            else:
                Res = [Sum, False]
        return Res

    # Run a round. Round number is updated accordingly
    def run(self, SampleSize, SubSetSize, indicesList = None):
        self.RecentData, UpdateList = self.PullSamples(SampleSize, SubSetSize, self.RoundNo, indicesList)
        for i in range(len(self.RecentData)):
            for j in self.RecentData[i]:
                self.Data[i].append(j)
        self.UpdateCorr(UpdateList)
        self.UpdateMeans(UpdateList)
        self.UpdateStdDiv(UpdateList)
        self.RoundNo += 1

    # Keep running rounds until all correlations are at most epsilon away from real correlation values
    def runUntilConverge(self,epsilon:float, SampleSize, SubSetSize):
        Converged = False
        while not Converged:
            # Run round
            self.RecentData, Updated = self.PullSamples(SampleSize, SubSetSize, self.RoundNo)
            for i in range(len(self.RecentData)):
                for j in self.RecentData[i]:
                    self.Data[i].append(j)
            self.UpdateMeans(Updated)
            self.UpdateStdDiv(Updated)
            self.UpdateCorr(Updated)
            self.RoundNo += 1
            print(f'\t\tRound{self.RoundNo}')
            # Check if the correlations have come close enough
            Converged = True
            for i in range(len(Updated)):
                Converged = (Converged and self.CheckCorrConverge(i, epsilon)[1])
            # Check if all population has been sampled
            if self.RoundNo >= (len(self.ObjPop.Populations[0])//SubSetSize):
                print("Could not reach close enough to real correlation")
                return
        print(f'Reached close enough to real correlation after {self.RoundNo} rounds')

    # Gets the approximations made after a specific round
    # Args(Round number(Default is last round), If to include parent variables W,V,X,Y,Z)
    def GetRoundData(self, Round = -1):
        Means = [self.Means[i][Round] for i in range(len(self.Means))]
        StdDivs = [self.StdDivs[i][Round] for i in range(len(self.StdDivs))]
        Corrs = [self.Corrs[i][Round] for i in range(len(self.Corrs))]
        return {"Means":Means, "StdDivs":StdDivs, "Corrs":Corrs}

    # Cluster the approximated data in a specific round.
    # Arg(Round to cluster data from (Dafault is last round))
    # Mean clusters are: ]-infty.-100], ]-100,-10[, [-10, 10], ]10, 100], ]100, infty[
    # Standard deviation clusters are: [0,20[, [20,40[, [40,60[, [60,80[, [80, infty[
    # Correlation clusters are: [0, 0.2[, [0.2, 0.4[, [0.4, 0.6[, [0.6, 0.8[, [0.8, 1]
    def ClusterAll(self, Round=-1):
        MeanCluster = [{},{},{},{},{}]
        MeanLabels = []
        StdDivCluster = [{},{},{},{},{}]
        StdDivLabels = []
        CorrCluster = [{},{},{},{},{}]
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
        for i in range(len(self.Corrs)):
            Val = self.Corrs[i][Round]
            Cluster = int(np.floor(abs(Val*4.9999)))        # Mapping from [0,1] to [0,5] for assigning clusters
            CorrCluster[Cluster].update({self.ObjPop.DataCols[i]:Val})
            CorrLabels.append(Cluster + 1)
        return MeanCluster, StdDivCluster, CorrCluster, MeanLabels, StdDivLabels, CorrLabels


