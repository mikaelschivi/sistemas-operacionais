from collections import deque

class IODevice:
    def __init__(self, device_id, capacity, operation_time):
        self.id = int(device_id)
        self.capacity = int(capacity)
        self.operation_time = int(operation_time)

        # tuplas: (process, time_remaining_on_io)
        self.users = []
        
        # wating list para o device
        self.wait_queue = deque()

    def __repr__(self):
        return (f"Device ID: {self.id} | Capacity: {len(self.users)}/{self.capacity} "
                f"| Waiting: {len(self.wait_queue)}")