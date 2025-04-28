import random
import threading
import time

def sum(thread_id, a, b):
    print(f"\nTHREAD {thread_id + 1}:")
    print("    matriz A:")
    print_matrix(a)
    print("    matriz B:")
    print_matrix(b)
    c = []
    for col in range(len(a)):
        row = []
        for row_idx in range(len(a[col])):
            row.append(a[col][row_idx] + b[col][row_idx])
        c.append(row)

    print(f"\nTHREAD {thread_id + 1} RESULT:")    
    print("    matriz C")
    print_matrix(c, 2)

def print_matrix(matrix, level=2):
    for row in matrix:
        for num in row:
            print( '    ' * level , num, end=" ")
        print()

if __name__ == "__main__":
    M = int(input("insira o tamanho M da matriz: "))
    N = int(input("insira o tamanho N da matriz: "))
    T = int(input("insira o numero de threads: "))
    
    threads = []
    for id in range(T):    
        a = [[random.randint(0, 100) for col in range(M)] for row in range(N)]
        b = [[random.randint(0, 100) for col in range(M)] for row in range(N)]

        t = threading.Thread(target=sum, args=(id, a,b,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
