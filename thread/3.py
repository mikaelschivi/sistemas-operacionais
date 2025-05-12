import random
import threading

def transpose_section(a, b, start_col, end_col, thread_id, lock):
    for i in range(start_col, end_col):
        for j in range(len(a)):
            b[i][j] = a[j][i]
    
    with lock:
        print(f"\nTHREAD {thread_id + 1} -> transpôs colunas {start_col} até {end_col - 1}")

def print_matrix(matrix, level=2):
    indent = '    ' * level
    for row in matrix:
        print(indent + " ".join(f"{num:4}" for num in row))

if __name__ == '__main__':
    M = int(input("insira o tamanho M da matriz (colunas): "))
    N = int(input("insira o tamanho N da matriz (linhas): "))
    T = int(input("insira o numero de threads: "))

    a = [[random.randint(0, 100) for _ in range(M)] for _ in range(N)]
    b = [[0 for _ in range(N)] for _ in range(M)]  #  resultado

    print("\nMatriz A:")
    print_matrix(a)

    threads = []
    lock = threading.Lock()
    thread_range = M // T
    extra = M % T
    start = 0

    for thread_id in range(T):
        end = start + thread_range + (1 if thread_id < extra else 0)
        t = threading.Thread(target=transpose_section,
                             args=(a, b, start, end, thread_id, lock))
        threads.append(t)
        t.start()
        start = end

    for t in threads:
        t.join()

    print("\nMatriz B (transposta):")
    print_matrix(b)
