from enum import Enum

class state(Enum):
    NEW = 0
    READY = 1
    RUNNING = 2
    BLOCKED = 3
    TERMINATED = 4

class Process:
    def __init__(self, created_at, pid, execution_time, priority):
        self.created_at = int(created_at)
        self.pid = int(pid)
        self.execution_time = int(execution_time)
        self.priority = int(priority)
        self.state = state.NEW


        self.remaining_time = self.execution_time
        self.wait_time = 0
        self.completion_time = 0

    def __repr__(self):
        turnaround_time = self.completion_time - self.created_at
        return (f"PID: {self.pid} | Turnaround: {turnaround_time} "
                f"| Tempo de Espera: {self.wait_time} | Prioridade: {self.priority}")
