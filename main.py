import tkinter as tk
from tkinter import ttk, messagebox
from scheduling import fcfs, sjf, round_robin


# ============================================================
# CPU SCHEDULING ALGORITHMS
# ============================================================

def fcfs(processes):
    processes = sorted(processes, key=lambda x: (x["arrival"], x["pid"]))

    time = 0
    results = []
    gantt = []

    for p in processes:

        if time < p["arrival"]:
            gantt.append(("IDLE", time, p["arrival"]))
            time = p["arrival"]

        start = time
        time += p["burst"]

        results.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "completion": time,
            "turnaround": time - p["arrival"],
            "waiting": time - p["arrival"] - p["burst"],
            "response": start - p["arrival"]
        })

        gantt.append((p["pid"], start, time))

    return results, gantt


def sjf(processes):

    processes = [p.copy() for p in processes]

    time = 0
    completed = 0
    n = len(processes)

    results = []
    gantt = []
    done = set()

    while completed < n:

        available = [
            p for p in processes
            if p["arrival"] <= time and p["pid"] not in done
        ]

        if not available:

            remaining = [
                p for p in processes
                if p["pid"] not in done
            ]

            next_process = min(
                remaining,
                key=lambda x: x["arrival"]
            )

            if time < next_process["arrival"]:

                gantt.append(
                    ("IDLE", time, next_process["arrival"])
                )

                time = next_process["arrival"]

            continue

        p = min(
            available,
            key=lambda x: (
                x["burst"],
                x["arrival"],
                x["pid"]
            )
        )

        start = time

        time += p["burst"]

        results.append({
            "pid": p["pid"],
            "arrival": p["arrival"],
            "burst": p["burst"],
            "completion": time,
            "turnaround": time - p["arrival"],
            "waiting": time - p["arrival"] - p["burst"],
            "response": start - p["arrival"]
        })

        gantt.append(
            (p["pid"], start, time)
        )

        done.add(p["pid"])
        completed += 1

    return results, gantt


def round_robin(processes, quantum):

    processes = sorted(
        [p.copy() for p in processes],
        key=lambda x: (x["arrival"], x["pid"])
    )

    n = len(processes)

    remaining = {
        p["pid"]: p["burst"]
        for p in processes
    }

    first_start = {
        p["pid"]: None
        for p in processes
    }

    completion = {}

    ready_queue = []

    time = 0
    index = 0

    gantt = []

    while len(completion) < n:

        while (
            index < n
            and processes[index]["arrival"] <= time
        ):

            ready_queue.append(
                processes[index]
            )

            index += 1

        if not ready_queue:

            if index < n:

                next_arrival = processes[index]["arrival"]

                gantt.append(
                    ("IDLE", time, next_arrival)
                )

                time = next_arrival

                continue

        p = ready_queue.pop(0)

        pid = p["pid"]

        if first_start[pid] is None:
            first_start[pid] = time

        run_time = min(
            quantum,
            remaining[pid]
        )

        start = time

        time += run_time

        remaining[pid] -= run_time

        gantt.append(
            (pid, start, time)
        )

        while (
            index < n
            and processes[index]["arrival"] <= time
        ):

            ready_queue.append(
                processes[index]
            )

            index += 1

        if remaining[pid] == 0:

            completion[pid] = time

        else:

            ready_queue.append(p)

    results = []

    for p in processes:

        pid = p["pid"]

        ct = completion[pid]

        tat = ct - p["arrival"]

        wt = tat - p["burst"]

        rt = first_start[pid] - p["arrival"]

        results.append({
            "pid": pid,
            "arrival": p["arrival"],
            "burst": p["burst"],
            "completion": ct,
            "turnaround": tat,
            "waiting": wt,
            "response": rt
        })

    return results, gantt


# ============================================================
# GUI APPLICATION
# ============================================================

class CPUSchedulerApp:

    def __init__(self, root):

        self.root = root

        root.title(
            "CPU Scheduling Simulator"
        )

        root.geometry(
            "1150x750"
        )

        root.configure(
            bg="#f2f2f2"
        )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = tk.Label(
            root,
            text="CPU SCHEDULING SIMULATOR",
            font=("Arial", 24, "bold"),
            bg="#f2f2f2"
        )

        title.pack(pady=(15, 3))

        subtitle = tk.Label(
            root,
            text="FCFS • SJF • Round Robin",
            font=("Arial", 11),
            bg="#f2f2f2"
        )

        subtitle.pack(
            pady=(0, 15)
        )

        # ----------------------------------------------------
        # INPUT FRAME
        # ----------------------------------------------------

        input_frame = tk.LabelFrame(
            root,
            text=" Add Process ",
            font=("Arial", 11, "bold"),
            bg="#f2f2f2",
            padx=10,
            pady=10
        )

        input_frame.pack(
            fill="x",
            padx=25
        )

        tk.Label(
            input_frame,
            text="Process ID",
            bg="#f2f2f2"
        ).grid(row=0, column=0, padx=10)

        tk.Label(
            input_frame,
            text="Arrival Time",
            bg="#f2f2f2"
        ).grid(row=0, column=1, padx=10)

        tk.Label(
            input_frame,
            text="Burst Time",
            bg="#f2f2f2"
        ).grid(row=0, column=2, padx=10)

        self.pid_entry = tk.Entry(
            input_frame,
            width=15
        )

        self.pid_entry.grid(
            row=1,
            column=0,
            padx=10,
            pady=5
        )

        self.arrival_entry = tk.Entry(
            input_frame,
            width=15
        )

        self.arrival_entry.grid(
            row=1,
            column=1,
            padx=10
        )

        self.burst_entry = tk.Entry(
            input_frame,
            width=15
        )

        self.burst_entry.grid(
            row=1,
            column=2,
            padx=10
        )

        tk.Button(
            input_frame,
            text="Add Process",
            command=self.add_process,
            width=15
        ).grid(
            row=1,
            column=3,
            padx=10
        )

        tk.Button(
            input_frame,
            text="Remove Selected",
            command=self.remove_process,
            width=15
        ).grid(
            row=1,
            column=4,
            padx=10
        )

        # ----------------------------------------------------
        # PROCESS TABLE
        # ----------------------------------------------------

        table_frame = tk.Frame(
            root,
            bg="#f2f2f2"
        )

        table_frame.pack(
            pady=10
        )

        self.process_table = ttk.Treeview(
            table_frame,
            columns=(
                "PID",
                "Arrival",
                "Burst"
            ),
            show="headings",
            height=5
        )

        self.process_table.heading(
            "PID",
            text="Process"
        )

        self.process_table.heading(
            "Arrival",
            text="Arrival Time"
        )

        self.process_table.heading(
            "Burst",
            text="Burst Time"
        )

        self.process_table.column(
            "PID",
            width=150
        )

        self.process_table.column(
            "Arrival",
            width=180
        )

        self.process_table.column(
            "Burst",
            width=180
        )

        self.process_table.pack()

        # ----------------------------------------------------
        # CONTROL FRAME
        # ----------------------------------------------------

        control = tk.LabelFrame(
            root,
            text=" Scheduling ",
            font=("Arial", 11, "bold"),
            bg="#f2f2f2",
            padx=10,
            pady=10
        )

        control.pack(
            fill="x",
            padx=25,
            pady=5
        )

        tk.Label(
            control,
            text="Algorithm:",
            bg="#f2f2f2"
        ).grid(
            row=0,
            column=0,
            padx=10
        )

        self.algorithm = ttk.Combobox(
            control,
            values=[
                "FCFS",
                "SJF",
                "Round Robin"
            ],
            state="readonly",
            width=18
        )

        self.algorithm.set("FCFS")

        self.algorithm.grid(
            row=0,
            column=1,
            padx=10
        )

        tk.Label(
            control,
            text="Time Quantum:",
            bg="#f2f2f2"
        ).grid(
            row=0,
            column=2
        )

        self.quantum_entry = tk.Entry(
            control,
            width=10
        )

        self.quantum_entry.insert(
            0,
            "2"
        )

        self.quantum_entry.grid(
            row=0,
            column=3,
            padx=10
        )

        tk.Button(
            control,
            text="RUN SIMULATION",
            command=self.run_simulation,
            width=20,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=4,
            padx=20
        )

        tk.Button(
            control,
            text="COMPARE",
            command=self.compare_algorithms,
            width=15
        ).grid(
            row=0,
            column=5,
            padx=5
        )

        tk.Button(
            control,
            text="CLEAR ALL",
            command=self.clear_all,
            width=15
        ).grid(
            row=0,
            column=6,
            padx=5
        )

        # ----------------------------------------------------
        # GANTT CHART
        # ----------------------------------------------------

        tk.Label(
            root,
            text="Gantt Chart",
            font=("Arial", 14, "bold"),
            bg="#f2f2f2"
        ).pack(
            pady=(10, 5)
        )

        self.gantt_frame = tk.Frame(
            root,
            bg="#f2f2f2"
        )

        self.gantt_frame.pack()

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        tk.Label(
            root,
            text="Scheduling Results",
            font=("Arial", 14, "bold"),
            bg="#f2f2f2"
        ).pack(
            pady=(10, 5)
        )

        result_frame = tk.Frame(
            root
        )

        result_frame.pack()

        self.result_table = ttk.Treeview(
            result_frame,
            columns=(
                "PID",
                "AT",
                "BT",
                "CT",
                "TAT",
                "WT",
                "RT"
            ),
            show="headings",
            height=5
        )

        headings = {
            "PID": "Process",
            "AT": "Arrival",
            "BT": "Burst",
            "CT": "Completion",
            "TAT": "Turnaround",
            "WT": "Waiting",
            "RT": "Response"
        }

        for column, heading in headings.items():

            self.result_table.heading(
                column,
                text=heading
            )

            self.result_table.column(
                column,
                width=110
            )

        self.result_table.pack()

        self.average_label = tk.Label(
            root,
            text="",
            font=("Arial", 11, "bold"),
            bg="#f2f2f2"
        )

        self.average_label.pack(
            pady=10
        )

    # ========================================================
    # ADD PROCESS
    # ========================================================

    def add_process(self):

        pid = self.pid_entry.get().strip()
        arrival = self.arrival_entry.get().strip()
        burst = self.burst_entry.get().strip()

        if not pid or not arrival or not burst:

            messagebox.showerror(
                "Input Error",
                "Please enter all values."
            )

            return

        try:

            arrival = int(arrival)
            burst = int(burst)

            if arrival < 0 or burst <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Input Error",
                "Arrival Time must be >= 0 and Burst Time must be > 0."
            )

            return

        for item in self.process_table.get_children():

            values = self.process_table.item(
                item
            )["values"]

            if values[0] == pid:

                messagebox.showerror(
                    "Input Error",
                    "Process ID already exists."
                )

                return

        self.process_table.insert(
            "",
            "end",
            values=(
                pid,
                arrival,
                burst
            )
        )

        self.pid_entry.delete(
            0,
            tk.END
        )

        self.arrival_entry.delete(
            0,
            tk.END
        )

        self.burst_entry.delete(
            0,
            tk.END
        )

    # ========================================================
    # REMOVE PROCESS
    # ========================================================

    def remove_process(self):

        selected = self.process_table.selection()

        for item in selected:

            self.process_table.delete(
                item
            )

    # ========================================================
    # GET PROCESSES
    # ========================================================

    def get_processes(self):

        processes = []

        for item in self.process_table.get_children():

            values = self.process_table.item(
                item
            )["values"]

            processes.append({
                "pid": str(values[0]),
                "arrival": int(values[1]),
                "burst": int(values[2])
            })

        return processes

    # ========================================================
    # RUN SIMULATION
    # ========================================================

    def run_simulation(self):

        processes = self.get_processes()

        if not processes:

            messagebox.showerror(
                "Error",
                "Add at least one process."
            )

            return

        algorithm = self.algorithm.get()

        if algorithm == "FCFS":

            results, gantt = fcfs(
                processes
            )

        elif algorithm == "SJF":

            results, gantt = sjf(
                processes
            )

        else:

            try:

                quantum = int(
                    self.quantum_entry.get()
                )

                if quantum <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter a valid Time Quantum."
                )

                return

            results, gantt = round_robin(
                processes,
                quantum
            )

        self.display_results(
            results,
            gantt
        )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    def display_results(
        self,
        results,
        gantt
    ):

        for item in self.result_table.get_children():

            self.result_table.delete(
                item
            )

        for r in sorted(
            results,
            key=lambda x: x["pid"]
        ):

            self.result_table.insert(
                "",
                "end",
                values=(
                    r["pid"],
                    r["arrival"],
                    r["burst"],
                    r["completion"],
                    r["turnaround"],
                    r["waiting"],
                    r["response"]
                )
            )

        n = len(results)

        avg_wt = sum(
            r["waiting"]
            for r in results
        ) / n

        avg_tat = sum(
            r["turnaround"]
            for r in results
        ) / n

        avg_rt = sum(
            r["response"]
            for r in results
        ) / n

        self.average_label.config(
            text=(
                f"Average Waiting Time: {avg_wt:.2f}"
                f"     |     "
                f"Average Turnaround Time: {avg_tat:.2f}"
                f"     |     "
                f"Average Response Time: {avg_rt:.2f}"
            )
        )

        self.display_gantt(
            gantt
        )

    # ========================================================
    # GANTT CHART
    # ========================================================

    def display_gantt(
        self,
        gantt
    ):

        for widget in self.gantt_frame.winfo_children():

            widget.destroy()

        chart = tk.Frame(
            self.gantt_frame
        )

        chart.pack()

        for pid, start, end in gantt:

            duration = end - start

            width = max(
                70,
                duration * 35
            )

            box = tk.Label(
                chart,
                text=pid,
                width=max(8, duration * 3),
                height=2,
                relief="solid",
                borderwidth=1,
                font=("Arial", 10, "bold")
            )

            box.pack(
                side=tk.LEFT
            )

        times = tk.Frame(
            self.gantt_frame
        )

        times.pack()

        for pid, start, end in gantt:

            tk.Label(
                times,
                text=str(start),
                width=10
            ).pack(
                side=tk.LEFT
            )

        if gantt:

            tk.Label(
                times,
                text=str(gantt[-1][2]),
                width=10
            ).pack(
                side=tk.LEFT
            )

    # ========================================================
    # COMPARE
    # ========================================================

    def compare_algorithms(self):

        processes = self.get_processes()

        if not processes:

            messagebox.showerror(
                "Error",
                "Add processes first."
            )

            return

        try:

            quantum = int(
                self.quantum_entry.get()
            )

            if quantum <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Error",
                "Enter a valid Time Quantum."
            )

            return

        algorithms = [
            (
                "FCFS",
                fcfs(processes)[0]
            ),
            (
                "SJF",
                sjf(processes)[0]
            ),
            (
                "Round Robin",
                round_robin(
                    processes,
                    quantum
                )[0]
            )
        ]

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Algorithm Comparison"
        )

        window.geometry(
            "750x400"
        )

        tk.Label(
            window,
            text="Algorithm Performance Comparison",
            font=("Arial", 17, "bold")
        ).pack(
            pady=15
        )

        table = ttk.Treeview(
            window,
            columns=(
                "Algorithm",
                "WT",
                "TAT",
                "RT"
            ),
            show="headings"
        )

        table.heading(
            "Algorithm",
            text="Algorithm"
        )

        table.heading(
            "WT",
            text="Avg Waiting Time"
        )

        table.heading(
            "TAT",
            text="Avg Turnaround Time"
        )

        table.heading(
            "RT",
            text="Avg Response Time"
        )

        table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        for name, results in algorithms:

            n = len(results)

            wt = sum(
                r["waiting"]
                for r in results
            ) / n

            tat = sum(
                r["turnaround"]
                for r in results
            ) / n

            rt = sum(
                r["response"]
                for r in results
            ) / n

            table.insert(
                "",
                "end",
                values=(
                    name,
                    f"{wt:.2f}",
                    f"{tat:.2f}",
                    f"{rt:.2f}"
                )
            )

    # ========================================================
    # CLEAR ALL
    # ========================================================

    def clear_all(self):

        for item in self.process_table.get_children():

            self.process_table.delete(
                item
            )

        for item in self.result_table.get_children():

            self.result_table.delete(
                item
            )

        for widget in self.gantt_frame.winfo_children():

            widget.destroy()

        self.average_label.config(
            text=""
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CPUSchedulerApp(
        root
    )

    root.mainloop()