from collections import deque
from process import state

def round_robin(processes, quantum):
    time = 0
    queue = deque()
    finished_processes = []

    processes.sort(key=lambda p: p.created_at)
    i = 0

    while i < len(processes) or queue:
        while i < len(processes) and processes[i].created_at <= time:
            processes[i].state = state.READY
            queue.append(processes[i])
            i += 1

        if not queue:
            time += 1
            continue

        current = queue.popleft()
        current.state = state.RUNNING

        run_time = min(current.remaining_time, quantum)
        print(f"[Time {time}] Running PID {current.pid} for {run_time} units")

        # Atualiza tempo de espera dos outros prontos
        for p in queue:
            if p.state == state.READY:
                p.wait_time += run_time

        time += run_time
        current.remaining_time -= run_time

        if current.remaining_time <= 0:
            current.state = state.TERMINATED
            current.completion_time = time
            finished_processes.append(current)
            print(f"[Time {time}] PID {current.pid} terminated")
        else:
            current.state = state.READY
            while i < len(processes) and processes[i].created_at <= time:
                processes[i].state = state.READY
                queue.append(processes[i])
                i += 1
            queue.append(current)

    # Resumo final
    print("\nResumo da Execução:")
    for p in sorted(finished_processes, key=lambda p: int(p.pid)):
        turnaround = p.completion_time - p.created_at
        print(f"PID: {int(p.pid):>2} | Turnaround: {turnaround:>4} | Tempo de Espera: {p.wait_time:>4} | Prioridade: {p.priority:>3}")

    return finished_processes
