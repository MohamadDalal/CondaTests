import numpy as np
from scipy import stats
import pandas
from ClassRNG import *
import seaborn as sns
import matplotlib as plt

# This function is used to create pandas dataframes of the lists of lists generated by the RNG objects
# Cols is the column names list that is found in RNG1 and RNG2 for example
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

# This function is used to run multiple rounds at once instead of having to do that manually
# Iterations is number of rounds to run, and size is the samples created per round
def multiRound(Object:RNG,Iterations:int, Size:int):
    for i in range(Iterations):
        Object.run(Size)

# Function used to run the test run that was recorded
def testRun():
    Obj1 = RNG1()
    Obj2 = RNG2()
    multiRound(Obj1, 1000, 100)
    multiRound(Obj2, 1000, 100)
    DataDF1 = makeDF(Obj1.Data, Obj1.DataCols)
    DataDF2 = makeDF(Obj2.Data, Obj2.DataCols)
    CorrDF1 = makeDF(Obj1.Correlations, Obj1.CorrCols)
    CorrDF2 = makeDF(Obj2.Correlations, Obj2.CorrCols)
    return DataDF1, DataDF2, CorrDF1, CorrDF2

# Function used to plot line plots for each list of correlations alone
def plotAllLine(DF, Columns):
    plt.rc("font", size=16)
    AxesList = []
    for i in range(len(Columns)):
        ax = sns.lineplot(data=DF, x=DF.index, y=Columns[i])
        Center = DF.iloc[-5, i]
        ax.axhspan(Center-0.0005, Center+0.0005, 0.85, ec="black", fc="gray", alpha=0.7)

        #print(f'Adding line at {DF.iloc[-5, i] - 0.0005}')
        #ax.axhline(DF.iloc[-5, i] - 0.0005, 0.5, 1)
        #ax.axhline(DF.iloc[-5, i] + 0.0005, 0.5, 1)
        AxesList.append(ax)
        plt.pyplot.show()
    return AxesList

# Function used to plot scatter plots for all combinations of random variables
def plotAllScatter(DF,Columns):
    plt.rc("font", size=12)
    AxesList = []
    for i in range(len(Columns)):
        for j in range(i+1,len(Columns)):
            ax = sns.scatterplot(data=DF, x=Columns[i], y=Columns[j])
            #ax = sns.regplot(data=DF, x=Columns[i], y=Columns[j], ci=None)
            #ax.text(0.85, 1.05, "Something", transform=ax.transAxes)
            AxesList.append(ax)
            plt.pyplot.show()
    return AxesList

def plotAllReg(DataDF,Columns, CorrDF):
    plt.rc("font", size=12)
    AxesList = []
    for i in range(len(Columns)):
        for j in range(i + 1, len(Columns)):
            ax = sns.regplot(data=DataDF, x=Columns[i], y=Columns[j], ci=None, line_kws={"color":"k"})
            Correlation = CorrDF[Columns[i]+Columns[j]].iloc[-1]
            ax.text(0.70, 1.03, f"Correlation: {Correlation:.3f}", transform=ax.transAxes)
            AxesList.append(ax)
            plt.pyplot.show()
    return AxesList

# Does what plotAllLine does, but it combines all the plots in one figure
def subplotAllLine(DF, Columns):
    plt.rc("font", size=5)
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

# Does what plotAllScatter does, but it combines all the plots in one figure
def subplotAllScatter(DF, Columns):
    plt.rc("font", size=5)
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

CorrDF = pandas.read_csv("TestRun/Data/RNG1_Correlations.csv", index_col=0)
DataDF = pandas.read_csv("TestRun/Data/RNG1_Data.csv", index_col=0)
Obj = RNG1()
#AxList1 = plotAllLine(CorrDF, Obj.CorrCols)
#AxList2 = plotAllScatter(DataDF, Obj.DataCols)
AxList3 = plotAllReg(DataDF, Obj.DataCols, CorrDF)
