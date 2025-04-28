import random
import threading

def transpose(thread_id, a):
    print(f"\nTHREAD {thread_id + 1}:")
    print("    matriz A:")
    print_matrix(a)
    
    b = [[row[i] for row in a] for i in range(len(a[0]))]
    print(f"\nTHREAD {thread_id + 1} RESULT:")    
    print("    matriz B")
    print_matrix(b)

def print_matrix(matrix, level=2):
    for row in matrix:
        for num in row:
            print( '    ' * level , num, end=" ")
        print()

if __name__ == '__main__':
    M = int(input("insira o tamanho M da matriz: "))
    N = int(input("insira o tamanho N da matriz: "))
    T = int(input("insira o numero de threads: "))
    
    threads = []
    for id in range(T):    
        a = [[random.randint(0, 100) for col in range(M)] for row in range(N)]

        t = threading.Thread(target=transpose, args=(id, a,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
