#import matplotlib.pyplot as plt
#import numpy as np

from CorrRoundingError3 import *
import multiprocessing as mp
import scipy.stats as stats
import pickle

CoresNo = mp.cpu_count()

#def CreateFigure(Data, FileName):



def main(Reps, Range, Size, Decimals, FileName, Func, Mean=0, Correlation=0):
    RepsPerCore = Reps//CoresNo
    print(f'Number of cores {CoresNo}')
    print(f'Repititions per core {RepsPerCore}')
    Processes = []
    Manager = mp.Manager()
    ReturnDict = Manager.dict()
    Time1 = perf_counter()
    #FixCorr = not type(Correlation)==type(None)
    #print(f'FixCorr is {FixCorr}')
    for i in range(CoresNo):
        P = mp.Process(target=ParallelRun, args=(ReturnDict, i, RepsPerCore, Func,
                                                 Range, Size, Decimals, Mean, Correlation,))    # Map function to process
        Processes.append(P)                                                                     # Append process to list
        Processes[-1].start()                                                                   # Start the newly appended process
        #print(f'Started process {i}')
    Time2 = perf_counter()
    for i in range(len(Processes)):
        Processes[i].join()						                        # Join the processes one by one
        print(f'Joined process {i}')
    Time3 = perf_counter()
    print(f'Time taken to create processes = {Time2-Time1}')
    print(f'Time taken for all processes to finish = {Time3-Time2}')
    #print(ReturnDict.values())
    #print(len(ReturnDict))
    Errors = [i[2] for i in ReturnDict.values()]
    AllErrors = np.concatenate((Errors))
    Fig, ax = plt.subplots()
    BinVal, _, _ = ax.hist(AllErrors, bins="sqrt", density=True, alpha=0.75, histtype='bar', ec='black', zorder=1)
    #ax = sns.histplot(AllErrors, bins="auto")
    print(f'Number of bins is {len(BinVal)}')
    PlotMean = AllErrors.mean()
    PlotStdDiv = AllErrors.std()
    #sns.histplot(AllErrors, bins="auto", ax=ax)
    #Frame = sns.displot(AllErrors, kde=True)
    #LimX = Frame.ax.get_xlim()
    LimX = ax.get_xlim()
    AxisX = np.linspace(LimX[0], LimX[1], 100)
    AxisY = stats.norm.pdf(AxisX, PlotMean, PlotStdDiv)
    #MaxBin = max(BinVal)
    #print(MaxBin)
    #MaxY = max(AxisY)
    #print(MaxY)
    #AxisY = AxisY*(MaxBin/MaxY)
    ax.plot(AxisX, AxisY, color="orange")
    #ax = sns.displot(AllErrors, bins="auto", kde=True)
    #Frame.ax.text(0, 1.03, f"Range {Range}   Size {Size}   Decimals {Decimals}   Reps {Reps}"
    #                       f"\nMean {Mean}  Correlation {Correlation}  {Func.__name__}", transform=Frame.ax.transAxes)

    ax.text(0, 1.03, f"Range {Range}   Size {Size}   Decimals {Decimals}   Reps {Reps} #Bins {len(BinVal)}"
                     f"\n          Mean {Mean}  Correlation {Correlation}  {Func.__name__}", transform=ax.transAxes)
    #if len(FileName) > 0:
    #    plt.savefig(f'Figures/CorrRoundError/{FileName}.png')
    #else:
    #    plt.savefig(f'Figures/CorrRoundError/Temp.png')
    #plt.title(f"Numpy Errors")
    #plt.show()
    return ReturnDict, ax
    #return ReturnDict, Frame.ax

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
    # Args(Reps, Range, Size, Decimals, Filename, Function, Mean(s), Correlation)
    Args = {"Reps": 100000, "Range": 0.1, "Size": 10000, "Filename": "Test4123",
            "FuncName": "DoubleNormal", "Mean": ((0.0, 0.6), (0.0, 0.6))}
    Res, ax = main(1000, 0.1, 10000, 3, "Test4123", Experiment.DoubleNormal, Mean=((0.0, 0.6), (0.0, 0.6)))
    #Res = main(1000, 1, 10000, 3, "Test21", Experiment.Uniform, Mean=0)
    #Res = main(100000, 1, 10000, 3, "Bivariate/Corr10", Experiment.Bivariate, Mean=(0,0), Correlation=1)
    #for i in range(11):
    #    Corr = 0.1*i
    #    main(100000, 1, 10000, 3, f"Bivariate/Corr{i}", Experiment.Bivariate, Mean=(0, 0), Correlation=Corr)
    #for i in range(10):
    #    Mean2 = 0.1*(i+1)
    #    Mean2 = np.round(Mean2, 1)
    #    Res = main(100000, 0.1, 10000, 3, f"DoubleNormal/2ndMeans2{i}", Experiment.DoubleNormal, Mean=((0, Mean2), (0, Mean2)))
    Finish = perf_counter()
    print(f'Time taken by entire process {Finish-Start}')
