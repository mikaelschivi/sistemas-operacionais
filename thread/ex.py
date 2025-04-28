import logging
import threading
import time

def thread_function(id):
    logging.info("Thread %s: starting", id)
    time.sleep(2)
    logging.info("Thread %s: finishing", id)

if __name__ == "__main__":

    threads = [] #armazena os descritores das threads

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    for id in range(1,10):
        t = threading.Thread(target=thread_function, args=(id,)) #inicializa a thread, informa o nome da função e os parâmetros
        logging.info("Main    : before running thread") 
        t.start()
        threads.append(t)
        logging.info("Main    : wait for the thread %s to finish\n", id)

    for t in threads:
        t.join()

    logging.info("Main    : all done")