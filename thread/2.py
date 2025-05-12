import random
import threading

lock = threading.Lock()

def sum_slice(thread_id, a_slice, b_slice, result, start_row):
    with lock:
        print(f"\nTHREAD {thread_id + 1}:")
        print("    slice A:")
        print_matrix(a_slice)
        print("    slice B:")
        print_matrix(b_slice)

        for i in range(len(a_slice)):
            row_result = []
            for j in range(len(a_slice[0])):
                row_result.append(a_slice[i][j] + b_slice[i][j])
            result[start_row + i] = row_result

        print(f"THREAD {thread_id + 1} terminou.\n")

def print_matrix(matrix, level=2):
    for row in matrix:
        print('    ' * level + ' '.join(f"{num:2}" for num in row))

if __name__ == "__main__":
    M = int(input("insira o tamanho M da matriz: "))  # colunas
    N = int(input("insira o tamanho N da matriz: "))  # linhas
    T = int(input("insira o numero de threads: "))

    a = [[random.randint(0, 10) for _ in range(M)] for _ in range(N)]
    b = [[random.randint(0, 10) for _ in range(M)] for _ in range(N)]
    result = [None] * N

    print(f'\nMATRIZ A:')
    print_matrix(a, level=1)
    print(f'\nMATRIZ B:')
    print_matrix(b, level=1)

    threads = []
    slice_size = N // T if T <= N else 1
    remainder = N % T if T <= N else 0
    actual_threads = min(T, N)

    start = 0
    for i in range(actual_threads):
        end = start + slice_size + (1 if i < remainder else 0)
        a_slice = a[start:end]
        b_slice = b[start:end]

        t = threading.Thread(target=sum_slice, args=(i, a_slice, b_slice, result, start))
        t.start()
        threads.append(t)

        start = end

    for t in threads:
        t.join()

    with lock:
        print(f'\nMATRIZ RESULTADO (A + B):')
        print_matrix(result, level=1)