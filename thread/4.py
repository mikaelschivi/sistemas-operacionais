import random
import threading

lock = threading.Lock()

def matrix_multiply_section(a, b, r, start_row, end_row, thread_id, lock):
    for i in range(start_row, end_row):
        for j in range(len(b[0])):
            r[i][j] = sum(a[i][k] * b[k][j] for k in range(len(b)))

    with lock:
        print(f"\nTHREAD {thread_id + 1} -> calculou linhas {start_row} até {end_row - 1}")

def print_matrix(matrix, level=2):
    for row in matrix:
        for num in row:
            print( '    ' * level , num, end=" ")
        print()

if __name__ == "__main__":
    M = int(input("insira o tamanho M da matriz A (linhas): "))
    N = int(input("insira o tamanho N da matriz A / linhas da B: "))
    P = int(input("insira o tamanho P da matriz B (colunas): "))
    T = int(input("insira o numero de threads: "))

    a = [[random.randint(0, 100) for _ in range(N)] for _ in range(M)]
    b = [[random.randint(0, 100) for _ in range(P)] for _ in range(N)]
    r = [[0 for _ in range(P)] for _ in range(M)]

    print("\nMatriz A:")
    print_matrix(a)
    print("\nMatriz B:")
    print_matrix(b)

    lock = threading.Lock()
    threads = []
    rows_per_thread = M // T
    extra = M % T
    start = 0

    for thread_id in range(T):
        end = start + rows_per_thread + (1 if thread_id < extra else 0)
        t = threading.Thread(target=matrix_multiply_section,
                             args=(a, b, r, start, end, thread_id, lock))
        threads.append(t)
        t.start()
        start = end

    for t in threads:
        t.join()

    print("\nResultado (matriz A x B):")
    print_matrix(r)