import random
import os
import pandas as pd
import matplotlib.pyplot as plt

class Process:
	def __init__(self, ID=0, arrivalTime=0, burstTime=0, executeTime=0):
		self.ID = ID
		self.arrivalTime = arrivalTime
		self.burstTime = burstTime
		self.remainingTime = burstTime
		self.executeTime = executeTime
    
	def info(self):
		print(f"ID: {self.ID}")
		print(f"Arrival Time: {self.arrivalTime}ms")
		print(f"Burst Time: {self.burstTime}ms")
	
	def run(self) -> int():
		self.remainingTime -= 1
		return 1

def createProcess() -> list():
	Processes = list()
	MAX_PROCESS = int(input("Enter the number of Processes> "))

	for i in range(0, MAX_PROCESS):
		ID = random.randint(0, 10000)
		print(f"[{ID}]")

		arrivalTime = int(input("Arrival Time: "))
		burstTime = int(input("Burst Time: "))
		Processes.append(Process(ID, arrivalTime, burstTime))

		os.system("cls")

	return Processes

def showProcess(Processes) -> None:
	startIndex = 1
	endIndex = len(Processes) + 1
	indexes = [f"[P{i}]" for i in range(startIndex, endIndex)]
	data = {
		"Process ID": [],
		"Arrival Time": [],
		"Burst Time": []
	}

	for process in Processes:
		data["Process ID"].append(process.ID)
		data["Arrival Time"].append(process.arrivalTime)
		data["Burst Time"].append(process.burstTime)
	
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

def shortestRemainingTime(Processes=[], currentTime=0) -> int():
	minBurstTime = float('inf')
	shortestJob = -1
	for index, process in enumerate(Processes):
		if process.arrivalTime <= currentTime and process.remainingTime < minBurstTime and process.remainingTime > 0:
			minBurstTime = process.remainingTime
			shortestJob = index
	return shortestJob

def SRTF(Processes=[]):
	MAX_TIME = sum(process.burstTime for process in Processes)
	MAX_PROCESS = len(Processes)
	runTimes = {i: [] for i in range(MAX_PROCESS)}
	waitingTimes = [0] * MAX_PROCESS
	turnAroundTimes = [0] * MAX_PROCESS

	totalRemainingTime = MAX_TIME
	currentTime = 0

	prevIndex = -1
	while totalRemainingTime > 0:
		# Search for the job that has the smallest remaining time.
		index = shortestRemainingTime(Processes, currentTime)
		if index == -1:
			currentTime += 1
			continue
		
		# Run process.
		executionTime = Processes[index].run()

		# Update Gantchart runtimes.
		if prevIndex != index:
			runTimes[index].append([currentTime, executionTime])
			Processes[index].executeTime += 1
		else:
			runTimes[index][Processes[index].executeTime - 1][1] += executionTime
		
		currentTime += 1
		prevIndex = index

		# Finished execution.
		if Processes[index].remainingTime == 0:
			totalRemainingTime -= Processes[index].burstTime
			pwTime = currentTime - Processes[index].arrivalTime
			turnAroundTimes[index] = pwTime
			waitingTimes[index] = max(0, pwTime - Processes[index].burstTime)

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
	SRTF(Processes)

if __name__ == '__main__':
	main()
	