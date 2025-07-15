import threading
import time
import random

# Capacidade do buffer
BUFFER_SIZE = 5
buffer = []

# Semáforos
empty_slots = threading.Semaphore(BUFFER_SIZE)
full_slots = threading.Semaphore(0)

# Mutex para exclusão mútua
mutex = threading.Lock()

#produtor gera a informação
def produtor(id):
    while True:
        item = random.randint(1, 100)
        empty_slots.acquire()
        mutex.acquire()                # Exclusao mútua para acessar o buffer

        buffer.append(item)      # Insere o item no buffer
        print(f"Produtor {id} produziu: {item} | Buffer: {buffer}")

        mutex.release()        # Libera o acesso ao buffer
        full_slots.release()           # Incrementa o contador de itens disponíveis
        time.sleep(random.random())

#consumidor responsavel por cinsumir a informação
def consumidor(id):
    while True:
        full_slots.acquire()        # Espera por itens no buffer
        mutex.acquire()                # Exclusão mútua para acessar o buffer

        item = buffer.pop(0)
        print(f"Consumidor {id} consumiu: {item} | Buffer: {buffer}")

        mutex.release()
        empty_slots.release()      # Incrementa o contador de espaços disponíveis
        time.sleep(random.random())    # Simula tempo de consumo

#Criação de threads para produtores e consumidores
produtores = [threading.Thread(target=produtor, args=(i,)) for i in range(2)]
consumidores = [threading.Thread(target=consumidor, args=(i,)) for i in range(2)]

# Inicia as threads
for p in produtores:
    p.start()
for c in consumidores:
    c.start()

# Aguarda as threads
for p in produtores:
    p.join()
for c in consumidores:
    c.join()