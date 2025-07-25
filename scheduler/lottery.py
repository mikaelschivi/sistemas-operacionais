import random
from process import state

def lottery(processes, quantum):
    time = 0
    ready_queue = []
    finished = []

    processes.sort(key=lambda p: p.created_at)
    i = 0

    while i < len(processes) or ready_queue:
        # novos processos
        while i < len(processes) and processes[i].created_at <= time:
            processes[i].state = state.READY
            ready_queue.append(processes[i])
            i += 1

        if not ready_queue:
            time += 1
            continue

        # sorteio com peso baseado em prioridade
        ticket_pool = []
        for p in ready_queue:
            ticket_pool.extend([p] * p.priority)

        current = random.choice(ticket_pool)
        current.state = state.RUNNING

        run_time = min(current.execution_time, quantum)
        print(f"[Time {time}] Running PID {current.pid} for {run_time} units")

        time += run_time
        current.execution_time -= run_time

        if current.execution_time <= 0:
            current.state = state.TERMINATED
            current.completion_time = time
            finished.append(current)
            ready_queue.remove(current)
            print(f"[Time {time}] PID {current.pid} terminated")
        else:
            current.state = state.READY

        # novos processos após execução
        while i < len(processes) and processes[i].created_at <= time:
            processes[i].state = state.READY
            ready_queue.append(processes[i])
            i += 1

    # Resumo da execução
    print("\nResumo da Execução:")
    for p in sorted(finished, key=lambda p: int(p.pid)):
        turnaround = p.completion_time - p.created_at
        print(f"PID: {int(p.pid):>2} | Turnaround: {turnaround:>4} | Tempo de Espera: {p.wait_time:>4} | Prioridade: {p.priority:>3}")

    return finished