import random
import pandas as pd

class Process:
    def __init__(self, ID, arrivalTime, burstTime, priority):
        self.ID = ID
        self.arrivalTime = arrivalTime
        self.burstTime = burstTime
        self.remainingTime = burstTime
        self.priority = priority

    def execute(self):
        executionTime = self.burstTime
        self.remainingTime = 0
        return executionTime

def min_prior(Processes=[], currentTime=0):
    min = 99999
    index = -1
    for i, process in enumerate(Processes):
        if process.remainingTime > 0:
            if process.arrivalTime <= currentTime and process.priority < min:
                min = process.priority
                index = i
    return index


def non_preemptiveP(Processes=[], MAX_PROCESS=0):
    currentTime = min(process.arrivalTime for process in Processes)
    MAX_TIME = currentTime + sum(process.burstTime for process in Processes)
    completionTimes = [0] * MAX_PROCESS
    turnaroundTimes = [0] * MAX_PROCESS
    waitingTimes = [0] * MAX_PROCESS

    while currentTime < MAX_TIME:
        index = min_prior(Processes, currentTime)
        if index == -1:
            currentTime += 1
            continue
        
        currentTime += Processes[index].execute()
        completionTimes[index] = currentTime
        turnaroundTimes[index] = currentTime - Processes[index].arrivalTime
        waitingTimes[index] = max(0, turnaroundTimes[index] - Processes[index].burstTime)
    
    startIndex = 1
    endIndex = MAX_PROCESS + 1
    indexes = [f"[P{i}]" for i in range(startIndex, endIndex)]
    result = {
        "Process": [],
        "Waiting Time": [],
        "Turnaround Time": []
    }
    result["Process"] = [process.ID for process in Processes]
    result["Waiting Time"] = waitingTimes
    result["Turnaround Time"] = turnaroundTimes

    df = pd.DataFrame(result, index=indexes)
    print(df)

    avgTAT = sum(time for time in turnaroundTimes) / MAX_PROCESS
    avgWT = sum(time for time in waitingTimes) / MAX_PROCESS
    print(f"Avg. T: {avgTAT}")
    print(f"Avg. WT: {avgWT}")
    


def main():
    Processes = list()
    with open("data.txt", "rt") as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')

            ID = random.randint(1, 1000)
            aT, bT, p = line.split(' ') # Process properties.

            Processes.append(Process(ID, int(aT), int(bT), int(p)))
        f.close()
    non_preemptiveP(Processes, len(Processes))

if __name__ == '__main__':
    try:
        main()
    except Exception as E:
        print(f"An error occured {E}")