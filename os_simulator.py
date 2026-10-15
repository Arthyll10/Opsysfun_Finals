# CPU Scheduling and Page Replacement Simulator - Python 3
# A menu-driven program that runs six algorithms on user input:
#   CPU scheduling: FCFS, Non-Preemptive Priority, Preemptive Priority, Round Robin
#   Page replacement: LRU, MRU
# Options 7 and 8 run the algorithms on the same input and compare them.
# No extra packages are needed. Full citations are in REFERENCES.md.

DISPLAY_WIDTH = 78
DIVIDER = "=" * DISPLAY_WIDTH
SUBDIVIDER = "-" * DISPLAY_WIDTH


# ----------------------------------------------------------------------------
# Display and input helpers
# ----------------------------------------------------------------------------

def show_heading(title):
    """Print a centered heading between dividers."""
    print(DIVIDER)
    print(title.center(DISPLAY_WIDTH))


def show_table(headers, rows, title=""):
    """Print rows as a tab-aligned table with an optional title."""
    # Give each column enough 8-character tab stops for its longest value.
    tab_stops = []
    for column in range(len(headers)):
        width = len(headers[column])
        for row in rows:
            width = max(width, len(str(row[column])))
        tab_stops.append(width // 8 + 1)

    print(DIVIDER)
    if title:
        print(title.center(DISPLAY_WIDTH))
        print(SUBDIVIDER)
    for number, row in enumerate([headers] + rows):
        line = ""
        for column in range(len(headers)):
            value = str(row[column])
            line += value
            if column < len(headers) - 1:
                line += "\t" * (tab_stops[column] - len(value) // 8)
        print(line)
        if number == 0:
            print(SUBDIVIDER)


def read_number(message, minimum):
    """Keep asking until the user enters a whole number >= minimum."""
    while True:
        try:
            value = int(input(message))
            if value >= minimum:
                return value
        except ValueError:
            pass
        print(f"Enter a whole number that is at least {minimum}.")


def add_step(timeline, process, start, end):
    """Add a block to the timeline. -1 means the CPU is idle."""
    # Merge with the previous block if the same process keeps running.
    if timeline and timeline[-1][0] == process:
        timeline[-1][2] = end
    else:
        timeline.append([process, start, end])


# ----------------------------------------------------------------------------
# CPU scheduling algorithms
# Each one returns (completion times, timeline of [process, start, end]).
# ----------------------------------------------------------------------------

# [1] https://www.askpython.com/python/examples/first-come-first-serve
def fcfs(arrival, burst):
    """Run processes in order of arrival. Ties go to the earlier input."""
    n = len(arrival)
    completion = [0] * n
    done = [False] * n
    timeline = []
    time = 0

    for count in range(n):
        # Pick the earliest-arriving process that has not run yet.
        current = -1
        for i in range(n):
            if not done[i]:
                if current == -1 or arrival[i] < arrival[current]:
                    current = i

        # If it has not arrived yet, the CPU is idle until it does.
        if time < arrival[current]:
            add_step(timeline, -1, time, arrival[current])
            time = arrival[current]
        add_step(timeline, current, time, time + burst[current])
        time += burst[current]
        completion[current] = time
        done[current] = True

    return completion, timeline


# [2] https://github.com/malshahin/priorityScheduling/blob/main/priority.py
def non_preemptive_priority(arrival, burst, priority):
    """Run the highest-priority ready process to completion.

    A lower number means higher priority. Ties go to the shorter burst.
    """
    n = len(arrival)
    completion = [0] * n
    done = [False] * n
    timeline = []
    time = 0
    finished = 0

    while finished < n:
        # Pick the best process among those that have arrived.
        current = -1
        for i in range(n):
            if not done[i] and arrival[i] <= time:
                if current == -1 or priority[i] < priority[current]:
                    current = i
                elif priority[i] == priority[current] and burst[i] < burst[current]:
                    current = i

        if current == -1:
            # Nothing has arrived yet, so the CPU idles for one unit.
            add_step(timeline, -1, time, time + 1)
            time += 1
        else:
            add_step(timeline, current, time, time + burst[current])
            time += burst[current]
            completion[current] = time
            done[current] = True
            finished += 1

    return completion, timeline


# [3] https://github.com/shahidazam2020-oss/priority-preemptive-scheduling2/blob/main/python3%20priority_preemptive.py
def preemptive_priority(arrival, burst, priority):
    """Re-pick the highest-priority ready process every time unit.

    A lower number means higher priority. On equal priority the running
    process keeps the CPU; otherwise the earlier input wins.
    """
    n = len(arrival)
    remaining = burst.copy()
    completion = [0] * n
    timeline = []
    time = 0
    finished = 0
    last = -1  # Process that ran in the previous time unit.

    while finished < n:
        current = -1
        for i in range(n):
            if arrival[i] <= time and remaining[i] > 0:
                if current == -1 or priority[i] < priority[current]:
                    current = i
                elif priority[i] == priority[current] and i == last:
                    current = i  # Do not preempt on a tie.

        # Run the chosen process (or idle) for one time unit.
        add_step(timeline, current, time, time + 1)
        time += 1
        if current != -1:
            remaining[current] -= 1
            if remaining[current] == 0:
                completion[current] = time
                finished += 1
        last = current

    return completion, timeline


# [4] https://www.geeksforgeeks.org/dsa/round-robin-scheduling-with-different-arrival-times/
def round_robin(arrival, burst, quantum):
    """Give each process in the ready queue up to 'quantum' units per turn."""
    n = len(arrival)
    remaining = burst.copy()
    completion = [0] * n
    added = [False] * n  # True once a process has entered the queue.
    queue = []
    timeline = []
    time = 0
    finished = 0

    while finished < n:
        for i in range(n):
            if arrival[i] <= time and not added[i]:
                queue.append(i)
                added[i] = True

        if not queue:
            add_step(timeline, -1, time, time + 1)
            time += 1
            continue

        current = queue.pop(0)
        for step in range(quantum):
            if remaining[current] == 0:
                break
            add_step(timeline, current, time, time + 1)
            time += 1
            remaining[current] -= 1

            # New arrivals join the queue before the current process returns.
            for i in range(n):
                if arrival[i] <= time and not added[i]:
                    queue.append(i)
                    added[i] = True

        if remaining[current] > 0:
            queue.append(current)
        else:
            completion[current] = time
            finished += 1

    return completion, timeline


# ----------------------------------------------------------------------------
# Page replacement algorithms
# Each one returns (fault count, history of [page, frames, HIT/FAULT]).
# ----------------------------------------------------------------------------

# [5] https://www.geeksforgeeks.org/dsa/program-for-least-recently-used-lru-page-replacement-algorithm/
def lru(pages, capacity):
    """When frames are full, replace the least recently used page."""
    frames = []
    recent = []  # Pages ordered from least to most recently used.
    faults = 0
    history = []

    for page in pages:
        if page in frames:
            status = "HIT"
            recent.remove(page)
        else:
            status = "FAULT"
            faults += 1
            if len(frames) < capacity:
                frames.append(page)
            else:
                victim = recent.pop(0)  # Least recently used.
                position = frames.index(victim)
                frames[position] = page
        recent.append(page)
        history.append([page, frames.copy(), status])

    return faults, history


# [6] https://github.com/rakesh4407/OS-Lab-Assignment-3/blob/main/page_replacement.py
def mru(pages, capacity):
    """When frames are full, replace the most recently used page."""
    frames = []
    recent = []  # Pages ordered from least to most recently used.
    faults = 0
    history = []

    for page in pages:
        if page in frames:
            status = "HIT"
            recent.remove(page)
        else:
            status = "FAULT"
            faults += 1
            if len(frames) < capacity:
                frames.append(page)
            else:
                victim = recent.pop()  # Most recently used.
                position = frames.index(victim)
                frames[position] = page
        recent.append(page)
        history.append([page, frames.copy(), status])

    return faults, history


# ----------------------------------------------------------------------------
# CPU input and output
# ----------------------------------------------------------------------------

def read_processes(use_priority):
    """Read process IDs, arrival times, burst times and (optionally) priorities."""
    show_heading("PROCESS INPUT")
    n = read_number("Number of processes: ", 1)
    ids, arrival, burst, priority = [], [], [], []
    for i in range(n):
        print(SUBDIVIDER)
        print(f"Process {i + 1} of {n}")
        while True:
            name = input("Process ID: ").strip()
            # IDLE is reserved for gaps in the timeline.
            if name and name not in ids and name.upper() != "IDLE":
                break
            print("Use a unique ID other than IDLE.")
        ids.append(name)
        arrival.append(read_number("Arrival time: ", 0))
        burst.append(read_number("Burst time: ", 1))
        if use_priority:
            priority.append(read_number("Priority (lower number = higher): ", 0))
        else:
            priority.append("-")
    return ids, arrival, burst, priority


def averages(arrival, burst, completion):
    """Return (average waiting time, average turnaround time)."""
    n = len(arrival)
    total_waiting = 0
    total_turnaround = 0
    for i in range(n):
        turnaround = completion[i] - arrival[i]
        total_turnaround += turnaround
        total_waiting += turnaround - burst[i]
    return total_waiting / n, total_turnaround / n


def show_cpu(ids, arrival, burst, priority, completion, timeline):
    """Print the timeline, per-process results and averages."""
    timeline_rows = []
    for process, start, end in timeline:
        name = "IDLE" if process == -1 else ids[process]
        timeline_rows.append([name, start, end])
    show_table(["Process", "Start", "End"], timeline_rows, "EXECUTION TIMELINE")

    # Turnaround = finish - arrival; waiting = turnaround - burst.
    result_rows = []
    for i in range(len(ids)):
        turnaround = completion[i] - arrival[i]
        waiting = turnaround - burst[i]
        result_rows.append([ids[i], arrival[i], burst[i], priority[i],
                            completion[i], turnaround, waiting])
    show_table(["PID", "Arrival", "Burst", "Priority", "Finish", "Turnaround", "Waiting"],
               result_rows, "PROCESS RESULTS")

    avg_waiting, avg_turnaround = averages(arrival, burst, completion)
    show_table(["Metric", "Value"], [
        ["Average waiting time", f"{avg_waiting:.2f}"],
        ["Average turnaround time", f"{avg_turnaround:.2f}"]
    ], "SUMMARY")


def compare_cpu():
    """Run all four CPU algorithms on one input and compare their averages."""
    ids, arrival, burst, priority = read_processes(True)
    quantum = read_number("Time quantum (for Round Robin): ", 1)
    results = [
        ["FCFS", fcfs(arrival, burst)[0]],
        ["Non-Preemptive Priority", non_preemptive_priority(arrival, burst, priority)[0]],
        ["Preemptive Priority", preemptive_priority(arrival, burst, priority)[0]],
        [f"Round Robin (q = {quantum})", round_robin(arrival, burst, quantum)[0]],
    ]
    rows = []
    for name, completion in results:
        avg_waiting, avg_turnaround = averages(arrival, burst, completion)
        rows.append([name, f"{avg_waiting:.2f}", f"{avg_turnaround:.2f}"])
    show_table(["Algorithm", "Avg Waiting", "Avg Turnaround"], rows,
               "CPU SCHEDULING COMPARISON")


# ----------------------------------------------------------------------------
# Paging input and output
# ----------------------------------------------------------------------------

def read_pages():
    """Read a page reference string and the number of frames."""
    show_heading("PAGE INPUT")
    while True:
        try:
            text = input("Page references (separated by spaces): ")
            pages = []
            for item in text.split():
                page = int(item)
                if page < 0:
                    raise ValueError
                pages.append(page)
            if pages:
                break
        except ValueError:
            pass
        print("Enter nonnegative whole numbers, for example: 1 2 3 1 4")
    capacity = read_number("Number of frames: ", 1)
    return pages, capacity


def show_pages(pages, capacity, faults, history):
    """Print each step of page replacement and the hit/fault rates."""
    show_table(["Input", "Value"], [["Page references", str(pages)],
               ["Number of frames", capacity]], "INPUT SUMMARY")
    rows = []
    for i in range(len(history)):
        page, frames, status = history[i]
        rows.append([i + 1, page, status, str(frames)])
    show_table(["Step", "Page", "Result", "Frames after access"], rows, "PAGE REPLACEMENT STEPS")
    hits = len(pages) - faults
    show_table(["Metric", "Value"], [
        ["Page faults", faults], ["Page hits", hits],
        ["Fault rate", f"{faults / len(pages) * 100:.2f}%"],
        ["Hit rate", f"{hits / len(pages) * 100:.2f}%"]
    ], "SUMMARY")


def compare_pages():
    """Run LRU and MRU on one input and compare their fault and hit rates."""
    pages, capacity = read_pages()
    rows = []
    for name, algorithm in [["LRU", lru], ["MRU", mru]]:
        faults = algorithm(pages, capacity)[0]
        hits = len(pages) - faults
        rows.append([name, faults, hits,
                     f"{faults / len(pages) * 100:.2f}%",
                     f"{hits / len(pages) * 100:.2f}%"])
    show_table(["Algorithm", "Faults", "Hits", "Fault Rate", "Hit Rate"], rows,
               f"PAGE REPLACEMENT COMPARISON ({capacity} frames)")


# ----------------------------------------------------------------------------
# Main menu
# ----------------------------------------------------------------------------

def main():
    """Show the menu and run the chosen option until the user exits."""
    while True:
        show_table(["Option", "Algorithm"], [
            [1, "FCFS"], [2, "Non-Preemptive Priority"],
            [3, "Preemptive Priority"], [4, "Round Robin"],
            [5, "LRU"], [6, "MRU"],
            [7, "Compare CPU Scheduling"], [8, "Compare Page Replacement"],
            [0, "Exit"]
        ], "CPU SCHEDULING AND PAGE REPLACEMENT")
        print(DIVIDER)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            show_heading("Goodbye!")
            print(DIVIDER)
            break
        elif choice in ("1", "2", "3", "4"):
            # Priority is only asked for the two priority algorithms.
            ids, arrival, burst, priority = read_processes(choice in ("2", "3"))
            if choice == "1":
                show_heading("FCFS")
                completion, timeline = fcfs(arrival, burst)
            elif choice == "2":
                show_heading("NON-PREEMPTIVE PRIORITY")
                completion, timeline = non_preemptive_priority(arrival, burst, priority)
            elif choice == "3":
                show_heading("PREEMPTIVE PRIORITY")
                completion, timeline = preemptive_priority(arrival, burst, priority)
            else:
                quantum = read_number("Time quantum: ", 1)
                show_heading(f"ROUND ROBIN (quantum = {quantum})")
                completion, timeline = round_robin(arrival, burst, quantum)
            show_cpu(ids, arrival, burst, priority, completion, timeline)
        elif choice in ("5", "6"):
            pages, capacity = read_pages()
            if choice == "5":
                show_heading("LRU")
                faults, history = lru(pages, capacity)
            else:
                show_heading("MRU")
                faults, history = mru(pages, capacity)
            show_pages(pages, capacity, faults, history)
        elif choice == "7":
            compare_cpu()
        elif choice == "8":
            compare_pages()
        else:
            print("Choose a number from 0 to 8.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("Program ended.")
