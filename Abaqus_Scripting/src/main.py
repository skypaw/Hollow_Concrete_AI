from odbAccess import *
from createCae import *
from readConfig import *
from saveResults import *
import os


class Main:
    file_name = None
    file_path = None

    def __init__(self):
        self.file_name = ReadConfig.file_name
        self.file_path = ReadConfig.abaqus_file_path

    def creating_model(self):
        pass

    def checking_database(self):
        full_path = self.file_path + self.file_name

        if os.path.isfile(full_path):
            pass
        else:
            CreateCae(self.file_name)

    def calculate(self):
        pass

    def save_results(self):
        SaveResults(results_array=[1,2])

    def read_odb(self):
        pass

    def modify_model(self):
        pass
