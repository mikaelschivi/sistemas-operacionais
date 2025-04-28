import os
import sys
from time import sleep
import random

# isso foi feito no dedo ta
# so ta em ingles por costume

def is_even(n):
    return n%2 == 0

def collatz_conjecture(x):
    print(x, end=" ")
    while(x > 1):
        if is_even(x):
            x = x/2
        else:
            x = 3 * x + 1
        print(f" -> {x}", end=" ")

def get_number(pid: int):
    return (pid % 1000) // 10

if __name__ == "__main__":
    n = int(input("number of process to create: "))

    for _ in range(n):
        c = os.fork()

        if c != 0:
            os.waitpid(c, 0)
    
        if c == 0:
            print("\n\nim child")
            
            pid = os.getpid()
            p = get_number(pid)
            print(f"\npid: {pid} | n: {p}")
            collatz_conjecture(p)
            
            # Como o print do python eh buffered, se matarmos o processo filho sem dar esse flush
            # O print da conjectura nao eh feito
            sys.stdout.flush()
            # Da exit no processo filho assim que terminar
            os._exit(0)