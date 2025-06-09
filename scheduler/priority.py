from process import state

def prioridade(processos, quantum):
    tempo_atual = 0
    prontos = []
    finalizados = []

    processos.sort(key=lambda p: p.created_at) # Sem isso os processos começam atrasados 

    while len(finalizados) < len(processos):
        # Verifica se há novos processos a cada unidade de tempo
        for p in processos:
            if p.created_at == tempo_atual and p.state == state.NEW:
                p.state = state.READY
                prontos.append(p)
                print(f"[Tempo {tempo_atual}] Processo PID {p.pid} criado e adicionado à fila de prontos.")

        # Filtra processos prontos
        fila_prontos = [p for p in prontos if p.state != state.TERMINATED and p.remaining_time > 0]
        fila_prontos.sort(key=lambda p: p.priority)

        if fila_prontos:
            processo = fila_prontos[0]
            processo.state = state.RUNNING
            tempo_exec = min(quantum, processo.remaining_time)

            print(f"[Tempo {tempo_atual}] Executando processo PID {processo.pid} com prioridade {processo.priority} por {tempo_exec} unidades de tempo. Tempo restante: {processo.remaining_time}.")

            # Avança o tempo unidade por unidade para detectar novos processos
            for _ in range(tempo_exec):
                tempo_atual += 1
                processo.remaining_time -= 1

                # Atualiza processos prontos
                for p in processos:
                    if p.created_at == tempo_atual and p.state == state.NEW:
                        p.state = state.READY
                        prontos.append(p)
                        print(f"[Tempo {tempo_atual}] Processo PID {p.pid} criado e adicionado à fila de prontos.")

                # Incrementa tempo de espera dos outros prontos
                for p in prontos:
                    if p != processo and p.state == state.READY:
                        p.wait_time += 1

                # Preempção só acontece ao final do quantum

            if processo.remaining_time == 0:
                processo.state = state.TERMINATED
                processo.completion_time = tempo_atual
                finalizados.append(processo)
                print(f"[Tempo {tempo_atual}] Processo PID {processo.pid} finalizado.")
            else:
                processo.state = state.READY
        else:
            # Nenhum processo pronto; avança o tempo
            tempo_atual += 1

    # Resultado das métricas
    print("\nResumo da Execução:")
    for p in sorted(finalizados, key=lambda p: p.pid):
        turnaround = p.completion_time - p.created_at
        print(f"PID: {p.pid} | Turnaround: {turnaround} | Tempo de Espera: {p.wait_time} | Prioridade: {p.priority}")