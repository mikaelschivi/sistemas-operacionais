import os
from time import sleep
import random

# isso foi feito no dedo ta
# so ta em ingles por costume

# p | p -> vector * vector
# i | i -> vector - vector
# i | p -> vector + vector
# p | i -> all

def random_vec(dimension):
    vec = []
    for _ in range(dimension):
        vec.append(random.randint(0, 20))
    return vec

def mult(vec1, vec2):
    if len(vec1) != len(vec2):
        return 0
    prod = []
    for i in range(len(vec1)):
        prod.append(vec1[i] * vec2[i])
    return prod

def add(vec1, vec2):
    if len(vec1) != len(vec2):
        return 0
    prod = []
    for i in range(len(vec1)):
        prod.append(vec1[i] + vec2[i])
    return prod

def sub(vec1, vec2):
    if len(vec1) != len(vec2):
        return 0
    prod = []
    for i in range(len(vec1)):
        prod.append(vec1[i] - vec2[i])
    return prod

def is_even(num):
    return num%2 == 0

if __name__ == "__main__":
    d = int(input("matrix dimension [int]: "))
    
    c = os.fork()
    main = os.getpid()
    p = os.getppid()
    
    print(f"main proc {main} -> child: {c} | parent {p}")
    
    # parent
    if c != 0:
        print(f"waiting child {c}")
        x = os.waitpid(c, 0)
        print(f"child {x[0]} end")
    
    # child
    if c == 0:
        print(f"im child")
        c = os.getpid()    
        p = os.getppid()
        
        v1 = random_vec(d)
        v2 = random_vec(d)
      
        if is_even(c) and is_even(p):
            print(f"child ({c}) even | parent ({p}) even")
            print(f"MULT: {v1} * {v2}")
            print(f"RES:{mult(v1, v2)}")
        
        if not is_even(c) and not is_even(p):
            print(f"child ({c}) odd | parent ({p}) odd")
            print(f"SUB: {v1} - {v2}")
            print(f"RES: {sub(v1, v2)}")
        
        if is_even(c) and not is_even(p):
            print(f"child ({c}) even | parent ({p}) odd")
            print(f"ADD: {v1} + {v2}")
            print(f"RES: {add(v1, v2)}")
        
        if not is_even(c) and is_even(p):
            print(f"child ({c}) odd | parent ({p}) even")
            print(f"MULT: {v1} * {v2}")
            print(f"RES: {mult(v1, v2)}")
        
            print(f"\nSUB: {v1} - {v2}")
            print(f"RES: {sub(v1, v2)}")

            print(f"\nADD: {v1} + {v2}")
            print(f"RES: {add(v1, v2)}")
        sleep(0.5)