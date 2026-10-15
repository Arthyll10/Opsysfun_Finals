# CPU Scheduling and Page Replacement Simulator

A menu-driven Python program that simulates six operating system algorithms and compares their performance.

> **For educational purposes only.** This project was made as coursework for an Operating Systems class. It is a simplified simulation for learning, not a model of how a real operating system schedules processes or manages memory.

## Algorithms

| CPU Scheduling | Page Replacement |
|---|---|
| First-Come, First-Served (FCFS) | Least Recently Used (LRU) |
| Non-Preemptive Priority | Most Recently Used (MRU) |
| Preemptive Priority | |
| Round Robin | |

Options 7 and 8 run the algorithms on the same input and show a comparison table:

- **CPU scheduling:** average waiting time and average turnaround time
- **Page replacement:** page faults, page hits, fault rate and hit rate

## How to Run

Requires Python 3. No extra packages are needed.

```
python os_simulator.py
```

Choose an option from the menu and enter the requested values. The menu repeats until you choose `0` to exit.

## References

1. AskPython. *First Come First Serve (FCFS) Scheduling in Python.* https://www.askpython.com/python/examples/first-come-first-serve
2. malshahin. *priorityScheduling* (priority.py). GitHub. https://github.com/malshahin/priorityScheduling/blob/main/priority.py
3. shahidazam2020-oss. *priority-preemptive-scheduling2* (python3 priority_preemptive.py). GitHub. https://github.com/shahidazam2020-oss/priority-preemptive-scheduling2/blob/main/python3%20priority_preemptive.py
4. GeeksforGeeks. *Round Robin Scheduling with Different Arrival Times.* https://www.geeksforgeeks.org/dsa/round-robin-scheduling-with-different-arrival-times/
5. GeeksforGeeks. *Program for Least Recently Used (LRU) Page Replacement Algorithm.* https://www.geeksforgeeks.org/dsa/program-for-least-recently-used-lru-page-replacement-algorithm/
6. rakesh4407. *OS-Lab-Assignment-3* (page_replacement.py). GitHub. https://github.com/rakesh4407/OS-Lab-Assignment-3/blob/main/page_replacement.py

### Changes from the references

- **Preemptive Priority [3]:** When priorities are equal, the running process keeps the CPU. In the reference, the process entered earlier preempts it.
