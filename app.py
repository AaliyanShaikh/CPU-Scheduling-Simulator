import streamlit as st
from scheduling import fcfs, sjf, round_robin

st.set_page_config(
    page_title="CPU Scheduling Simulator",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ CPU Scheduling Simulator")
st.write("Simulate FCFS, SJF and Round Robin CPU scheduling algorithms.")

# -------------------------------
# Input
# -------------------------------

st.subheader("Process Input")

num_processes = st.number_input(
    "Number of Processes",
    min_value=1,
    max_value=20,
    value=4,
    step=1
)

processes = []

cols = st.columns(3)

with cols[0]:
    st.write("**Process ID**")

with cols[1]:
    st.write("**Arrival Time**")

with cols[2]:
    st.write("**Burst Time**")


for i in range(num_processes):

    cols = st.columns(3)

    with cols[0]:
        pid = st.text_input(
            f"PID {i+1}",
            value=f"P{i+1}",
            key=f"pid_{i}"
        )

    with cols[1]:
        arrival = st.number_input(
            f"Arrival {i+1}",
            min_value=0,
            value=i,
            step=1,
            key=f"arrival_{i}"
        )

    with cols[2]:
        burst = st.number_input(
            f"Burst {i+1}",
            min_value=1,
            value=5,
            step=1,
            key=f"burst_{i}"
        )

    processes.append({
        "pid": pid,
        "arrival": arrival,
        "burst": burst
    })


# -------------------------------
# Algorithm
# -------------------------------

st.subheader("Scheduling Algorithm")

algorithm = st.selectbox(
    "Select Algorithm",
    [
        "FCFS",
        "SJF",
        "Round Robin"
    ]
)

quantum = 2

if algorithm == "Round Robin":

    quantum = st.number_input(
        "Time Quantum",
        min_value=1,
        value=2,
        step=1
    )


# -------------------------------
# Run
# -------------------------------

if st.button(
    "▶ Run Simulation",
    type="primary"
):

    if algorithm == "FCFS":

        results, gantt = fcfs(processes)

    elif algorithm == "SJF":

        results, gantt = sjf(processes)

    else:

        results, gantt = round_robin(
            processes,
            quantum
        )

    # ---------------------------
    # Results
    # ---------------------------

    st.subheader("Gantt Chart")

    gantt_text = ""

    for pid, start, end in gantt:

        gantt_text += f"| {pid} "

    gantt_text += "|"

    st.code(gantt_text)

    times = ""

    for _, start, end in gantt:

        times += f"{start:<8}"

    if gantt:
        times += str(gantt[-1][2])

    st.code(times)

    # ---------------------------
    # Result table
    # ---------------------------

    st.subheader("Scheduling Results")

    table_data = []

    for r in results:

        table_data.append({
            "Process": r["pid"],
            "Arrival Time": r["arrival"],
            "Burst Time": r["burst"],
            "Completion Time": r["completion"],
            "Turnaround Time": r["turnaround"],
            "Waiting Time": r["waiting"],
            "Response Time": r["response"]
        })

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------
    # Averages
    # ---------------------------

    n = len(results)

    avg_wt = sum(
        r["waiting"] for r in results
    ) / n

    avg_tat = sum(
        r["turnaround"] for r in results
    ) / n

    avg_rt = sum(
        r["response"] for r in results
    ) / n

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Waiting Time",
        f"{avg_wt:.2f}"
    )

    col2.metric(
        "Average Turnaround Time",
        f"{avg_tat:.2f}"
    )

    col3.metric(
        "Average Response Time",
        f"{avg_rt:.2f}"
    )