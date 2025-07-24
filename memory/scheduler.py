class Scheduler:
    def __init__(self, processes, quantum, mem_manager):
        self.time = 0
        self.quantum = quantum
        self.mem = mem_manager
        self.future = sorted(processes, key=lambda p: p.creation_time)  # processos a serem admitidos, ordenados por tempo de criacao
        self.ready = []  # processos readys
        self.done = []   # processos done
        self.all_processes = list(self.future)

    def run(self):
        print("--- iniciando simulacao ---")

        while self.future or self.ready:
            self._admit_new_processes()

            # se nao ha processos prontos, avanca o tempo e tenta puxar novos
            if not self.ready:
                self.time += 1
                continue

            proc = self.ready.pop(0)  # pega o proximo processo da fila (round robin)
            # tempo de execucao e o minimo entre o quantum e o tempo restante
            exec_time = min(self.quantum, proc.remaining_time)
            print(f"tempo {self.time}: pid {proc.pid} executando por {exec_time} unidades.")

            self._update_wait_times(exec_time)
            self._simulate_memory_access(proc, exec_time)

            self.time += exec_time
            proc.remaining_time -= exec_time

            # processo terminou -> lista de concluidos
            if proc.remaining_time <= 0:
                proc.completion_time = self.time
                self.done.append(proc)
                print(f"tempo {self.time}: pid {proc.pid} finalizado.")
            # processo nao terminou -> fim da fila de prontos
            else:
                self._admit_new_processes()
                self.ready.append(proc)

        self._summary()

    # move processos da lista de futuros para a de prontos se seu tempo de criacao chegou
    def _admit_new_processes(self):
        arriving = [p for p in self.future if p.creation_time <= self.time]
        self.ready.extend(arriving)
        self.future = [p for p in self.future if p.creation_time > self.time]

    # incrementa o tempo de espera para todos os processos que estao na fila de prontos
    def _update_wait_times(self, exec_time):
        for p in self.ready:
            p.wait_time += exec_time

    # para cada unidade de tempo, simula um acesso a memoria
    def _simulate_memory_access(self, proc, exec_time):
        for _ in range(exec_time):
            self.mem.access(proc, self.all_processes)

    def _summary(self):
        print("\n--- final ---")
        for p in sorted(self.done, key=lambda p: p.pid):
            # turnaround (conclusao - criacao) e a espera
            turnaround = p.completion_time - p.creation_time
            print(f"pid {p.pid} | turnaround {turnaround} | espera {p.wait_time}")

        faults = self.mem.faults
        print("\n--- faltas de pagina ---")

        for algo, count in faults.items():
            print(f"{algo.upper()}: {count}")

        print(f"\noverall -> {faults['fifo']}|{faults['lru']}|{faults['lfu']}|{faults['optimal']}|", end='')

        # melhor algo - com menos fault quando comparado ao otimo
        diffs = {k: abs(faults[k] - faults['optimal']) for k in ['fifo', 'lru', 'lfu']}
        min_diff = min(diffs.values())
        closest_algos = [k for k, v in diffs.items() if v == min_diff]

        print("empate" if len(closest_algos) > 1 else closest_algos[0])