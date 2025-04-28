import os

# isso foi feito no dedo ta
# so ta em ingles por costume

if __name__ == "__main__":
    c = os.fork()
    msg = "hello world"
    if c != 0:
        print("waiting for child..")
        os.waitpid(c, 0)
    else:
        print("im child")
        os.execl("/bin/echo", "echo", msg)

    print("end process")