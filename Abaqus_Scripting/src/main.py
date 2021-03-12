from odbAccess import *
from createCae import *
from saveResults import *
from readConfig import *
from readOdb import *
import os


class Main:
    __file_name = None
    __file_path = None
    __full_path = None
    __results = None

    def __init__(self):
        config()

    def full_path(self, extension):
        __full_path = self.__file_path + self.__file_name + extension

    def creating_model(self):
        pass

    def checking_database(self):
        """Checking database
        ====================

        Function responsible for checking if there is specific database.
        If there is no database -> creating a new cea database for model

        Possible databases:
        1. cea
        """

        if os.path.isfile(self.__full_path) is False:
            CreateCae(self.__full_path)



    def calculate(self):
        """Calculate
        ============

        Function responsible for creating a job for specific model in cea database.
        """

        pass

    def read_odb(self):
        """Read Odb
        ===========

        Function responsible for reading results from completed job.
        """

        result = read_odb()
        self.__results = result

    def save_results(self):
        """"Save results
        ================

        Function for saving results of the calculation to csv file
        """

        save_to_csv(self.__results)

    def modify_model(self):
        """Modify model
        ===============

        Function responsible for modifying existing model in cea database
        """

        pass
