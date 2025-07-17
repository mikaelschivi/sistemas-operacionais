import threading
import time
import random

# Capacidade do buffer
tamanho_buffer = 5
buffer = []

# Semáforos
slots_vazios = threading.Semaphore(tamanho_buffer)
itens_disp = threading.Semaphore(0)

# Mutex para exclusão mútua
mutex = threading.Lock()

#produtor gera a informação
def produtor(id):
    while True:
        item = random.randint(1, 100)
        slots_vazios.acquire()
        mutex.acquire()                # Exclusao mútua para acessar o buffer

        buffer.append(item)      # Insere o item no buffer
        print(f"Produtor {id} produziu: {item} | Buffer: {buffer}")

        mutex.release()        # Libera o acesso ao buffer
        itens_disp.release()           # Incrementa o contador de itens disponíveis
        time.sleep(random.random())

#consumidor responsavel por cinsumir a informação
def consumidor(id):
    while True:
        itens_disp.acquire()        # Espera por itens no buffer
        mutex.acquire()                # Exclusão mútua para acessar o buffer

        item = buffer.pop(0)
        print(f"Consumidor {id} consumiu: {item} | Buffer: {buffer}")

        mutex.release()
        slots_vazios.release()      # Incrementa o contador de espaços disponíveis
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