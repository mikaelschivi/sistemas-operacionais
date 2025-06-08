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
        self.pid = pid
        self.execution_time = int(execution_time)
        self.priority = int(priority)
        self.state = state.NEW

    def __repr__(self):
        return f"created at: {self.created_at}\npid: {self.pid}\nexecution_time: {self.execution_time}\npriority: {self.priority}\nstate: {self.state}\n"