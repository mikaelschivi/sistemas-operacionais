from process import Process
from round_robin import round_robin
from lottery import lottery
from priority import prioridade
from cfs import cfs_rbt

def parse_file(filename):
    with open(filename, "r") as f:
        data = f.read()
        # raw = data
        data = data.split()
    algo, cpu_time = data[0].split("|")
    
    print(algo, cpu_time)
    
    children = []
    for i in range(1, len(data)):
       created_at, pid, execution_time, priority = data[i].split("|")
       child = Process(created_at, pid, execution_time, priority)
       children.append(child)

    print(f"number of new process: {len(children)}\n")

    return algo, int(cpu_time), children

if __name__ == "__main__":
    algo, quantum, process_list = parse_file("entradaEscalonador.txt")

    for i in range(len(process_list)):
        cur = process_list[i]
        print(f"[Process {i}] execution_time: {cur.execution_time} - priority: {cur.priority}")
    print()

    if algo == "alternanciaCircular":
        round_robin(process_list, quantum)
    if algo == "prioridade":
        prioridade(process_list, quantum)
    if algo == "loteria":
        lottery(process_list, quantum)
    if algo == "CFS":
        cfs_rbt(process_list, quantum)