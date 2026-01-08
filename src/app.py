import random
import time
import sys

while True:
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    result = a * b
    print(f"{a} × {b} = {result}", flush=True)
    sys.stdout.flush()
    time.sleep(5)