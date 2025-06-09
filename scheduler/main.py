from process import Process
from round_robin import round_robin
from lottery import lottery
from priority import prioridade

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

    print(f"number of new process: {len(children)}")

    return algo, int(cpu_time), children

if __name__ == "__main__":
    algo, quantum, process_list = parse_file("entradaEscalonador.txt")

    if algo == "alternanciaCircular":
        round_robin(process_list, quantum)
    if algo == "prioridade":
        prioridade(process_list, quantum)
    if algo == "loteria":
        lottery(process_list, quantum)
    if algo == "CFS":
        ...