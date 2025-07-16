import threading
import random
import time

# Contadores e acumuladores globais
hit_credito = miss_credito = 0
hit_debito = miss_debito = 0
hit_consulta = miss_consulta = 0

tempo_credito = tempo_debito = tempo_consulta = 0.0

contador_lock = threading.Lock()

class ContaBancaria:
    def __init__(self, id, saldo=1000):
        self.id = id
        self.saldo = saldo
        self.lock = threading.Lock()
        self.consulta_sem = threading.Semaphore(5)
        self.consultas_ativas = 0
        self.consulta_lock = threading.Lock()

    def debito(self, valor):
        global hit_debito, miss_debito, tempo_debito

        thread_id = threading.get_ident()
        print(f"[Thread {thread_id:<6}] | tentando DÉBITO na conta {self.id}")

        start = time.time()
        if not self.lock.acquire(timeout=1):
            with contador_lock:
                miss_debito += 1
            print(f"[Thread {thread_id:<6}] | BLOQUEADA: não conseguiu DÉBITO na conta {self.id}")
            return

        try:
            print(f"[Thread {thread_id:<6}] | acessando conta {self.id} realizando operação: DÉBITO de R$ {valor}")
            time.sleep(1)
            if self.saldo >= valor:
                self.saldo -= valor
                print(f"[Conta  {self.id:<3}]    | Novo saldo após débito: R$ {self.saldo}")
            else:
                print(f"[Conta  {self.id:<3}]    | Saldo insuficiente para débito de R$ {valor}")
        finally:
            self.lock.release()
            with contador_lock:
                hit_debito += 1
                tempo_debito += time.time() - start

    def credito(self, valor):
        global hit_credito, miss_credito, tempo_credito

        thread_id = threading.get_ident()
        print(f"[Thread {thread_id:<6}] | tentando CRÉDITO na conta {self.id}")

        start = time.time()
        if not self.lock.acquire(timeout=1):
            with contador_lock:
                miss_credito += 1
            print(f"[Thread {thread_id:<6}] | BLOQUEADA: não conseguiu CRÉDITO na conta {self.id}")
            return

        try:
            print(f"[Thread {thread_id:<6}] | acessando conta {self.id} realizando operação: CRÉDITO de R$ {valor}")
            time.sleep(1)
            self.saldo += valor
            print(f"[Conta  {self.id:<3}]    | Novo saldo após crédito: R$ {self.saldo}")
        finally:
            self.lock.release()
            with contador_lock:
                hit_credito += 1
                tempo_credito += time.time() - start

    def consultar_saldo(self):
        global hit_consulta, miss_consulta, tempo_consulta

        thread_id = threading.get_ident()
        print(f"[Thread {thread_id:<6}] | tentando CONSULTA na conta {self.id}")

        start = time.time()
        if not self.consulta_sem.acquire(timeout=1):
            with contador_lock:
                miss_consulta += 1
            print(f"[Thread {thread_id:<6}] | BLOQUEADA: limite de consultas ativas na conta {self.id}")
            return

        with self.consulta_lock:
            self.consultas_ativas += 1
            if self.consultas_ativas == 1:
                if not self.lock.acquire(timeout=1):
                    print(f"[Thread {thread_id:<6}] | BLOQUEADA: conta {self.id} ocupada para debito/credito")
                    self.consultas_ativas -= 1
                    self.consulta_sem.release()
                    with contador_lock:
                        miss_consulta += 1
                    return

        print(f"[Thread {thread_id:<6}] | acessando conta {self.id} realizando operação: CONSULTA DE SALDO")
        print(f"[Conta  {self.id:<3}]    | Saldo atual: R$ {self.saldo}")
        time.sleep(1)

        with self.consulta_lock:
            self.consultas_ativas -= 1
            if self.consultas_ativas == 0:
                self.lock.release()

        self.consulta_sem.release()

        with contador_lock:
            hit_consulta += 1
            tempo_consulta += time.time() - start


def operacao_randomica():
    while True:
        conta = random.choice(contas)
        tipo = random.choice(["credito", "debito", "consulta"])
        valor = random.randint(10, 200)

        if tipo == "credito":
            conta.credito(valor)
        elif tipo == "debito":
            conta.debito(valor)
        else:
            conta.consultar_saldo()

        time.sleep(0.1)


# Inicialização
contas = [ContaBancaria(i) for i in range(3)]
threads = []
for i in range(10):
    t = threading.Thread(target=operacao_randomica, name=f"T{i}")
    t.daemon = True # Mata as threads quando o programa principal é encerrado (demoníaco ( ͡° ͜ʖ ͡°))
    t.start()
    threads.append(t)

# Execução por tempo limitado
try:
    time.sleep(10)
except KeyboardInterrupt:
    pass


def mostrar_relatorio():
    print("\n======= RELATÓRIO FINAL =======")
    def media(t, h): return (t / h) if h > 0 else 0
    # Tempo médio mostra o tempo das operações bem sucedidas
    print(f"CRÉDITOS:  {hit_credito} sucessos | {miss_credito} bloqueios | tempo médio: {media(tempo_credito, hit_credito):.3f}s")
    print(f"DÉBITOS:   {hit_debito} sucessos  | {miss_debito} bloqueios  | tempo médio: {media(tempo_debito, hit_debito):.3f}s")
    print(f"CONSULTAS: {hit_consulta} sucessos | {miss_consulta} bloqueios | tempo médio: {media(tempo_consulta, hit_consulta):.3f}s")
    print("================================\n")

mostrar_relatorio()
print("Encerrando simulação.")
