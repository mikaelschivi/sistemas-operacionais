import threading
import time
import random

N = 5
is_running = True
estados = ["PENSANDO"] * N
mutex = threading.Semaphore(1)
semaforos = [threading.Semaphore(0) for _ in range(N)]

def get_left(i):
    # forma de fila, quando i = 0: i-1 = N
    return (i + N - 1) % N 

def get_right(i):
    # forma de fila, quando i + 1 > N retorna i=0
    return (i + 1) % N

def release_if_done(i):
    if estados[i] == "FAMINTO" and estados[get_left(i)] != "COMENDO" and estados[get_right(i)] != "COMENDO":
        estados[i] = "COMENDO"
        semaforos[i].release()

def lock_hashi(i):
    with mutex:
        estados[i] = "FAMINTO"
        release_if_done(i)
    semaforos[i].acquire()

def free_hashi(i):
    with mutex:
        estados[i] = "PENSANDO"
        release_if_done(get_left(i))
        release_if_done(get_right(i))

def filosofo(i):
    while is_running:
        j = i+1
        print(f"Filósofo {j} está pensando.")
        time.sleep(random.uniform(0.5, 1.5))
        print(f"Filósofo {j} está com fome.")
        print(f"Filósofo {j} está esperando hashis.")
        lock_hashi(i)
        print(f"\nFilósofo {j} pegou hashis.")
        print(f"Filósofo {j} está comendo.")
        time.sleep(random.uniform(0.5, 1.0))
        print(f"Filósofo {j} terminou de comer.")
        free_hashi(i)
        print(f"Filósofo {j} largou hashis.")

if __name__ == "__main__":
    threads = []
    for i in range(N):
        t = threading.Thread(target=filosofo, args=(i,))
        threads.append(t)
        t.start()

    try:
        time.sleep(2)
    finally:
        is_running = False
        for s in semaforos:
            s.release()
        for t in threads:
            t.join()

    print("\ndone")