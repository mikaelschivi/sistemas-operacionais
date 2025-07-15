import threading
import time
import random

NUM_CHAIRS = 0
IS_RUNNING = True

mutex = threading.Lock()
client_arrived = threading.Semaphore(0)
barber_ready = threading.Semaphore(0)

waiting_clients = 0

def do_sleep():
    time.sleep(random.uniform(0.1, 0.5))

def cut_hair():
    print("Barbeiro está cortando cabelo.")
    do_sleep()
    print("Barbeiro terminou o corte.")

def barber_thread():
    global waiting_clients, IS_RUNNING

    while IS_RUNNING:
        client_arrived.acquire()

        if not IS_RUNNING:
            break

        with mutex:
            waiting_clients -= 1
            print(f"Cliente senta na cadeira do barbeiro. Clientes esperando: {waiting_clients}")

        barber_ready.release()
        cut_hair()
    print("Barbeiro foi para casa (thread finalizada).")

def client_thread(client_id):
    global waiting_clients, NUM_CHAIRS

    do_sleep()

    with mutex:
        if waiting_clients < NUM_CHAIRS:
            waiting_clients += 1
            print(f"Cliente {client_id+1} chegou e está esperando. Clientes esperando: {waiting_clients}")
            client_arrived.release()
        else:
            print(f"Cliente {client_id+1} chegou e foi embora (sem cadeira).")
            return

    barber_ready.acquire()
    print(f"Cliente {client_id+1} está sendo atendido.")

if __name__ == "__main__":
    NUM_CHAIRS = int(input("Número de cadeiras? "))

    t_barber = threading.Thread(target=barber_thread)
    t_barber.start()

    max_clients = NUM_CHAIRS * 2
    client_threads = []
    for i in range(max_clients):
        t_client = threading.Thread(target=client_thread, args=(i,))
        client_threads.append(t_client)
        t_client.start()

    for t in client_threads:
        t.join()

    IS_RUNNING = False
    client_arrived.release()
    t_barber.join()

    print("\ndone")