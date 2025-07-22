class Scheduler:
    def __init__(self, processes, quantum, mem_manager):
        self.time = 0
        self.q = quantum
        self.mem = mem_manager
        self.future = sorted(processes, key=lambda p: p.creation_time)
        self.ready = []
        self.done = []
        self.all = list(self.future)

    def run(self):
        print("--- Iniciando Simulação ---")
        while self.future or self.ready:
            self.ready += [p for p in self.future if p.creation_time <= self.time]
            self.future = [p for p in self.future if p.creation_time > self.time]

            if not self.ready:
                self.time += 1
                continue

            proc = self.ready.pop(0)
            t = min(self.q, proc.remaining_time)
            print(f"Tempo {self.time}: PID {proc.pid} executando por {t} unidades.")

            for p in self.ready:
                p.wait_time += t

            for _ in range(t):
                self.mem.access(proc, self.all)

            self.time += t
            proc.remaining_time -= t

            if proc.remaining_time <= 0:
                proc.completion_time = self.time
                self.done.append(proc)
                print(f"Tempo {self.time}: PID {proc.pid} finalizado.")
            else:
                self.ready += [p for p in self.future if p.creation_time <= self.time]
                self.future = [p for p in self.future if p.creation_time > self.time]
                self.ready.append(proc)

        self._summary()

    def _summary(self):
        print("\n--- Final ---")
        for p in sorted(self.done, key=lambda p: p.pid):
            print(f"PID {p.pid} | Turnaround {p.completion_time - p.creation_time} | Espera {p.wait_time}")

        f = self.mem.faults
        print("\n--- Faltas de Página ---")
        for k in f: print(f"{k.upper()}: {f[k]}")
        best = min(['fifo', 'lru', 'lfu'], key=lambda k: f[k])
        print(f"\nMelhor algoritmo prático: {best.upper()} | Ótimo teve {f['optimal']} faltas")