class Process:
    def __init__(self, creation_time, pid, execution_time, priority, mem_size, page_size, alloc_perc, page_order):
        self.creation_time = creation_time
        self.pid = pid
        self.execution_time = execution_time
        self.priority = priority
        self.page_order = page_order
        
        self.remaining_time = execution_time
        self.page_order_index = 0
        self.is_finished = False
        self.wait_time = 0
        self.completion_time = 0
        
        self.pages_in_memory = {'fifo': 0, 'lru': 0, 'lfu': 0, 'optimal': 0}
        
        virtual_pages = mem_size // page_size
        self.page_amount_limit = int(virtual_pages * (alloc_perc / 100.0))

    def __repr__(self):
        return f"Process(pid={self.pid})"
    
class Page:
    def __init__(self, page_id, process_pid):
        self.id = page_id
        self.process_pid = process_pid
        self.last_used = 0
        self.times_used = 1

class Simulation:
    def __init__(self, input_path):
        self.cpu_quantum = 0
        self.where = ''
        self.memory_size = 0
        self.page_size = 0
        self.alloc_perc = 0
        self.processes = []
        self.page_limit = 0
        self._parse_file(input_path)

    def _parse_file(self, path):
        with open(path) as f:
            s = f.readline().strip().split('|')
            self.cpu_quantum = int(s[1])
            self.where = s[2].lower()
            self.memory_size = int(s[3])
            self.page_size = int(s[4])
            self.alloc_perc = int(s[5])
            self.page_limit = self.memory_size / self.page_size
            for line in f:
                parts = line.strip().split('|')
                self.processes.append(Process(
                    int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]),
                    int(parts[4]), self.page_size, self.alloc_perc,
                    list(map(int, parts[5].split()))
                ))