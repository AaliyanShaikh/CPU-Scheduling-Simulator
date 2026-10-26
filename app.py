
import streamlit as st
import pandas as pd
import plotly.express as px

from scheduling import fcfs, sjf, round_robin


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="CPU Scheduling Simulator",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ CPU Scheduling Simulator")

st.write(
    "Simulate and compare FCFS, SJF, and Round Robin "
    "CPU scheduling algorithms."
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def run_algorithm(algorithm, processes, quantum):
    """Execute the selected scheduling algorithm."""

    # Pass copies so algorithms cannot accidentally
    # modify the original process data.
    process_copy = [p.copy() for p in processes]

    if algorithm == "FCFS":
        return fcfs(process_copy)

    elif algorithm == "SJF":
        return sjf(process_copy)

    else:
        return round_robin(process_copy, quantum)


def compare_algorithms(processes, quantum):
    """Run all algorithms and compare their performance."""

    algorithms = ["FCFS", "SJF", "Round Robin"]
    comparison = []

    for algorithm in algorithms:

        results, gantt = run_algorithm(
            algorithm,
            processes,
            quantum
        )

        if not results:
            continue

        n = len(results)

        avg_waiting = sum(
            r["waiting"] for r in results
        ) / n

        avg_turnaround = sum(
            r["turnaround"] for r in results
        ) / n

        avg_response = sum(
            r["response"] for r in results
        ) / n

        completion_time = max(
            r["completion"] for r in results
        )

        first_arrival = min(
            p["arrival"] for p in processes
        )

        elapsed_time = completion_time - first_arrival

        scheduling_steps = len(gantt)

        comparison.append({
            "Algorithm": algorithm,
            "Average Waiting Time": round(avg_waiting, 2),
            "Average Turnaround Time": round(avg_turnaround, 2),
            "Average Response Time": round(avg_response, 2),
            "Completion Time": completion_time,
            "Elapsed Time": elapsed_time,
            "Scheduling Steps": scheduling_steps
        })

    return pd.DataFrame(comparison)


def rank_algorithms(comparison):
    """
    Rank algorithms using average waiting,
    turnaround, and response times.

    Lower values are better.
    """

    metrics = [
        "Average Waiting Time",
        "Average Turnaround Time",
        "Average Response Time"
    ]

    for metric in metrics:

        comparison[metric + " Rank"] = (
            comparison[metric]
            .rank(method="min", ascending=True)
            .astype(int)
        )

    rank_columns = [
        metric + " Rank" for metric in metrics
    ]

    comparison["Total Rank Score"] = (
        comparison[rank_columns].sum(axis=1)
    )

    comparison["Overall Rank"] = (
        comparison["Total Rank Score"]
        .rank(method="min", ascending=True)
        .astype(int)
    )

    comparison = comparison.sort_values(
        by=[
            "Overall Rank",
            "Average Waiting Time",
            "Average Turnaround Time",
            "Average Response Time"
        ]
    ).reset_index(drop=True)

    return comparison


# ==========================================
# PROCESS INPUT
# ==========================================

st.subheader("1. Process Input")

num_processes = st.number_input(
    "Number of Processes",
    min_value=1,
    max_value=20,
    value=4,
    step=1
)

processes = []

header_cols = st.columns(3)

header_cols[0].write("**Process ID**")
header_cols[1].write("**Arrival Time**")
header_cols[2].write("**Burst Time**")

for i in range(int(num_processes)):

    cols = st.columns(3)

    with cols[0]:
        pid = st.text_input(
            f"PID {i + 1}",
            value=f"P{i + 1}",
            key=f"pid_{i}"
        )

    with cols[1]:
        arrival = st.number_input(
            f"Arrival {i + 1}",
            min_value=0,
            value=i,
            step=1,
            key=f"arrival_{i}"
        )

    with cols[2]:
        burst = st.number_input(
            f"Burst {i + 1}",
            min_value=1,
            value=5,
            step=1,
            key=f"burst_{i}"
        )

    processes.append({
        "pid": pid.strip(),
        "arrival": int(arrival),
        "burst": int(burst)
    })


# ==========================================
# ALGORITHM SELECTION
# ==========================================

st.subheader("2. Scheduling Algorithm")

algorithm = st.selectbox(
    "Select Algorithm",
    ["FCFS", "SJF", "Round Robin"]
)

quantum = 2

if algorithm == "Round Robin":

    quantum = st.number_input(
        "Time Quantum",
        min_value=1,
        value=2,
        step=1
    )


# ==========================================
# RUN SIMULATION
# ==========================================

if st.button("▶ Run Simulation", type="primary"):

    # Validate process IDs.
    pids = [p["pid"] for p in processes]

    if any(not pid for pid in pids):

        st.error("Process IDs cannot be empty.")

    elif len(pids) != len(set(pids)):

        st.error("Each process must have a unique Process ID.")

    else:

        # --------------------------------------
        # SELECTED ALGORITHM
        # --------------------------------------

        results, gantt = run_algorithm(
            algorithm,
            processes,
            quantum
        )

        if not results:

            st.error("No scheduling results were generated.")

        else:

            # ==================================
            # GANTT CHART
            # ==================================

            st.divider()
            st.subheader(
                f"3. Gantt Chart — {algorithm}"
            )

            if gantt:

                gantt_data = []

                for pid, start, end in gantt:

                    gantt_data.append({
                        "Process": pid,
                        "Start": start,
                        "End": end,
                        "Duration": end - start
                    })

                gantt_df = pd.DataFrame(gantt_data)

                # Draw each execution interval as a bar.
                fig_gantt = px.bar(
                    gantt_df,
                    x="Duration",
                    y="Process",
                    base="Start",
                    orientation="h",
                    text="Process",
                    title="CPU Execution Timeline",
                    hover_data=["Start", "End"]
                )

                fig_gantt.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Process",
                    showlegend=False
                )

                st.plotly_chart(
                    fig_gantt,
                    use_container_width=True
                )

                # Display interval boundaries.
                st.write("**Execution Intervals**")

                st.code(
                    " | ".join(
                        f"{pid} ({start}-{end})"
                        for pid, start, end in gantt
                    )
                )

            else:

                st.warning("The Gantt chart is empty.")


            # ==================================
            # SCHEDULING RESULTS TABLE
            # ==================================

            st.subheader("4. Scheduling Results")

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

            results_df = pd.DataFrame(table_data)

            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True
            )


            # ==================================
            # SELECTED ALGORITHM METRICS
            # ==================================

            st.subheader("5. Performance Summary")

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


            # ==================================
            # ALGORITHM COMPARISON
            # ==================================

            st.divider()

            st.header("📊 Algorithm Comparison & Ranking")

            st.write(
                "All three algorithms are evaluated using "
                "the same process inputs and Round Robin "
                "time quantum."
            )

            comparison = compare_algorithms(
                processes,
                int(quantum)
            )

            if comparison.empty:

                st.error("Unable to compare the algorithms.")

            else:

                comparison = rank_algorithms(comparison)

                # ----------------------------------
                # COMPARISON TABLE
                # ----------------------------------

                st.subheader("Performance Comparison")

                st.dataframe(
                    comparison,
                    use_container_width=True,
                    hide_index=True
                )


                # ----------------------------------
                # BEST ALGORITHM
                # ----------------------------------

                best_rank = comparison["Overall Rank"].min()

                winners = comparison.loc[
                    comparison["Overall Rank"] == best_rank,
                    "Algorithm"
                ].tolist()

                if len(winners) == 1:

                    st.success(
                        f"🏆 Best Overall Algorithm: {winners[0]}"
                    )

                else:

                    st.info(
                        "🏆 Best Overall Algorithms: "
                        + ", ".join(winners)
                        + " (tie)"
                    )

                st.caption(
                    "Ranking uses equal importance for average "
                    "waiting, turnaround, and response times. "
                    "Lower total rank scores are better. "
                    "This is a comparison heuristic, not a "
                    "universal measure of scheduling quality."
                )


                # ==================================
                # PERFORMANCE CHARTS
                # ==================================

                st.subheader("Performance Visualization")

                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:

                    fig_waiting = px.bar(
                        comparison,
                        x="Algorithm",
                        y="Average Waiting Time",
                        title="Average Waiting Time",
                        text="Average Waiting Time"
                    )

                    st.plotly_chart(
                        fig_waiting,
                        use_container_width=True
                    )

                with chart_col2:

                    fig_turnaround = px.bar(
                        comparison,
                        x="Algorithm",
                        y="Average Turnaround Time",
                        title="Average Turnaround Time",
                        text="Average Turnaround Time"
                    )

                    st.plotly_chart(
                        fig_turnaround,
                        use_container_width=True
                    )

                chart_col3, chart_col4 = st.columns(2)

                with chart_col3:

                    fig_response = px.bar(
                        comparison,
                        x="Algorithm",
                        y="Average Response Time",
                        title="Average Response Time",
                        text="Average Response Time"
                    )

                    st.plotly_chart(
                        fig_response,
                        use_container_width=True
                    )

                with chart_col4:

                    fig_steps = px.bar(
                        comparison,
                        x="Algorithm",
                        y="Scheduling Steps",
                        title="Number of Scheduling Intervals",
                        text="Scheduling Steps"
                    )

                    st.plotly_chart(
                        fig_steps,
                        use_container_width=True
                    )


                # ==================================
                # ALGORITHM EXPLANATION
                # ==================================

                st.divider()

                st.subheader("6. Algorithm Insights")

                st.markdown(
                    """
                    - **FCFS (First Come, First Served):**
                      Executes processes in arrival order.
                      Simple to implement, but long processes
                      can delay shorter ones.

                    - **SJF (Shortest Job First):**
                      Selects the available process with the
                      shortest burst time. Non-preemptive SJF
                      can reduce average waiting time, but long
                      processes may wait longer.

                    - **Round Robin:**
                      Gives each ready process a time slice.
                      It improves responsiveness in interactive
                      systems, but small time quanta can cause
                      more scheduling intervals and context
                      switches.
                    """
                )

                st.info(
                    "There is no universally best scheduling "
                    "algorithm. The best choice depends on "
                    "process characteristics and system goals."
                )

