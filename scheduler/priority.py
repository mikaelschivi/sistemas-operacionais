from process import state

def prioridade(processos, quantum):
    tempo_atual = 0
    prontos = []
    finalizados = []
    prioridadeMinima = 1

    def adicionar_processos_novos():
        for p in processos:
            if p.created_at == tempo_atual and p.state == state.NEW:
                p.state = state.READY
                prontos.append(p)
                print(f"[Tempo {tempo_atual}] Processo PID {p.pid} criado e adicionado à fila de prontos.")

    while len(finalizados) < len(processos):
        adicionar_processos_novos()

        # Filtra processos prontos
        fila_prontos = [p for p in prontos if p.state != state.TERMINATED and p.remaining_time > 0]
        fila_prontos.sort(key=lambda p: p.priority)

        if fila_prontos:
            processo = fila_prontos[0]
            processo.state = state.RUNNING
            tempo_exec = min(quantum, processo.remaining_time)

            print(f"[Tempo {tempo_atual}] Executando processo PID {processo.pid} com prioridade {processo.priority} por {tempo_exec} unidades de tempo. Tempo restante: {processo.remaining_time}.")

            for _ in range(tempo_exec):
                tempo_atual += 1
                processo.remaining_time -= 1

                adicionar_processos_novos()

                # Aging
                for p in prontos:
                    if p != processo and p.state == state.READY and p.priority > prioridadeMinima:
                        p.priority -= 1

            if processo.remaining_time == 0:
                processo.state = state.TERMINATED
                processo.completion_time = tempo_atual
                finalizados.append(processo)
                prontos.remove(processo)
                print(f"[Tempo {tempo_atual}] Processo PID {processo.pid} finalizado.")
            else:
                processo.state = state.READY
        else:
            tempo_atual += 1

    print("\nResumo da Execução:")
    for p in sorted(finalizados, key=lambda p: int(p.pid)):
        turnaround = p.completion_time - int(p.created_at)
        print(f"PID: {int(p.pid):>2} | Turnaround: {turnaround:>4} | Tempo de Espera: {p.wait_time:>4} | Prioridade: {p.priority:>3}")

    return finalizados
