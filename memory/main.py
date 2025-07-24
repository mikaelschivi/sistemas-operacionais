from helper import Simulation
from memory import MemoryManager
from scheduler import Scheduler

if __name__ == '__main__':
    simulation = Simulation('entradaMemoria.txt')

    print(f"Algoritmo: ROUND-ROBIN | Quantum: {simulation.cpu_quantum}")
    print(f"Política de Memória: {simulation.where.upper()} | Frames: {int(simulation.page_limit)} | Alocação: {simulation.alloc_perc}%\n")

    mm = MemoryManager(
        page_limit=int(simulation.page_limit),
        locality=(simulation.where == 'local')
    )

    Scheduler(simulation.processes, simulation.cpu_quantum, mm).run()