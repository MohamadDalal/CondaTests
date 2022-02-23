import numpy as np
#from numpy.random import default_rng
import pandas
#from scipy import stats
from ClassRNG import *
import seaborn as sns
import matplotlib as plt
'''
class RNG:

    def __init__(self):
        self.rng = np.random.default_rng()
        self.Data = [[],[],[],[]]
        self.RecentData = [[],[],[],[]]
        self.Correlations = [[],[],[],[],[],[]]


    #def Generation_Round(self, Size):
    #    X = self.rng.normal(100, 10, Size)
    #    Y = self.rng.normal(50, 5, Size)
    #    Z = 0.5*X + Y
    #    W = Z + X + self.rng.normal(0, 10, Size)
    #    return W,X,Y,Z


    def Generation_Round(self, Size):
        Res = [[],[],[],[]]
        for i in range(Size):
            X = self.rng.normal(100, 10)
            Y = self.rng.normal(50, 5)
            Z = 0.5*X + Y
            W = Z + X + self.rng.normal(0, 10)
            Res[0].append(W)
            Res[1].append(X)
            Res[2].append(Y)
            Res[3].append(Z)
        return Res

    def GenerationRoundDF(self, Size):
        X = self.rng.normal(100, 10, Size)
        Y = self.rng.normal(50, 5, Size)
        Z = 0.5*X + Y
        W = Z + X + self.rng.normal(0, 10, Size)
        return pandas.DataFrame(data={"W":W, "X":X, "Y":Y, "Z":Z})

    def UpdateCorr(self):
        self.Correlations[0].append(stats.pearsonr(self.Data[0], self.Data[1])[0])
        self.Correlations[1].append(stats.pearsonr(self.Data[0], self.Data[2])[0])
        self.Correlations[2].append(stats.pearsonr(self.Data[0], self.Data[3])[0])
        self.Correlations[3].append(stats.pearsonr(self.Data[1], self.Data[2])[0])
        self.Correlations[4].append(stats.pearsonr(self.Data[1], self.Data[3])[0])
        self.Correlations[5].append(stats.pearsonr(self.Data[2], self.Data[3])[0])

    def CheckCorrConverge(self, epsilon):
        Res = []
        for i in self.Correlations:
            Sum = 0
            for j in range(5):
                Sum += np.abs(i[-1-j]-i[-2-j])
            if Sum < epsilon and Sum > -epsilon:
                Res.append([Sum,True])
            else:
                Res.append([Sum,False])
        return Res


    #def run(self, Size):
    #    W,X,Y,Z = self.Generation_Round(Size)
    #    self.RecentData = [W,X,Y,Z]
    #    for i in range(len(self.Data)):
    #        for j in self.RecentData[i]:
    #            self.Data[i].append(j)

    def run(self, Size):
       self.RecentData = self.Generation_Round(Size)
       for i in range(len(self.Data)):
           for j in self.RecentData[i]:
               self.Data[i].append(j)
       self.UpdateCorr()
'''


Cols = ["W", "X", "Y", "Z"]
Cols2 = ["WX", "WY", "WZ", "XY", "XZ", "YZ"]
#Obj = RNG1()
#Obj.run(10)


def makeDF(List, Cols=None):
    DF = []
    try:
        DF = pandas.DataFrame(List,columns=Cols)
    except Exception as e:
        #print(e)
        New = np.transpose(List)
        DF = pandas.DataFrame(New, columns=Cols)
    finally:
        #print(DF)
        return DF

def multiRound(Object:RNG,Iterations:int, Size:int):
    for i in range(Iterations):
        Object.run(Size)

def plotAllLine(DF, Columns):
    for i in range(len(Columns)):
        sns.lineplot(data=DF, x=DF.index, y=Columns[i])
        plt.pyplot.show()


def subplotAllLine(DF, Columns):
    Num = len(Columns)
    Cols = int(np.ceil(np.math.sqrt(Num)))
    Rows = int(np.ceil(Num/Cols))
    print(f'Num={Num}\tRows={Rows}\tCols={Cols}')
    Fig, ax = plt.pyplot.subplots(Rows,Cols)
    Index = 0
    for i in range(Num):
        print(f'Current Row={Index//Cols}\tCurrent Collumn={Index%Cols}')
        sns.lineplot(data=DF, x=DF.index, y=Columns[i], ax=ax[Index//Cols][Index%Cols])
        Index += 1
    Fig.tight_layout()
    Fig.show()
    return Fig, ax

def plotAllScatter(DF,Columns):
    for i in range(len(Columns)):
        for j in range(i+1,len(Columns)):
            sns.scatterplot(data=DF, x=Columns[i], y=Columns[j])
            plt.pyplot.show()

def subplotAllScatter(DF, Columns):
    Num = np.math.factorial(len(Columns)-1)
    L   = len(Columns)
    Num = (L*(L-1)/2)
    Cols = int(np.ceil(np.math.sqrt(Num)))
    Rows = int(np.ceil(Num/Cols))
    print(f'Num={Num}\tRows={Rows}\tCols={Cols}')
    Fig, ax = plt.pyplot.subplots(Rows,Cols)
    Index = 0
    for i in range(len(Columns)):
        for j in range(i+1,len(Columns)):
            print(f'Current Row={Index//Cols}\tCurrent Collumn={Index%Cols}')
            sns.scatterplot(data=DF, x=Columns[i], y=Columns[j], ax=ax[Index//Cols][Index%Cols])
            Index += 1
    Fig.tight_layout()
    Fig.show()
    return Fig, ax


#makeDF(Obj.Data, Cols)

#RNGTing = np.random.default_rng()
#X = RNGTing.normal(100,10,10)
#Y = X + RNGTing.normal(50,5,10)
#Arr = np.empty((0,4))
#np.append(Arr, X)
#Arr = []
#for i in X:
#    print(i)
#    Arr.append(i)
#Arr.append(i for i in X)

#Frame = pandas.DataFrame(data={"X":X, "Y":Y})

#def findCorr(RNGObj, Size, Frame = pandas.DataFrame()):
#    pass

#def run():
#    pass

#if __name__ == "__main__":
#    global Obj
    #Obj = RNG()
#    findCorr(Obj, 10)
