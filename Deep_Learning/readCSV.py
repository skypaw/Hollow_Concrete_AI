import numpy as np
from os import path


def read_batches(name):
    i = 1
    data_list = []
    while path.exists(f"resources\\batches\\{name}{float(i)}.csv"):

        array_data = np.genfromtxt(
            f"resources\\batches\\{name}{float(i)}.csv", delimiter=","
        )

        for line in array_data:

            if data_list != []:

                data_list = np.vstack([data_list, line])
            else:
                data_list = np.array(line)

        i += 50

    return data_list


def clear_full_data():
    array_data = np.genfromtxt("full_data.csv", delimiter=",")
    for line in array_data:
        if int(line[0]) >= 12001:
            line[6] = 0

    return array_data


def shuffle_data():
    array_data = np.genfromtxt("full_data.csv", delimiter=",")

    np.random.shuffle(array_data)

    return array_data


if __name__ == "__main__":
    # data_to_new = read_batches("batch_results")
    print("commented out")
    shuffle_data()

    # data_to_new=clear_full_data()

    # np.savetxt("resources\\full_data.csv", data_to_new, delimiter=",", fmt='% s')
