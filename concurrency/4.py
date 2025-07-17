import threading
import random
import time

# ======= Contadores globais para estatísticas das operações =======
hit_credito = miss_credito = 0
hit_debito = miss_debito = 0
hit_consulta = miss_consulta = 0

tempo_credito = tempo_debito = tempo_consulta = 0.0

# Lock para proteger o acesso concorrente aos contadores globais (usado nas estatísticas)
contador_lock = threading.Lock()


# ======= Classe que representa uma conta bancária =======
class ContaBancaria:
    def __init__(self, id, saldo=1000):
        self.id = id
        self.saldo = saldo

        # Lock usado para debito e crédito
        self.lock = threading.Lock()

        # Semáforo que permite até 5 consultas simultâneas
        self.consulta_sem = threading.Semaphore(5)

        # Quantidade de consultas ativas em execução
        self.consultas_ativas = 0

        # Lock para proteger o contador de consultas_ativas (para duas threads não modificarem ao mesmo tempo)
        self.consulta_lock = threading.Lock()

    # ==== Operação de débito ====
    def debito(self, valor):
        global hit_debito, miss_debito, tempo_debito

        thread_id = threading.get_ident()
        print(f"[Thread {thread_id:<6}] | tentando DÉBITO na conta {self.id}")

        start = time.time()

        # Tenta adquirir o lock da conta com timeout de 1 segundo
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

    # ==== Operação de crédito ====
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

    # ==== Operação de consulta ====
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

        # Protege o incremento de consultas_ativas
        with self.consulta_lock:
            self.consultas_ativas += 1

            # Se for a primeira consulta, bloqueia o lock da conta (impede crédito/débito durante as consultas)
            if self.consultas_ativas == 1:
                if not self.lock.acquire(timeout=1):
                    print(f"[Thread {thread_id:<6}] | BLOQUEADA: conta {self.id} ocupada para debito/credito")
                    self.consultas_ativas -= 1
                    self.consulta_sem.release()
                    with contador_lock:
                        miss_consulta += 1
                    return

        # Realiza a consulta
        print(f"[Thread {thread_id:<6}] | acessando conta {self.id} realizando operação: CONSULTA DE SALDO")
        print(f"[Conta  {self.id:<3}]    | Saldo atual: R$ {self.saldo}")
        time.sleep(1)

        # Finaliza a consulta, decrementando o contador
        with self.consulta_lock:
            self.consultas_ativas -= 1

            # Se for a última consulta ativa, libera o lock da conta
            if self.consultas_ativas == 0:
                self.lock.release()

        # Libera o semáforo para permitir novas consultas
        self.consulta_sem.release()

        with contador_lock:
            hit_consulta += 1
            tempo_consulta += time.time() - start


# ==== Função que cada thread executa ====
def operacao_randomica():
    while True:
        conta = random.choice(contas)
        tipo = random.choice(["credito", "debito", "consulta"])
        #tipo = "consulta"     #Linha para testes de bloqueios
        valor = random.randint(10, 200)

        if tipo == "credito":
            conta.credito(valor)
        elif tipo == "debito":
            conta.debito(valor)
        else:
            conta.consultar_saldo()

        time.sleep(0.5)  # Espera entre as operações


# ==== Inicialização das contas e threads ====
contas = [ContaBancaria(i) for i in range(3)]
threads = []

for i in range(15):
    t = threading.Thread(target=operacao_randomica, name=f"T{i}")
    t.daemon = True # Mata as threads quando o programa principal é encerrado (demoníaco ( ͡° ͜ʖ ͡°))
    t.start()
    threads.append(t)
    time.sleep(1)

try:
    time.sleep(10)
except KeyboardInterrupt:
    pass


# ==== Mostra estatísticas finais ====
def mostrar_relatorio():
    print("\n===================== RELATÓRIO FINAL =====================")
    def media(t, h): return (t / h) if h > 0 else 0

    print(f"{'Operação':<10} | {'Sucessos':<9} | {'Bloqueios':<9} | {'Tempo médio':<12}")
    print("-" * 55)
    print(f"{'CRÉDITO':<10} | {hit_credito:<9} | {miss_credito:<9} | {media(tempo_credito, hit_credito):<12.3f}s")
    print(f"{'DÉBITO':<10} | {hit_debito:<9} | {miss_debito:<9} | {media(tempo_debito, hit_debito):<12.3f}s")
    print(f"{'CONSULTA':<10} | {hit_consulta:<9} | {miss_consulta:<9} | {media(tempo_consulta, hit_consulta):<12.3f}s")
    print("===========================================================\n")



mostrar_relatorio()
print("Encerrando simulação.")

