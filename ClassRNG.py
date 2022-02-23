import numpy as np
from scipy import stats

# Parent class. Can be used to create different variable combinations
class RNG:
    # Takes in the number of variables that the child will include as argument
    # This is so that it can create the correct lists
    def __init__(self, DataNum:int):
        self.rng = np.random.default_rng()      # Object that is used as a random number generator
        self.Data = []                          # List of lists with data from the random variables
        self.RecentData = []                    # List of lists with data generated in the latest round
        self.Correlations = []                  # List of lists with the correlations of all random variables
        for i in range(DataNum):
            self.Data.append([])
            self.RecentData.append([])
        for i in range(int((DataNum*(DataNum-1))/2)):
            self.Correlations.append([])
    # Supposed to be an abstract function that is filled by the child classes
    def Generation_Round(self, Size:int):
        return []
    # Calcultes the correlation from the latest round and updates the correlation list with it
    def UpdateCorr(self):
        Index  = 0
        Len = len(self.Data)
        for i in range(Len):
            for j in range(i+1, Len):
                self.Correlations[Index].append(stats.pearsonr(self.Data[i], self.Data[j])[0])
                Index += 1
    # Used to check if the correlation data is converging
    # Takes two arguments (epsilon: The bound of divergence, CheckNum: Number of correlation data to check)
    def CheckCorrConverge(self, epsilon:float = 0.0005, CheckNum:int = 5):
        Res = []
        for i in self.Correlations:
            Sum = 0
            for j in range(CheckNum):
                Sum += np.abs(i[-1-j]-i[-2-j])
            if Sum < epsilon and Sum > -epsilon:
                Res.append([Sum,True])
            else:
                Res.append([Sum,False])
        return Res
    # The function to run each round. Responsible for generating data and updating correlations
    # Argument is the amount of samples to be generated per round
    def run(self, Size):
        self.RecentData = self.Generation_Round(Size)
        for i in range(len(self.RecentData)):
            for j in self.RecentData[i]:
                self.Data[i].append(j)
        self.UpdateCorr()

# The next two classes are the child classes of RNG. More can be created with different random variables
class RNG1(RNG):

    def __init__(self):
        super().__init__(4)
        self.DataCols = ["W", "X", "Y", "Z"]            # The column names used for the pandas dataframe
        self.CorrCols = ["WX", "WY", "WZ",              # Same as above but for correlations list
                         "XY", "XZ",
                         "YZ"]

    def Generation_Round(self, Size):
        Res = [[], [], [], []]
        for i in range(Size):
            X = self.rng.normal(100, 10)
            Y = self.rng.normal(50, 5)
            Z = 0.5 * X + Y
            W = Z + X + self.rng.normal(0, 10)
            Res[0].append(W)
            Res[1].append(X)
            Res[2].append(Y)
            Res[3].append(Z)
        return Res

class RNG2(RNG):

    def __init__(self):
        super().__init__(6)
        self.DataCols = ["U", "V", "W", "X", "Y", "Z"]
        self.CorrCols = ["UV", "UW", "UX", "UY", "UZ",
                         "VW", "VX", "VY", "VZ",
                         "WX", "WY", "WZ",
                         "XY", "XZ",
                         "YZ"]

    def Generation_Round(self, Size):
        Res = [[], [], [], [], [], []]
        for i in range(Size):
            U = self.rng.normal(100, 10)
            V = self.rng.normal(100, 20)
            W = V + 2*U
            X = W + U**2
            Y = V**2 + self.rng.normal(0,1000)
            Z = U**2 + V**2
            Res[0].append(U)
            Res[1].append(V)
            Res[2].append(W)
            Res[3].append(X)
            Res[4].append(Y)
            Res[5].append(Z)
        return Res


class RNG3(RNG):

    def __init__(self):
        super().__init__(5)
        self.DataCols = ["U","V", "W", "X", "Y"]
        self.CorrCols = ["XY"]
        self.Correlations = [[]]
        self.SingleRoundCorr = [[]]
        self.rng = np.random.default_rng(seed=39916801)
        self.Temperature = 15

    def Gen_Temp(self):
        TempAddition = self.rng.normal(0, 0.5)
        self.Temperature += TempAddition
        if (self.Temperature>40) or (self.Temperature<-10):
            self.Temperature -= 2*TempAddition

    def Generation_Round(self, Size):
        Res = [[], [], [], [], []]
        for i in range(Size):
            self.Gen_Temp()
            U = self.Temperature
            V = np.abs(self.rng.normal(0,1))
            W = np.abs(self.rng.normal(2,2))
            X = U - V
            Y = U - W

            Res[0].append(U)
            Res[1].append(V)
            Res[2].append(W)
            Res[3].append(X)
            Res[4].append(Y)
        return Res

    def UpdateCorr(self):
        self.Correlations[0].append(stats.pearsonr(self.Data[3], self.Data[4])[0])
        self.SingleRoundCorr[0].append(stats.pearsonr(self.RecentData[3], self.RecentData[4])[0])
