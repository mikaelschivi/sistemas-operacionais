import random
import threading

def cross_prod(thread_id: int, a_slice: list, b_slice: list, results: list, start_idx: int): 
    if len(a_slice) != len(b_slice):
        print("error: os dois vetores têm de ser do mesmo tamanho")
        return

    print(f"thread {thread_id + 1}\n    {a_slice} x {b_slice}")    
    for i in range(len(a_slice)):
        results[start_idx + i] = a_slice[i] * b_slice[i]

    print(f"thread {thread_id + 1}\n    result: {results[start_idx:start_idx+len(a_slice)]}\n")       

if __name__ == "__main__":
    N = int(input("insira o tamanho dos vetores: "))
    a = [random.randint(1, 3) for _ in range(N)]
    b = [random.randint(1, 3) for _ in range(N)]
    T = int(input("insira o número de threads: "))
    print(f'a x b = {a} x {b}')
    
    

    results = [0] * N  # Lista para armazenar o resultado final

    slice_size = N // T
    threads = []

    for id in range(T):
        start = id * slice_size
        # A última thread pega o restante, mesmo que seja maior
        end = (id + 1) * slice_size if id != T - 1 else N

        a_slice = a[start:end]
        b_slice = b[start:end]

        t = threading.Thread(target=cross_prod, args=(id, a_slice, b_slice, results, start))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"\na: {a}")
    print(f"b: {b}")
    print(f"produto elemento a elemento: {results}")
