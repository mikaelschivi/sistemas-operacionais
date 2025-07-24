from helper import Page
import time

class MemoryManager:
    def __init__(self, page_limit, locality):
        self.limit = page_limit
        self.local = locality
        self.memory = {algo: [] for algo in ['fifo', 'lru', 'lfu', 'optimal']}
        self.faults = {algo: 0 for algo in self.memory}

        self.strategies = {
            'fifo': self._select_fifo,
            'lru': self._select_lru,
            'lfu': self._select_lfu,
            'optimal': self._select_optimal
        }

    # procura uma pagina especifica na memoria de um algoritmo
    def _find_page(self, mem, pid, page_id):
        return next((p for p in mem if p.id == page_id and p.process_pid == pid), None)

    # fifo: retorna a primeira pagina da lista (a mais antiga)
    def _select_fifo(self, pages, *_):
        return pages[0]

    # lru: retorna a pagina com o timestamp de ultimo uso mais antigo
    def _select_lru(self, pages, *_):
        return min(pages, key=lambda p: p.last_used)

    # lfu: retorna a pagina menos usada. usa o id da pagina como criterio de desempate.
    def _select_lfu(self, pages, *_):
        return min(pages, key=lambda p: (p.times_used, p.id))

    # otimo: retorna a pagina que sera usada o mais tarde possivel no futuro.
    def _select_optimal(self, pages, proc, idx):
        future = proc.page_order[idx:]  # sequencia de acessos futuros
        best = None
        
        for p in pages:
            try:
                dist = future.index(p.id)  # encontra a proxima ocorrencia da pagina
            except ValueError:
                return p  # se a pagina nao for mais usada, e a vitima ideal
            
            # procura a pagina cuja proxima utilizacao esta mais distante
            if best is None or dist > best[0]:
                best = (dist, p)
        
        return best[1] if best else pages[0]

    # remove uma pagina se a memoria estiver cheia
    def _evict_if_needed(self, mem, proc, algo, all_procs, selector, access_idx):
        # verifica se a remocao e necessaria
        if len(mem) < self.limit and proc.pages_in_memory[algo] < proc.page_amount_limit:
            return
        
        candidate_space = [p for p in mem if p.process_pid == proc.pid] if self.local else mem
        
        # se a politica e local mas o processo nao tem paginas, usa o escopo global
        if not candidate_space:
            candidate_space = mem
        
        victim = selector(candidate_space, proc, access_idx)  # seleciona a vitima
        mem.remove(victim)
        
        # atualiza a contagem de paginas para o processo dono da pagina removida
        for p in all_procs:
            if p.pid == victim.process_pid:
                p.pages_in_memory[algo] -= 1
                break

    # simula um acesso a uma pagina de memoria
    def access(self, proc, all_procs):
        if proc.page_order_index >= len(proc.page_order):
            return

        page_id = proc.page_order[proc.page_order_index]
        access_idx = proc.page_order_index
        proc.page_order_index += 1
        now = time.time()

        # executa a simulacao para cada algoritmo
        for algo, mem in self.memory.items():
            page = self._find_page(mem, proc.pid, page_id)
            
            # page hit
            if page:
                if algo == 'lru':
                    page.last_used = now
                elif algo == 'lfu':
                    page.times_used += 1
                continue

            # page fault
            self.faults[algo] += 1
            new_page = Page(page_id, proc.pid)
            new_page.last_used = now

            selector = self.strategies[algo]
            # remove uma pagina, se necessario, antes de adicionar a nova
            self._evict_if_needed(mem, proc, algo, all_procs, selector, access_idx)

            mem.append(new_page)
            proc.pages_in_memory[algo] += 1