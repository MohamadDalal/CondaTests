from CorrRoundingError2 import *

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
    ax = sns.histplot(AllErrors, bins="auto")
    ax.text(0, 1.03, f"Range {Range}   Size {Size}   Decimals {Decimals}   Reps {Reps}", transform=ax.transAxes)
    if len(FileName) > 0:
        plt.savefig(f'Figures/CorrRoundError/{FileName}.png')
    else:
        plt.savefig(f'Figures/CorrRoundError/Temp.png')
    #plt.title(f"Numpy Errors")
    plt.show()
    return ReturnDict

if __name__ == "__main__":
    Start = perf_counter()
    # Args(Reps, Range, Size, Decimals)
    Res = main(1000, 1, 10000, 3, "Test21", Experiment.Bivariate, Mean=(0,0), Correlation=0.5)
    Finish = perf_counter()
    print(f'Time taken by entire process {Finish-Start}')
