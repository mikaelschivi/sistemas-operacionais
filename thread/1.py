import random
import threading
import time

def cross_prod(thread_id: int, a: list, b: list) -> int: 
    if len(a) != len(b):
        print("error: os dois vetores tem de ser do mesmo tamanho")
    
    print(f"thread {thread_id + 1}\n    {a} x {b}")    
    c = []
    for i in range(len(a)):
        c.append( a[i] * b[i] )
    print(f"thread {thread_id + 1}\n    result: {c}\n")       

if __name__ == "__main__":
    N = int(input("insira o tamanho dos vetores: "))
    T = int(input("insira o numero de threads: "))

    threads = []
    for id in range(T):
        a = [random.randint(1, 100) for _ in range(N)]
        b = [random.randint(1, 100) for _ in range(N)]

        t = threading.Thread(target=cross_prod, args=(id, a,b,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()