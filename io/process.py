from enum import Enum

class state(Enum):
    NEW = 0
    READY = 1
    RUNNING = 2
    BLOCKED = 3
    TERMINATED = 4

class Process:
    def __init__(self, created_at, pid, execution_time, priority, memory_qty, access_sequence, io_chance):
        self.created_at = int(created_at)
        self.pid = int(pid)
        self.execution_time = int(execution_time)
        self.priority = int(priority)
        self.memory_qty = int(memory_qty)
        self.access_sequence = access_sequence
        self.io_chance = float(io_chance)
        
        self.state = state.NEW
        self.remaining_time = self.execution_time
        self.wait_time = 0
        self.blocked_time = 0 # Novo atributo
        self.completion_time = 0
        
        # Atributos para controle de E/S
        self.blocked_on_device_id = None

    def __repr__(self):
        return (f"PID: {self.pid} (Restante: {self.remaining_time})")