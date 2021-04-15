import numpy as np


def read_csv(name):
    array_data = np.genfromtxt(f"resources\\{name}.csv", delimiter=" ")
    return array_data


print(read_csv('results'))
print(read_csv('dimensions'))
