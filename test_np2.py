import numpy as np
import time

counts = np.random.randint(1, 100, size=1_000)

start = time.time()
top_indices = np.argsort(-counts)[:1000]
print("argsort time:", time.time() - start)

start = time.time()
kth = 1000 - 1
if len(counts) > kth:
    top_indices_unsorted = np.argpartition(-counts, kth)[:1000]
    top_indices2 = top_indices_unsorted[np.argsort(-counts[top_indices_unsorted])]
else:
    top_indices2 = np.argsort(-counts)
print("argpartition time:", time.time() - start)

print("Match:", np.array_equal(-counts[top_indices], -counts[top_indices2]))
