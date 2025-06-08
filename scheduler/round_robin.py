from collections import deque
from process import state

def round_robin(processes, quantum):
    time = 0
    queue = deque()
    finished_processes = []
    
    processes.sort(key=lambda p: int(p.created_at))

    i = 0
    while i < len(processes) or queue:
        # new process
        while i < len(processes) and int(processes[i].created_at) <= time:
            processes[i].state = state.READY
            queue.append(processes[i])
            i += 1

        if not queue:
            time += 1
            continue

        current = queue.popleft()
        current.state = state.RUNNING

        remaining_time = int(current.execution_time)
        run_time = min(quantum, remaining_time)
        
        print(f"[Time {time}] Running PID {current.pid} for {run_time} units")
        time += run_time
        current.execution_time = str(remaining_time - run_time)

        # if process finished
        if int(current.execution_time) <= 0:
            current.state = state.TERMINATED
            finished_processes.append(current)
            print(f"[Time {time}] PID {current.pid} terminated")
        else:
            current.state = state.READY
            # add processes before requeue
            while i < len(processes) and int(processes[i].created_at) <= time:
                processes[i].state = state.READY
                queue.append(processes[i])
                i += 1
            queue.append(current)

    return finished_processes
