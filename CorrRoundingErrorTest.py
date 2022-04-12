from CorrRoundingError2 import *

def main(Reps, Range, Size, Decimals):
    RepsPerCore = Reps//CoresNo
    print(f'Number of cores {CoresNo}')
    print(f'Repititions per core {RepsPerCore}')
    Processes = []
    Manager = mp.Manager()
    ReturnDict = Manager.dict()
    Time1 = perf_counter()
    for i in range(CoresNo):
        P = mp.Process(target=ParallelRun, args=(ReturnDict, i, RepsPerCore, Range, Size, Decimals,))         # Map function to process
        Processes.append(P)                                                                       # Append process to list
        Processes[-1].start()                                                                           # Start the newly appended process
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
    Errors = [i for i in ReturnDict.values()]
    AllErrors = np.concatenate((Errors))
    sns.histplot(AllErrors, bins="auto")
    plt.title(f"Numpy Errors")
    plt.show()

if __name__ == "__main__":
    Start = perf_counter()
    main(100000, 1, 1000, 3)
    Finish = perf_counter()
    print(f'Time taken by entire process {Finish-Start}')
