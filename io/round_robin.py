from collections import deque
from process import state
import random

def print_system_state(time, processes, devices, running_process):
    ready_processes = [p for p in processes if p.state == state.READY]
    blocked_processes = [p for p in processes if p.state == state.BLOCKED]

    print(f"\n[Time {time}] CONTEXT SWITCH")

    # Processo em execução
    if running_process:
        print(f"  RUNNING  : PID {running_process.pid} (Restante: {running_process.remaining_time})")
    else:
        print("  RUNNING  : None")

    # Processos prontos
    ready_str = ", ".join([f"PID {p.pid} ({p.remaining_time})" for p in ready_processes])
    print(f"  READY    : [{ready_str}]")

    # Processos bloqueados
    blocked_str = ", ".join([f"PID {p.pid} ({p.remaining_time}, Dev: {p.blocked_on_device_id})" for p in blocked_processes])
    print(f"  BLOCKED  : [{blocked_str}]")
    
    # Estado dos dispositivos
    print("\n  I/O Devices:")
    for dev in devices.values():
        gap = "    "
        users_str = ", ".join([f"PID {p.pid}" for p, _ in dev.users])
        wait_str = ", ".join([f"PID {p.pid}" for p in dev.wait_queue])
        print(f"{gap}Device {dev.id} (Capacity: {len(dev.users)}/{dev.capacity})")
        print(f"{gap*2}Users: [{users_str}]")
        print(f"{gap*2}Queue: [{wait_str}]")

def round_robin(processes, devices, quantum):
    time = 0
    ready_queue = deque()
    finished_processes = []
    
    all_processes = processes[:]
    processes.sort(key=lambda p: p.created_at)
    
    current_process = None
    time_in_quantum = 0
    
    # variaves de io
    io_request_at_time = -1
    io_request_device = None

    proc_idx = 0
    num_terminated = 0

    while num_terminated < len(all_processes):
        # Conclusão de E/S e mover processos para READY
        for dev in devices.values():
            finished_io_users = []
            for i, (proc, io_remaining) in enumerate(dev.users):
                dev.users[i] = (proc, io_remaining - 1)
                if dev.users[i][1] <= 0:
                    finished_io_users.append(dev.users[i])
            
            for proc, _ in finished_io_users:
                dev.users.remove((proc, 0)) # remove o processo que terminou
                proc.state = state.READY
                proc.blocked_on_device_id = None
                ready_queue.append(proc)
                
                # verifica se alguém na fila de espera pode usar o dispositivo
                if dev.wait_queue:
                    next_proc = dev.wait_queue.popleft()
                    next_proc.blocked_on_device_id = dev.id # garante o device correto
                    dev.users.append((next_proc, dev.operation_time))


        # Adicionar processos recém-chegados fila de prontos
        while proc_idx < len(processes) and processes[proc_idx].created_at <= time:
            processes[proc_idx].state = state.READY
            ready_queue.append(processes[proc_idx])
            proc_idx += 1

        # 3. Gerenciar a CPU
        if current_process is None:
            if ready_queue:
                current_process = ready_queue.popleft()
                current_process.state = state.RUNNING
                time_in_quantum = 0
                
                # chance de IO
                if random.random() < current_process.io_chance:
                    # Ocorre em algum momento aleatório dentro do quantum
                    io_request_at_time = time + random.randint(1, quantum)
                    io_request_device = random.choice(list(devices.values()))
                else:
                    io_request_at_time = -1 # Sem requisição de E/S

        # Se um processo estiver na CPU
        if current_process:
            # Caso 1: Processo solicita E/S
            if io_request_at_time == time:
                device = io_request_device
                print("\nIO REQUEST -------> ", device)
                current_process.state = state.BLOCKED
                current_process.blocked_on_device_id = device.id
                
                if len(device.users) < device.capacity:
                    device.users.append((current_process, device.operation_time))
                else:
                    device.wait_queue.append(current_process)

                print_system_state(time, all_processes, devices, None)
                current_process = None

            # Caso 2: Quantum do processo expira
            elif time_in_quantum >= quantum:
                current_process.state = state.READY
                ready_queue.append(current_process)
                print_system_state(time, all_processes, devices, None)
                current_process = None
            
            # Caso 3: Processo termina
            elif current_process.remaining_time <= 0:
                current_process.state = state.TERMINATED
                current_process.completion_time = time
                finished_processes.append(current_process)
                num_terminated += 1
                print_system_state(time, all_processes, devices, None)
                current_process = None
        
        # 4. Atualizar contadores e tempo
        if current_process:
            current_process.remaining_time -= 1
            time_in_quantum += 1

        for p in all_processes:
            if p.state == state.READY:
                p.wait_time += 1
            elif p.state == state.BLOCKED:
                p.blocked_time += 1
        
        time += 1
    
    # Resumo Final
    print("\n" + "="*20 + " Resumo da Execução " + "="*20)
    for p in sorted(finished_processes, key=lambda p: int(p.pid)):
        turnaround = p.completion_time - p.created_at
        print(f"PID: {int(p.pid):>2} | Turnaround: {turnaround:>4} | Tempo de Espera (Ready): {p.wait_time:>4} | Tempo Bloqueado (I/O): {p.blocked_time:>4}")