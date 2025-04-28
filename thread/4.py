import random
import threading

lock = threading.Lock()

def mult_matrix(thread_id, a, b):
    with lock:  # só uma thread por vez faz isso
        print(f"\n\nTHREAD {thread_id + 1}:")
        print("    matriz A:")
        print_matrix(a)
        
        print("    matriz B:")
        print_matrix(b)
        
        r = [[0 for _ in range(len(b[0]))] for _ in range(len(a))]
        for i in range(len(a)):
            for j in range(len(b[0])):
                for k in range(len(b)):
                    r[i][j] += a[i][k] * b[k][j]
        
        print(f"\nTHREAD {thread_id + 1} RESULT:")    
        print("    resultado:")
        print_matrix(r)

def print_matrix(matrix, level=2):
    for row in matrix:
        for num in row:
            print( '    ' * level , num, end=" ")
        print()

if __name__ == "__main__":
    M = int(input("insira o tamanho M da matriz: "))
    N = int(input("insira o tamanho N da matriz: "))
    P = int(input("insira o tamanho P da matriz: "))
    if M == P:
        print("M não pode ser igual a P")
        exit()

    T = int(input("insira o numero de threads: "))
    
    threads = []
    for id in range(T):    
        a = [[random.randint(0, 100) for col in range(N)] for row in range(M)]
        b = [[random.randint(0, 100) for col in range(P)] for row in range(N)]

        t = threading.Thread(target=mult_matrix, args=(id, a,b,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
