from joblib import load
import numpy as np

import time

start = time.time()

clf = load("testmodel3.joblib")

array_data = np.genfromtxt("resources/batches/batch_results151.0.csv", delimiter=",")


X = array_data[:, 2:7]

X = X[0][:]
first = False

for i in np.linspace(0.1, 0.2, 5):
    if not first:
        X = np.insert(X, 0, i, axis=0)
        first = True
    if first:
        X[0] = i

    print(X)
    info = clf.predict([X])
    print(info)


end = time.time()

print(end - start)
