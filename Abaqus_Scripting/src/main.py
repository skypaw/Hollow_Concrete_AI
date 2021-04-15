from odbAccess import *
from saveResults import *
from readOdb import *
from createModel import *
import os
from createModel import CreateModel
from log import log
import time


class Main:
    __file_name = None
    __file_path = None
    __full_path = None
    __results = []
    __dimensions = []
    __model_database = None

    model_object = None
    __i = None

    def __init__(self):
        self.model_object = CreateModel()

    def creating_model(self):
        self.model_object.create_database()

    def read_odb(self):
        """Read Odb
        ===========

        Function responsible for reading results from completed job.
        """

        result = read_odb(self.__i)
        self.__results.append(result)

        '''if os.path.exists('C:\\temp\\HC-Slab-Job-{}.odb'.format(self.__i)):
            os.remove('C:\\temp\\HC-Slab-Job-{}.com'.format(self.__i))
            os.remove('C:\\temp\\HC-Slab-Job-{}.dat'.format(self.__i))
            os.remove('C:\\temp\\HC-Slab-Job-{}.inp'.format(self.__i))
            os.remove('C:\\temp\\HC-Slab-Job-{}.log'.format(self.__i))
            os.remove('C:\\temp\\HC-Slab-Job-{}.msg'.format(self.__i))
            #os.remove('C:\\temp\\HC-Slab-Job-{}.odb'.format(self.__i))
            os.remove('C:\\temp\\HC-Slab-Job-{}.prt'.format(self.__i))
            os.remove('C:\\temp\\HC-Slab-Job-{}.sim'.format(self.__i))
            os.remove('C:\\temp\\HC-Slab-Job-{}.sta'.format(self.__i))'''

    def save_results(self):
        """"Save results
        ================

        Function for saving results of the calculation to csv file
        """

        save_to_csv(self.__results, 'results')

    def save_dimensions(self):
        save_to_csv(self.__dimensions, 'dimensions')

    def read_dimensions(self):
        self.__dimensions.append(self.model_object.save_dimensions())

    def modify_model(self, a, h, a_s, as1, r, l, c_nom):
        self.__i = self.model_object.i
        self.model_object.dimensions_setter(a, h, a_s, as1, r, l, c_nom)
