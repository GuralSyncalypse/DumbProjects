import tkinter as tk
import tkinter as tk
import random as rd
from tkinter import messagebox

resource_types = ("A", "B", "C", "D", "E")
operation = ("Sample", "Find Available", "Find Need", "Find Safe Sequence", "Reset")
maxTable = {'max': 3, 'current': 0}
p_and_r = [f"{i}" for i in range(1, 6)]

def init_window(window, title, resolution, resizable=(True, True)):
    window.title(title)
    window.geometry(resolution)
    window.resizable(*resizable)

def init_window_grid(window, i_minsize, j_minsize, i=list(), j=list()):
    window.rowconfigure(index=i, minsize=i_minsize, weight=1)
    window.columnconfigure(index=j, minsize=j_minsize, weight=1)

def warning(title, message):
    messagebox.showwarning(title, message)

def confirm(title, message, icon):
    return messagebox.askyesno(title, message, icon=icon)

class Table:
    Instances = None
    Alloc = None 
    Max = None
    Need = None 
    Avail = None
    Result = None

    def __init__(self, window, MAX_PROCESS, MAX_RESOURCE):
        self.__window = tk.Toplevel(master=window)
        self.__top = tk.Frame(master=self.__window, bg="green", relief=tk.GROOVE, borderwidth=5)
        self.__bottom = tk.Frame(master=self.__window, bg="blue", relief=tk.SUNKEN)

        self.__processes = MAX_PROCESS
        self.__resources = MAX_RESOURCE
        self.__indexes = [[i for i in range(0, self.__processes + 2)], [i for i in range(0, self.__resources + 1)]]
        self.__Render()

    def __Onclose(self):
        maxTable["current"] -= 1
        self.__window.destroy()

    def __Render(self):
        init_window(self.__window, f"Table {self.__processes} x {self.__resources}", "1280x480")

        # Render Top.
        self.__RenderTop()                                                                          

        # Allocation - Need - Max matrix.
        init_window_grid(self.__bottom, 25, 100, [0, 1], [0, 1, 2, 3])
        self.Alloc = self.__ResourceGraph("Allocation", [0, 0])
        self.Max = self.__ResourceGraph("Max", [0, 1])
        self.Need = self.__ResourceGraph("Need", [0, 2])
        self.Avail = self.__AvailableResource()

        # Safe sequences.
        result_frame = tk.Frame(master=self.__bottom)
        result_labels = [] 
        for i in range(0, self.__processes):
            lbl = tk.Label(master=result_frame, bg="pink", text="X")
            lbl.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
            result_labels.append(lbl)
        self.Result = result_labels
        result_frame.grid(row=1, column=3, sticky="NSEW")

        # Grid main frames.
        self.__top.pack(side=tk.TOP)
        self.__bottom.pack(fill=tk.BOTH, side=tk.TOP, expand=True, anchor="w")

        self.__window.protocol('WM_DELETE_WINDOW', self.__Onclose)

    def __Sample(self):
        self.__Reset()
        rng = lambda start, end: rd.randrange(start, end + 1)
        prev_alloc = [0] * self.__resources
        total_avail = []

        for resource in range(0, self.__resources):
            value = rng(5, 21)
            self.Instances[resource].set(str(value))
            total_avail.append(value)

        for process in range(0, self.__processes):
            for resource in range(0, self.__resources):
                total_instance = total_avail[resource] - prev_alloc[resource]
                value = rng(0, total_instance)

                self.Alloc[process][resource].set(str(value))
                prev_alloc[resource] = int(self.Alloc[process][resource].get())
                total_avail[resource] = total_instance

                start = int(self.Alloc[process][resource].get())
                value = rng(0, total_avail[resource])
                self.Max[process][resource].set(str(value))

    def __FindNeed(self):
        try:
            for i in range(0, self.__processes):
                for j in range(0, self.__resources):
                    val_1 = int(self.Max[i][j].get())
                    val_2 = int(self.Alloc[i][j].get())
                    result = val_1 - val_2
                    self.Need[i][j].set(str(result))
        except Exception as e:
            message = str(e) + ", reset?"
            if confirm("__FindNeed", message, 'error'):
                self.__Reset()

    def __FindAvailable(self):
        try:
            for i in range(0, self.__resources):
                inst = int(self.Instances[i].get())
                if inst < 0:
                    inst = abs(inst)
                    self.Instances[i].set(str(inst))
                
                sum_alloc = 0
                for j in range(0, self.__processes):
                    sum_alloc += int(self.Alloc[j][i].get())
                result = inst - sum_alloc
                self.Avail[i].set(str(result))
        except Exception as e:
            message = str(e) + ", reset?"
            if confirm("__FindAvailable", message, 'error'):
                self.__Reset()

    def __FindSafeSequence(self):
        self.__FindNeed()
        self.__FindAvailable()

        sequence = []
        finish = [False] * self.__processes

        for _ in range(0, 5):
            for process in range(0, self.__processes):
                if not finish[process]:
                    # Assumption.
                    finished = True

                    for resource in range(0, self.__resources):
                        exceeded = lambda i, j: int(self.Need[i][j].get()) > int(self.Avail[j].get())
                        if exceeded(process, resource):
                            finished = False
                            break
                    
                    if finished:
                        sequence.append(process)

                        for resource in range(0, self.__resources):
                            new_avail = int(self.Avail[resource].get()) + int(self.Alloc[process][resource].get())
                            if new_avail <= int(self.Instances[resource].get()):
                                self.Avail[resource].set(new_avail)

                        finish[process] = True

        if False in finish:
            warning("Unsafe", "Deadlock detected!")
        else:
            for i in range(0, self.__processes):
                self.Result[i].config(text=str(sequence[i]))

    def __Request(self, process, req_list):
        try:
            # Step 1: Ensure that req <= Need[i]
            for resource in range(0, self.__resources):
                if int(req_list[resource].get()) > int(self.Need[process][resource].get()):
                    warning("Unsafe Request", f"P{process}'s request has exceeded its NEED!")
                    return
            
            # Step 2: Ensure that req <= Avail
            for resource in range(0, self.__resources):
                if int(req_list[resource].get()) > int(self.Avail[resource].get()):
                    warning("Unsafe Request", f"Insufficient system resources!")
                    return
            
            for resource in range(0, self.__resources):
                req_i = int(req_list[resource].get())
                self.Avail[resource].set(f"{int(self.Avail[resource].get()) - req_i}")
                self.Alloc[process][resource].set(f"{int(self.Alloc[process][resource].get()) + req_i}")
                self.Need[process][resource].set(f"{int(self.Need[process][resource].get()) - req_i}")
        except Exception as e:
            message = str(e) + ", reset?"
            if confirm("__Request", message, 'error'):
                for req in req_list:
                    req.set("0")

    def __RequestWindow(self):
        # Create sub-window.
        sub_win = tk.Toplevel(master=self.__window)
        init_window(sub_win, "Input Request List", "320x320", (False, False))
        init_window_grid(sub_win, 25, 100, [i for i in range(0, self.__resources)], [0, 1, 2])

        # Request list.
        req_list = [tk.IntVar() for _ in range(0, self.__resources)]
        req_labels = [
            tk.Label(
                master=sub_win,
                text=resource_types[i],
                relief=tk.GROOVE,
                borderwidth=3
            ).grid(row=i, column=0, sticky="NSEW") for i in range(0, self.__resources)
        ]
        req_entries = [
            tk.Entry(
                master=sub_win, 
                textvariable=req_list[i],
                justify="center",
                relief=tk.SUNKEN,
                borderwidth=3
            ).grid(row=i, column=1, sticky="NSEW") for i in range(0, self.__resources)
        ]

        # Process to perform a request.
        option_frame = tk.Frame(master=sub_win)
        init_window_grid(option_frame, 25, 100, [0, 1], [0])

        p_var = tk.StringVar()
        p_var.set("P0")
        dropbox = tk.OptionMenu(option_frame, p_var, *[f"P{i}" for i in range(0, self.__processes)]).grid(row=0, column=0)

        btn = tk.Button(master=option_frame, text="REQUEST", relief=tk.RAISED, command=lambda:self.__Request(int(p_var.get()[1:]), req_list))
        btn.grid(row=1, column=0)

        option_frame.grid(row=0, rowspan=self.__resources, column=2, sticky="NSEW")

    def __Reset(self):
        for resource in range(0, self.__resources):
            self.Instances[resource].set("0")
            self.Avail[resource].set("0")

        for process in range(0, self.__processes):
            for resource in range(0, self.__resources):
                self.Alloc[process][resource].set("0")
                self.Max[process][resource].set("0")
                self.Need[process][resource].set("0")

    def __RenderTop(self):
        init_window_grid(self.__top, 25, 100, [0, 1], self.__indexes[1])

        # Resource entries.
        self.Instances = [tk.IntVar() for i in range(0, self.__resources)]
        for i in range(0, self.__resources):
            lbl = tk.Label(master=self.__top, width=5, bg="green", text=resource_types[i])
            lbl.grid(row=0, column=i, sticky="NSEW")
            entry = tk.Entry(master=self.__top, width=7, textvariable=self.Instances[i], justify="center")
            entry.grid(row=1, column=i, sticky="NSEW")

        # Operation Frame setup.
        op_frame = tk.Frame(master=self.__top, bg="black", relief=tk.SUNKEN, borderwidth=2)
        btn_1 = tk.Button(master=op_frame, text="Sample", relief=tk.RAISED, command=self.__Sample).pack(side=tk.LEFT, padx=10)
        btn_2 = tk.Button(master=op_frame, text="Find Available", relief=tk.RAISED, command=self.__FindAvailable).pack(side=tk.LEFT, padx=10)
        btn_3 = tk.Button(master=op_frame, text="Find Need", relief=tk.RAISED, command=self.__FindNeed).pack(side=tk.LEFT, padx=10)
        btn_4 = tk.Button(master=op_frame, text="Find Safe Sequence", relief=tk.RAISED, command=self.__FindSafeSequence).pack(side=tk.LEFT, padx=10)
        btn_5 = tk.Button(master=op_frame, text="Request", relief=tk.RAISED, command=self.__RequestWindow).pack(side=tk.LEFT, padx=10)
        btn_6 = tk.Button(master=op_frame, text="Reset", relief=tk.RAISED, command=self.__Reset).pack(side=tk.LEFT, padx=10)
        op_frame.grid(row=0, rowspan=2, column=self.__resources, stick="NSEW")

    def __ResourceGraph(self, name, cell):
        entries = []
        frame = tk.Frame(master=self.__bottom, relief=tk.RAISED, borderwidth=5)
        init_window_grid(frame, 10, 10, self.__indexes[0], self.__indexes[1])

        frame_title = tk.Label(master=frame, text=name, justify="center", relief=tk.GROOVE, borderwidth=3)
        frame_title.grid(row=0, column=0, columnspan=self.__resources + 1, sticky="NSEW")

        for r in range(1, self.__resources + 1):
            lbl = tk.Label(
                master=frame, 
                width=3, 
                text=resource_types[r - 1], 
                relief=tk.GROOVE
            )
            lbl.grid(row=1, column=r, sticky="NSEW")

        for i in range(2, self.__processes + 2):
            arr = []
            for j in range(1, self.__resources + 1):
                entry = tk.IntVar()
                ent = tk.Entry(
                    master=frame,
                    textvariable=entry, 
                    width=3,
                    justify="center",
                    relief=tk.SUNKEN,
                    borderwidth=2
                )
                arr.append(entry)
                ent.grid(row=i, column=j, sticky="NSEW")
            lbl = tk.Label(master=frame, text=f"P{i - 2}", relief=tk.GROOVE)
            lbl.grid(row=i, column=0, sticky="NSEW")
            entries.append(arr)
        
        frame.grid(row=cell[0], rowspan=2, column=cell[1], sticky="NSEW")
        return entries

    def __AvailableResource(self):
        entries = []
        frame = tk.Frame(master=self.__bottom, relief=tk.RAISED, borderwidth=5)
        init_window_grid(frame, 10, 10, [0, 1, 2], self.__indexes[1])

        frame_title = tk.Label(master=frame, text="Available", justify="center", relief=tk.GROOVE, borderwidth=3)
        frame_title.grid(row=0, column=0, columnspan=self.__resources + 1, sticky="NSEW")

        for r in range(1, self.__resources + 1):
            lbl = tk.Label(
                master=frame, 
                width=3, 
                text=resource_types[r - 1], 
                relief=tk.GROOVE
            )
            lbl.grid(row=1, column=r, sticky="NSEW")

        for j in range(1, self.__resources + 1):
            entry = tk.IntVar()
            ent = tk.Entry(
                master=frame, 
                width=3,
                textvariable=entry,
                justify="center",
                relief=tk.SUNKEN,
                borderwidth=2
            )
            ent.grid(row=2, column=j, sticky="NSEW")
            entries.append(entry)
        lbl = tk.Label(master=frame, width=2, text=f"I", relief=tk.GROOVE)
        lbl.grid(row=2, column=0, sticky="NSEW")

        frame.grid(row=0, column=3, sticky="NSEW")
        return entries

def start(window, process, resource):
    if maxTable["current"] >= maxTable["max"]:
        return
    Table(window, process, resource)
    maxTable["current"] += 1 

# Main section.
def main():
    window = tk.Tk()
    init_window(window, "Main", "320x200", (False, False))
    init_window_grid(window, 25, 100, [0, 1, 2], [0, 1, 2])

    # Variables.
    processVar = tk.StringVar()
    resourceVar = tk.StringVar()
    processVar.set("5")
    resourceVar.set("5")

    p_lbl = tk.Label(master=window, text="No. Processes").grid(row=0, column=0)
    r_lbl = tk.Label(master=window, text="No. Resources").grid(row=0, column=1)

    p_dropbox = tk.OptionMenu(window, processVar, *p_and_r).grid(row=1, column=0)
    r_dropbox = tk.OptionMenu(window, resourceVar, *p_and_r).grid(row=1, column=1)


    start_btn = tk.Button(master=window, text="START", relief=tk.RAISED, command=lambda : start(window, int(processVar.get()), int(resourceVar.get())))
    start_btn.grid(row=0, rowspan=2, column=2)

    # End section.
    window.mainloop()

if "__main__" == __name__:
    try:
        main()
    except Exception as e:
        print("Error: " + Exception)