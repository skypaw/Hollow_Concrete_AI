import numpy as np


class SaveResults:
    __results_array = None

    def __init__(self, results_array):
        self.__results_array = results_array
        self.__save_to_csv()

    def __save_to_csv(self):
        """"Save to csv
        ===============

        Saving passed data to specific csv file using numpy
        """

        try:
            np.savetxt('results.csv', self.__results_array, delimiter=" ", fmt='% s')

        except IOError:
            print ('Problem with results.csv file')
