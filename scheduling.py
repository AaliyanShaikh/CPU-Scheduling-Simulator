def fcfs(processes):
    processes = sorted(processes, key=lambda p: p["arrival"])

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
    remaining = processes.copy()
    results = []
    gantt = []
    time = 0

    while remaining:

        available = [
            p for p in remaining
            if p["arrival"] <= time
        ]

        if not available:
            time = min(p["arrival"] for p in remaining)
            continue

        p = min(
            available,
            key=lambda x: x["burst"]
        )

        remaining.remove(p)

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


def round_robin(processes, quantum):

    processes = sorted(
        processes,
        key=lambda p: p["arrival"]
    )

    queue = []
    remaining = {
        p["pid"]: p["burst"]
        for p in processes
    }

    first_start = {}
    completion = {}

    time = 0
    index = 0
    gantt = []

    while len(completion) < len(processes):

        while (
            index < len(processes)
            and processes[index]["arrival"] <= time
        ):
            queue.append(processes[index])
            index += 1

        if not queue:
            time = processes[index]["arrival"]
            continue

        p = queue.pop(0)
        pid = p["pid"]

        if pid not in first_start:
            first_start[pid] = time

        run = min(
            quantum,
            remaining[pid]
        )

        start = time
        time += run
        remaining[pid] -= run

        gantt.append(
            (pid, start, time)
        )

        while (
            index < len(processes)
            and processes[index]["arrival"] <= time
        ):
            queue.append(processes[index])
            index += 1

        if remaining[pid] > 0:
            queue.append(p)
        else:
            completion[pid] = time

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