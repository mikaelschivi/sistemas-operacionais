import os
from time import sleep
import random

# isso foi feito no dedo ta
# so ta em ingles por costume

if __name__ == "__main__":
    c = os.fork()
    main = os.getpid()
    p = os.getppid()
    print(f"main proc {main} -> child: {c} | parent {p}")
    
    if c != 0:
        print(f"waiting child {c}")
        x = os.waitpid(c, 0)
        print(f"child {x[0]} end")

    else:
        print(f"\nim child")
        sleep(0.5)
        
        d = int(input("select vector dimension N: "))
        
        n1 = []
        n2 = []
        for _ in range(d):
            n1.append(random.randint(0, 100))
            n2.append(random.randint(0, 1000))

        print(f"{n1} x {n2}")
        
        prod = []
        for i in range(d):
            prod.append(n1[i] * n2[i])
        print(f"result: {prod}")

        print(f"child finished\n")
        
        sleep(0.5)
