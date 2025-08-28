from process import Process
from io_device import IODevice
from round_robin import round_robin

def parse_file(filename):
    devices = {}
    processes = []
    
    with open(filename, "r") as f:
        config_line = f.readline().strip()
        parts = config_line.split('|')

        algo = parts[0]
        cpu_quantum = int(parts[1])
        num_devices = int(parts[6])

        print(f"Algorithm: {algo}, Quantum: {cpu_quantum}, Devices: {num_devices}\n")

        # devices
        for _ in range(num_devices):
            device_line = f.readline().strip()
            dev_id_str, capacity, op_time = device_line.split('|')
            
            # formato "device-X"
            dev_id = int(dev_id_str.split('-')[1])

            devices[dev_id] = IODevice(dev_id, capacity, op_time)

        # process
        for line in f:
            if line.strip():
                proc_parts = line.strip().split('|')
                created_at, pid, exec_time, priority, mem_qty, seq, io_chance_percent = proc_parts
                io_chance = float(io_chance_percent) / 100.0
                child = Process(created_at, pid, exec_time, priority, mem_qty, seq, io_chance)
                processes.append(child)

    print(f"Number of new processes: {len(processes)}")
    print(f"Number of I/O devices: {len(devices)}\n")

    return algo, cpu_quantum, processes, devices

if __name__ == "__main__":
    _, quantum, process_list, device_list = parse_file("entrada_ES.txt")

    round_robin(process_list, device_list, quantum)