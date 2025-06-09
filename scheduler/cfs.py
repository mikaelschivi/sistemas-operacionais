from sortedcontainers import SortedList
from process import state

def cfs_rbt(processes, quantum):
    time = 0
    finished = []
    processes.sort(key=lambda p: p.created_at)
    i = 0

    ready_queue = SortedList(key=lambda p: (p.virtual_runtime, p.pid))

    for p in processes:
        p.virtual_runtime = 0

    while i < len(processes) or ready_queue:
        # Insert new arrivals
        while i < len(processes) and processes[i].created_at <= time:
            processes[i].state = state.READY
            processes[i].virtual_runtime = 0
            ready_queue.add(processes[i])
            i += 1

        if not ready_queue:
            time += 1
            continue

        current = ready_queue.pop(0)
        current.state = state.RUNNING

        run_time = min(current.remaining_time, quantum)
        print(f"[Time {time}] Running PID {current.pid} for {run_time} units")

        # Update wait time for others
        for p in ready_queue:
            p.wait_time += run_time

        time += run_time
        current.remaining_time -= run_time
        current.virtual_runtime += run_time

        if current.remaining_time <= 0:
            current.state = state.TERMINATED
            current.completion_time = time
            finished.append(current)
            print(f"[Time {time}] PID {current.pid} terminated")
        else:
            current.state = state.READY
            ready_queue.add(current)

        # Add new arrivals after time advanced
        while i < len(processes) and processes[i].created_at <= time:
            processes[i].state = state.READY
            processes[i].virtual_runtime = 0
            ready_queue.add(processes[i])
            i += 1

    # Resultado das métricas
    print("\nResumo da Execução:")
    for p in sorted(finished, key=lambda p: int(p.pid)):
        turnaround = p.completion_time - int(p.created_at)
        print(f"PID: {int(p.pid):>2} | Turnaround: {turnaround:>4} | Tempo de Espera: {p.wait_time:>4} | Prioridade: {p.priority:>3}")

    return finished
