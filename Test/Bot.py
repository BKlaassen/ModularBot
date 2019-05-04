import time

def instance(arg):
    while True:
        with open(arg + "_out.txt", "a+") as f:
            f.write(arg)
        time.sleep(2)