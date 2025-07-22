from helper import Page
import time

class MemoryManager:
    def __init__(self, page_limit, locality):
        self.limit = page_limit
        self.local = locality
        self.memory = {k: [] for k in ['fifo', 'lru', 'lfu', 'optimal']}
        self.faults = {k: 0 for k in self.memory}

    def _find(self, mem, pid, page_id):
        return next((p for p in mem if p.id == page_id and p.process_pid == pid), None)

    def _replace(self, mem, proc, algo, all_procs, select):
        if len(mem) >= self.limit or proc.pages_in_memory[algo] >= proc.page_amount_limit:
            space = [p for p in mem if p.process_pid == proc.pid] if self.local else mem
            if not space: space = mem
            victim = select(space)
            mem.remove(victim)
            for p in all_procs:
                if p.pid == victim.process_pid:
                    p.pages_in_memory[algo] -= 1
                    break
        proc.pages_in_memory[algo] += 1

    def access(self, proc, all_procs):
        if proc.page_order_index >= len(proc.page_order): return
        pid, idx = proc.pid, proc.page_order_index
        page_id = proc.page_order[idx]
        proc.page_order_index += 1

        now = time.time()

        for algo in self.memory:
            mem = self.memory[algo]
            p = self._find(mem, pid, page_id)
            if p:
                if algo == 'lru': p.last_used = now
                if algo == 'lfu': p.times_used += 1
                continue

            self.faults[algo] += 1
            new_page = Page(page_id, pid)
            new_page.last_used = now

            def fifo(s): return s[0]
            def lru(s): return min(s, key=lambda p: p.last_used)
            def lfu(s): return min(s, key=lambda p: p.times_used)
            def opt(s):
                future = proc.page_order[idx:]
                for p in s:
                    try: dist = future.index(p.id)
                    except: return p
                    if 'best' not in locals() or dist > best[0]:
                        best = (dist, p)
                return best[1] if 'best' in locals() else s[0]

            strategy = {'fifo': fifo, 'lru': lru, 'lfu': lfu, 'optimal': opt}[algo]
            self._replace(mem, proc, algo, all_procs, strategy)
            mem.append(new_page)
