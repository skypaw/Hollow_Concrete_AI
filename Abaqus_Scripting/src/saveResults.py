import numpy as np


def save_to_csv(results_array, name):
    """"Save to csv
    ===============

    Saving passed data to specific csv file using numpy
    """

    try:
        np.savetxt("%s.csv" % name, results_array, delimiter=",", fmt='% s')

    except IOError:
        print('Problem with results.csv file')
