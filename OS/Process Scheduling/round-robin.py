import random
import os
import pandas as pd
from enum import Enum
import matplotlib.pyplot as plt

TIME_QUANTUM = 2

class PState(Enum):
	WAITING = 0
	READY = 1
	TERMINATED = 2

class Process:
	def __init__(self, ID=0, arrivalTime=0, burstTime=0, executeTime=0, state=PState.READY):
		self.ID = ID
		self.arrivalTime = arrivalTime
		self.burstTime = burstTime
		self.remainingTime = burstTime
		self.executeTime = executeTime
		self.state = state
    
	def info(self):
		print(f"ID: {self.ID}")
		print(f"Arrival Time: {self.arrivalTime}ms")
		print(f"Burst Time: {self.burstTime}ms")
		print(f"State: {self.state}")
	
	def run(self) -> int():
		executionTime = 0
		print(f"[Run process {self.ID}]", end='')
		if(self.remainingTime <= TIME_QUANTUM):
			executionTime = self.remainingTime
			self.remainingTime = 0
			self.state = PState.TERMINATED
			print(f"-> End", end='')
		else:
			self.remainingTime -= TIME_QUANTUM
			executionTime = TIME_QUANTUM
		print()
		return executionTime

def createProcess() -> list():
	Processes = list()
	MAX_PROCESS = int(input("Enter the number of Processes> "))

	for i in range(0, MAX_PROCESS):
		ID = random.randint(0, 10000)
		print(f"[{ID}]")

		arrivalTime = int(input("Arrival Time: "))
		burstTime = int(input("Burst Time: "))
		Processes.append(Process(ID, arrivalTime, burstTime, 0, PState.READY))

		os.system("cls")

	return Processes

def showProcess(Processes=[]) -> None:
	startIndex = 1
	endIndex = len(Processes) + 1
	indexes = [f"[P{i}]" for i in range(startIndex, endIndex)]
	data = {
		"Process ID": [],
		"Arrival Time": [],
		"Burst Time": [],
		"State": []
	}

	for process in Processes:
		data["Process ID"].append(process.ID)
		data["Arrival Time"].append(process.arrivalTime)
		data["Burst Time"].append(process.burstTime)
		data["State"].append(process.state)
	
	df = pd.DataFrame(data, index=indexes)
	print(df)

def showResult(Processes=[], waitingTimes=[], turnAroundTimes=[]) -> None:
	startIndex = 1
	endIndex = len(Processes) + 1
	indexes = [f"[P{i}]" for i in range(startIndex, endIndex)]
	result = {
		"Process": [],
		"Waiting Time": [],
		"Turnaround Time": []
	}
	result["Process"] = [process.ID for process in Processes]
	result["Waiting Time"] = waitingTimes
	result["Turnaround Time"] = turnAroundTimes

	df = pd.DataFrame(result, index=indexes)
	print(df)

def isAllTerminated(Processes=[]) -> bool():
	for process in Processes:
		if process.state != PState.TERMINATED:
			return False
	return True

def RR(Processes=[]):
	MAX_TIME = sum(process.burstTime for process in Processes)
	MAX_PROCESS = len(Processes)
	readyQueue = []
	waitQueue = []
	runTimes = {i: [] for i in range(MAX_PROCESS)}
	index = 0
	init = [False] * MAX_PROCESS
	waitingTimes = [0] * MAX_PROCESS
	completionTime = [0] * MAX_PROCESS
	turnAroundTimes = [0] * MAX_PROCESS

	currentTime = min(Process.arrivalTime for Process in Processes)

	while not isAllTerminated(Processes):
		for i in range(0, MAX_PROCESS):
			if Processes[i].arrivalTime <= currentTime and init[i] == False:
				readyQueue.append(Processes[i])
				init[i] = True

		while Processes[index].state == PState.TERMINATED:
			index = (index + 1) % MAX_PROCESS
		
		if waitQueue:
			is_waitingP = waitQueue.pop(0)
			is_waitingP.state = PState.WAITING
			readyQueue.append(is_waitingP)
		
		if readyQueue:
			to_run = readyQueue.pop(0)
			exec_time = to_run.run()
			while to_run.ID != Processes[index].ID:
				index = (index + 1) % MAX_PROCESS
			Processes[index] = to_run
			runTimes[index].append([currentTime, exec_time])
			Processes[index].executeTime += 1
			currentTime += exec_time

		if Processes[index].state == PState.TERMINATED:
			completionTime[index] = currentTime
			turnAroundTimes[index] = currentTime - Processes[index].arrivalTime
			waitingTimes[index] = turnAroundTimes[index] - Processes[index].burstTime
			if waitingTimes[index] < 0:
				waitingTimes[index] = 0
		else:
			Processes[index].state = PState.WAITING
			waitQueue.append(Processes[index])
		index = (index + 1) % MAX_PROCESS

	showResult(Processes, waitingTimes, turnAroundTimes)
	makeGChart(runTimes, MAX_TIME, MAX_PROCESS)


def makeGChart(runTimes=dict(), MAX_TIME=0, MAX_PROCESS=0) -> None:
	if not runTimes or MAX_TIME == 0 or MAX_PROCESS == 0:
		print("Please check your given arguments' validity, given arguments: ")
		print(f"[runTimes dict: {runTimes}]")
		print(f"[MAX_TIME: {MAX_TIME}]")
		print(f"[MAX_PROCESS: {MAX_PROCESS}]")
		return

	# Create a figure and subplot
	ax = plt.subplot()
    
	# Set the y-axis limits based on the number of processes
	y_limit = 4 * (MAX_PROCESS + 1)
	ax.set_ylim(0, y_limit)
    
	# Set the x-axis limit based on the maximum finish time
	x_limit = MAX_TIME
	ax.set_xlim(0, x_limit)
    
	# Set axis labels
	ax.set_xlabel('Time')
	ax.set_ylabel('Process')
    
	# Setting y-axis ticks and labels
	y_ticks = [i for i in range(4, y_limit, 4)]
	y_labels = [str(i) for i in range(1, MAX_PROCESS + 1)]
	ax.set_yticks(y_ticks)
	ax.set_yticklabels(y_labels)
    
	# Add a grid
	ax.grid(True)

	# Plot the Gantt chart
	height = 2
	for key, value in runTimes.items():
		position = (key + 1) * 3 + key
		for i in value:
			ax.broken_barh([tuple(i)], (position, height), facecolors=('tab:orange'))
    
	plt.savefig("result.png")


def main():
	Processes = createProcess()
	showProcess(Processes)
	RR(Processes)

if __name__ == '__main__':
	main()
	